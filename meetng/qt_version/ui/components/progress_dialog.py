from PyQt6.QtWidgets import QDialog, QVBoxLayout, QProgressBar, QLabel
from PyQt6.QtCore import Qt, pyqtSignal

class ProgressDialog(QDialog):
    """Progress dialog with cancel button"""
    
    cancelled = pyqtSignal()
    
    def __init__(self, parent=None, title="Processing...", can_cancel=True):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)
        
        layout = QVBoxLayout()
        
        self.status_label = QLabel("Initializing...")
        layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate by default
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
        self.resize(300, 100)
        
    def set_progress(self, value, maximum=100):
        """Set progress bar value and range"""
        self.progress_bar.setRange(0, maximum)
        self.progress_bar.setValue(value)
        
    def set_status(self, text):
        """Update status text"""
        self.status_label.setText(text)
