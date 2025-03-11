import os
from PyQt6.QtWidgets import QSplashScreen, QLabel
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPixmap, QFont, QPainter, QColor
import sys

class FadingSplashScreen(QSplashScreen):
    def __init__(self):
        # Create a styled pixmap
        pixmap = QPixmap(600, 300)
        pixmap.fill(QColor("#2c3e50"))  # Dark blue background
        
        # Create painter for custom drawing
        painter = QPainter(pixmap)
        
        try:
            # Set up font
            title_font = QFont("Arial", 24, QFont.Weight.Bold)
            subtitle_font = QFont("Arial", 12)
            
            # Draw title
            painter.setFont(title_font)
            painter.setPen(QColor("white"))
            painter.drawText(
                pixmap.rect(),
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap,
                "\n\nPowerPlay\nAI-Enhanced Meeting Assistant"
            )
            
            # Draw subtitle
            painter.setFont(subtitle_font)
            painter.drawText(
                pixmap.rect().adjusted(0, 150, 0, 0),
                Qt.AlignmentFlag.AlignHCenter | Qt.TextFlag.TextWordWrap,
                "Loading..."
            )
            
        finally:
            painter.end()

        super().__init__(pixmap)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | 
                          Qt.WindowType.FramelessWindowHint)
        
    def finish(self, window):
        """Override finish to add fade effect"""
        QTimer.singleShot(500, lambda: QSplashScreen.finish(self, window))
