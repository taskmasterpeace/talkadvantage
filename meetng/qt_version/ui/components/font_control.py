from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QToolButton,
    QFontComboBox, QComboBox, QLabel,
    QFrame, QSizePolicy, QMenu, QWidgetAction
)
from PyQt6.QtCore import pyqtSignal, Qt, QSettings
from PyQt6.QtGui import QFont

class FontControlPanel(QWidget):
    """Compact font control panel with dropdown menu"""
    
    fontChanged = pyqtSignal(QFont)
    
    def __init__(self, parent=None, settings_key=None):
        super().__init__(parent)
        
        # Initialize instance variables first
        self.settings_key = settings_key
        self.settings = QSettings("PowerPlay", "MeetingAssistant")
        
        # Create UI elements
        self.create_ui()
        
        # Load settings after UI is created
        self.load_settings()
        
    def create_ui(self):
        """Create and setup UI elements"""
        # Main layout
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)
        
        # Font button that shows current font
        self.font_button = QToolButton()
        self.font_button.setText("Aa")
        self.font_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.font_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        # Add some basic styling that will work with any theme
        self.font_button.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 2px 5px;
            }
            QToolButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
            }
        """)
        self.font_button.setToolTip("Change font settings")
        
        # Create font menu
        self.font_menu = QMenu(self)
        
        # Add font selector to menu
        font_widget = QWidget()
        font_layout = QHBoxLayout(font_widget)
        font_layout.setContentsMargins(4, 4, 4, 4)
        
        self.font_combo = QFontComboBox()
        self.font_combo.setMaximumWidth(120)
        self.font_combo.currentFontChanged.connect(self.on_font_change)
        font_layout.addWidget(self.font_combo)
        
        # Size selector (dropdown instead of spinbox)
        self.size_combo = QComboBox()
        self.size_combo.addItems(['8', '9', '10', '11', '12', '14', '16', '18', '20', '24'])
        self.size_combo.setCurrentText('11')
        self.size_combo.setMaximumWidth(45)
        self.size_combo.currentTextChanged.connect(lambda s: self.on_font_change())
        font_layout.addWidget(self.size_combo)
        
        # Add widget to menu using QWidgetAction
        widget_action = QWidgetAction(self)
        widget_action.setDefaultWidget(font_widget)
        self.font_menu.addAction(widget_action)
        
        self.font_button.setMenu(self.font_menu)
        layout.addWidget(self.font_button)
        
        self.setLayout(layout)
        
    def load_settings(self):
        """Load saved font settings"""
        if not self.settings_key:
            return
            
        font_family = self.settings.value(f"{self.settings_key}/font_family", "")
        font_size = self.settings.value(f"{self.settings_key}/font_size", "11")
        
        if font_family:
            index = self.font_combo.findText(font_family)
            if index >= 0:
                self.font_combo.setCurrentIndex(index)
                self.font_button.setFont(self.font_combo.currentFont())
        
        self.size_combo.setCurrentText(str(font_size))
        
    def save_settings(self):
        """Save current font settings"""
        if not self.settings_key:
            return
            
        self.settings.setValue(f"{self.settings_key}/font_family", 
                             self.font_combo.currentFont().family())
        self.settings.setValue(f"{self.settings_key}/font_size", 
                             self.size_combo.currentText())
    
    def on_font_change(self, *args):
        """Handle font changes"""
        font = self.font_combo.currentFont()
        font.setPointSize(int(self.size_combo.currentText()))
        self.font_button.setFont(font)
        self.fontChanged.emit(font)
        self.save_settings()
