"""
SOMERA Admin Dashboard - Voice Analytics & Coaching Insights

A beautiful analytics dashboard for SOMERA Voice and Text coaching sessions.
Tracks transcripts, readiness scores, latency metrics, and coaching patterns.
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor

st.set_page_config(
    page_title="SOMERA Admin",
    page_icon="💜",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        color: #6b7280;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f5f3ff 0%, #fdf4ff 100%);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid #e9d5ff;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #7c3aed;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .transcript-card {
        background: white;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #8b5cf6;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .user-message {
        background: linear-gradient(135deg, #ede9fe 0%, #fae8ff 100%);
        border-radius: 12px;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        border-left: 3px solid #a855f7;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #f0fdf4 0%, #ecfeff 100%);
        border-radius: 12px;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        border-left: 3px solid #10b981;
    }
    
    .readiness-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .readiness-explore {
        background: #dbeafe;
        color: #1e40af;
    }
    
    .readiness-transition {
        background: #fef3c7;
        color: #92400e;
    }
    
    .readiness-guide {
        background: #d1fae5;
        color: #065f46;
    }
    
    .latency-good {
        color: #10b981;
    }
    
    .latency-ok {
        color: #f59e0b;
    }
    
    .latency-slow {
        color: #ef4444;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f5f3ff 0%, #fdf4ff 100%);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f5f3ff;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%);
        color: white;
    }
    
    .insight-box {
        background: linear-gradient(135deg, #fef3c7 0%, #fce7f3 100%);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        border: 1px solid #fcd34d;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def get_db_connection():
    """Get PostgreSQL database connection."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        return None
    return psycopg2.connect(database_url, cursor_factory=RealDictCursor)


def get_voice_calls_summary():
    """Get summary statistics for voice calls."""
    conn = get_db_connection()
    if not conn:
        return {"total_calls": 0, "total_messages": 0, "avg_latency": 0, "booking_rate": 0}
    
    try:
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(DISTINCT call_id) as total_calls FROM voice_messages")
        total_calls = cur.fetchone()["total_calls"]
        
        cur.execute("SELECT COUNT(*) as total FROM voice_messages")
        total_messages = cur.fetchone()["total"]
        
        cur.execute("SELECT AVG(latency_ms) as avg FROM voice_messages WHERE latency_ms IS NOT NULL AND latency_ms > 0")
        avg_latency_result = cur.fetchone()["avg"]
        avg_latency = int(avg_latency_result) if avg_latency_result else 0
        
        cur.execute("""
            SELECT COUNT(DISTINCT call_id) as booking_calls 
            FROM voice_messages 
            WHERE closure_type = 'booking_request'
        """)
        booking_calls = cur.fetchone()["booking_calls"]
        booking_rate = (booking_calls / total_calls * 100) if total_calls > 0 else 0
        
        cur.close()
        conn.close()
        
        return {
            "total_calls": total_calls,
            "total_messages": total_messages,
            "avg_latency": avg_latency,
            "booking_rate": booking_rate
        }
    except Exception as e:
        print(f"Error getting voice summary: {e}")
        return {"total_calls": 0, "total_messages": 0, "avg_latency": 0, "booking_rate": 0}


def get_recent_calls(limit=10):
    """Get list of recent calls with summary info."""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                call_id,
                MIN(timestamp) as started_at,
                MAX(timestamp) as ended_at,
                COUNT(*) as message_count,
                AVG(CASE WHEN latency_ms > 0 THEN latency_ms END) as avg_latency,
                MAX(readiness_score) as peak_readiness,
                MAX(CASE WHEN closure_type = 'booking_request' THEN 1 ELSE 0 END) as had_booking,
                MAX(CASE WHEN closure_type = 'strong_goodbye' THEN 1 ELSE 0 END) as had_goodbye
            FROM voice_messages
            GROUP BY call_id
            ORDER BY MIN(timestamp) DESC
            LIMIT %s
        """, (limit,))
        
        calls = cur.fetchall()
        cur.close()
        conn.close()
        return calls
    except Exception as e:
        print(f"Error getting recent calls: {e}")
        return []


def get_call_transcript(call_id):
    """Get full transcript for a specific call."""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT role, content, readiness_score, readiness_recommendation, latency_ms, closure_type, timestamp
            FROM voice_messages
            WHERE call_id = %s
            ORDER BY timestamp
        """, (call_id,))
        
        messages = cur.fetchall()
        cur.close()
        conn.close()
        return messages
    except Exception as e:
        print(f"Error getting transcript: {e}")
        return []


