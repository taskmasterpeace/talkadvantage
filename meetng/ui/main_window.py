from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QComboBox, QTabWidget, QFrame, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSlot
from .tabs import FolderTab, SingleFileTab, RecordingTab

class APIKeyFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Raised)
        layout = QVBoxLayout()
        
        # OpenAI API Key
        layout.addWidget(QLabel("OpenAI API Key:"))
        self.openai_key = QLineEdit()
        self.openai_key.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.openai_key)
        
        # AssemblyAI API Key
        layout.addWidget(QLabel("AssemblyAI API Key:"))
        self.assemblyai_key = QLineEdit()
        self.assemblyai_key.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.assemblyai_key)
        
        self.setLayout(layout)

class MainWindow(QWidget):
    def __init__(self, parent=None, app=None):
        super().__init__(parent)
        self.app = app
        self.init_ui()
        
    def closeEvent(self, event):
        """Handle application closing"""
        # Accept the close event
        event.accept()
