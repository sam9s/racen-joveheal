"""
JoveHeal Wellness Chatbot - Main Streamlit Application

A RAG-based chatbot for JoveHeal wellness coaching business.
Provides information about programs, services, and offerings.
"""

import streamlit as st
import uuid
from datetime import datetime

from chatbot_engine import (
    generate_response,
    get_greeting_message,
    check_knowledge_base_status
)
from knowledge_base import (
    initialize_knowledge_base,
    ingest_pdf_file,
    ingest_text_file,
    get_knowledge_base_stats,
    clear_knowledge_base,
    ingest_website_content
)
from conversation_logger import (
    log_conversation,
    get_recent_logs,
    get_flagged_conversations,
    get_conversation_stats
)

st.set_page_config(
    page_title="JoveHeal Assistant",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .stApp {
        max-width: 800px;
        margin: 0 auto;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
    }
    .assistant-message {
        background-color: #f5f5f5;
    }
    .source-tag {
        font-size: 0.75rem;
        color: #666;
        margin-top: 0.5rem;
    }
    .status-badge {
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.8rem;
    }
    .status-ready {
        background-color: #c8e6c9;
        color: #2e7d32;
    }
    .status-loading {
        background-color: #fff3e0;
        color: #ef6c00;
    }
</style>
""", unsafe_allow_html=True)

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "kb_initialized" not in st.session_state:
    st.session_state.kb_initialized = False

if "show_admin" not in st.session_state:
    st.session_state.show_admin = False


def initialize_kb_if_needed():
    """Initialize knowledge base on first run."""
    if not st.session_state.kb_initialized:
        status = check_knowledge_base_status()
        if not status["ready"]:
            with st.spinner("Setting up knowledge base... This may take a few minutes on first run."):
                success = initialize_knowledge_base()
                st.session_state.kb_initialized = success
        else:
            st.session_state.kb_initialized = True


def render_chat_interface():
    """Render the main chat interface."""
    st.title("JoveHeal Assistant")
    st.markdown("*Your guide to wellness coaching programs and services*")
    
    status = check_knowledge_base_status()
    if status["ready"]:
        st.markdown(f'<span class="status-badge status-ready">Knowledge Base Ready ({status["chunks"]} documents)</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-badge status-loading">Knowledge Base Loading...</span>', unsafe_allow_html=True)
    
    st.divider()
    
    if not st.session_state.messages:
        greeting = get_greeting_message()
        st.session_state.messages.append({
            "role": "assistant",
            "content": greeting
        })
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sources"):
                sources_text = " | ".join(message["sources"][:3])
                st.caption(f"Sources: {sources_text}")
    
    if prompt := st.chat_input("Ask me about JoveHeal's programs and services..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = generate_response(
                    user_message=prompt,
                    conversation_history=st.session_state.messages[:-1]
                )
                
                response = result["response"]
                sources = result.get("sources", [])
                safety_triggered = result.get("safety_triggered", False)
                
                st.markdown(response)
                
                if sources and not safety_triggered:
                    sources_text = " | ".join(sources[:3])
                    st.caption(f"Sources: {sources_text}")
                
                log_conversation(
                    session_id=st.session_state.session_id,
                    user_question=prompt,
                    bot_answer=response,
                    safety_flagged=safety_triggered,
                    safety_category=result.get("safety_category")
                )
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "sources": sources
                })


def render_admin_panel():
    """Render the admin panel for knowledge base management."""
    st.title("Admin Panel")
    st.markdown("*Manage knowledge base and view conversation logs*")
    
    if st.button("Back to Chat", key="back_to_chat"):
        st.session_state.show_admin = False
        st.rerun()
    
    st.divider()
    
    tab1, tab2, tab3 = st.tabs(["Knowledge Base", "Upload Documents", "Conversation Logs"])
    
    with tab1:
        st.subheader("Knowledge Base Status")
        
        stats = get_knowledge_base_stats()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Chunks", stats["total_chunks"])
            st.metric("Website Pages", stats.get("website_pages", 0))
        with col2:
            last_scrape = stats.get("last_scrape", "Never")
            if last_scrape and last_scrape != "Never":
                try:
                    dt = datetime.fromisoformat(last_scrape)
                    last_scrape = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    pass
            st.metric("Last Website Scrape", last_scrape)
            st.metric("Documents Uploaded", len(stats.get("documents", [])))
        
        st.divider()
        
        st.subheader("Actions")
        
        if st.button("Clear Knowledge Base", type="secondary"):
            if st.session_state.get("confirm_clear"):
                clear_knowledge_base()
                st.session_state.kb_initialized = False
                st.session_state.confirm_clear = False
                st.success("Knowledge base cleared!")
                st.rerun()
            else:
                st.session_state.confirm_clear = True
                st.warning("Click again to confirm clearing all knowledge base content.")
        
        if stats.get("documents"):
            st.subheader("Uploaded Documents")
            for doc in stats["documents"]:
                st.text(f"- {doc['filename']} ({doc['type']}, {doc['chunks']} chunks)")
    
    with tab2:
        st.subheader("Upload Documents")
        st.markdown("Upload PDF or text files to expand the knowledge base.")
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["pdf", "txt"],
            help="Upload PDF or TXT files containing JoveHeal information"
        )
        
        if uploaded_file is not None:
            if st.button("Process Document"):
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    import tempfile
                    import os
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name
                    
                    try:
                        if uploaded_file.name.lower().endswith('.pdf'):
                            chunks = ingest_pdf_file(tmp_path, uploaded_file.name)
                        else:
                            chunks = ingest_text_file(tmp_path, uploaded_file.name)
                        
                        if chunks > 0:
                            st.success(f"Successfully added {chunks} chunks from {uploaded_file.name}!")
                        else:
                            st.warning("No content could be extracted from the file.")
                    finally:
                        os.unlink(tmp_path)
        
        st.divider()
        st.subheader("Instructions")
        st.markdown("""
        **How to update the knowledge base:**
        
        1. **Website Content**: Click "Refresh Website Content" to re-scrape the JoveHeal website
        2. **PDF Documents**: Upload PDF files (brochures, program guides, FAQs)
        3. **Text Files**: Upload .txt files with additional information
        
        The chatbot will use all this content to answer visitor questions.
        """)
    
    with tab3:
        st.subheader("Conversation Statistics")
        
        conv_stats = get_conversation_stats()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Conversations", conv_stats["total_conversations"])
        with col2:
            st.metric("Unique Sessions", conv_stats["unique_sessions"])
        with col3:
            st.metric("Safety Flags", conv_stats["safety_flags"])
        
        st.divider()
        
        st.subheader("Recent Conversations")
        logs = get_recent_logs(limit=20)
        
        if logs:
            for log in reversed(logs[-10:]):
                with st.expander(f"{log['timestamp'][:19]} - {log['user_question'][:50]}..."):
                    st.markdown(f"**User:** {log['user_question']}")
                    st.markdown(f"**Bot:** {log['bot_answer']}")
                    if log.get("safety_flagged"):
                        st.warning(f"Safety flagged: {log.get('safety_category', 'Unknown')}")
        else:
            st.info("No conversation logs yet.")
        
        st.divider()
        
        st.subheader("Flagged Conversations")
        flagged = get_flagged_conversations()
        
        if flagged:
            for log in flagged[-10:]:
                with st.expander(f"[FLAGGED] {log['timestamp'][:19]}"):
                    st.markdown(f"**Category:** {log.get('safety_category', 'Unknown')}")
                    st.markdown(f"**User:** {log['user_question']}")
                    st.markdown(f"**Bot:** {log['bot_answer']}")
        else:
            st.success("No flagged conversations.")


def main():
    """Main application entry point."""
    initialize_kb_if_needed()
    
    with st.sidebar:
        st.markdown("### Navigation")
        if st.button("Chat", use_container_width=True):
            st.session_state.show_admin = False
            st.rerun()
        if st.button("Admin Panel", use_container_width=True):
            st.session_state.show_admin = True
            st.rerun()
        
        st.divider()
        
        st.markdown("### About")
        st.markdown("""
        This chatbot provides information about JoveHeal's wellness coaching programs and services.
        
        For bookings or personal inquiries, please visit [joveheal.com](https://www.joveheal.com)
        """)
        
        if st.button("New Conversation"):
            st.session_state.messages = []
            st.session_state.session_id = str(uuid.uuid4())
            st.rerun()
    
    if st.session_state.show_admin:
        render_admin_panel()
    else:
        render_chat_interface()


if __name__ == "__main__":
    main()
