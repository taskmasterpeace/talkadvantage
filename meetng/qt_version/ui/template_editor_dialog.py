from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QTextEdit, QListWidget, QTabWidget,
    QMessageBox, QLineEdit, QGroupBox, QSplitter,
    QScrollArea, QWidget, QFrame, QFileDialog,
    QFormLayout, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QCheckBox, QApplication
)
from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt6.QtGui import QIcon
import json
import os
from .template_wizard_qt import TemplateWizardDialog
from .template_editor_qt import TemplateEditorQt

class TemplateEditorDialog(QDialog):
    """Dialog for editing templates"""
    
    def __init__(self, parent=None, template_manager=None):
        super().__init__(parent)
        self.setWindowTitle("Analysis Profile Editor")
        self.setMinimumSize(1200, 800)
        
        # Store app reference from parent
        self.app = parent.app if parent and hasattr(parent, 'app') else None
        
        # Debug output
        print(f"TemplateEditorDialog.__init__: parent={parent}, has app: {hasattr(parent, 'app') if parent else False}")
        print(f"TemplateEditorDialog.__init__: self.app={self.app}")
        print(f"TemplateEditorDialog.__init__: template_manager={template_manager}")
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for full-size editor
        
        # Ensure we have a template manager
        if template_manager is None and self.app and hasattr(self.app, 'langchain_service'):
            print("No template manager provided, using one from langchain_service")
            template_manager = self.app.langchain_service.template_manager
            print(f"Retrieved template_manager: {template_manager}")
        
        # Create template editor and explicitly pass app reference and template manager
        self.editor = TemplateEditorQt(self, template_manager)
        
        # Set fixed size for the editor to ensure it's visible
        self.editor.setMinimumSize(1180, 780)
        
        # Ensure app reference is passed correctly
        if hasattr(self, 'app') and self.app:
            print(f"TemplateEditorDialog: Setting editor.app from self.app: {self.app}")
            self.editor.app = self.app
        elif parent and hasattr(parent, 'app') and parent.app:
            print(f"TemplateEditorDialog: Setting editor.app from parent.app: {parent.app}")
            self.editor.app = parent.app
            self.app = parent.app  # Also update our own reference
        else:
            print("TemplateEditorDialog: No app reference available from self or parent")
            
        layout.addWidget(self.editor)
        
        # Force update
        self.update()
        QApplication.processEvents()
    
