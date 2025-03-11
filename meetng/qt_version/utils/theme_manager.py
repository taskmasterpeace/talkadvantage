from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QApplication
from dataclasses import dataclass
from typing import Dict, Optional, Tuple
import json
import os
from enum import Enum, auto

class ThemeType(Enum):
    """Enum defining the available theme types"""
    LIGHT = auto()
    DARK = auto()
    CUSTOM = auto()

@dataclass
class Theme:
    name: str
    description: str
    theme_type: ThemeType
    styles: Dict[str, str]
    palette: Dict[str, str]
    
    # Base colors
    primary: str
    secondary: str
    accent: str
    background: str
    surface: str
    text: str
    
    # Component colors
    button_gradient: Tuple[str, str]
    button_hover: str
    input_background: str
    
    # Additional colors
    success: str = "#4CAF50"
    warning: str = "#FF9800"
    error: str = "#F44336"
    info: str = "#2196F3"
    
    # Sizes
    button_height: int = 36
    input_height: int = 32
    border_radius: int = 6
    
    # Opacity levels
    disabled_opacity: float = 0.38
    hover_opacity: float = 0.12
    
    def __post_init__(self):
        """Initialize derived properties after dataclass initialization"""
        # Initialize empty dictionaries if None
        if self.styles is None:
            self.styles = {}
        if self.palette is None:
            self.palette = {}