def get_readiness_distribution():
    """Get distribution of readiness scores."""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                readiness_recommendation,
                COUNT(*) as count
            FROM voice_messages
            WHERE role = 'user' AND readiness_recommendation IS NOT NULL
            GROUP BY readiness_recommendation
        """)
        
        data = cur.fetchall()
        cur.close()
        conn.close()
        return data
    except Exception as e:
        print(f"Error getting readiness distribution: {e}")
        return []


def get_latency_over_time():
    """Get latency metrics over time."""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                DATE(timestamp) as date,
                AVG(latency_ms) as avg_latency,
                MIN(latency_ms) as min_latency,
                MAX(latency_ms) as max_latency,
                COUNT(*) as response_count
            FROM voice_messages
            WHERE latency_ms IS NOT NULL AND latency_ms > 0
            GROUP BY DATE(timestamp)
            ORDER BY DATE(timestamp) DESC
            LIMIT 30
        """)
        
        data = cur.fetchall()
        cur.close()
        conn.close()
        return data
    except Exception as e:
        print(f"Error getting latency over time: {e}")
        return []


def get_readiness_journey(call_id):
    """Get the readiness score journey for a specific call."""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT readiness_score, readiness_recommendation, timestamp
            FROM voice_messages
            WHERE call_id = %s AND role = 'user' AND readiness_score IS NOT NULL
            ORDER BY timestamp
        """, (call_id,))
        
        data = cur.fetchall()
        cur.close()
        conn.close()
        return data
    except Exception as e:
        print(f"Error getting readiness journey: {e}")
        return []


def format_duration(start_time, end_time):
    """Format call duration in human-readable format."""
    if not start_time or not end_time:
        return "N/A"
    
    if isinstance(start_time, str):
        start_time = datetime.fromisoformat(start_time)
    if isinstance(end_time, str):
        end_time = datetime.fromisoformat(end_time)
    
    duration = end_time - start_time
    total_seconds = int(duration.total_seconds())
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}m {seconds}s"


def render_header():
    """Render the main header."""
    st.markdown('<h1 class="main-header">SOMERA Analytics</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Voice Coaching Intelligence Dashboard</p>', unsafe_allow_html=True)


def render_voice_analytics():
    """Render the Voice Analytics tab."""
    st.markdown("### 📊 Overview Metrics")
    
    summary = get_voice_calls_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Calls",
            value=summary["total_calls"],
            help="Total number of voice coaching sessions"
        )
    
    with col2:
        st.metric(
            label="Total Messages",
            value=summary["total_messages"],
            help="Total conversation turns across all calls"
        )
    
    with col3:
        latency_color = "🟢" if summary["avg_latency"] < 3000 else "🟡" if summary["avg_latency"] < 5000 else "🔴"
        st.metric(
            label="Avg Latency",
            value=f"{summary['avg_latency']}ms",
            help="Average response time per turn"
        )
    
    with col4:
        st.metric(
            label="Booking Rate",
            value=f"{summary['booking_rate']:.1f}%",
            help="Percentage of calls with booking requests"
        )
    
    st.divider()
    
    st.markdown("### 📈 Latency Trends")
    latency_data = get_latency_over_time()
    
    if latency_data:
        df = pd.DataFrame(latency_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        st.line_chart(df.set_index('date')[['avg_latency', 'min_latency', 'max_latency']])
        
        col1, col2 = st.columns(2)
        with col1:
            recent_avg = df['avg_latency'].mean()
            st.info(f"**30-Day Average Latency:** {recent_avg:.0f}ms")
        with col2:
            best_day = df.loc[df['avg_latency'].idxmin()]
            st.success(f"**Best Day:** {best_day['date'].strftime('%b %d')} ({best_day['avg_latency']:.0f}ms)")
    else:
        st.info("No latency data available yet. Make some voice calls to see trends!")
    
    st.divider()
    
    st.markdown("### 🎯 Readiness Score Distribution")
    readiness_data = get_readiness_distribution()
    
    if readiness_data:
        df = pd.DataFrame(readiness_data)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.bar_chart(df.set_index('readiness_recommendation')['count'])
        
        with col2:
            total = df['count'].sum()
            for _, row in df.iterrows():
                pct = row['count'] / total * 100 if total > 0 else 0
                rec = row['readiness_recommendation']
                emoji = "🔵" if rec == "explore" else "🟡" if rec == "transition" else "🟢"
                st.markdown(f"{emoji} **{rec.title()}:** {row['count']} ({pct:.1f}%)")
    else:
        st.info("No readiness data available yet.")


def render_transcripts():
    """Render the Transcripts tab."""
    st.markdown("### 📝 Recent Voice Sessions")
    
    calls = get_recent_calls(limit=20)
    
    if not calls:
        st.info("No voice calls recorded yet. Start a voice session to see transcripts here!")
        return
    
    for call in calls:
        call_id = call['call_id']
        started_at = call['started_at']
        duration = format_duration(call['started_at'], call['ended_at'])
        msg_count = call['message_count']
        peak_readiness = call['peak_readiness']
        avg_latency = call['avg_latency']
        had_booking = call['had_booking']
        had_goodbye = call['had_goodbye']
        
        badges = []
        if had_booking:
            badges.append("📞 Booking")
        if had_goodbye:
            badges.append("👋 Completed")
        if peak_readiness and peak_readiness >= 0.5:
            badges.append("⭐ High Readiness")
        
        badge_str = " | ".join(badges) if badges else "💬 In Progress"
        
        time_str = started_at.strftime("%b %d, %Y at %I:%M %p") if started_at else "Unknown"
        latency_str = f"{int(avg_latency)}ms" if avg_latency else "N/A"
        
        with st.expander(f"**{time_str}** - {duration} ({msg_count} messages) | {badge_str}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.caption(f"**Call ID:** {call_id[:20]}...")
            with col2:
                st.caption(f"**Avg Latency:** {latency_str}")
            with col3:
                st.caption(f"**Peak Readiness:** {peak_readiness:.0%}" if peak_readiness else "N/A")
            
            st.divider()
            
            messages = get_call_transcript(call_id)
            
            for msg in messages:
                role = msg['role']
                content = msg['content']
                readiness = msg.get('readiness_score')
                rec = msg.get('readiness_recommendation')
                latency = msg.get('latency_ms')
                
                if role == 'user':
                    readiness_badge = ""
                    if readiness is not None:
                        badge_class = "readiness-explore" if rec == "explore" else "readiness-transition" if rec == "transition" else "readiness-guide"
                        readiness_badge = f'<span class="readiness-badge {badge_class}">{rec.title()} ({readiness:.0%})</span>'
                    
                    st.markdown(f"""
                    <div class="user-message">
                        <strong>👤 User</strong> {readiness_badge}<br>
                        {content}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    latency_info = f" • ⏱️ {latency}ms" if latency else ""
                    st.markdown(f"""
                    <div class="assistant-message">
                        <strong>💜 SOMERA</strong>{latency_info}<br>
                        {content}
                    </div>
                    """, unsafe_allow_html=True)
            
            st.divider()
            
            st.markdown("**Readiness Journey:**")
            journey = get_readiness_journey(call_id)
            if journey:
                journey_df = pd.DataFrame(journey)
                journey_df['timestamp'] = pd.to_datetime(journey_df['timestamp'])
                journey_df = journey_df.sort_values('timestamp')
                
                st.line_chart(journey_df.set_index('timestamp')['readiness_score'])
            else:
                st.caption("No readiness data for this call")


