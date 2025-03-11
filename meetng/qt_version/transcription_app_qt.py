from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QMessageBox
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon
import ctypes
import sys
import os
from datetime import datetime
from pathlib import Path
from qt_version.ui.main_window import MainWindow
from qt_version.services.qt_service_adapter import QtServiceAdapter
from utils.file_handler import FileHandler
from qt_version.utils.path_manager import PathManager

class TranscriptionAppQt(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PowerPlay - AI-Enhanced Meeting Assistant")
        self.setGeometry(100, 100, 1200, 800)
        
        # Set window icon explicitly
        icon_path = os.path.join("qt_version", "resources", "icons", "app_icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Get project root directory
        self.project_root = Path(__file__).parent.parent
        self.env_file = self.project_root / '.env'
        
        # Initialize settings manager first
        from qt_version.utils.settings_manager import SettingsManager
        self.settings_manager = SettingsManager()
        
        # Initialize services and handlers
        self.service_adapter = QtServiceAdapter()
        self.file_handler = FileHandler()
        self.path_manager = PathManager()
        
        # Initialize directories from settings
        self.initialize_directories()
        
        # Initialize theme manager
        from qt_version.utils.theme_manager import ThemeManager
        self.theme_manager = ThemeManager()
        saved_theme = self.settings_manager.get_setting('theme', 'modern_light')
        
        # Initialize LangChain service with settings manager BEFORE creating main window
        from services.langchain_service import LangChainService
        self.langchain_service = LangChainService(settings_manager=self.settings_manager)
        
        # Migrate templates to new format
        self.migrate_templates()
        
        # Now create main window after langchain_service is initialized
        self.main_window = MainWindow(parent=None, app=self)
        self.setCentralWidget(self.main_window)
        
        # Now apply theme to the entire application
        self.theme_manager.apply_theme(saved_theme)
        
        # Load or create environment file
        self.load_environment()
        
        # Connect service signals
        self.service_adapter.progress_update.connect(self.on_progress)
        self.service_adapter.status_update.connect(self.on_status)
        self.service_adapter.transcription_complete.connect(self.on_complete)
        
        # Connect service signals
        self.service_adapter.progress_update.connect(self.on_progress)
        self.service_adapter.status_update.connect(self.on_status)
        self.service_adapter.transcription_complete.connect(self.on_complete)
    
    def on_progress(self, file: str, current: int, total: int):
        """Handle progress updates"""
        self.main_window.status_label.setText(
            f"Processing {file} ({current}/{total})"
        )
    
    def on_status(self, message: str):
        """Handle status updates"""
        self.main_window.status_label.setText(message)
    
    def on_complete(self, success: bool, message: str):
        """Handle completion"""
        self.main_window.status_label.setText(
            "Success: " + message if success else "Error: " + message
        )
        
    def load_environment(self):
        """Load settings from database"""
        from qt_version.utils.settings_manager import SettingsManager
        
        self.settings_manager = SettingsManager()
        settings = self.settings_manager.get_all_settings()
        
        # Update environment with stored settings
        for key, value in settings.items():
            os.environ[key] = value
            
    def initialize_directories(self):
        """Initialize directories from settings"""
        # Get directory paths from settings
        workspace_dir = self.settings_manager.get_setting('workspace_dir', '')
        templates_dir = self.settings_manager.get_setting('templates_dir', '')
        
        # Set default paths if not configured
        if not workspace_dir:
            # Use user's home directory as base for default paths
            workspace_dir = str(Path.home() / "PowerPlay" / "Recordings")
            self.settings_manager.save_setting('workspace_dir', workspace_dir)
            print(f"Setting default workspace directory: {workspace_dir}")
            
        if not templates_dir:
            templates_dir = str(Path.home() / "PowerPlay" / "Templates")
            self.settings_manager.save_setting('templates_dir', templates_dir)
            print(f"Setting default templates directory: {templates_dir}")
        
        # Create directories if they don't exist
        try:
            os.makedirs(workspace_dir, exist_ok=True)
            os.makedirs(templates_dir, exist_ok=True)
            print(f"Created directories: {workspace_dir}, {templates_dir}")
        except Exception as e:
            print(f"Error creating directories: {e}")
        
        # Update path manager
        self.path_manager.set_workspace_dir(workspace_dir)
        self.path_manager.set_templates_dir(templates_dir)
        print(f"Path manager updated with workspace: {self.path_manager.workspace_dir}")
        
        # Refresh library tab if it exists
        if hasattr(self, 'main_window') and hasattr(self.main_window, 'library_tab'):
            self.main_window.library_tab.load_workspace_files()
        
    def check_api_keys(self):
        """Check if API keys are configured"""
        if not os.getenv('OPENAI_API_KEY') or not os.getenv('ASSEMBLYAI_API_KEY'):
            from qt_version.ui.settings_dialog import SettingsDialog
            dialog = SettingsDialog(self)
            dialog.exec()
            
    def migrate_templates(self):
        """Migrate templates to the new format with curiosity_prompt and conversation_mode"""
        try:
            # Check if migration is needed
            migration_needed = self.settings_manager.get_setting('template_migration_needed', 'true').lower() == 'true'
            
            if not migration_needed:
                print("Template migration already completed")
                return
                
            print("Starting template migration...")
            
            # Get template manager
            if hasattr(self.langchain_service, 'template_manager'):
                template_manager = self.langchain_service.template_manager
            else:
                from services.template_manager import TemplateManager
                template_manager = TemplateManager()
                
            # Run migration
            migration_stats = template_manager.migrate_templates(backup=True)
            
            # Log results
            print(f"Template migration completed:")
            print(f"  Total templates: {migration_stats['total']}")
            print(f"  Migrated: {migration_stats['migrated']}")
            print(f"  Skipped: {migration_stats['skipped']}")
            print(f"  Errors: {migration_stats['errors']}")
            print(f"  Backups created: {migration_stats['backups_created']}")
            
            # Mark migration as completed
            self.settings_manager.save_setting('template_migration_needed', 'false')
            self.settings_manager.save_setting('template_migration_date', datetime.now().isoformat())
            self.settings_manager.save_setting('template_version', '2')
            
        except Exception as e:
            print(f"Error during template migration: {e}")
            import traceback
            traceback.print_exc()

def main():
    app = QApplication(sys.argv)
    
    # Get application path
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys._MEIPASS)
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))

    # Check for .env file
    env_path = os.path.join(application_path, '.env')
    if not os.path.exists(env_path):
        QMessageBox.warning(
            None,
            "Configuration Missing",
            "No .env file found. Please ensure you have a .env file with your OpenAI API key."
        )
        # Create template .env file
        with open(env_path, 'w') as f:
            f.write("OPENAI_API_KEY=your-api-key-here\n")
    
    # Set application ID for Windows taskbar
    try:
        myappid = 'powerplay.transcription.app.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception as e:
        print(f"Failed to set app ID: {e}")
    
    # Set application-wide icon
    icon_path = os.path.join("qt_version", "resources", "icons", "app_icon.ico")
    if os.path.exists(icon_path):
        icon = QIcon(icon_path)
        app.setWindowIcon(icon)
    else:
        print(f"Icon not found at: {icon_path}")
    
    # Create and show splash screen
    from qt_version.ui.splash_screen import FadingSplashScreen
    splash = FadingSplashScreen()
    splash.show()
    app.processEvents()  # Ensure splash is displayed
    
    # Create main window
    window = TranscriptionAppQt()
    
    # Initialize window (this takes time)
    window.hide()  # Ensure it's hidden during initialization
    
    # Show window and fade out splash after delay
    QTimer.singleShot(1500, lambda: {
        window.show(),
        QTimer.singleShot(500, lambda: splash.finish(window))
    })
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
