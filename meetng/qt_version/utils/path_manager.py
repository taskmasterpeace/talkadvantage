import os
from datetime import datetime
from pathlib import Path

class PathManager:
    def __init__(self, base_dir=None):
        # Use program directory as base if not specified
        if base_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            
        self.base_dir = os.path.abspath(base_dir)
        self.workspace_dir = os.path.join(self.base_dir, "recordings")  # Default workspace is recordings folder
        self.templates_dir = os.path.join(self.base_dir, "templates")
        self.settings_dir = os.path.join(self.base_dir, "settings")
        self.cache_dir = os.path.join(self.base_dir, "cache")
        
        # Create all required directories
        self.init_directories()
        
    def init_directories(self):
        """Create all required directories if they don't exist"""
        for dir_path in [self.base_dir, self.workspace_dir, 
                        self.templates_dir, self.settings_dir, 
                        self.cache_dir]:
            os.makedirs(dir_path, exist_ok=True)
            
    def get_session_dir(self, session_name: str) -> str:
        """Get directory for a specific recording session"""
        # Use workspace directory for all recordings
        os.makedirs(self.workspace_dir, exist_ok=True)
        return self.workspace_dir
        
    def get_recording_path(self, session_dir: str, filename: str = None) -> str:
        """Get path for audio recording file"""
        if filename:
            return os.path.join(session_dir, f"{filename}.mp3")
        return os.path.join(session_dir, "audio.mp3")
        
    def get_transcript_path(self, session_dir: str, filename: str = None) -> str:
        """Get path for transcript file"""
        if filename:
            return os.path.join(session_dir, f"{filename}_transcript.txt")
        return os.path.join(session_dir, "transcript.txt")
        
    def get_analysis_path(self, session_dir: str, filename: str = None) -> str:
        """Get path for analysis file"""
        if filename:
            return os.path.join(session_dir, f"{filename}_analysis.txt")
        return os.path.join(session_dir, "analysis.txt")
        
    def set_workspace_dir(self, path: str):
        """Set the workspace directory path"""
        try:
            self.workspace_dir = os.path.abspath(path)
            os.makedirs(self.workspace_dir, exist_ok=True)
            print(f"Workspace directory set to: {self.workspace_dir}")
            return self.workspace_dir
        except Exception as e:
            print(f"Error setting workspace directory: {e}")
            # Fallback to a safe default if there's an error
            fallback_path = str(Path.home() / "PowerPlay" / "Recordings")
            os.makedirs(fallback_path, exist_ok=True)
            self.workspace_dir = fallback_path
            print(f"Using fallback workspace directory: {fallback_path}")
            return fallback_path

    def set_templates_dir(self, path: str):
        """Set the templates directory path"""
        try:
            self.templates_dir = os.path.abspath(path)
            os.makedirs(self.templates_dir, exist_ok=True)
            print(f"Templates directory set to: {self.templates_dir}")
            return self.templates_dir
        except Exception as e:
            print(f"Error setting templates directory: {e}")
            # Fallback to a safe default if there's an error
            fallback_path = str(Path.home() / "PowerPlay" / "Templates")
            os.makedirs(fallback_path, exist_ok=True)
            self.templates_dir = fallback_path
            print(f"Using fallback templates directory: {fallback_path}")
            return fallback_path
        
    def get_all_audio_files(self):
        """Get all audio files from workspace directory"""
        all_files = []
        
        # Check workspace directory
        if os.path.exists(self.workspace_dir):
            for root, _, files in os.walk(self.workspace_dir):
                for file in files:
                    if file.lower().endswith(('.mp3', '.wav', '.m4a')):
                        all_files.append(os.path.join(root, file))
        
        return all_files
    
    def get_all_transcript_files(self):
        """Get all transcript files from workspace directory"""
        all_files = []
        
        # Check workspace directory
        if os.path.exists(self.workspace_dir):
            for root, _, files in os.walk(self.workspace_dir):
                for file in files:
                    if file.lower().endswith('_transcript.txt'):
                        all_files.append(os.path.join(root, file))
        
        return all_files
    
    def find_related_files(self, file_path):
        """Find related files (audio, transcript, analysis) for a given file"""
        path = Path(file_path)
        base_name = path.stem
        
        # Remove suffixes if present
        if base_name.endswith('_transcript'):
            base_name = base_name[:-11]  # Remove '_transcript'
        elif base_name.endswith('_analysis'):
            base_name = base_name[:-9]  # Remove '_analysis'
            
        directory = path.parent
        
        # Look for related files
        related = {
            'audio': None,
            'transcript': None,
            'analysis': None
        }
        
        # Check for audio file
        audio_path = directory / f"{base_name}.mp3"
        if audio_path.exists():
            related['audio'] = str(audio_path)
        
        # Check for transcript file
        transcript_path = directory / f"{base_name}_transcript.txt"
        if transcript_path.exists():
            related['transcript'] = str(transcript_path)
            
        # Check for analysis file
        analysis_path = directory / f"{base_name}_analysis.txt"
        if analysis_path.exists():
            related['analysis'] = str(analysis_path)
            
        return related
