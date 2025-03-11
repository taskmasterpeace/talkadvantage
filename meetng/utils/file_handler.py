import re
import os
import json
import platform
from pathlib import Path
from typing import Tuple, List, Dict, Optional
from datetime import datetime, date
import shutil

class FileStatus:
    """Manages status and metadata for audio files"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.metadata_path = file_path.replace('.mp3', '_metadata.json')
        self.load_metadata()
        
    def load_metadata(self):
        """Load or initialize metadata"""
        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {
                "status": {
                    "has_audio": True,
                    "has_transcript": False,
                    "processed_by_llm": False,
                    "last_modified": datetime.now().strftime('%y%m%d_%H%M'),
                    "chunks": []
                },
                "summary": None,
                "chapters": [],
                "tags": [],
                "notes": ""
            }
            self.save_metadata()
            
    def update_status(self, **kwargs):
        """Update status fields and save"""
        self.metadata["status"].update(kwargs)
        self.metadata["status"]["last_modified"] = datetime.now().strftime('%y%m%d_%H%M')
        self.save_metadata()
        
    def save_metadata(self):
        """Save metadata to file"""
        with open(self.metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2)

class FileHandler:
    """Handles file operations for audio transcription files.
    
    Manages MP3 files and their corresponding transcripts, including file naming
    conventions and status tracking across different source types (batch, recordings, imports).
    """
    
    def __init__(self):
        from config.constants import RECORDINGS_DIR, IMPORTS_DIR, BATCH_DIR
        self.processed_files: List[str] = []
        self.skipped_files: List[Tuple[str, str]] = []
        self.date_pattern = re.compile(r'^(\d{6})_.*\.mp3$')
        self.strict_naming = True
        self._debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        
        # Use constants for folder structure
        self.recordings_dir = RECORDINGS_DIR
        self.imports_dir = IMPORTS_DIR 
        self.batch_dir = BATCH_DIR
        self.folders = {
            "recordings": self.recordings_dir,
            "imports": self.imports_dir,
            "batch": self.batch_dir
        }
        
        # Current working folder
        self._current_folder: Optional[str] = None
        self._folder_observers: List[callable] = []
        
    def setup_folders(self):
        """Create necessary folder structure"""
        for folder in self.folders.values():
            os.makedirs(folder, exist_ok=True)
            
    def get_dated_folder(self, base_folder: str) -> str:
        """Get or create a dated folder within the specified base folder"""
        date_str = datetime.now().strftime('%y%m%d')
        folder_path = os.path.join(self.folders[base_folder], date_str)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path
        
    def get_creation_date(self, file_path: str | Path) -> datetime:
        """Gets file creation date in a cross-platform compatible way.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            datetime: The file's creation date.
        """
        path = Path(file_path)
        
        if platform.system() == 'Windows':
            return datetime.fromtimestamp(path.stat().st_ctime)
            
        try:
            return datetime.fromtimestamp(path.stat().st_birthtime)
        except AttributeError:
            return datetime.fromtimestamp(path.stat().st_mtime)

    def rename_to_convention(self, original_path: str | Path) -> Optional[str]:
        """Renames file to match YYMMDD_ convention using file creation date.
        
        Args:
            original_path: Path to the file to be renamed.
            
        Returns:
            str: New filename if successful, None if rename failed.
        """
        try:
            path = Path(original_path)
            creation_date = self.get_creation_date(path)
            date_prefix = creation_date.strftime('%y%m%d')
            
            # Remove any existing date prefix if present
            clean_filename = re.sub(r'^\d{6}_', '', path.name)
            new_filename = f"{date_prefix}_{clean_filename}"
            new_path = path.parent / new_filename
            
            if new_path.exists():
                return None
                
            path.rename(new_path)
            return new_filename
            
        except Exception:
            return None

    def check_transcript_exists(self, file_path: str | Path, output_type: str = "txt") -> bool:
        """Checks if transcript already exists for given file.
        
        Args:
            file_path: Path to the audio file.
            output_type: Expected transcript file extension.
            
        Returns:
            bool: True if transcript exists, False otherwise.
        """
        # Update debug mode in case it changed
        self._debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        path = Path(file_path)
        
        # Always work with absolute paths
        if not path.is_absolute():
            if self._current_folder:
                path = Path(self._current_folder) / path
            else:
                # Try to find the file in current directory
                path = Path.cwd() / path
        
        # Ensure path exists
        if not path.exists():
            if self._debug_mode:
                print(f"File not found: {path}")
            return False
        
        transcript_path = path.parent / f"{path.stem}_transcript.{output_type}"
        
        # Debug logging
        debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        if debug_mode:
            print(f"\nChecking transcript for: {path}")
            print(f"Looking for: {transcript_path}")
            print(f"Exists: {transcript_path.exists()}")
            
        exists = transcript_path.exists()
        
        if not exists and debug_mode:
            print("Files in directory:")
            for f in path.parent.glob('*'):
                print(f"- {f.name}")
                
        return exists

    def get_mp3_files(self, folder_path: str | Path, include_subfolders: bool = False) -> Tuple[List[str], Dict[str, bool]]:
        """Return list of MP3 files with transcript status.
        
        Args:
            folder_path: Path to folder containing MP3 files.
            include_subfolders: Whether to scan subfolders recursively.
            
        Returns:
            Tuple containing:
                - List of MP3 filenames
                - Dictionary mapping filenames to transcript status
        """
        print(f"Scanning folder: {folder_path}")
        folder = Path(folder_path)
        mp3_files = []
        transcript_status = {}
        processed_files = set()  # Track processed files to avoid duplicates
        debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        
        try:
            # Store current folder for transcript checking
            self._current_folder = str(folder)
            
            # Get files based on recursion setting
            pattern = '**/*.mp3' if include_subfolders else '*.mp3'
            for f in folder.glob(pattern):
                abs_path = str(f.absolute())
                
                # Skip if already processed or not a valid MP3 file
                if abs_path in processed_files or not f.name.lower().endswith('.mp3'):
                    continue
                    
                # Skip files that don't match YYMMDD_ pattern
                if not re.match(r'^\d{6}_', f.name):
                    continue
                    
                if debug_mode:
                    print(f"\nProcessing file: {f}")
                
                # Check for transcript using absolute path
                has_transcript = self.check_transcript_exists(f.absolute())
                transcript_status[abs_path] = has_transcript
                processed_files.add(abs_path)
                
                if debug_mode:
                    print(f"Transcript status for {f.name}: {has_transcript}")
                
                mp3_files.append(abs_path)
            
            # Sort the final list
            mp3_files.sort()
            
        except Exception as e:
            print(f"Error scanning folder: {str(e)}")
            
        print(f"Final file list: {mp3_files}")
        return mp3_files, transcript_status
    
    def extract_date_from_filename(self, filename):
        """Extract date from filename format YYMMDD_*"""
        date_match = re.search(r'(\d{6})_', filename)
        if date_match:
            date_str = date_match.group(1)
            return datetime.datetime.strptime(date_str, '%y%m%d')
        return None
    
    def generate_output_filename(self, input_file: str | Path, output_type: str, source_type: str = "batch") -> str:
        """Generate output filename maintaining convention.
        
        Args:
            input_file: Input audio filename.
            output_type: Desired output file extension.
            source_type: Type of source ("recordings", "imports", or "batch").
            
        Returns:
            str: Generated output filename with transcript suffix.
        """
        path = Path(input_file)
        dated_folder = self.get_dated_folder(source_type)
        return os.path.join(dated_folder, f"{path.stem}_transcript.{output_type}")
        
    def add_folder_observer(self, callback: callable):
        """Add a callback to be notified when the current folder changes"""
        self._folder_observers.append(callback)
        
    def set_current_folder(self, folder_path: str):
        """Set the current working folder and notify observers"""
        self._current_folder = folder_path
        for callback in self._folder_observers:
            callback(folder_path)
            
    def get_current_folder(self) -> Optional[str]:
        """Get the current working folder"""
        return self._current_folder
        
    def load_files_from_folder(self, folder_path: str) -> Tuple[List[str], Dict[str, bool]]:
        """Load audio files from a folder and return their transcript status.
        
        Args:
            folder_path: Path to folder containing audio files
            
        Returns:
            Tuple containing:
                - List of audio filenames
                - Dictionary mapping filenames to transcript status
        """
        self.set_current_folder(folder_path)
        return self.get_mp3_files(folder_path)
        
    def save_recording(self, audio_data: bytes, filename: str, metadata: dict = None) -> str:
        """Save a recording to the recordings folder with standardized naming.
        
        Args:
            audio_data: Raw audio data.
            filename: Base filename (will be standardized).
            metadata: Optional dictionary of metadata to save alongside recording.
            
        Returns:
            str: Full path to saved recording.
        """
        dated_folder = self.get_dated_folder("recordings")
        # Ensure filename follows YYMMDD_HHMM_name convention
        if not re.match(r'^\d{6}_\d{4}_.*$', filename):
            current_time = datetime.now()
            filename = f"{current_time.strftime('%y%m%d_%H%M')}_{filename}"
        
        output_path = os.path.join(dated_folder, f"{filename}.mp3")
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save audio file
            with open(output_path, 'wb') as f:
                f.write(audio_data)
                
            # Save metadata if provided
            if metadata:
                metadata_path = output_path.replace('.mp3', '_metadata.json')
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2)
                
            return output_path
            
        except Exception as e:
            print(f"Error saving recording: {str(e)}")
            return None
