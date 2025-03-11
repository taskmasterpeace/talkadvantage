from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QFont
from PyQt6.QtCore import Qt

class TimerIndicator(QWidget):
    """Enhanced visual indicator showing countdown timer progress and audio levels"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 60)  # Further reduced size for better space usage
        self.progress = 0
        self.text = "M"
        self.audio_level = 0
        self.paused = False
        self.audio_level_text = ""
        self.audio_level_color = "#4CAF50"  # Default green
        self.silence_threshold_active = False
        
    def set_progress(self, value, text):
        """Update progress (0-100) and display text"""
        self.progress = value
        self.text = text
        self.update()
        
    def set_audio_level(self, level: int):
        """Update the audio level (0-100)"""
        self.audio_level = min(max(level, 0), 100)
        self.update()
        
    def set_audio_level_text(self, text: str):
        """Set the audio level text description"""
        self.audio_level_text = text
        self.update()
        
    def set_audio_level_color(self, color: str):
        """Set the audio level color"""
        self.audio_level_color = color
        self.update()
        
    def set_audio_level_text(self, text: str):
        """Set the audio level text description"""
        self.audio_level_text = text
        self.update()
        
    def set_audio_level_color(self, color: str):
        """Set the audio level color"""
        self.audio_level_color = color
        self.update()
        
    def set_silence_threshold_color(self, active: bool):
        """Set whether silence threshold is active (changes color)"""
        self.silence_threshold_active = active
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get widget dimensions for scaling
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2
        outer_radius = min(width, height) / 2 - 2
        
        # Draw outer circle with pause indication
        painter.setPen(Qt.PenStyle.NoPen)
        
        # Change color based on state
        if self.paused:
            outer_color = QColor('#FFA000')  # Amber for paused
        elif self.silence_threshold_active:
            outer_color = QColor('#E91E63')  # Pink for approaching silence threshold
        else:
            outer_color = QColor('#9E9E9E')  # Gray for normal
            
        painter.setBrush(outer_color)
        painter.drawEllipse(
            int(center_x - outer_radius),
            int(center_y - outer_radius),
            int(outer_radius * 2),
            int(outer_radius * 2)
        )
        
        # Draw progress arc
        if self.progress > 0:
            painter.setBrush(QColor('#4CAF50'))  # Green color
            span = int(360 * (self.progress / 100))
            painter.drawPie(
                int(center_x - outer_radius),
                int(center_y - outer_radius),
                int(outer_radius * 2),
                int(outer_radius * 2),
                0, span * 16
            )
        
        # Draw inner circle with audio level - with color coding
        inner_radius = outer_radius * 0.3 + (self.audio_level / 100) * (outer_radius * 0.4)
        
        # Use the specified color for audio level
        painter.setBrush(QColor(self.audio_level_color))
        
        # Draw audio level circle
        painter.drawEllipse(
            int(center_x - inner_radius),
            int(center_y - inner_radius),
            int(inner_radius * 2),
            int(inner_radius * 2)
        )
        
        # Draw threshold markers
        painter.setPen(QColor('#FFFFFF'))
        # Low threshold at 20%
        low_radius = outer_radius * 0.3 + (20 / 100) * (outer_radius * 0.4)
        painter.drawEllipse(
            int(center_x - low_radius),
            int(center_y - low_radius),
            int(low_radius * 2),
            int(low_radius * 2)
        )
        
        # High threshold at 80%
        high_radius = outer_radius * 0.3 + (80 / 100) * (outer_radius * 0.4)
        painter.drawEllipse(
            int(center_x - high_radius),
            int(center_y - high_radius),
            int(high_radius * 2),
            int(high_radius * 2)
        )
        
        # Draw countdown text
        painter.setPen(QColor('white'))
        painter.setFont(QFont("Arial", int(outer_radius * 0.4), QFont.Weight.Bold))
        painter.drawText(0, 0, width, height - height/4, Qt.AlignmentFlag.AlignCenter, str(self.text))
        
        # Draw audio level text below
        if self.audio_level_text:
            painter.setFont(QFont("Arial", int(outer_radius * 0.2)))
            painter.drawText(0, height/2, width, height/2, Qt.AlignmentFlag.AlignCenter, self.audio_level_text)
