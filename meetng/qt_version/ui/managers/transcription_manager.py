from PyQt6.QtCore import QObject, pyqtSignal, QTimer
import time
import os
import threading
import audioop
import math
from typing import Optional, List, Dict, Any, Tuple
from PyQt6.QtWidgets import QApplication
from services.assemblyai_realtime import AssemblyAIRealTimeTranscription
from qt_version.utils.logger import get_logger
from qt_version.utils.configuration_service import ConfigurationService

class TranscriptionManager(QObject):
    """
    Manages real-time transcription functionality.
    
    This class handles the real-time transcription of audio data, including
    initialization of the transcription service, processing of audio chunks,
    and detection of voice commands/triggers.
    
    Signals:
        transcription_ready: Emitted when new transcribed text is available
        transcription_error: Emitted when an error occurs during transcription
        status_changed: Emitted when the status of the transcription service changes
        trigger_detected: Emitted when a voice command trigger is detected
    """
    
    # Signals
    transcription_ready = pyqtSignal(str)  # transcribed text
    transcription_error = pyqtSignal(str)  # error message
    status_changed = pyqtSignal(str)  # status message
    trigger_detected = pyqtSignal(dict)  # trigger info
    
    def initialize(self, api_key: Optional[str] = None) -> bool:
        """
        Initialize the transcription service.
        
        Args:
            api_key: Optional API key for the transcription service.
                    If not provided, will use the key from configuration.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        
        Emits:
            transcription_error: If initialization fails
            status_changed: When initialization completes
        """
        try:
            # Use provided API key or the one from configuration
            api_key = api_key or self.api_key
                
            if not api_key:
                self.logger.error("AssemblyAI API key not found")
                self.transcription_error.emit("AssemblyAI API key not found. Please configure it in Settings.")
                return False
                
            self.logger.info("Initializing AssemblyAI transcription service")
            
            self.transcription = AssemblyAIRealTimeTranscription(
                api_key=api_key,
                sample_rate=self.sample_rate
            )
            
            # Set error callback
            self.transcription.on_error = self._on_transcription_error
            
            self.transcription.start()
            self.status_changed.emit("Transcription service initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize transcription: {str(e)}", exc_info=True)
            error_msg = f"Failed to initialize transcription: {str(e)}"
            self.transcription_error.emit(error_msg)
            return False
        
    def __init__(self, parent: Optional[QObject] = None) -> None:
        """
        Initialize the TranscriptionManager.
        
        Args:
            parent: The parent QObject for this manager
        """
        super().__init__(parent)
        self.config = ConfigurationService()
        self.logger = get_logger('TranscriptionManager')
        self._debug_mode = self.config.get_typed("debug_mode", bool, False)
        self.transcription: Optional[AssemblyAIRealTimeTranscription] = None
        self.triggers: List[Dict[str, Any]] = self.config.get_typed("system_triggers", list, [])
        self.accumulated_text: str = ""
        self.last_process_time: float = time.time()
        self.last_sound_time: float = time.time()
        
        # Initialize with default values from configuration
        self.sample_rate: int = self.config.get_typed("audio_sample_rate", int, 16000)
        self.api_key: str = self.config.get_typed("assemblyai_api_key", str, os.getenv('ASSEMBLYAI_API_KEY', ''))
    
    def _on_transcription_error(self, error: Any) -> None:
        """
        Handle errors from the transcription service.
        
        Args:
            error: The error object or message from the transcription service
        
        Emits:
            transcription_error: With the error message
        """
        self.logger.error(f"AssemblyAI error: {str(error)}")
        self.transcription_error.emit(f"AssemblyAI error: {str(error)}")
            
    def process_audio_chunk(self, chunk: bytes) -> None:
        """
        Process incoming audio chunk.
        
        This method sends the audio chunk to the transcription service and
        handles any resulting transcription text.
        
        Args:
            chunk: Raw audio data bytes
        
        Emits:
            transcription_ready: When new transcribed text is available
            transcription_error: If an error occurs during processing
            status_changed: When status changes
        """
        if not self.transcription:
            return
            
        try:
            # Log audio statistics for diagnostics
            if self._debug_mode:
                self.log_audio_stats(chunk)
                
            # Apply audio normalization
            try:
                # Peak normalization
                max_sample = audioop.max(chunk, 2)  # 2 bytes per sample for 16-bit audio
                if max_sample > 0:
                    # Normalize to 80% of maximum to avoid clipping
                    target_peak = int(32767 * 0.8)
                    normalized_chunk = audioop.mul(chunk, 2, target_peak / max_sample)
                else:
                    normalized_chunk = chunk
                    
                # Check if audio level is above noise floor
                rms = audioop.rms(normalized_chunk, 2)
                if rms < 500:  # Approximate -45dB noise floor
                    if self._debug_mode:
                        print(f"Audio level too low: {rms} RMS, skipping chunk")
                    return
                    
            except Exception as e:
                self.logger.error(f"Error normalizing audio: {str(e)}", exc_info=True)
                normalized_chunk = chunk  # Use original if normalization fails
            
            # Send normalized audio chunk to AssemblyAI
            self.transcription.process_audio_chunk(normalized_chunk)
            
            # Get latest transcription - this is quick since we're just checking the queue
            transcript_text = self.transcription.get_next_transcription()
            
            # Only process if we have text
            if transcript_text and transcript_text.strip():
                # Debug output
                self.logger.debug(f"Received transcript: {transcript_text}")
                    
                # Emit signal with transcribed text
                self.transcription_ready.emit(transcript_text)
                
                # Add to accumulated text
                self.accumulated_text += transcript_text + " "
                
                # Check for voice commands/triggers - this should be quick
                self.check_triggers(transcript_text)
                
                # Update status to show transcription is working
                self.status_changed.emit("Transcription active")
                
        except Exception as e:
            self.logger.error(f"Error processing audio chunk: {str(e)}", exc_info=True)
            
            # For serious errors, schedule reconnection in a separate thread
            if self._is_connection_error(str(e)):
                self._schedule_reconnection()
            else:
                self.transcription_error.emit(f"Transcription error: {str(e)}")
                
    def _is_connection_error(self, error_message: str) -> bool:
        """
        Check if an error is related to connection issues.
        
        Args:
            error_message: The error message to check
            
        Returns:
            bool: True if it's a connection-related error, False otherwise
        """
        connection_keywords = ["connection", "closed", "timeout", "disconnected"]
        return any(keyword in error_message.lower() for keyword in connection_keywords)
        
    def _schedule_reconnection(self) -> None:
        """
        Schedule a reconnection attempt in a separate thread.
        
        This avoids blocking the UI thread during reconnection attempts.
        """
        self.logger.warning("Connection issue detected, attempting to reconnect")
        self.status_changed.emit("Reconnecting transcription service...")
        
        def reconnect():
            try:
                self.stop()
                time.sleep(1)
                self.initialize()
            except Exception as reinit_error:
                self.logger.error(f"Failed to reconnect: {str(reinit_error)}", exc_info=True)
                self.transcription_error.emit(f"Failed to reconnect: {str(reinit_error)}")
        
        # Use a thread for reconnection to avoid blocking the UI
        threading.Thread(target=reconnect, daemon=True).start()
            
    def pause(self) -> None:
        """
        Pause transcription.
        
        This pauses the transcription service but keeps the connection open.
        """
        if self.transcription:
            self.logger.info("Pausing transcription")
            self.transcription.pause()
            
    def resume(self) -> None:
        """
        Resume transcription.
        
        This resumes a previously paused transcription service.
        """
        if self.transcription:
            self.logger.info("Resuming transcription")
            self.transcription.resume()
            
    def stop(self) -> None:
        """
        Stop transcription service.
        
        This completely stops the transcription service and closes the connection.
        """
        if self.transcription:
            self.logger.info("Stopping transcription service")
            self.transcription.stop()
            self.transcription = None
            
    def set_triggers(self, triggers: List[Dict[str, Any]]) -> None:
        """
        Set voice command triggers.
        
        Args:
            triggers: List of trigger dictionaries, each containing at minimum
                     'trigger_phrase' and 'action' keys
        """
        self.logger.info(f"Setting {len(triggers)} voice command triggers")
        self.triggers = triggers
        
    def check_triggers(self, text: str) -> None:
        """
        Check for trigger phrases in text.
        
        This method scans the provided text for any configured trigger phrases
        and emits a signal if a match is found.
        
        Args:
            text: The text to check for trigger phrases
        
        Emits:
            trigger_detected: When a trigger phrase is detected in the text
        """
        if not self.triggers:
            return
            
        self.logger.debug(f"Checking triggers in text: {text[:50]}...")
        
        # Convert to lowercase once for efficiency
        text = text.lower()
        
        # Check each trigger
        for trigger in self.triggers:
            if self._check_single_trigger(trigger, text):
                # Emit signal with trigger info
                self.trigger_detected.emit(trigger)
                
    def _check_single_trigger(self, trigger: Dict[str, Any], text: str) -> bool:
        """
        Check if a single trigger matches the text.
        
        Args:
            trigger: The trigger dictionary containing action and phrases
            text: The lowercase text to check against
            
        Returns:
            bool: True if the trigger matches, False otherwise
        """
        # Text is already lowercase from the calling function
        
        # Split trigger phrases by semicolon and strip whitespace
        trigger_phrases = [phrase.strip().lower() 
                         for phrase in trigger['trigger_phrase'].split(';')]
        
        # Check each phrase - use more flexible matching
        for phrase in trigger_phrases:
            if not phrase:
                continue
                
            # Try exact match first
            if phrase in text:
                self.logger.info(f"Matched trigger phrase: '{phrase}' for action: {trigger['action']}")
                return True
                
            # Try word boundary matching for more accuracy
            words = phrase.split()
            if len(words) > 1:  # Only for multi-word phrases
                # Check if all words appear in the text in the correct order
                text_words = text.split()
                for i in range(len(text_words) - len(words) + 1):
                    if all(text_words[i+j].lower().startswith(words[j]) for j in range(len(words))):
                        self.logger.info(f"Matched partial trigger phrase: '{phrase}' for action: {trigger['action']}")
                        return True
        
        return False
    
    def log_audio_stats(self, chunk: bytes) -> None:
        """
        Log statistics about the audio chunk for diagnostic purposes.
        
        Args:
            chunk: Raw audio data bytes
        """
        try:
            # Calculate RMS (volume level)
            rms = audioop.rms(chunk, 2)  # 2 bytes per sample for 16-bit audio
            
            # Calculate peak level
            peak = audioop.max(chunk, 2)
            
            # Calculate signal-to-noise ratio (approximate)
            if rms > 0:
                snr = 20 * math.log10(peak / rms) if peak > 0 else 0
            else:
                snr = 0
                
            self.logger.debug(f"Audio stats - Size: {len(chunk)} bytes, RMS: {rms}, "
                             f"Peak: {peak}, SNR: {snr:.2f}dB")
        except Exception as e:
            self.logger.error(f"Error calculating audio stats: {str(e)}")
                
    def get_accumulated_text(self) -> str:
        """
        Get accumulated text from recent transcriptions.
        
        Returns:
            str: The accumulated text
        """
        return self.accumulated_text
        
    def reset_accumulated_text(self) -> None:
        """
        Reset accumulated text.
        
        This clears the accumulated text buffer and resets the process timer.
        """
        self.accumulated_text = ""
        self.last_process_time = time.time()
        
    def should_process_chunk(self, interval_type: str, interval_value: float) -> bool:
        """
        Determine if current chunk should be processed based on interval settings.
        
        Args:
            interval_type: The type of interval ('manual', 'time', 'words', 'silence')
            interval_value: The value for the interval (seconds, word count, etc.)
        
        Returns:
            bool: True if the chunk should be processed, False otherwise
        """
        if interval_type == "manual":
            return False
            
        elif interval_type == "time":
            current_time = time.time()
            return (current_time - self.last_process_time) >= interval_value
            
        elif interval_type == "words":
            word_count = len(self.accumulated_text.split())
            return word_count >= interval_value
            
        elif interval_type == "silence":
            # Silence detection is handled separately with audio levels
            return False
            
        return False
