from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QSlider, QStyle, QSizePolicy
)
from PyQt6.QtCore import Qt, QUrl, QTimer, pyqtSignal
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtGui import QPainter, QPen, QColor
from datetime import timedelta
import soundfile as sf
import numpy as np
from pathlib import Path
import os
import re

class BookmarkLegend(QWidget):
    """Legend widget for bookmarks"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(2)
        self.bookmark_colors = {}  # Map bookmark to color
        
    def update_bookmarks(self, bookmarks):
        # Clear existing items
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().deleteLater()
            
        # Generate colors for bookmarks
        colors = [
            QColor(255, 165, 0),   # Orange
            QColor(50, 205, 50),   # Lime Green
            QColor(30, 144, 255),  # Dodger Blue
            QColor(255, 105, 180), # Hot Pink
            QColor(147, 112, 219)  # Medium Purple
        ]
        
        # Add legend items
        for i, bookmark in enumerate(bookmarks):
            color = colors[i % len(colors)]
            self.bookmark_colors[bookmark['position']] = color
            
            item = QWidget()
            item_layout = QHBoxLayout(item)
            item_layout.setContentsMargins(0, 0, 0, 0)
            
            # Color sample
            color_sample = QLabel()
            color_sample.setFixedSize(12, 12)
            color_sample.setStyleSheet(
                f"background-color: {color.name()}; border: 1px solid #999;"
            )
            item_layout.addWidget(color_sample)
            
            # Bookmark text
            text = QLabel(f"{bookmark['text'][:30]}...")
            item_layout.addWidget(text)
            
            self.layout.addWidget(item)

class WaveformWidget(QWidget):
    """Custom widget for audio waveform visualization"""
    bookmark_clicked = pyqtSignal(int)  # Emit position when bookmark clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.waveform_data = None
        self.playhead_position = 0
        self.duration = 0
        self.bookmarks = []
        self.setMinimumHeight(200)
        self.setMouseTracking(True)
        
    def load_audio(self, file_path):
        """Load audio and look for transcript bookmarks"""
        try:
            # Load audio file
            data, sample_rate = sf.read(file_path)
            
            # Look for transcript and load bookmarks
            transcript_path = str(Path(file_path).with_suffix('')) + '_transcript.txt'
            self.bookmarks = []
            if os.path.exists(transcript_path):
                with open(transcript_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        # Look for timestamp patterns like [MM:SS]
                        matches = re.finditer(r'\[(\d{2}:\d{2})\]\s*([^\n\[\]]+)', line)
                        for match in matches:
                            timestamp, text = match.groups()
                            # Convert MM:SS to milliseconds
                            m, s = map(int, timestamp.split(':'))
                            ms = (m * 60 + s) * 1000
                            self.bookmarks.append({
                                'position': ms,
                                'text': text.strip()
                            })
            
            # Convert to mono if stereo
            if len(data.shape) > 1:
                data = np.mean(data, axis=1)
            
            # Downsample for display
            samples = len(data)
            target_points = self.width() or 1000  # Use widget width or default
            step = max(1, samples // target_points)
            
            # Calculate absolute peak values for chunks
            self.waveform_data = []
            for i in range(0, samples, step):
                chunk = data[i:i+step]
                # Use peak value instead of RMS
                peak = np.max(np.abs(chunk))
                self.waveform_data.append(peak)
            
            # Normalize to full height
            if self.waveform_data:
                max_peak = max(self.waveform_data)
                if max_peak > 0:  # Prevent division by zero
                    self.waveform_data = [v / max_peak for v in self.waveform_data]
            
            self.duration = len(data) / sample_rate
            self.update()
            
        except Exception as e:
            print(f"Error loading audio for waveform: {e}")
            self.waveform_data = None
            
    def set_playhead(self, position_ms):
        """Update playhead position"""
        if self.duration:
            self.playhead_position = position_ms / 1000.0  # Convert to seconds
            self.update()
            
    def mouseMoveEvent(self, event):
        """Show tooltip when hovering over bookmark lines"""
        if not self.bookmarks or not self.duration:
            return
            
        # Calculate mouse position in time
        x = event.pos().x()
        time_pos = (x / self.width()) * self.duration * 1000
        
        # Find nearest bookmark (within 5% of width)
        tolerance = (self.width() * 0.05) * (self.duration * 1000 / self.width())
        for bookmark in self.bookmarks:
            if abs(bookmark['position'] - time_pos) < tolerance:
                # Format tooltip with full bookmark text
                minutes = bookmark['position'] // 60000
                seconds = (bookmark['position'] % 60000) // 1000
                tooltip = f"[{minutes:02d}:{seconds:02d}] {bookmark['text']}"
                self.setToolTip(tooltip)
                return
        
        self.setToolTip("")  # Clear tooltip when not over a bookmark

    def mousePressEvent(self, event):
        if not self.bookmarks or not self.duration:
            return
            
        # Calculate clicked position
        x = event.pos().x()
        time_pos = (x / self.width()) * self.duration * 1000
        
        # Find nearest bookmark (within 5% of width)
        tolerance = (self.width() * 0.05) * (self.duration * 1000 / self.width())
        for bookmark in self.bookmarks:
            if abs(bookmark['position'] - time_pos) < tolerance:
                self.bookmark_clicked.emit(bookmark['position'])
                break
                
    def paintEvent(self, event):
        """Draw the waveform and bookmarks"""
        if not self.waveform_data:
            painter = QPainter(self)
            painter.fillRect(self.rect(), QColor("#f5f5f5"))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No audio loaded")
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate dimensions
        width = self.width()
        height = self.height()
        center_y = height / 2
        
        # Fill background
        painter.fillRect(self.rect(), QColor("#f5f5f5"))
    
        # Draw peak level indicator in top-right corner
        if self.waveform_data:
            max_level = max(self.waveform_data)
            level_text = f"Peak: {int(max_level * 100)}%"
            painter.drawText(width - 80, 20, level_text)
    
        # Draw waveform
        painter.setPen(QPen(QColor(65, 105, 225), 1))  # Royal blue, thin line
        
        if self.waveform_data:
            points_per_pixel = len(self.waveform_data) / width
            for x in range(width):
                idx = int(x * points_per_pixel)
                if idx < len(self.waveform_data):
                    amplitude = self.waveform_data[idx] * (height/2 - 10)  # Leave margin
                    y1 = center_y - amplitude
                    y2 = center_y + amplitude
                    painter.drawLine(x, int(y1), x, int(y2))
        
        # Draw bookmarks
        if self.bookmarks and self.duration:
            for bookmark in self.bookmarks:
                x = int((bookmark['position'] / (self.duration * 1000)) * width)
                painter.setPen(QPen(QColor(255, 165, 0), 2))  # Orange, thicker line
                painter.drawLine(x, 0, x, height)
        
        # Draw playhead
        if self.duration:
            playhead_x = int((self.playhead_position / self.duration) * width)
            painter.setPen(QPen(QColor(255, 0, 0), 2))  # Bright red, thicker line
            painter.drawLine(playhead_x, 0, playhead_x, height)


class MediaPlayerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(400)  # Ensure minimum height
        print("Initializing MediaPlayerWidget")  # Debug
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # File info
        self.file_label = QLabel()
        self.file_label.setWordWrap(True)
        layout.addWidget(self.file_label)
        
        # Waveform - simplified container
        self.waveform = WaveformWidget(self)
        self.waveform.setMinimumHeight(200)  # Make it taller
        layout.addWidget(self.waveform, stretch=1)  # Give it stretch priority
        
        # Time display
        time_layout = QHBoxLayout()
        self.position_label = QLabel("0:00")
        self.position_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.duration_label = QLabel("/ 0:00")
        self.duration_label.setStyleSheet("font-size: 16px;")
        time_layout.addWidget(self.position_label)
        time_layout.addWidget(self.duration_label)
        time_layout.addStretch()
        layout.addLayout(time_layout)
        
        # Seek slider
        self.seek_slider = QSlider(Qt.Orientation.Horizontal)
        self.seek_slider.setRange(0, 0)
        self.seek_slider.sliderMoved.connect(self.seek_position)
        layout.addWidget(self.seek_slider)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        # Play button
        self.play_button = QPushButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_button.clicked.connect(self.play_pause)
        controls_layout.addWidget(self.play_button)
        
        # Stop button
        self.stop_button = QPushButton()
        self.stop_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        self.stop_button.clicked.connect(self.stop)
        controls_layout.addWidget(self.stop_button)
        
        controls_layout.addStretch()
        
        # Add volume control
        volume_layout = QHBoxLayout()
        volume_icon = QPushButton()
        volume_icon.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume))
        volume_icon.clicked.connect(self.toggle_mute)
        volume_layout.addWidget(volume_icon)
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)  # Default volume
        self.volume_slider.setMaximumWidth(100)
        self.volume_slider.valueChanged.connect(self.set_volume)
        volume_layout.addWidget(self.volume_slider)
        
        controls_layout.addLayout(volume_layout)
        layout.addLayout(controls_layout)
        
        # Set up media player
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.7)  # Set initial volume to 70%
        
        # Connect bookmark clicks
        self.waveform.bookmark_clicked.connect(self.seek_position)
        
        # Connect signals
        self.player.positionChanged.connect(self.position_changed)
        self.player.durationChanged.connect(self.duration_changed)
        self.player.playbackStateChanged.connect(self.state_changed)
        
        # Update timer for smooth slider movement
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_position)
        self.update_timer.start(1000)  # Update every second
        
    def load_file(self, file_path: str, autoplay: bool = True):
        """Load an audio file
        
        Args:
            file_path: Path to the audio file
            autoplay: Whether to automatically start playing (default: True)
        """
        print(f"Loading file: {file_path}")  # Debug
        self.player.stop()
        self.player.setSource(QUrl.fromLocalFile(file_path))
        self.file_label.setText(file_path.split('/')[-1])
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        
        # Load waveform with debug
        print("Loading waveform...")  # Debug
        self.waveform.load_audio(file_path)
        self.waveform.show()
        self.waveform.update()
        print(f"Waveform size after load: {self.waveform.size()}")  # Debug
        
        if autoplay:
            self.player.play()
        
    def play_pause(self):
        """Toggle play/pause"""
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        else:
            self.player.play()
            
    def stop(self):
        """Stop playback"""
        self.player.stop()
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        
    def seek_position(self, position):
        """Seek to position"""
        self.player.setPosition(position)
        
    def position_changed(self, position):
        """Handle position change"""
        self.seek_slider.setValue(position)
        minutes = position // 60000
        seconds = (position % 60000) // 1000
        self.position_label.setText(f"{minutes}:{seconds:02d}")
        
        # Update waveform playhead
        self.waveform.set_playhead(position)
        
    def duration_changed(self, duration):
        """Handle duration change"""
        self.seek_slider.setRange(0, duration)
        minutes = duration // 60000
        if minutes >= 60:
            hours = minutes // 60
            minutes = minutes % 60
            self.duration_label.setText(f"/ {hours}h {minutes}m")
        else:
            self.duration_label.setText(f"/ {minutes}m")
            
    def state_changed(self, state):
        """Handle playback state change"""
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        else:
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            
    def update_position(self):
        """Update position for smooth slider movement"""
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.position_changed(self.player.position())
            
    def set_volume(self, value):
        """Set volume level"""
        self.audio_output.setVolume(value / 100.0)
        
    def toggle_mute(self):
        """Toggle mute state"""
        if self.audio_output.isMuted():
            self.audio_output.setMuted(False)
            self.sender().setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume))
        else:
            self.audio_output.setMuted(True)
            self.sender().setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolumeMuted))
