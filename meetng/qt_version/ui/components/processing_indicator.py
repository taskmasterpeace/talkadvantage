from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import QTimer, Qt
from datetime import datetime

class ProcessingIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(30)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        
        self.start_time = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        
        self.setStyleSheet("""
            QLabel {
                color: #FF9800;
                font-weight: bold;
                font-size: 12px;
                padding: 4px 8px;
                border-radius: 4px;
                background: #FFF3E0;
            }
        """)
        
        self.hide()
        
    def start(self):
        """Start the processing timer"""
        self.start_time = datetime.now()
        self.timer.start(100)  # Update every 100ms
        self.show()
        self.update_time()
        
    def stop(self):
        """Stop the timer and show final time"""
        if self.start_time:
            self.timer.stop()
            elapsed = (datetime.now() - self.start_time).total_seconds()
            self.label.setText(f"Completed in {elapsed:.1f}s")
            self.setStyleSheet("""
                QLabel {
                    color: #4CAF50;
                    font-weight: bold;
                    font-size: 12px;
                    padding: 4px 8px;
                    border-radius: 4px;
                    background: #E8F5E9;
                }
            """)
            QTimer.singleShot(2000, self.hide)  # Hide after 2 seconds
            
    def update_time(self):
        """Update the elapsed time display"""
        if self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            self.label.setText(f"Processing... {elapsed:.1f}s")
