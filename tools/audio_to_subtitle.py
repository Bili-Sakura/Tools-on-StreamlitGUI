from openai import OpenAI
from pydub import AudioSegment
from pathlib import Path
import srt
import datetime
import os
import tempfile

def audio_to_subtitle(file_path, chunk_length_ms=10*60*1000, api_key=None):
    """
    Convert audio/video file to SRT subtitle format using OpenAI Whisper API.
    
    Args:
        file_path (str): Path to the audio/video file
        chunk_length_ms (int): Length of audio chunks in milliseconds (default: 10 minutes)
        api_key (str): OpenAI API key (optional, will use environment variable if not provided)
    
    Returns:
        str: SRT formatted subtitle content
    """
    # Initialize OpenAI client
    client_kwargs = {}
    if api_key:
        client_kwargs['api_key'] = api_key
    client = OpenAI(**client_kwargs)
    
    def split_audio(file_path, chunk_length_ms):
        """Split audio into chunks for processing."""
        audio = AudioSegment.from_file(file_path)
        chunks = []
        
        # Create temporary directory for chunks
        temp_dir = tempfile.mkdtemp()
        
        for i, start_ms in enumerate(range(0, len(audio), chunk_length_ms)):
            chunk = audio[start_ms:start_ms+chunk_length_ms]
            chunk_path = Path(temp_dir) / f"chunk_{i}.mp3"
            chunk.export(chunk_path, format="mp3")
            chunks.append((chunk_path, start_ms))
        return chunks, temp_dir

    def transcribe_chunk(file_path, offset_ms):
        """Transcribe a single audio chunk."""
        with open(file_path, "rb") as f:
            result = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="verbose_json"  # needed for timestamps
            )

        subs = []
        if "segments" in result and result["segments"]:
            for seg in result["segments"]:
                start = datetime.timedelta(milliseconds=offset_ms) + datetime.timedelta(seconds=seg["start"])
                end = datetime.timedelta(milliseconds=offset_ms) + datetime.timedelta(seconds=seg["end"])
                subs.append(srt.Subtitle(
                    index=len(subs)+1, 
                    start=start, 
                    end=end, 
                    content=seg["text"].strip()
                ))
        return subs

    def transcribe_long_audio(file_path):
        """Transcribe long audio by splitting into chunks."""
        all_subs = []
        chunks, temp_dir = split_audio(file_path, chunk_length_ms)
        
        try:
            for chunk_path, offset_ms in chunks:
                subs = transcribe_chunk(chunk_path, offset_ms)
                all_subs.extend(subs)
                chunk_path.unlink()  # clean up chunk file
        finally:
            # Clean up temporary directory
            try:
                os.rmdir(temp_dir)
            except:
                pass  # Directory might not be empty or already removed
        
        # Re-index subtitles
        for i, sub in enumerate(all_subs):
            sub.index = i + 1
            
        return all_subs

    # Convert audio to subtitles
    subs = transcribe_long_audio(file_path)
    
    # Return SRT formatted content
    return srt.compose(subs)