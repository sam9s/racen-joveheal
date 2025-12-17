"""
Video/Audio Transcription Tool using OpenAI Whisper API
Supports: Direct upload OR Google Drive links for large files
"""

import streamlit as st
import os
import tempfile
import subprocess
import math
import re
import gdown
from pathlib import Path

st.set_page_config(
    page_title="Video Transcription Tool",
    page_icon="🎙️",
    layout="centered"
)

st.title("🎙️ Video Transcription Tool")

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

def extract_gdrive_id(url: str) -> str:
    """Extract Google Drive file ID from various URL formats."""
    patterns = [
        r'/file/d/([a-zA-Z0-9_-]+)',
        r'id=([a-zA-Z0-9_-]+)',
        r'/d/([a-zA-Z0-9_-]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def download_from_gdrive(file_id: str, output_path: str, progress_callback=None) -> bool:
    """Download file from Google Drive using gdown (handles large files)."""
    try:
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, output_path, quiet=False, fuzzy=True)
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            return True
        return False
    except Exception as e:
        st.error(f"Download error: {e}")
        return False

def extract_audio_fast(video_path: str, output_path: str) -> bool:
    """Extract audio using ffmpeg copy mode (very fast)."""
    try:
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vn", "-acodec", "copy",
            "-y", output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0 or not os.path.exists(output_path):
            cmd = [
                "ffmpeg", "-i", video_path,
                "-vn", "-acodec", "libmp3lame", "-ab", "64k", "-ar", "16000",
                "-y", output_path.replace('.m4a', '.mp3')
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if result.returncode == 0:
                return output_path.replace('.m4a', '.mp3')
            return False
        return output_path
    except Exception as e:
        st.error(f"Audio extraction error: {e}")
        return False

def split_audio(audio_path: str, temp_dir: str, chunk_duration: int = 600) -> list:
    """Split audio into chunks of specified duration (default 10 minutes)."""
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
            "-acodec", "libmp3lame", "-ab", "64k", "-ar", "16000",
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
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        st.warning("⚠️ OPENAI_API_KEY not found. Please add it to the Secrets tab.")
        return
    else:
        st.success("✓ OpenAI API key configured")
    
    tab1, tab2 = st.tabs(["📤 Upload File", "🔗 Google Drive Link"])
    
    with tab1:
        st.markdown("""
        **For files under 200MB** - Upload directly here.
        
        **Cost**: ~$0.006 per minute of audio
        """)
        
        uploaded_file = st.file_uploader(
            "Choose a video or audio file",
            type=["mp4", "mov", "avi", "mkv", "mp3", "wav", "m4a", "ogg", "webm"]
        )
        
        if uploaded_file:
            file_size_mb = uploaded_file.size / (1024 * 1024)
            st.info(f"📁 **{uploaded_file.name}** ({file_size_mb:.1f} MB)")
            
            if st.button("🎙️ Transcribe Upload", type="primary", key="btn_upload"):
                process_file(uploaded_file=uploaded_file)
    
    with tab2:
        st.markdown("""
        **For large files (200MB+)** - Use Google Drive link.
        
        ### How to use:
        1. Upload your video to Google Drive
        2. Right-click → Share → "Anyone with the link"
        3. Copy the link and paste below
        
        **Cost**: ~$0.006 per minute of audio
        """)
        
        gdrive_url = st.text_input(
            "Google Drive Link",
            placeholder="https://drive.google.com/file/d/xxx/view?usp=sharing"
        )
        
        output_name = st.text_input(
            "Output filename (optional)",
            placeholder="Relationship_Session_1"
        )
        
        if gdrive_url:
            file_id = extract_gdrive_id(gdrive_url)
            if file_id:
                st.success(f"✓ Valid Google Drive link detected")
                
                if st.button("🎙️ Download & Transcribe", type="primary", key="btn_gdrive"):
                    process_gdrive(file_id, output_name or "transcript")
            else:
                st.error("❌ Could not extract file ID from URL. Please check the link.")

def process_gdrive(file_id: str, output_name: str):
    """Process video from Google Drive link."""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        video_path = os.path.join(temp_dir, "video.mp4")
        
        status_text.text("📥 Downloading from Google Drive...")
        
        def update_download_progress(pct):
            progress_bar.progress(int(pct * 30))
        
        if not download_from_gdrive(file_id, video_path, update_download_progress):
            st.error("❌ Failed to download from Google Drive. Make sure the file is shared publicly ('Anyone with the link').")
            return
        
        file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        st.info(f"📁 Downloaded: {file_size_mb:.1f} MB")
        progress_bar.progress(30)
        
        status_text.text("🎵 Extracting audio (fast copy mode)...")
        audio_path = os.path.join(temp_dir, "audio.m4a")
        result = extract_audio_fast(video_path, audio_path)
        
        if not result:
            st.error("Failed to extract audio from video.")
            return
        
        if isinstance(result, str):
            audio_path = result
        
        progress_bar.progress(40)
        
        audio_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
        duration = get_audio_duration(audio_path)
        duration_min = duration / 60
        st.info(f"🎵 Audio: {audio_size_mb:.1f} MB, Duration: {duration_min:.1f} minutes")
        
        transcribe_audio_file(audio_path, temp_dir, output_name, progress_bar, status_text, start_progress=40)

def process_file(uploaded_file):
    """Process uploaded file."""
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
            cmd = [
                "ffmpeg", "-i", input_path,
                "-vn", "-acodec", "libmp3lame", "-ab", "64k", "-ar", "16000",
                "-y", audio_path
            ]
            subprocess.run(cmd, capture_output=True)
        else:
            status_text.text("Preparing audio...")
            audio_path = os.path.join(temp_dir, "prepared.mp3")
            cmd = [
                "ffmpeg", "-i", input_path,
                "-acodec", "libmp3lame", "-ab", "64k", "-ar", "16000",
                "-y", audio_path
            ]
            subprocess.run(cmd, capture_output=True)
        
        progress_bar.progress(20)
        
        output_name = Path(uploaded_file.name).stem
        transcribe_audio_file(audio_path, temp_dir, output_name, progress_bar, status_text, start_progress=20)

def transcribe_audio_file(audio_path: str, temp_dir: str, output_name: str, progress_bar, status_text, start_progress: int = 20):
    """Common transcription logic for both upload and gdrive."""
    duration = get_audio_duration(audio_path)
    duration_min = duration / 60
    st.info(f"⏱️ Audio duration: {duration_min:.1f} minutes")
    
    status_text.text("Splitting audio into chunks...")
    chunks = split_audio(audio_path, temp_dir)
    num_chunks = len(chunks)
    st.info(f"📦 Split into {num_chunks} chunk(s) for processing")
    progress_bar.progress(start_progress + 10)
    
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
        
        progress = start_progress + 10 + int((i + 1) / num_chunks * (90 - start_progress - 10))
        progress_bar.progress(progress)
    
    progress_bar.progress(95)
    status_text.text("Combining transcripts...")
    
    full_transcript = "\n\n".join(all_transcripts)
    
    progress_bar.progress(100)
    status_text.text("")
    
    st.success(f"✅ Transcription complete! ({num_chunks} chunks, {duration_min:.1f} minutes)")
    
    st.text_area("Transcript", full_transcript, height=400)
    
    output_filename = f"{output_name}_transcript.txt"
    st.download_button(
        label="📥 Download Transcript",
        data=full_transcript,
        file_name=output_filename,
        mime="text/plain"
    )

if __name__ == "__main__":
    main()
