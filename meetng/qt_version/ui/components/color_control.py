from PyQt6.QtWidgets import (
    QToolButton, QColorDialog, QMenu, 
    QWidgetAction, QGridLayout, QWidget
)
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtCore import pyqtSignal, Qt, QSize

class ColorPresetButton(QToolButton):
    """Quick-select color preset button"""
    clicked = pyqtSignal(QColor)
    
    def __init__(self, color: QColor, size=20):
        super().__init__()
        self.color = color
        self.setFixedSize(size, size)
        self.clicked.connect(lambda: self.clicked.emit(self.color))
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw color square
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.color)
        painter.drawRect(self.rect())
        
        # Draw border
        painter.setPen(Qt.GlobalColor.gray)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))

class ColorControlButton(QToolButton):
    """Color picker button with presets"""
    
    colorChanged = pyqtSignal(QColor)
    
    DEFAULT_PRESETS = [
        "#000000", "#FFFFFF", "#FF0000", "#00FF00", "#0000FF",
        "#FFFF00", "#FF00FF", "#00FFFF", "#808080", "#800000",
        "#008000", "#000080", "#808000", "#800080", "#008080"
    ]
    
    def __init__(self, parent=None, presets=None):
        super().__init__(parent)
        self.current_color = QColor("#000000")
        self.presets = [QColor(c) for c in (presets or self.DEFAULT_PRESETS)]
        
        self.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        self.setFixedSize(32, 24)
        
        # Create color menu
        self.setup_menu()
        
        # Connect signals
        self.clicked.connect(self.show_color_dialog)
        
    def setup_menu(self):
        """Create popup menu with presets grid"""
        self.menu = QMenu(self)
        
        # Create presets widget
        presets_widget = QWidget()
        grid = QGridLayout(presets_widget)
        grid.setSpacing(2)
        
        # Add preset buttons
        for i, color in enumerate(self.presets):
            btn = ColorPresetButton(color)
            btn.clicked.connect(self.set_color)
            grid.addWidget(btn, i // 5, i % 5)
            
        # Add custom color option
        action = QWidgetAction(self.menu)
        action.setDefaultWidget(presets_widget)
        self.menu.addAction(action)
        
        self.setMenu(self.menu)
        
    def set_color(self, color: QColor):
        """Update current color"""
        self.current_color = color
        self.colorChanged.emit(color)
        self.update()
        
    def show_color_dialog(self):
        """Show full color picker dialog"""
        color = QColorDialog.getColor(
            self.current_color, 
            self,
            "Select Color",
            QColorDialog.ColorDialogOption.ShowAlphaChannel
        )
        if color.isValid():
            self.set_color(color)
            
    def paintEvent(self, event):
        """Draw color preview"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw color rectangle
        rect = self.rect().adjusted(2, 2, -2, -2)
        painter.setPen(Qt.GlobalColor.gray)
        painter.setBrush(self.current_color)
        painter.drawRect(rect)
