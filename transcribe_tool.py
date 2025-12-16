"""
Video/Audio Transcription Tool using OpenAI Whisper API
Simple Streamlit interface for transcribing coaching session videos.
"""

import streamlit as st
import os
import tempfile
import subprocess
from pathlib import Path

st.set_page_config(
    page_title="Video Transcription Tool",
    page_icon="🎙️",
    layout="centered"
)

st.title("🎙️ Video Transcription Tool")
st.markdown("Upload video or audio files to transcribe using OpenAI Whisper API.")

def extract_audio(video_path: str, output_path: str) -> bool:
    """Extract audio from video file using ffmpeg."""
    try:
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vn", "-acodec", "mp3", "-ab", "128k",
            "-y", output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        st.error(f"Error extracting audio: {e}")
        return False

def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio using OpenAI Whisper API."""
    from openai import OpenAI
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        st.error("Please set your OPENAI_API_KEY in the Secrets tab.")
        return None
    
    client = OpenAI(api_key=api_key)
    
    with open(audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )
    
    return transcript

def main():
    st.markdown("""
    ### How to use:
    1. Upload a video (mp4, mov, avi) or audio (mp3, wav, m4a) file
    2. Click "Transcribe"
    3. Download the transcript
    
    **Cost**: ~$0.006 per minute of audio (~$0.36 for 1 hour)
    """)
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        st.warning("⚠️ OPENAI_API_KEY not found. Please add it to the Secrets tab.")
        st.info("You need a direct OpenAI API key (not Replit's proxy) for Whisper transcription.")
        return
    else:
        st.success("✓ OpenAI API key configured")
    
    uploaded_file = st.file_uploader(
        "Choose a video or audio file",
        type=["mp4", "mov", "avi", "mkv", "mp3", "wav", "m4a", "ogg", "webm"]
    )
    
    if uploaded_file:
        file_size_mb = uploaded_file.size / (1024 * 1024)
        st.info(f"📁 **{uploaded_file.name}** ({file_size_mb:.1f} MB)")
        
        if file_size_mb > 25:
            st.warning("⚠️ File is larger than 25MB. Whisper API limit is 25MB per request. The file will be compressed.")
        
        if st.button("🎙️ Transcribe", type="primary"):
            with st.spinner("Processing..."):
                with tempfile.TemporaryDirectory() as temp_dir:
                    input_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(input_path, "wb") as f:
                        f.write(uploaded_file.read())
                    
                    file_ext = Path(uploaded_file.name).suffix.lower()
                    video_extensions = [".mp4", ".mov", ".avi", ".mkv", ".webm"]
                    
                    if file_ext in video_extensions:
                        st.text("Extracting audio from video...")
                        audio_path = os.path.join(temp_dir, "audio.mp3")
                        if not extract_audio(input_path, audio_path):
                            st.error("Failed to extract audio from video.")
                            return
                    else:
                        audio_path = input_path
                    
                    audio_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
                    if audio_size_mb > 25:
                        st.text("Compressing audio to meet API limits...")
                        compressed_path = os.path.join(temp_dir, "compressed.mp3")
                        cmd = [
                            "ffmpeg", "-i", audio_path,
                            "-ab", "64k", "-ar", "16000",
                            "-y", compressed_path
                        ]
                        subprocess.run(cmd, capture_output=True)
                        audio_path = compressed_path
                    
                    st.text("Transcribing with Whisper API...")
                    try:
                        transcript = transcribe_audio(audio_path)
                        if transcript:
                            st.success("✅ Transcription complete!")
                            
                            st.text_area("Transcript", transcript, height=400)
                            
                            output_filename = Path(uploaded_file.name).stem + "_transcript.txt"
                            st.download_button(
                                label="📥 Download Transcript",
                                data=transcript,
                                file_name=output_filename,
                                mime="text/plain"
                            )
                    except Exception as e:
                        st.error(f"Transcription failed: {e}")

if __name__ == "__main__":
    main()
