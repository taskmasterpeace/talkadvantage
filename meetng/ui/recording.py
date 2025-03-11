"""
Recording module for audio capture and real-time transcription.
This module provides the UI and functionality for recording audio,
processing it through speech-to-text services, and analyzing the content.
"""

import os
import time
import threading
import datetime
import pyaudio
import wave
import numpy as np
from pydub import AudioSegment
import tkinter as tk
from tkinter import ttk, messagebox

class AudioRecorder:
    """
    Audio recording class that handles capturing audio from microphone
    and saving it to disk.
    """
    def __init__(self, format=pyaudio.paInt16, channels=1, rate=44100, 
                 chunk=1024, mp3_bitrate='128k'):
        self.format = format
        self.channels = channels
        self.rate = rate
        self.chunk = chunk
        self.mp3_bitrate = mp3_bitrate
        self.audio = pyaudio.PyAudio()
        self.frames = []
        self.stream = None
        self.is_recording = False
        
    def start(self, callback=None):
        """Start recording audio"""
        self.frames = []
        self.is_recording = True
        
        def record_thread():
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            while self.is_recording:
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                self.frames.append(data)
                if callback:
                    callback(data)
                    
        self.thread = threading.Thread(target=record_thread)
        self.thread.daemon = True
        self.thread.start()
        
    def stop(self):
        """Stop recording and return the audio data"""
        if not self.is_recording:
            return None
            
        self.is_recording = False
        if self.thread:
            self.thread.join(timeout=2.0)
            
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            
        # Convert frames to audio segment
        if not self.frames:
            return None
            
        # Create WAV data
        wav_data = b''.join(self.frames)
        
        # Convert to AudioSegment
        audio_segment = AudioSegment(
            data=wav_data,
            sample_width=self.audio.get_sample_size(self.format),
            frame_rate=self.rate,
            channels=self.channels
        )
        
        return audio_segment
        
    def get_audio_level(self):
        """Get current audio level (0.0 to 1.0)"""
        if not self.frames or len(self.frames) < 2:
            return 0.0
            
        # Get the most recent frame
        recent_frame = self.frames[-1]
        
        # Convert to numpy array
        try:
            data_np = np.frombuffer(recent_frame, dtype=np.int16)
            # Calculate RMS and normalize
            rms = np.sqrt(np.mean(np.square(data_np)))
            # Normalize to 0-1 range (16-bit audio has max value of 32768)
            normalized = min(1.0, rms / 32768)
            return normalized
        except:
            return 0.0
            
    def __del__(self):
        """Clean up resources"""
        if self.stream:
            self.stream.close()
        if hasattr(self, 'audio') and self.audio:
            self.audio.terminate()
