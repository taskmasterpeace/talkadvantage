from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen

class TimerIndicator(QWidget):
    """Visual indicator showing countdown timer progress"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(120, 120)  # Increased from 100
        self.setMaximumSize(120, 120)  # Increased from 100
        self.progress = 0
        self.audio_level = 0
        self.time_text = "M"
        self.paused = False
        
    def set_progress(self, progress: float, time_text: str = ""):
        """Update progress value (0-100) and time text"""
        self.progress = min(100, max(0, progress))
        self.time_text = time_text
        self.update()
        
    def set_audio_level(self, level: int):
        """Update audio level indicator (0-100)"""
        self.audio_level = min(100, max(0, level))
        self.update()
        
    def paintEvent(self, event):
        """Draw the circular progress indicator"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate center and radius
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) / 2 - 4
    
        # Draw base circle - change color to a darker gray for better contrast
        painter.setPen(QPen(QColor("#2c3e50"), 12))  # Changed from "#e0e0e0" to "#2c3e50" (darker blue-gray)
        painter.drawEllipse(int(center_x - radius), int(center_y - radius),
                          int(radius * 2), int(radius * 2))

        # Draw progress arc - keep green but make it slightly brighter
        if self.progress > 0:
            # Use orange for paused state, green for active
            progress_color = QColor("#f39c12") if self.paused else QColor("#2ecc71")
            painter.setPen(QPen(progress_color, 12))
            span = int(-self.progress * 3.6)  # Convert progress to degrees (negative for clockwise)
            painter.drawArc(int(center_x - radius), int(center_y - radius),
                          int(radius * 2), int(radius * 2),
                          90 * 16, span * 16)  # Qt uses 16th of degrees
    
        # Draw audio level indicator - make it thicker and red
        if self.audio_level > 0:
            painter.setPen(QPen(QColor("#e74c3c"), 6))  # Changed to red (#e74c3c) and increased thickness to 6
            inner_radius = radius * 0.6
            audio_radius = inner_radius + (radius - inner_radius) * (self.audio_level / 100)
            painter.drawEllipse(int(center_x - audio_radius), int(center_y - audio_radius),
                              int(audio_radius * 2), int(audio_radius * 2))
    
        # Draw time text - make it white for better contrast
        if self.time_text:
            painter.setPen(QColor("#ffffff"))  # Changed from "#000000" to "#ffffff" (white)
            font = painter.font()
            font.setPointSize(24)  # Keep the same size
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.time_text)
