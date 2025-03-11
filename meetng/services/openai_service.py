import os
import tempfile
from openai import OpenAI
from pydub import AudioSegment
from .base_service import TranscriptionService

class OpenAITranscriptionService(TranscriptionService):
    def __init__(self):
        super().__init__()
        self.client = None
        self.model = "whisper-1"
        
    def get_env_key(self):
        return 'OPENAI_API_KEY'
        
    def setup(self, api_key=None):
        if super().setup(api_key):
            self.client = OpenAI(api_key=self._api_key)
            return True
        return False
        
    def split_audio_file(self, file_path: str, max_size_bytes: int = 25 * 1024 * 1024) -> list[str]:
        """Split audio file into chunks under max size"""
        try:
            # Load audio file
            audio = AudioSegment.from_file(file_path)
            
            # If file is under limit, return original
            if os.path.getsize(file_path) <= max_size_bytes:
                return [file_path]
                
            # Calculate split points
            total_duration = len(audio)
            num_chunks = (os.path.getsize(file_path) // max_size_bytes) + 1
            chunk_duration = total_duration // num_chunks
            
            # Create temp directory for chunks
            temp_dir = tempfile.mkdtemp()
            chunk_paths = []
            
            # Split and export chunks
            for i in range(num_chunks):
                start_time = i * chunk_duration
                end_time = (i + 1) * chunk_duration if i < num_chunks - 1 else total_duration
                
                chunk = audio[start_time:end_time]
                chunk_path = os.path.join(temp_dir, f"chunk_{i}.mp3")
                chunk.export(chunk_path, format="mp3")
                chunk_paths.append(chunk_path)
                
            return chunk_paths
            
        except Exception as e:
            print(f"Error splitting audio file: {e}")
            return [file_path]  # Return original if splitting fails

    def _transcribe_impl(self, file_path, config=None):
        print(f"OpenAI: Starting transcription for {file_path}")
        try:
            # Split file if needed
            print("OpenAI: Analyzing file size and splitting if needed...")
            chunk_paths = self.split_audio_file(file_path)
            
            transcripts = []
            total_chunks = len(chunk_paths)
            print(f"OpenAI: Processing {total_chunks} chunks...")
            
            for i, chunk_path in enumerate(chunk_paths):
                print(f"OpenAI: Processing chunk {i+1}/{total_chunks} ({(i+1)/total_chunks*100:.1f}%)")
                with open(chunk_path, "rb") as audio_file:
                    print("OpenAI: File opened successfully")
                    response = self.client.audio.transcriptions.create(
                        model=self.model,
                        file=audio_file,
                        response_format="text"  # Use text format for consistent output
                    )
                    transcripts.append(response)
            
            # Combine transcripts
            full_transcript = "\n".join(transcripts)
            
            # Clean up temp files if we split
            if len(chunk_paths) > 1:
                temp_dir = os.path.dirname(chunk_paths[0])
                for path in chunk_paths:
                    try:
                        os.remove(path)
                    except:
                        pass
                try:
                    os.rmdir(temp_dir)
                except:
                    pass
            
            # Format transcript with timestamps if requested
            if config and config.get('timestamps'):
                # OpenAI doesn't provide timestamps, so we'll just add a start marker
                timestamp = "[00:00:00]"
                return f"{timestamp} {full_transcript}"
            else:
                return full_transcript
                
        except Exception as e:
            print(f"OpenAI: Error during transcription: {str(e)}")
            raise
