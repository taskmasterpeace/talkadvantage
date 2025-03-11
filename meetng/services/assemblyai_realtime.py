import assemblyai as aai
import queue
import logging
import threading
import time
from typing import Optional, Dict, Any, Callable, List, Union
from qt_version.utils.logger import get_logger
from qt_version.utils.configuration_service import ConfigurationService

# Configure logging to suppress websockets debug messages
logging.getLogger('websockets').setLevel(logging.WARNING)
logging.getLogger('websockets.client').setLevel(logging.WARNING)

class AssemblyAIRealTimeTranscription:
    """
    Handles real-time transcription using AssemblyAI's SDK.
    
    This class provides a wrapper around the AssemblyAI real-time transcription
    service, handling connection management, audio streaming, and transcript
    processing. It includes features like automatic reconnection, heartbeat
    monitoring, and pause/resume functionality.
    
    Attributes:
        is_running (bool): Whether the transcription service is running
        is_paused (bool): Whether the transcription is currently paused
        on_error (Callable): Optional callback for error handling
    """
    
    def __init__(self, api_key: str, sample_rate: int = 16000):
        """
        Initialize the AssemblyAI real-time transcription service.
        
        Args:
            api_key: The AssemblyAI API key
            sample_rate: Audio sample rate in Hz (default: 16000)
        
        Raises:
            Exception: If initialization of the transcriber fails
        """
        self.config = ConfigurationService()
        self.logger = get_logger('AssemblyAIRealTime')
        # Set API key in AssemblyAI settings
        if not api_key:
            # Already imported ConfigurationService at the top
            api_key = self.config.get_typed("assemblyai_api_key", str, "")
            
        if not api_key:
            raise ValueError("AssemblyAI API key not provided and not found in configuration")
            
        aai.settings.api_key = api_key
        self.sample_rate = sample_rate
        self.transcript_queue: queue.Queue = queue.Queue()
        self.is_running: bool = False
        self.is_paused: bool = False
        self._audio_data: bytearray = bytearray()
        self.on_error: Optional[Callable[[Any], None]] = None  # Error callback attribute
        self.last_activity: float = time.time()  # Track last activity
        
        # Store configuration for potential reconnection
        self.api_key = api_key
        
        # Initialize transcriber with partial transcripts disabled
        try:
            self._initialize_transcriber()
            
            # Start heartbeat timer
            self._start_heartbeat()
        except Exception as e:
            self.logger.error(f"Failed to initialize AssemblyAI transcriber: {str(e)}", exc_info=True)
            raise
            
    def _initialize_transcriber(self) -> None:
        """
        Initialize the transcriber with current settings.
        
        This creates a new RealtimeTranscriber instance with the configured
        sample rate and callback handlers.
        """
        # Check SDK version to determine available parameters
        try:
            # Try to create transcriber with new parameters
            self.transcriber = aai.RealtimeTranscriber(
                sample_rate=self.sample_rate,
                on_data=self._handle_transcript,
                on_error=self._handle_error,
                on_open=self._handle_open,
                on_close=self._handle_close,
                # Disable partial transcripts to prevent duplicates
                disable_partial_transcripts=True
            )
            self.logger.info("Initialized transcriber with current SDK version")
        except TypeError as e:
            # If that fails, try with minimal parameters
            self.logger.warning(f"Error initializing with full parameters: {e}. Trying minimal configuration.")
            self.transcriber = aai.RealtimeTranscriber(
                sample_rate=self.sample_rate,
                on_data=self._handle_transcript,
                on_error=self._handle_error,
                on_open=self._handle_open,
                on_close=self._handle_close
            )
            self.logger.info("Initialized transcriber with minimal parameters")
        
        # Initialize tracking for transcript deduplication
        self.prev_transcript = ""
        
    def _handle_open(self, session_opened: aai.RealtimeSessionOpened) -> None:
        """
        Internal handler for session open events.
        
        Args:
            session_opened: The session opened event object
        """
        self.logger.info(f"Session opened with ID: {session_opened.session_id}")
        
    def _handle_close(self) -> None:
        """
        Internal handler for session close events.
        
        This is called when the WebSocket connection to AssemblyAI is closed.
        """
        self.logger.info("Session closed")
        
    def _handle_transcript(self, transcript: aai.RealtimeTranscript) -> None:
        """
        Internal handler for transcript events.
        
        This processes incoming transcripts from AssemblyAI and adds them
        to the transcript queue for later retrieval.
        
        Args:
            transcript: The transcript event object
        """
        if not transcript.text:
            return
            
        # Process final transcripts
        if isinstance(transcript, aai.RealtimeFinalTranscript):
            # Apply deduplication to avoid repeating text
            cleaned_text = self._deduplicate_transcript(transcript.text)
            if cleaned_text:  # Only add non-empty text
                self.transcript_queue.put(cleaned_text)
                self.logger.debug(f"Received final transcript: {cleaned_text}")
        # We're not processing partial transcripts anymore
        
        self.last_activity = time.time()  # Update activity timestamp
        
    def _handle_error(self, error: aai.RealtimeError) -> None:
        """
        Internal handler for error events.
        
        This processes error events from AssemblyAI and attempts to reconnect
        if a connection issue is detected.
        
        Args:
            error: The error event object
        """
        self.logger.error(f"AssemblyAI error: {error}")
        if self.on_error:
            self.on_error(error)
        
        # Try to reconnect if connection was lost
        if "connection" in str(error).lower():
            self._attempt_reconnection("Connection issue detected")
            
    def _attempt_reconnection(self, reason: str) -> bool:
        """
        Attempt to reconnect to the AssemblyAI service.
        
        Args:
            reason: The reason for reconnection attempt
            
        Returns:
            bool: True if reconnection was successful, False otherwise
        """
        self.logger.warning(f"{reason}, attempting to reconnect")
        try:
            self.transcriber.close()
            # Re-initialize the transcriber with fresh settings
            self._initialize_transcriber()
            self.transcriber.connect()
            self.logger.info("Reconnection successful")
            self.last_activity = time.time()
            return True
        except Exception as e:
            self.logger.error(f"Reconnection failed: {e}", exc_info=True)
            return False
    
    def _start_heartbeat(self) -> None:
        """
        Start a heartbeat timer to keep connection alive.
        
        This creates a background thread that periodically checks the connection
        status and attempts to reconnect if no activity is detected for a while.
        It also sends small keepalive packets to prevent the connection from
        timing out.
        """
        def heartbeat():
            while self.is_running:
                time.sleep(5)  # Check more frequently
                if self.is_running and not self.is_paused:
                    # If no activity for more than 30 seconds, try to reconnect
                    if time.time() - self.last_activity > 30:
                        # Use a separate thread for reconnection to avoid blocking
                        def reconnect():
                            self._attempt_reconnection("No activity detected for 30 seconds")
                        
                        threading.Thread(target=reconnect, daemon=True).start()
                    else:
                        # Send a small ping to keep the connection alive
                        try:
                            if hasattr(self.transcriber, '_connection') and self.transcriber._connection:
                                # This is a dummy audio chunk to keep the connection alive
                                # Use a very small chunk to minimize impact
                                self._send_keepalive()
                        except Exception as e:
                            self.logger.error(f"Error sending keepalive: {e}", exc_info=True)
        
        threading.Thread(target=heartbeat, daemon=True).start()
    
    def start(self) -> None:
        """
        Start real-time transcription.
        
        This connects to the AssemblyAI service and begins the transcription session.
        
        Raises:
            Exception: If connection to the service fails
        """
        try:
            self.is_running = True
            self.transcriber.connect()
            self.last_activity = time.time()
            self.logger.info("Started real-time transcription")
        except Exception as e:
            self.logger.error(f"Failed to start transcription: {str(e)}", exc_info=True)
            raise
                        
    def process_audio_chunk(self, audio_data: bytes) -> None:
        """
        Process incoming audio chunk.
        
        This sends the audio data to AssemblyAI for transcription.
        
        Args:
            audio_data: Raw audio data bytes
        """
        if self.is_running and not self.is_paused:
            try:
                self._audio_data.extend(audio_data)
                self.transcriber.stream(audio_data)
                self.last_activity = time.time()  # Update last activity time
            except Exception as e:
                self.logger.error(f"Error processing audio chunk: {str(e)}", exc_info=True)
                if self.on_error:
                    self.on_error(e)

    def pause(self) -> None:
        """
        Pause transcription.
        
        This pauses the processing of audio chunks but keeps the connection open.
        """
        self.is_paused = True
        self.logger.info("Transcription paused")
        
    def resume(self) -> None:
        """
        Resume transcription.
        
        This resumes the processing of audio chunks after being paused.
        """
        self.is_paused = False
        self.logger.info("Transcription resumed")
        
    def get_next_transcription(self) -> Optional[str]:
        """
        Get next available transcription result.
        
        This retrieves and combines up to 5 transcription results from the queue.
        
        Returns:
            str: Combined transcription text, or None if no transcriptions are available
        """
        try:
            # Process up to 5 items at once to avoid blocking too long
            results = []
            for _ in range(5):  # Process max 5 items at once
                if self.transcript_queue.empty():
                    break
                results.append(self.transcript_queue.get_nowait())
            
            # Return combined results if any
            if results:
                return " ".join(results)
            return None
        except queue.Empty:
            return None
        except Exception as e:
            self.logger.error(f"Error getting next transcription: {str(e)}", exc_info=True)
            return None
            
    def get_audio_data(self) -> bytes:
        """
        Get recorded audio data.
        
        Returns:
            bytes: All accumulated audio data since recording started
        """
        return bytes(self._audio_data)
        
    def stop(self) -> None:
        """
        Stop transcription.
        
        This closes the connection to AssemblyAI and stops the transcription session.
        """
        if self.is_running:
            try:
                self.is_running = False
                self.transcriber.close()
                self.logger.info("Stopped transcription")
            except Exception as e:
                self.logger.error(f"Error stopping transcription: {str(e)}", exc_info=True)
    def _deduplicate_transcript(self, text: str) -> str:
        """
        Remove partial transcript remnants from final output.
        
        Args:
            text: The transcript text to deduplicate
            
        Returns:
            str: Deduplicated text
        """
        if self.prev_transcript and text.startswith(self.prev_transcript):
            # Only return the new part
            new_text = text[len(self.prev_transcript):].lstrip()
            self.prev_transcript = text
            return new_text
        
        # Store for future deduplication
        self.prev_transcript = text
        return text
        
    def _send_keepalive(self) -> None:
        """
        Send a small audio chunk to keep the connection alive.
        
        This sends a minimal audio packet to prevent the connection from timing out
        during periods of silence.
        """
        self.transcriber.stream(b'\x00' * 10)