def render_insights():
    """Render the Coaching Insights tab."""
    st.markdown("### 💡 Coaching Insights")
    
    conn = get_db_connection()
    if not conn:
        st.warning("Database not connected")
        return
    
    try:
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                COUNT(DISTINCT call_id) as total_calls,
                AVG(CASE WHEN role = 'user' THEN readiness_score END) as avg_readiness,
                MAX(CASE WHEN role = 'user' THEN readiness_score END) as max_readiness
            FROM voice_messages
        """)
        stats = cur.fetchone()
        
        st.markdown("""
        <div class="insight-box">
            <h4>📊 Key Coaching Metrics</h4>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_r = stats['avg_readiness'] or 0
            st.metric("Avg Readiness Score", f"{avg_r:.0%}")
        with col2:
            max_r = stats['max_readiness'] or 0
            st.metric("Peak Readiness Achieved", f"{max_r:.0%}")
        with col3:
            st.metric("Total Sessions", stats['total_calls'])
        
        st.divider()
        
        st.markdown("### 🎯 Readiness Threshold Analysis")
        
        cur.execute("""
            SELECT 
                call_id,
                MAX(readiness_score) as peak,
                COUNT(*) FILTER (WHERE readiness_score >= 0.35) as guide_moments,
                COUNT(*) FILTER (WHERE readiness_score >= 0.2 AND readiness_score < 0.35) as transition_moments
            FROM voice_messages
            WHERE role = 'user' AND readiness_score IS NOT NULL
            GROUP BY call_id
        """)
        threshold_data = cur.fetchall()
        
        if threshold_data:
            df = pd.DataFrame(threshold_data)
            
            high_readiness_calls = len(df[df['peak'] >= 0.5])
            guide_ready_calls = len(df[df['peak'] >= 0.35])
            
            st.markdown(f"""
            - **{high_readiness_calls}** calls reached high readiness (≥50%)
            - **{guide_ready_calls}** calls reached guidance threshold (≥35%)
            - Average peak readiness: **{df['peak'].mean():.0%}**
            """)
        
        st.divider()
        
        st.markdown("### 📞 Conversion Funnel")
        
        cur.execute("SELECT COUNT(DISTINCT call_id) FROM voice_messages")
        total_calls = cur.fetchone()[0]
        
        cur.execute("""
            SELECT COUNT(DISTINCT call_id) FROM voice_messages 
            WHERE closure_type = 'booking_request'
        """)
        booking_calls = cur.fetchone()[0]
        
        cur.execute("""
            SELECT COUNT(DISTINCT call_id) FROM voice_messages 
            WHERE closure_type = 'strong_goodbye'
        """)
        completed_calls = cur.fetchone()[0]
        
        if total_calls > 0:
            booking_pct = booking_calls / total_calls * 100
            completed_pct = completed_calls / total_calls * 100
            
            st.markdown(f"""
            | Stage | Count | % of Total |
            |-------|-------|------------|
            | Started Calls | {total_calls} | 100% |
            | Requested Booking | {booking_calls} | {booking_pct:.1f}% |
            | Completed Naturally | {completed_calls} | {completed_pct:.1f}% |
            """)
        
        cur.close()
        conn.close()
        
    except Exception as e:
        st.error(f"Error loading insights: {e}")


def main():
    """Main application entry point."""
    render_header()
    
    with st.sidebar:
        st.markdown("### 💜 SOMERA Admin")
        st.markdown("---")
        st.markdown("**Quick Stats**")
        
        summary = get_voice_calls_summary()
        st.metric("Active Calls", summary["total_calls"])
        st.metric("Avg Response", f"{summary['avg_latency']}ms")
        
        st.markdown("---")
        st.markdown("**Navigation**")
        st.markdown("""
        - 📊 **Voice Analytics** - Performance metrics
        - 📝 **Transcripts** - View call history
        - 💡 **Insights** - Coaching patterns
        """)
        
        st.markdown("---")
        st.caption("SOMERA Voice Analytics v1.0")
        st.caption(f"Last updated: {datetime.now().strftime('%I:%M %p')}")
    
    tab1, tab2, tab3 = st.tabs(["📊 Voice Analytics", "📝 Transcripts", "💡 Insights"])
    
    with tab1:
        render_voice_analytics()
    
    with tab2:
        render_transcripts()
    
    with tab3:
        render_insights()


if __name__ == "__main__":
    main()