class ThemeManager:
    def __init__(self):
        self.current_theme = None
        self.themes = {
            "modern_light": Theme(
                name="Modern Light",
                description="Clean, modern light theme with subtle gradients",
                theme_type=ThemeType.LIGHT,
                primary="#2196F3",
                secondary="#4CAF50",
                accent="#FF4081",
                background="#FFFFFF",
                surface="#F5F5F5",
                text="#212121",
                button_gradient=("#2196F3", "#1976D2"),
                button_hover="#1E88E5",
                input_background="#FFFFFF",
                success="#4CAF50",
                warning="#FF9800",
                error="#F44336",
                info="#2196F3",
                styles={},
                palette={}
            ),
            "modern_dark": Theme(
                name="Modern Dark",
                description="Professional dark theme with vibrant accents",
                theme_type=ThemeType.DARK,
                primary="#BB86FC",
                secondary="#03DAC6",
                accent="#CF6679",
                background="#121212",
                surface="#1E1E1E",
                text="#FFFFFF",  # Ensure white text
                button_gradient=("#BB86FC", "#8858D0"),
                button_hover="#9F66E1",
                input_background="#2D2D2D",  # Darker input background
                success="#81C784",
                warning="#FFB74D",
                error="#E57373",
                info="#64B5F6",
                styles={},
                palette={}
            ),
            "oceanic": Theme(
                name="Oceanic",
                description="Calming blue-green theme inspired by the ocean",
                theme_type=ThemeType.DARK,
                primary="#00ACC1",
                secondary="#26A69A",
                accent="#FFB300",
                background="#263238",
                surface="#37474F",
                text="#ECEFF1",
                button_gradient=("#00ACC1", "#0097A7"),
                button_hover="#00BCD4",
                input_background="#455A64",
                success="#66BB6A",
                warning="#FFA726",
                error="#EF5350",
                info="#42A5F5",
                styles={},
                palette={}
            ),
            "high_contrast": Theme(
                name="High Contrast",
                description="High contrast theme for accessibility",
                theme_type=ThemeType.DARK,
                primary="#FFFFFF",
                secondary="#FFFF00",
                accent="#00FFFF",
                background="#000000",
                surface="#0F0F0F",
                text="#FFFFFF",
                button_gradient=("#0066CC", "#004499"),  # Changed to blue for better contrast with white text
                button_hover="#0055AA",
                input_background="#1A1A1A",
                success="#00FF00",
                warning="#FFFF00",
                error="#FF0000",
                info="#00FFFF",
                styles={},
                palette={}
            ),
            "classic_light": Theme(
                name="Classic Light",
                description="Traditional light theme with classic styling",
                theme_type=ThemeType.LIGHT,
                primary="#007bff",
                secondary="#6c757d",
                accent="#fd7e14",
                background="#ffffff",
                surface="#f8f9fa",
                text="#212529",
                button_gradient=("#007bff", "#0069d9"),
                button_hover="#0062cc",
                input_background="#ffffff",
                success="#28a745",
                warning="#ffc107",
                error="#dc3545",
                info="#17a2b8",
                styles={},
                palette={}
            ),
            "classic_dark": Theme(
                name="Classic Dark",
                description="Traditional dark theme with classic styling",
                theme_type=ThemeType.DARK,
                primary="#007bff",
                secondary="#6c757d",
                accent="#fd7e14",
                background="#343a40",
                surface="#495057",
                text="#f8f9fa",  # Light text for dark background
                button_gradient=("#007bff", "#0069d9"),
                button_hover="#0062cc",
                input_background="#2b3035",  # Darker input background for better contrast
                success="#28a745",
                warning="#ffc107",
                error="#dc3545",
                info="#17a2b8",
                styles={},
                palette={}
            )
        }
        
    def apply_theme(self, theme_name: str):
        """Apply selected theme to application"""
        if theme_name not in self.themes:
            print(f"Theme {theme_name} not found, using default")
            theme_name = "modern_light"  # Fallback to default theme
            
        theme = self.themes[theme_name]
        self.current_theme = theme
        
    def _convert_to_dark_mode(self, theme: Theme) -> Theme:
        """Convert a light theme to dark mode"""
        # Create a copy of the theme with dark mode colors
        dark_theme = Theme(
            name=f"{theme.name} (Dark)",
            description=f"Dark version of {theme.name}",
            theme_type=ThemeType.DARK,
            primary=theme.primary,  # Keep accent colors
            secondary=theme.secondary,
            accent=theme.accent,
            background="#1e1e1e",  # Dark background
            surface="#2d2d2d",     # Dark surface
            text="#ffffff",        # Light text
            button_gradient=theme.button_gradient,
            button_hover=theme.button_hover,
            input_background="#363636",
            success=theme.success,
            warning=theme.warning,
            error=theme.error,
            info=theme.info,
            styles=theme.styles.copy() if theme.styles else {},
            palette=theme.palette.copy() if theme.palette else {}
        )
        return dark_theme
        
    def get_current_theme(self) -> Theme:
        """Get the current theme"""
        return self.current_theme
    
    def get_theme(self, theme_name: str) -> Optional[Theme]:
        """Get a theme by name"""
        return self.themes.get(theme_name)
    
    def get_available_themes(self) -> Dict[str, str]:
        """Get a dictionary of available theme IDs and names"""
        return {theme_id: theme.name for theme_id, theme in self.themes.items()}
        
    def create_stylesheet(self, theme: Theme) -> str:
        """Generate stylesheet from theme"""
        # Generate stylesheet with theme colors
        stylesheet = f"""
            /* Global Variables */
            * {{
                --color-primary: {theme.primary};
                --color-secondary: {theme.secondary};
                --color-accent: {theme.accent};
                --color-background: {theme.background};
                --color-surface: {theme.surface};
                --color-text: {theme.text};
                --color-success: {theme.success};
                --color-warning: {theme.warning};
                --color-error: {theme.error};
                --color-info: {theme.info};
            }}
            
            /* Global styles - apply to ALL widgets */
            QWidget {{
                background-color: {theme.background};
                color: {theme.text};
                font-size: 10pt;
            }}
            
            /* Application window */
            QMainWindow, QDialog {{
                background-color: {theme.background};
                color: {theme.text};
            }}
            
            /* Main window components */
            QMainWindow {{
                background-color: {theme.background};
                color: {theme.text};
            }}
            
            /* Frames and containers */
            QFrame, QGroupBox, QTabWidget::pane {{
                background-color: {theme.surface};
                color: {theme.text};
            }}
            
            /* Menus and status bar */
            QMenuBar {{
                background-color: {theme.surface};
                color: {self.get_contrasting_text_color(theme.surface)};
                border-bottom: 1px solid {theme.primary};
                font-weight: normal;
            }}
            
            QStatusBar {{
                background-color: {theme.surface};
                color: {self.get_contrasting_text_color(theme.surface)};
                border-top: 1px solid {theme.primary};
            }}
            
            QStatusBar QLabel {{
                background-color: transparent;
                color: {self.get_contrasting_text_color(theme.surface)};
            }}
            
            QMainWindow::separator {{
                background-color: {theme.primary};
                width: 1px;
                height: 1px;
            }}
            
            QMenuBar::item {{
                background-color: transparent;
                padding: 4px 10px;
                color: {self.get_contrasting_text_color(theme.surface)};
                font-weight: normal;
            }}
            
            QMenuBar::item:selected {{
                background-color: {theme.primary};
                color: {self.get_contrasting_text_color(theme.primary)};
                font-weight: bold;
            }}
            
            QMenu {{
                background-color: {theme.surface};
                color: {self.get_contrasting_text_color(theme.surface)};
                border: 1px solid {theme.primary};
            }}
            
            QMenu::item {{
                padding: 4px 20px 4px 20px;
                color: {self.get_contrasting_text_color(theme.surface)};
                font-weight: normal;
            }}
            
            QMenu::item:selected {{
                background-color: {theme.primary};
                color: {self.get_contrasting_text_color(theme.primary)};
                font-weight: bold;
            }}
            
            QMenu::item:disabled {{
                color: {self._adjust_color(self.get_contrasting_text_color(theme.surface), 70)};
            }}
            
            /* Text areas and inputs */
            QTextEdit, QLineEdit, QPlainTextEdit {{
                background-color: {theme.input_background};
                color: {self.get_contrasting_text_color(theme.input_background)};
                border: 1px solid {theme.surface};
                border-radius: 4px;
                padding: 4px;
                selection-background-color: {theme.primary};
                selection-color: {self.get_contrasting_text_color(theme.primary)};
            }}
            
            /* Lists and trees - ensure proper contrast */
            QListWidget, QTreeWidget, QTableWidget, QTableView, QListView, QTreeView {{
                background-color: {theme.input_background};
                color: {self.get_contrasting_text_color(theme.input_background)};
                border: 1px solid {theme.surface};
                border-radius: 4px;
                alternate-background-color: {self._adjust_color(theme.input_background, 10)};
            }}
            
            QListWidget::item, QTreeWidget::item, QTableWidget::item, 
            QTableView::item, QListView::item, QTreeView::item {{
                color: {self.get_contrasting_text_color(theme.input_background)};
            }}
            
            QListWidget::item:selected, QTreeWidget::item:selected,
            QTableWidget::item:selected, QTableView::item:selected,
            QListView::item:selected, QTreeView::item:selected {{
                background-color: {theme.primary};
                color: {self.get_contrasting_text_color(theme.primary)};
            }}
            
            /* Tabs */
            QTabWidget::pane {{
                border: 1px solid {theme.surface};
                background: {theme.surface};
                color: {self.get_contrasting_text_color(theme.surface)};
            }}
            
            /* Ensure all text elements have proper contrast */
            QLabel, QCheckBox, QRadioButton, QGroupBox {{
                color: {self.get_contrasting_text_color(theme.background)};
            }}
            
            QTabBar::tab {{
                background: {theme.surface};
                color: {theme.text};
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            
            QTabBar::tab:selected {{
                background: {theme.primary};
                color: {self.get_contrasting_text_color(theme.primary)};
                border-bottom: none;
            }}
            
            QTabBar::tab:!selected {{
                background: {self._adjust_color(theme.surface, -15)};
                color: {theme.text};
            }}
            
            QTabBar::tab:!selected:hover {{
                background: {self._adjust_color(theme.surface, -5)};
            }}
            
            QTabBar::tab:disabled {{
                color: {self._adjust_color(theme.text, 70)};
                background: {self._adjust_color(theme.surface, -5)};
            }}
            
            /* Group boxes */
            QGroupBox {{
                background-color: {theme.surface};
                border: 1px solid {theme.surface};
                border-radius: 6px;
                margin-top: 1em;
                padding-top: 1em;
            }}
            
            QGroupBox::title {{
                color: {theme.primary};
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }}
            
            /* Buttons */
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {theme.button_gradient[0]},
                    stop:1 {theme.button_gradient[1]});
                border: none;
                border-radius: {theme.border_radius}px;
                padding: 8px 16px;
                color: {self.get_contrasting_text_color(theme.button_gradient[0])};
                min-height: {theme.button_height}px;
                font-weight: bold;
            }}
            
            QPushButton:hover {{
                background: {theme.button_hover};
                color: {self.get_contrasting_text_color(theme.button_hover)};
            }}
            
            QPushButton:disabled {{
                background: {self._adjust_color(theme.button_gradient[1], 30)};
                color: {self.get_contrasting_text_color(self._adjust_color(theme.button_gradient[1], 30))};
                opacity: {theme.disabled_opacity};
            }}
            
            /* Tool buttons */
            QToolButton {{
                background-color: {theme.surface};
                color: {theme.text};
                border: 1px solid {theme.primary};
                border-radius: 4px;
                padding: 3px;
            }}
            
            QToolButton:hover {{
                background-color: {theme.primary};
                color: {self.get_contrasting_text_color(theme.primary)};
            }}
            
            QToolButton:pressed {{
                background-color: {self._adjust_color(theme.primary, -20)};
                color: {self.get_contrasting_text_color(self._adjust_color(theme.primary, -20))};
            }}
            
            QToolButton:disabled {{
                color: {self._adjust_color(theme.text, 70)};
                border-color: {self._adjust_color(theme.surface, 20)};
            }}
            
            /* Combo boxes and spinners */
            QComboBox, QSpinBox, QDoubleSpinBox {{
                background-color: {theme.input_background};
                color: {theme.text};
                border: 1px solid {theme.primary};
                border-radius: {theme.border_radius}px;
                padding: 4px 8px;
                min-height: {theme.input_height}px;
            }}
            
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid {theme.primary};
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {theme.input_background};
                color: {theme.text};
                selection-background-color: {theme.primary};
                selection-color: {self.get_contrasting_text_color(theme.primary)};
                border: 1px solid {theme.primary};
            }}
            
            QComboBox:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled {{
                background-color: {self._adjust_color(theme.input_background, -10)};
                color: {self._adjust_color(theme.text, 70)};
                border-color: {self._adjust_color(theme.surface, 20)};
            }}
            
            /* Scrollbars */
            QScrollBar:vertical {{
                background: {theme.surface};
                width: 12px;
                margin: 12px 0 12px 0;
            }}
            
            QScrollBar::handle:vertical {{
                background: {theme.primary};
                min-height: 20px;
                border-radius: 6px;
            }}
            
            QScrollBar:horizontal {{
                background: {theme.surface};
                height: 12px;
                margin: 0 12px 0 12px;
            }}
            
            QScrollBar::handle:horizontal {{
                background: {theme.primary};
                min-width: 20px;
                border-radius: 6px;
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                background: none;
                border: none;
            }}
            
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background: none;
            }}
            
            /* Sliders */
            QSlider::groove:horizontal {{
                border: 1px solid {theme.surface};
                height: 8px;
                background: {theme.surface};
                margin: 2px 0;
                border-radius: 4px;
            }}
            
            QSlider::handle:horizontal {{
                background: {theme.primary};
                border: 1px solid {theme.primary};
                width: 18px;
                height: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }}
            
            /* Progress bars */
            QProgressBar {{
                border: 1px solid {theme.surface};
                border-radius: 4px;
                text-align: center;
                background-color: {theme.surface};
                color: {theme.text};
            }}
            
            QProgressBar::chunk {{
                background-color: {theme.primary};
                width: 1px;
            }}
            
            /* Checkboxes and radio buttons */
            QCheckBox, QRadioButton {{
                color: {theme.text};
                spacing: 5px;
            }}
            
            QCheckBox::indicator, QRadioButton::indicator {{
                width: 18px;
                height: 18px;
            }}
            
            QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
                background-color: {theme.primary};
                border: 2px solid {theme.primary};
            }}
            
            QCheckBox::indicator:unchecked, QRadioButton::indicator:unchecked {{
                background-color: {theme.input_background};
                border: 2px solid {theme.surface};
            }}
            
            /* Headers */
            QHeaderView::section {{
                background-color: {theme.surface};
                color: {theme.text};
                padding: 4px;
                border: 1px solid {self._adjust_color(theme.surface, -10)};
            }}
            
            /* Tooltips */
            QToolTip {{
                background-color: {theme.surface};
                color: {theme.text};
                border: 1px solid {theme.primary};
                padding: 5px;
            }}
            
            /* Dock widgets */
            QDockWidget {{
                titlebar-close-icon: url(close.png);
                titlebar-normal-icon: url(undock.png);
            }}
            
            QDockWidget::title {{
                text-align: center;
                background: {theme.surface};
                color: {theme.text};
                padding: 6px;
            }}
            
            /* Status bar */
            QStatusBar {{
                background: {theme.surface};
                color: {theme.text};
            }}
            
            QStatusBar QLabel {{
                background: transparent;
            }}
            
            /* Calendar widget */
            QCalendarWidget QToolButton {{
                color: {theme.text};
                background-color: transparent;
                border: none;
            }}
            
            QCalendarWidget QMenu {{
                background-color: {theme.surface};
                color: {theme.text};
            }}
            
            QCalendarWidget QSpinBox {{
                background-color: {theme.input_background};
                color: {theme.text};
            }}
            
            QCalendarWidget QWidget#qt_calendar_navigationbar {{
                background-color: {theme.surface};
            }}
            
            QCalendarWidget QWidget {{
                alternate-background-color: {self._adjust_color(theme.surface, 5)};
            }}
        """
        
        return stylesheet
        
    def apply_theme(self, theme_name: str):
        """Apply selected theme to application"""
        if theme_name not in self.themes:
            print(f"Theme {theme_name} not found, using default")
            theme_name = "modern_light"  # Fallback to default theme
            
        theme = self.themes[theme_name]
        self.current_theme = theme
        
        try:
            # Generate stylesheet and apply it
            stylesheet = self.create_stylesheet(theme)
            
            # Apply the stylesheet
            app = QApplication.instance()
            if app:
                # First update the palette
                self._update_application_palette(theme)
                
                # Then apply the stylesheet
                app.setStyleSheet(stylesheet)
                
                # Force update
                from PyQt6.QtCore import QCoreApplication
                QCoreApplication.processEvents()
                
                print(f"Theme applied: {theme.name} ({theme.theme_type.name})")
            else:
                print("Warning: QApplication instance not available")
        except Exception as e:
            print(f"Error applying theme: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to a simpler stylesheet if there's an error
            if QApplication.instance():
                QApplication.instance().setStyleSheet("")
        
    def _adjust_color(self, color: str, amount: int) -> str:
        """Adjust a hex color by the given amount (positive=lighter, negative=darker)"""
        if not color.startswith('#') or len(color) != 7:
            return color
            
        # Convert hex to RGB
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        
        # Adjust values
        r = max(0, min(255, r + amount))
        g = max(0, min(255, g + amount))
        b = max(0, min(255, b + amount))
        
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"
        
    def get_contrasting_text_color(self, bg_color: str) -> str:
        """
        Determine the best text color (black or white) based on background brightness.
        Uses the W3C recommended contrast algorithm.
        
        Args:
            bg_color: Background color in hex format (#RRGGBB)
            
        Returns:
            '#000000' for dark text or '#FFFFFF' for light text
        """
        if not bg_color.startswith('#') or len(bg_color) != 7:
            return '#000000'  # Default to black for invalid colors
            
        # Convert hex to RGB
        r = int(bg_color[1:3], 16)
        g = int(bg_color[3:5], 16)
        b = int(bg_color[5:7], 16)
        
        # Calculate luminance (perceived brightness)
        # Using the formula: 0.299*R + 0.587*G + 0.114*B
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        
        # Use white text for dark backgrounds, black text for light backgrounds
        return '#FFFFFF' if luminance < 0.5 else '#000000'
        
    def _update_application_palette(self, theme: Theme):
        """Update application palette based on theme"""
        palette = QPalette()
        
        # Set colors based on theme
        palette.setColor(QPalette.ColorRole.Window, QColor(theme.background))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(theme.text))
        palette.setColor(QPalette.ColorRole.Base, QColor(theme.surface))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(self._adjust_color(theme.surface, 10)))
        palette.setColor(QPalette.ColorRole.Text, QColor(theme.text))
        palette.setColor(QPalette.ColorRole.Button, QColor(theme.primary))
        
        # Use contrasting text colors based on background
        button_text_color = self.get_contrasting_text_color(theme.primary)
        highlight_text_color = self.get_contrasting_text_color(theme.primary)
        
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(button_text_color))
        palette.setColor(QPalette.ColorRole.BrightText, QColor("#FFFFFF"))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(theme.primary))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(highlight_text_color))
        
        # Additional palette roles for better coverage
        palette.setColor(QPalette.ColorRole.Light, QColor(self._adjust_color(theme.surface, 30)))
        palette.setColor(QPalette.ColorRole.Midlight, QColor(self._adjust_color(theme.surface, 15)))
        palette.setColor(QPalette.ColorRole.Mid, QColor(self._adjust_color(theme.surface, 0)))
        palette.setColor(QPalette.ColorRole.Dark, QColor(self._adjust_color(theme.surface, -30)))
        palette.setColor(QPalette.ColorRole.Shadow, QColor(self._adjust_color(theme.surface, -50)))
        
        # Link colors
        palette.setColor(QPalette.ColorRole.Link, QColor(theme.primary))
        palette.setColor(QPalette.ColorRole.LinkVisited, QColor(theme.accent))
        
        # Disabled state colors - ensure they have proper contrast
        disabled_text = self._adjust_color(theme.text, -70)
        if theme.theme_type == ThemeType.DARK:
            # For dark themes, make disabled text lighter
            disabled_text = self._adjust_color(theme.text, -50)
        
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, 
                        QColor(disabled_text))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, 
                        QColor(disabled_text))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, 
                        QColor(disabled_text))
        
        # Ensure menu and status bar colors are set
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(theme.surface))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(theme.text))
        
        # Special handling for High Contrast theme
        if theme.name == "High Contrast":
            # Ensure all text is white except highlighted text
            palette.setColor(QPalette.ColorRole.ButtonText, QColor("#FFFFFF"))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#000000"))
            
            # Make disabled text more visible
            palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, 
                            QColor("#AAAAAA"))
            palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, 
                            QColor("#AAAAAA"))
            palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, 
                            QColor("#AAAAAA"))
        
        # Apply the palette
        app = QApplication.instance()
        if app:
            app.setPalette(palette)
        
    def export_theme(self, theme_name: str, file_path: str) -> bool:
        """Export a theme to a JSON file"""
        if theme_name not in self.themes:
            return False
            
        theme = self.themes[theme_name]
        
        # Convert theme to dictionary
        theme_dict = {
            "name": theme.name,
            "description": theme.description,
            "theme_type": theme.theme_type.name,
            "primary": theme.primary,
            "secondary": theme.secondary,
            "accent": theme.accent,
            "background": theme.background,
            "surface": theme.surface,
            "text": theme.text,
            "button_gradient": list(theme.button_gradient),
            "button_hover": theme.button_hover,
            "input_background": theme.input_background,
            "success": theme.success,
            "warning": theme.warning,
            "error": theme.error,
            "info": theme.info,
            "button_height": theme.button_height,
            "input_height": theme.input_height,
            "border_radius": theme.border_radius,
            "disabled_opacity": theme.disabled_opacity,
            "hover_opacity": theme.hover_opacity
        }
        
        try:
            with open(file_path, 'w') as f:
                json.dump(theme_dict, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting theme: {e}")
            return False
            
    def import_theme(self, file_path: str) -> Optional[str]:
        """Import a theme from a JSON file and return its ID"""
        try:
            with open(file_path, 'r') as f:
                theme_dict = json.load(f)
                
            # Generate a theme ID from the name
            theme_id = theme_dict.get("name", "custom_theme").lower().replace(" ", "_")
            
            # Ensure theme ID is unique
            if theme_id in self.themes:
                base_id = theme_id
                counter = 1
                while f"{base_id}_{counter}" in self.themes:
                    counter += 1
                theme_id = f"{base_id}_{counter}"
            
            # Create theme object
            theme = Theme(
                name=theme_dict.get("name", "Custom Theme"),
                description=theme_dict.get("description", "Imported custom theme"),
                theme_type=ThemeType[theme_dict.get("theme_type", "CUSTOM")],
                primary=theme_dict.get("primary", "#2196F3"),
                secondary=theme_dict.get("secondary", "#4CAF50"),
                accent=theme_dict.get("accent", "#FF4081"),
                background=theme_dict.get("background", "#FFFFFF"),
                surface=theme_dict.get("surface", "#F5F5F5"),
                text=theme_dict.get("text", "#212121"),
                button_gradient=tuple(theme_dict.get("button_gradient", ("#2196F3", "#1976D2"))),
                button_hover=theme_dict.get("button_hover", "#1E88E5"),
                input_background=theme_dict.get("input_background", "#FFFFFF"),
                success=theme_dict.get("success", "#4CAF50"),
                warning=theme_dict.get("warning", "#FF9800"),
                error=theme_dict.get("error", "#F44336"),
                info=theme_dict.get("info", "#2196F3"),
                button_height=theme_dict.get("button_height", 36),
                input_height=theme_dict.get("input_height", 32),
                border_radius=theme_dict.get("border_radius", 6),
                styles={},
                palette={}
            )
            
            # Add theme to available themes
            self.themes[theme_id] = theme
            
            return theme_id
        except Exception as e:
            print(f"Error importing theme: {e}")
            return None
