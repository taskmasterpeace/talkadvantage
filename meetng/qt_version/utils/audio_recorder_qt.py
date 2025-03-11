from PyQt6.QtCore import QObject, pyqtSignal
import pyaudio
import numpy as np
import wave
import threading
from typing import Optional, Callable, Tuple, List, Union, Any
from pydub import AudioSegment
import io
import os
from datetime import datetime
from qt_version.utils.configuration_service import ConfigurationService

class AudioRecorderQt(QObject):
    """
    Handles real-time audio recording with Qt signals.
    
    This class provides audio recording functionality with PyAudio, including
    features like pause/resume, mute/unmute, and audio level monitoring.
    It emits signals for audio level visualization and provides audio chunks
    for real-time processing.
    
    Signals:
        audio_level: Emitted with the current audio level (0.0-1.0)
        chunk_ready: Emitted with each new audio chunk
    """
    
    # Signals
    audio_level = pyqtSignal(float)  # Audio level for visualization
    chunk_ready = pyqtSignal(bytes)  # Audio chunk for processing
    
    def __init__(self, format: int = pyaudio.paInt16, channels: int = 1, 
                 rate: int = 16000, chunk: int = 3200) -> None:
        """
        Initialize the audio recorder.
        
        Args:
            format: PyAudio format constant (default: paInt16)
            channels: Number of audio channels (default: 1 for mono)
            rate: Sample rate in Hz (default: 16000)
            chunk: Frames per buffer (default: 3200 - 200ms at 16kHz)
        """
        super().__init__()
        self.config = ConfigurationService()
        self.format = format
        self.channels = channels
        self.rate = rate
        self.chunk = chunk
        self.recording: bool = False
        self.paused: bool = False
        self.muted: bool = False
        self.audio = pyaudio.PyAudio()
        self._stream: Optional[pyaudio.Stream] = None
        self._frames: List[bytes] = []
        
        # Get output directory from configuration
        self.output_dir = self.config.get_typed("recordings_dir", str, "recordings")
        
    def start(self) -> None:
        """
        Start recording audio.
        
        This initializes the PyAudio stream and begins capturing audio data.
        If recording is already in progress, this method does nothing.
        """
        if self.recording:
            return
            
        self._frames = []
        self.recording = True
        
        # Open audio stream
        self._stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk,
            stream_callback=self._audio_callback
        )
        
    def _audio_callback(self, in_data: bytes, frame_count: int, 
                       time_info: dict, status: int) -> Tuple[bytes, int]:
        """
        Handle incoming audio data from PyAudio.
        
        This callback is called by PyAudio when new audio data is available.
        It stores the data, calculates the audio level, and emits signals.
        
        Args:
            in_data: Raw audio data
            frame_count: Number of frames
            time_info: Dictionary with timing information
            status: Status flag from PyAudio
        
        Returns:
            tuple: (in_data, paContinue) to continue recording
        
        Emits:
            audio_level: With the current audio level (0.0-1.0)
            chunk_ready: With the raw audio data (if not muted)
        """
        if self.recording and not self.paused:
            self._frames.append(in_data)
            
            # Calculate audio level
            audio_data = np.frombuffer(in_data, dtype=np.int16)
            level = np.abs(audio_data).mean() / 32767.0  # Normalize to 0-1
            self.audio_level.emit(level)
            
            # Emit chunk for processing if not muted
            if not self.muted:
                self.chunk_ready.emit(in_data)
            
        return (in_data, pyaudio.paContinue)

    def pause(self) -> None:
        """
        Pause recording.
        
        This pauses the recording without stopping the audio stream.
        Audio data will not be stored while paused.
        """
        self.paused = True
        
    def resume(self) -> None:
        """
        Resume recording.
        
        This resumes a previously paused recording.
        """
        self.paused = False
        
    def mute(self) -> None:
        """
        Mute audio processing.
        
        When muted, audio is still recorded but not emitted for processing.
        This affects the chunk_ready signal but not the actual recording.
        """
        self.muted = True
        
    def unmute(self) -> None:
        """
        Unmute audio processing.
        
        This resumes emitting audio chunks for processing after being muted.
        """
        self.muted = False
        
    def toggle_mute(self) -> bool:
        """
        Toggle mute state.
        
        Returns:
            bool: The new mute state (True if muted, False if unmuted)
        """
        self.muted = not self.muted
        return self.muted
        
    def stop(self, output_dir: Optional[str] = None) -> Tuple[str, bytes]:
        """
        Stop recording and save the recorded audio data.
        
        This stops the recording, closes the audio stream, and saves the
        recorded audio as an MP3 file.
        
        Args:
            output_dir: Optional directory to save the recording.
                       If not provided, uses the configured output directory.
        
        Returns:
            tuple: (mp3_path, mp3_data) where mp3_path is the path to the saved
                  MP3 file and mp3_data is the binary content of the file.
                  Returns empty strings if recording fails.
        """
        if not self.recording:
            return "", b''
            
        self.recording = False
        
        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
            
        # Use provided output directory or default from config
        output_dir = output_dir or self.output_dir
            
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename based on current timestamp
        timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
        base_filename = f"{timestamp}"
        wav_path = os.path.join(output_dir, f"{base_filename}_temp.wav")
        mp3_path = os.path.join(output_dir, f"{base_filename}.mp3")
        
        try:
            # Save raw audio to temporary WAV first
            with wave.open(wav_path, 'wb') as wav_file:
                wav_file.setnchannels(self.channels)
                wav_file.setsampwidth(self.audio.get_sample_size(self.format))
                wav_file.setframerate(self.rate)
                wav_file.writeframes(b''.join(self._frames))
            
            # Convert WAV to MP3 using pydub
            audio_segment = AudioSegment.from_wav(wav_path)
            audio_segment.export(mp3_path, format='mp3', bitrate='192k')
            
            # Read the MP3 data
            with open(mp3_path, 'rb') as mp3_file:
                mp3_data = mp3_file.read()
            
            # Clean up temporary WAV file
            os.remove(wav_path)
            
            # Clean up memory
            self._frames = []
            
            return mp3_path, mp3_data
            
        except Exception as e:
            print(f"Error during audio conversion: {e}")
            # Clean up any temporary files
            if os.path.exists(wav_path):
                os.remove(wav_path)
            return "", b''
        
    def __del__(self) -> None:
        """
        Cleanup resources when the object is destroyed.
        
        This ensures that PyAudio resources are properly released.
        """
        if self._stream:
            self._stream.close()
        self.audio.terminate()
