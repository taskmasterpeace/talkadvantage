from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QComboBox, QTabWidget, QFrame, QLineEdit, QMenuBar,
    QMainWindow
)
from PyQt6.QtGui import QAction
from .library_tab import LibraryTab
from .settings_dialog import SettingsDialog
from PyQt6.QtCore import Qt, pyqtSlot
from .tabs import ImportTab, RecordingTab
from .deep_analysis_tab import DeepAnalysisTab
from .documentation_viewer import DocumentationViewer
import os
from dotenv import load_dotenv

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

class MainWindow(QMainWindow):
    def __init__(self, parent=None, app=None):
        super().__init__(parent)
        self.app = app
        
        # Load API keys from environment
        load_dotenv(self.app.env_file)
        self.openai_key = os.getenv('OPENAI_API_KEY', '')
        self.assemblyai_key = os.getenv('ASSEMBLYAI_API_KEY', '')
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.central_layout = QVBoxLayout()
        central_widget.setLayout(self.central_layout)
        
        print("Creating main window layout")  # Debug print
        
        # Create menu bar
        menubar = self.menuBar()
        
        # Settings menu
        settings_menu = menubar.addMenu("Settings")
        
        # API Keys
        api_action = settings_menu.addAction("API Configuration")
        api_action.triggered.connect(self.show_settings)
        print("Connected API Configuration to show_settings")  # Debug print
        
        # Template Editor
        template_action = settings_menu.addAction("Analytics Profiles")
        template_action.triggered.connect(self.show_template_editor)
        print("Connected Analytics Profiles to show_template_editor")  # Debug print
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        # Documentation action
        doc_action = help_menu.addAction("Documentation")
        doc_action.triggered.connect(self.show_documentation)
        
        # Store settings
        self.openai_key = ""
        self.assemblyai_key = ""
        self.system_prompt = "You are an AI assistant helping to analyze meeting transcripts."
        
        
        # Add tab widget for different views
        self.tab_widget = QTabWidget()
        self.central_layout.addWidget(self.tab_widget)
        
        # Add the tabs
        # Add Library tab first
        self.library_tab = LibraryTab(parent=self, app=self.app)
        self.tab_widget.addTab(self.library_tab, "Library")
        
        self.import_tab = ImportTab(parent=self)
        self.tab_widget.addTab(self.import_tab, "Import Audio")
        
        self.live_session_tab = RecordingTab(parent=self)
        self.tab_widget.addTab(self.live_session_tab, "Live Workspace")
        
        # Add Deep Analysis tab with LangChain service
        self.deep_analysis_tab = DeepAnalysisTab(
            parent=self,
            langchain_service=self.app.langchain_service
        )
        self.tab_widget.addTab(self.deep_analysis_tab, "Deep Analysis")
        
        # Add status bar
        self.status_label = QLabel("Ready")
        self.central_layout.addWidget(self.status_label)
    
    @pyqtSlot()
    def on_start_clicked(self):
        """Handle start button click"""
        current_tab = self.tab_widget.currentWidget()
        
        if isinstance(current_tab, ImportTab):
            self.status_label.setText("Processing files...")
        elif isinstance(current_tab, RecordingTab):
            self.start_recording()
    
    def start_recording(self):
        """Start/stop recording based on current state"""
        if self.recording_tab.recording:
            self.status_label.setText("Recording started...")
        else:
            self.status_label.setText("Recording stopped")
            
    def show_settings(self):
        """Show settings dialog"""
        print("Opening Settings Dialog")  # Debug print
        dialog = SettingsDialog(self)
        dialog.set_values(self.openai_key, self.assemblyai_key)
        if dialog.exec():
            self.openai_key, self.assemblyai_key = dialog.get_values()
            
    def show_system_prompt(self):
        """Show system prompt configuration dialog"""
        from .system_prompt_dialog import SystemPromptDialog
        dialog = SystemPromptDialog(self)
        dialog.exec()
        
    def show_documentation(self):
        """Show documentation viewer"""
        # Check if documentation tab already exists
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == "Documentation":
                # Select the existing tab
                self.tab_widget.setCurrentIndex(i)
                return
        
        # Create and add documentation tab
        doc_viewer = DocumentationViewer(parent=self)
        doc_index = self.tab_widget.addTab(doc_viewer, "Documentation")
        
        # Select the new tab
        self.tab_widget.setCurrentIndex(doc_index)
        
    def show_template_editor(self):
        """Show template editor dialog"""
        print("Opening Template Editor Dialog")  # Debug print
        from .template_editor_dialog import TemplateEditorDialog
        
        # Pass self as parent which has app attribute
        editor = TemplateEditorDialog(self, self.app.langchain_service.template_manager)
        editor.exec()
