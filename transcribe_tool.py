"""
Video/Audio Transcription Tool using OpenAI Whisper API
Handles large files by splitting into chunks.
"""

import streamlit as st
import os
import tempfile
import subprocess
import math
from pathlib import Path

st.set_page_config(
    page_title="Video Transcription Tool",
    page_icon="🎙️",
    layout="centered"
)

st.title("🎙️ Video Transcription Tool")
st.markdown("Upload video or audio files to transcribe using OpenAI Whisper API.")

def get_audio_duration(audio_path: str) -> float:
    """Get audio duration in seconds using ffprobe."""
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            audio_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return float(result.stdout.strip())
    except:
        return 0

def extract_audio(video_path: str, output_path: str) -> bool:
    """Extract audio from video file using ffmpeg."""
    try:
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vn", "-acodec", "mp3", "-ab", "64k", "-ar", "16000",
            "-y", output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        st.error(f"Error extracting audio: {e}")
        return False

def split_audio(audio_path: str, temp_dir: str, chunk_duration: int = 600) -> list:
    """Split audio into chunks of specified duration (default 10 minutes).
    
    10 minutes at 64kbps 16kHz mono ≈ 4.8MB per chunk (well under 25MB limit)
    """
    duration = get_audio_duration(audio_path)
    if duration == 0:
        return [audio_path]
    
    num_chunks = math.ceil(duration / chunk_duration)
    
    if num_chunks <= 1:
        return [audio_path]
    
    chunk_paths = []
    for i in range(num_chunks):
        start_time = i * chunk_duration
        chunk_path = os.path.join(temp_dir, f"chunk_{i:03d}.mp3")
        
        cmd = [
            "ffmpeg", "-i", audio_path,
            "-ss", str(start_time),
            "-t", str(chunk_duration),
            "-acodec", "mp3", "-ab", "64k", "-ar", "16000",
            "-y", chunk_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(chunk_path):
            chunk_paths.append(chunk_path)
    
    return chunk_paths

def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio using OpenAI Whisper API."""
    from openai import OpenAI
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
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
    
    **Large files**: Automatically split into 10-minute chunks for processing.
    """)
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        st.warning("⚠️ OPENAI_API_KEY not found. Please add it to the Secrets tab.")
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
            st.info("ℹ️ Large file detected. Will be split into chunks for transcription.")
        
        if st.button("🎙️ Transcribe", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            with tempfile.TemporaryDirectory() as temp_dir:
                status_text.text("Saving uploaded file...")
                input_path = os.path.join(temp_dir, uploaded_file.name)
                with open(input_path, "wb") as f:
                    f.write(uploaded_file.read())
                progress_bar.progress(10)
                
                file_ext = Path(uploaded_file.name).suffix.lower()
                video_extensions = [".mp4", ".mov", ".avi", ".mkv", ".webm"]
                
                if file_ext in video_extensions:
                    status_text.text("Extracting audio from video...")
                    audio_path = os.path.join(temp_dir, "audio.mp3")
                    if not extract_audio(input_path, audio_path):
                        st.error("Failed to extract audio from video.")
                        return
                else:
                    status_text.text("Preparing audio...")
                    audio_path = os.path.join(temp_dir, "prepared.mp3")
                    cmd = [
                        "ffmpeg", "-i", input_path,
                        "-acodec", "mp3", "-ab", "64k", "-ar", "16000",
                        "-y", audio_path
                    ]
                    subprocess.run(cmd, capture_output=True)
                
                progress_bar.progress(20)
                
                duration = get_audio_duration(audio_path)
                duration_min = duration / 60
                st.info(f"⏱️ Audio duration: {duration_min:.1f} minutes")
                
                status_text.text("Splitting audio into chunks...")
                chunks = split_audio(audio_path, temp_dir)
                num_chunks = len(chunks)
                st.info(f"📦 Split into {num_chunks} chunk(s) for processing")
                progress_bar.progress(30)
                
                all_transcripts = []
                for i, chunk_path in enumerate(chunks):
                    chunk_size_mb = os.path.getsize(chunk_path) / (1024 * 1024)
                    status_text.text(f"Transcribing chunk {i+1}/{num_chunks} ({chunk_size_mb:.1f} MB)...")
                    
                    try:
                        transcript = transcribe_audio(chunk_path)
                        if transcript:
                            all_transcripts.append(transcript)
                    except Exception as e:
                        st.error(f"Error transcribing chunk {i+1}: {e}")
                        all_transcripts.append(f"[Error in chunk {i+1}]")
                    
                    progress = 30 + int((i + 1) / num_chunks * 60)
                    progress_bar.progress(progress)
                
                progress_bar.progress(95)
                status_text.text("Combining transcripts...")
                
                full_transcript = "\n\n".join(all_transcripts)
                
                progress_bar.progress(100)
                status_text.text("")
                
                st.success(f"✅ Transcription complete! ({num_chunks} chunks processed)")
                
                st.text_area("Transcript", full_transcript, height=400)
                
                output_filename = Path(uploaded_file.name).stem + "_transcript.txt"
                st.download_button(
                    label="📥 Download Transcript",
                    data=full_transcript,
                    file_name=output_filename,
                    mime="text/plain"
                )

if __name__ == "__main__":
    main()
