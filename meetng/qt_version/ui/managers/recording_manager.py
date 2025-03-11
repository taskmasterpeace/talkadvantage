from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QMessageBox, QApplication
import time
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Union, Any, List
from qt_version.utils.audio_recorder_qt import AudioRecorderQt
from qt_version.utils.logger import get_logger
from qt_version.utils.configuration_service import ConfigurationService

class RecordingManager(QObject):
    """
    Manages audio recording functionality.
    
    This class handles all aspects of audio recording including starting, stopping,
    pausing, and resuming recordings. It also manages audio levels and provides
    signals for UI components to respond to recording state changes.
    
    Signals:
        recording_started: Emitted when recording begins
        recording_stopped: Emitted when recording ends with path and data
        recording_paused: Emitted when recording is paused
        recording_resumed: Emitted when recording is resumed
        mute_toggled: Emitted when mute state changes
        audio_level_changed: Emitted when audio level changes
        status_changed: Emitted when status message changes
        error_occurred: Emitted when an error occurs
        audio_chunk_ready: Emitted when a new audio chunk is available
    """
    
    # Signals
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal(str, bytes)  # path, data
    recording_paused = pyqtSignal()
    recording_resumed = pyqtSignal()
    mute_toggled = pyqtSignal(bool)  # is_muted
    audio_level_changed = pyqtSignal(float)
    status_changed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    audio_chunk_ready = pyqtSignal(bytes)  # Add this signal for audio chunks
    
    def __init__(self, parent: Optional[QObject] = None) -> None:
        """
        Initialize the RecordingManager.
        
        Args:
            parent: The parent QObject for this manager
        """
        super().__init__(parent)
        self.config = ConfigurationService()
        self.logger = get_logger('RecordingManager')
        self._debug_mode = self.config.get_typed("debug_mode", bool, False)
        self.recorder: Optional[AudioRecorderQt] = None
        self.recording: bool = False
        self.paused: bool = False
        self.start_time: Optional[float] = None
        self.session_name: str = ""
        self.app = parent.app if parent and hasattr(parent, 'app') else None
        self.chunk_timer = QTimer()  # Timer for getting audio chunks
        self.chunk_timer.timeout.connect(self.emit_audio_chunk)
        # Replace single chunk storage with a buffer
        self.audio_buffer = bytearray()
        self.min_chunk_size = 6400  # 400ms of audio at 16kHz (16-bit samples = 2 bytes per sample)
        
        # Initialize with default values from configuration
        self.sample_rate: int = self.config.get_typed("audio_sample_rate", int, 16000)
        self.channels: int = self.config.get_typed("audio_channels", int, 1)
        
        # Keep the chunk timer but change its purpose to check the buffer
        self.chunk_timer = QTimer()
        self.chunk_timer.timeout.connect(self.check_audio_buffer)
        
        # Check for API keys in environment and store in config if not already set
        self._ensure_api_keys_in_config()
        
    def _ensure_api_keys_in_config(self) -> None:
        """Ensure API keys from environment are stored in configuration"""
        # Use a common method to check and store API keys
        self._check_and_store_api_key('OPENAI_API_KEY', 'openai_api_key')
        self._check_and_store_api_key('ASSEMBLYAI_API_KEY', 'assemblyai_api_key')
    
    def _check_and_store_api_key(self, env_var: str, config_key: str) -> None:
        """Check for API key in environment and store in config if not already set
        
        Args:
            env_var: Environment variable name
            config_key: Configuration key name
        """
        api_key = os.getenv(env_var)
        if api_key and not self.config.get_typed(config_key, str, ""):
            self.config.set(config_key, api_key)
        
    def set_session_name(self, name: str) -> None:
        """
        Set the session name for recording.
        
        Args:
            name: The name to use for the recording session
        """
        self.session_name = name
        
    def start_recording(self) -> bool:
        """
        Start recording audio.
        
        This method initializes the audio recorder and begins capturing audio.
        It also starts the chunk timer to regularly emit audio chunks for processing.
        
        Returns:
            bool: True if recording started successfully, False otherwise
        
        Emits:
            recording_started: When recording begins successfully
            error_occurred: If an error occurs during startup
        """
        if not self.session_name:
            self.error_occurred.emit("Please enter a session name")
            return False
            
        try:
            # Initialize recorder with configured sample rate and larger chunk size
            self.logger.info(f"Starting recording session: {self.session_name}")
            self.recorder = AudioRecorderQt(rate=self.sample_rate, channels=self.channels, chunk=3200)
            self.recorder.audio_level.connect(self.on_audio_level)
            self.recorder.chunk_ready.connect(self.on_chunk_ready)  # Connect to chunk_ready signal
            
            # Start recording
            self.recorder.start()
            self.recording = True
            self.paused = False
            self.start_time = time.time()
            
            # Start the chunk timer to periodically check the buffer
            self.chunk_timer.start(50)  # Check more frequently
            
            # Emit signal
            self.recording_started.emit()
            self.status_changed.emit("🎙️ Recording in progress")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start recording: {str(e)}", exc_info=True)
            error_msg = f"Failed to start recording: {str(e)}"
            self.error_occurred.emit(error_msg)
            self.recording = False
            return False
            
    def stop_recording(self) -> Tuple[Optional[str], Optional[bytes]]:
        """
        Stop recording and save the audio file.
        
        This method stops the audio recorder, saves the recording to disk,
        and returns the file path and binary data of the recording.
        
        Returns:
            tuple: (file_path, file_data) where file_path is the path to the saved
                  recording and file_data is the binary content of the file.
                  Both will be None if recording wasn't active or an error occurred.
        
        Emits:
            recording_stopped: When recording is successfully stopped with path and data
            error_occurred: If an error occurs during shutdown
        """
        if not self.recording:
            return None, None
            
        try:
            # Stop chunk timer
            self.chunk_timer.stop()
            
            # Show status while stopping
            self.status_changed.emit("Stopping recording and saving...")
            QApplication.processEvents()  # Keep UI responsive
            
            self.logger.info("Stopping recording session")
            
            # Define a function to stop recording in a separate thread
            def stop_recording_thread():
                try:
                    # Stop recording
                    mp3_path, mp3_data = self.recorder.stop()
                    self.recording = False
                    self.paused = False
                    
                    # Get session name and timestamp
                    timestamp = datetime.now().strftime("%y%m%d_%H%M")  # Format: YYMMDD_HHMM
                    
                    self.logger.info(f"Recording saved to: {mp3_path}")
                    
                    # Emit signal with data
                    self.recording_stopped.emit(mp3_path, mp3_data)
                    self.status_changed.emit("Recording stopped")
                except Exception as e:
                    self.logger.error(f"Error stopping recording: {str(e)}", exc_info=True)
                    error_msg = f"Error stopping recording: {str(e)}"
                    self.error_occurred.emit(error_msg)
            
            # Run in a separate thread to avoid blocking UI
            threading.Thread(target=stop_recording_thread, daemon=True).start()
            
            # Return None for now, the actual data will be emitted via signal
            return None, None
            
        except Exception as e:
            self.logger.error(f"Error in stop_recording: {str(e)}", exc_info=True)
            error_msg = f"Error stopping recording: {str(e)}"
            self.error_occurred.emit(error_msg)
            return None, None
            
    def pause_recording(self) -> bool:
        """
        Pause the current recording.
        
        Returns:
            bool: True if recording was paused successfully, False otherwise
        
        Emits:
            recording_paused: When recording is successfully paused
        """
        if not self.recording or not self.recorder:
            return False
            
        self.logger.info("Pausing recording")
        self.paused = True
        self.recorder.pause()
        self.recording_paused.emit()
        self.status_changed.emit("Recording paused")
        return True
        
    def resume_recording(self) -> bool:
        """
        Resume a paused recording.
        
        Returns:
            bool: True if recording was resumed successfully, False otherwise
        
        Emits:
            recording_resumed: When recording is successfully resumed
        """
        if not self.recording or not self.recorder:
            return False
            
        self.logger.info("Resuming recording")
        self.paused = False
        self.recorder.resume()
        self.recording_resumed.emit()
        self.status_changed.emit("Recording resumed")
        return True
        
    def toggle_pause(self) -> bool:
        """
        Toggle between paused and recording states.
        
        Returns:
            bool: True if operation was successful, False otherwise
        
        Emits:
            recording_paused: When recording is paused
            recording_resumed: When recording is resumed
        """
        if not self.recording:
            return False
            
        if self.paused:
            return self.resume_recording()
        else:
            return self.pause_recording()
            
    def toggle_mute(self) -> bool:
        """
        Toggle microphone mute state.
        
        When muted, audio is still recorded but not sent for transcription.
        
        Returns:
            bool: True if microphone is now muted, False if unmuted
        
        Emits:
            mute_toggled: With the new mute state
        """
        if not self.recording or not self.recorder:
            return False
            
        is_muted = self.recorder.toggle_mute()
        self.mute_toggled.emit(is_muted)
        
        if is_muted:
            self.logger.info("Microphone muted")
            self.status_changed.emit("Microphone muted - still recording but not transcribing")
        else:
            self.logger.info("Microphone unmuted")
            self.status_changed.emit("Microphone unmuted - recording and transcribing")
            
        return is_muted
        
    def on_audio_level(self, level: float) -> None:
        """
        Handle audio level updates from recorder.
        
        Args:
            level: Audio level value between 0.0 and 1.0
        
        Emits:
            audio_level_changed: With the current audio level
        """
        self.audio_level_changed.emit(level)
        
    def get_elapsed_time(self) -> float:
        """
        Get elapsed recording time in seconds.
        
        Returns:
            float: The number of seconds elapsed since recording started,
                  or 0 if recording hasn't started
        """
        if not self.start_time:
            return 0
        return time.time() - self.start_time
        
    def is_recording(self) -> bool:
        """
        Check if recording is in progress.
        
        Returns:
            bool: True if recording is active (even if paused), False otherwise
        """
        return self.recording
        
    def is_paused(self) -> bool:
        """
        Check if recording is paused.
        
        Returns:
            bool: True if recording is paused, False otherwise
        """
        return self.paused
        
    def on_chunk_ready(self, chunk: bytes) -> None:
        """
        Store incoming audio chunk in the buffer.
        
        Args:
            chunk: Raw audio data bytes
        """
        if not self.recording or self.paused:
            return
            
        # Add to buffer
        self.audio_buffer.extend(chunk)
        
    def check_audio_buffer(self) -> None:
        """
        Check audio buffer and emit chunks when enough data is accumulated.
        """
        if not self.is_ready_for_chunk_emission():
            return
            
        # Process when we have enough data
        while len(self.audio_buffer) >= self.min_chunk_size:
            # Extract a chunk of the desired size
            emit_chunk = bytes(self.audio_buffer[:self.min_chunk_size])
            
            # Remove the processed data from the buffer
            self.audio_buffer = self.audio_buffer[self.min_chunk_size:]
            
            # Emit the chunk
            self.audio_chunk_ready.emit(emit_chunk)
            
            if self._debug_mode:
                print(f"Emitted chunk of size: {len(emit_chunk)} bytes")
    
    def get_audio_chunk(self) -> Optional[bytes]:
        """
        Get the latest audio chunk if available.
        
        Returns:
            bytes: The latest audio chunk data, or None if no chunk is available
        """
        if len(self.audio_buffer) >= self.min_chunk_size:
            return bytes(self.audio_buffer[:self.min_chunk_size])
        return None
        
    def emit_audio_chunk(self) -> None:
        """
        Emit the latest audio chunk if available.
        
        This method is called by the chunk timer to regularly emit audio chunks
        for processing by other components (like the transcription service).
        
        Emits:
            audio_chunk_ready: With the latest audio chunk data
        """
        self.check_audio_buffer()
        
    def is_ready_for_chunk_emission(self) -> bool:
        """
        Check if the recorder is ready to emit audio chunks.
        
        Returns:
            bool: True if the recorder is active and has data to emit
        """
        return (self.recording and 
                not self.paused and 
                len(self.audio_buffer) >= self.min_chunk_size)
