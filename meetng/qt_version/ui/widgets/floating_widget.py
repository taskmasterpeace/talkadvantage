from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFrame, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, QPoint, QSettings
from PyQt6.QtGui import QPainter, QColor

class FloatingWidget(QFrame):
    def __init__(self, parent=None, title="Floating Widget", widget_id=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Raised)
        self.widget_id = widget_id or title.lower().replace(" ", "_")
        
        # Enable mouse tracking and set window flags
        self.setMouseTracking(True)
        self.setWindowFlags(
            Qt.WindowType.Tool | 
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        
        # Widget state
        self.dragging = False
        self.resizing = False
        self.drag_start = QPoint()
        self.resize_start = None
        self.resize_edge = None
        self.start_geometry = None
        self.resize_margin = 10  # Pixels for resize detection
        
        # Set larger default size
        self.setMinimumSize(400, 300)
        self.resize(500, 400)  # Default size
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)  # Reduce spacing
        
        # Title bar
        title_bar = QWidget()
        title_bar.setStyleSheet("""
            QWidget {
                background: #2C3E50;
                color: white;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QPushButton {
                background: transparent;
                border: none;
                color: white;
                padding: 4px 8px;
                border-radius: 0px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
            }
            QPushButton#closeButton:hover {
                background: #e81123;
            }
        """)
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(8, 2, 2, 2)
        title_bar_layout.setSpacing(0)
        
        # Icon and Title
        icon_label = QLabel(self.icon if hasattr(self, 'icon') else "🔲")
        icon_label.setStyleSheet("padding-right: 5px;")
        title_bar_layout.addWidget(icon_label)
        
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-weight: bold;")
        title_bar_layout.addWidget(self.title_label)
        
        title_bar_layout.addStretch()
        
        # Window controls
        self.min_btn = QPushButton("─")
        self.min_btn.setFixedSize(30, 24)
        self.min_btn.clicked.connect(self.toggle_minimize)
        title_bar_layout.addWidget(self.min_btn)
        
        self.max_btn = QPushButton("□")
        self.max_btn.setFixedSize(30, 24)
        self.max_btn.clicked.connect(self.toggle_maximize)
        title_bar_layout.addWidget(self.max_btn)
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("closeButton")
        self.close_btn.setFixedSize(30, 24)
        self.close_btn.clicked.connect(self.close_widget)
        title_bar_layout.addWidget(self.close_btn)
        
        layout.addWidget(title_bar)
        
        # Content area
        self.content = QWidget()
        self.content.setStyleSheet("""
            QWidget {
                background: white;
                border-bottom-left-radius: 5px;
                border-bottom-right-radius: 5px;
            }
        """)
        self.content_layout = QVBoxLayout(self.content)
        layout.addWidget(self.content)
        
        # State
        self.floating = False
        self.minimized = False
        self.maximized = False
        self.restore_geometry = None
        
        # Load saved position
        self.load_geometry()
    
    def load_geometry(self):
        """Load saved position and size"""
        settings = QSettings("PowerPlay", "MeetingAssistant")
        geometry = settings.value(f"geometry/{self.widget_id}")
        if geometry:
            self.setGeometry(geometry)
    
    def save_geometry(self):
        """Save current position and size"""
        settings = QSettings("PowerPlay", "MeetingAssistant")
        settings.setValue(f"geometry/{self.widget_id}", self.geometry())
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if click is in resize area
            pos = event.pos()
            rect = self.rect()
            
            # Determine if click is on an edge
            on_right = abs(rect.right() - pos.x()) <= self.resize_margin
            on_bottom = abs(rect.bottom() - pos.y()) <= self.resize_margin
            
            if on_right and on_bottom:
                self.resizing = True
                self.resize_start = event.pos()
                self.start_geometry = self.geometry()
            else:
                # Handle dragging as before
                self.dragging = True
                self.drag_start = event.pos()
                self.start_geometry = self.geometry()
            
            event.accept()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.resizing = False
            self.save_geometry()
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
    
    def mouseMoveEvent(self, event):
        if self.resizing:
            delta = event.pos() - self.resize_start
            new_width = max(self.minimumWidth(), self.start_geometry.width() + delta.x())
            new_height = max(self.minimumHeight(), self.start_geometry.height() + delta.y())
            self.resize(new_width, new_height)
            event.accept()
        elif self.dragging:
            delta = event.pos() - self.drag_start
            new_pos = self.mapToParent(delta)
            self.move(new_pos)
            event.accept()
        else:
            # Update cursor based on position
            pos = event.pos()
            rect = self.rect()
            on_right = abs(rect.right() - pos.x()) <= self.resize_margin
            on_bottom = abs(rect.bottom() - pos.y()) <= self.resize_margin
            
            if on_right and on_bottom:
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def close_widget(self):
        """Close the widget and remove from parent's floating_widgets list"""
        if self.parent() and hasattr(self.parent(), 'floating_widgets'):
            self.parent().floating_widgets.remove(self)
        self.deleteLater()

    def toggle_minimize(self):
        """Toggle minimized state"""
        if not self.minimized:
            self.restore_geometry = self.geometry()
            self.setFixedHeight(self.title_label.height() + 10)
            self.content.hide()
            self.min_btn.setText("─")
            self.minimized = True
        else:
            self.setGeometry(self.restore_geometry)
            self.setMinimumHeight(150)
            self.setMaximumHeight(16777215)
            self.content.show()
            self.min_btn.setText("─")
            self.minimized = False
        self.save_geometry()

    def toggle_maximize(self):
        """Toggle maximized state"""
        if not self.maximized:
            self.restore_geometry = self.geometry()
            parent_rect = self.parent().rect()
            self.setGeometry(parent_rect)
            self.max_btn.setText("❐")
            self.maximized = True
        else:
            self.setGeometry(self.restore_geometry)
            self.max_btn.setText("□")
            self.maximized = False
        self.save_geometry()
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, QPoint, QSettings
from PyQt6.QtGui import QPainter, QColor

class FloatingWidget(QFrame):
    def __init__(self, parent=None, title="Floating Widget", widget_id=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Raised)
        self.widget_id = widget_id or title.lower().replace(" ", "_")
        
        # Enable mouse tracking
        self.setMouseTracking(True)
        
        # Widget state
        self.dragging = False
        self.resizing = False
        self.drag_start = QPoint()
        self.resize_start = None
        self.resize_edge = None
        self.start_geometry = None
        self.resize_margin = 10  # Pixels for resize detection
        
        # Set larger default size
        self.setMinimumSize(400, 300)
        self.resize(500, 400)  # Default size
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        
        # Title bar
        title_bar = QWidget()
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(5, 2, 5, 2)
        
        # Title
        self.title_label = QLabel(title)
        title_bar_layout.addWidget(self.title_label)
        
        # Controls
        self.float_btn = QPushButton("🗗")
        self.float_btn.setFixedSize(24, 24)
        self.float_btn.clicked.connect(self.toggle_float)
        title_bar_layout.addWidget(self.float_btn)
        
        self.min_btn = QPushButton("🗕")
        self.min_btn.setFixedSize(24, 24)
        self.min_btn.clicked.connect(self.toggle_minimize)
        title_bar_layout.addWidget(self.min_btn)
        
        layout.addWidget(title_bar)
        
        # Content area
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        layout.addWidget(self.content)
        
        # State
        self.floating = False
        self.minimized = False
        self.restore_geometry = None
        
        # Load saved position
        self.load_geometry()
    
    def load_geometry(self):
        """Load saved position and size"""
        settings = QSettings("PowerPlay", "MeetingAssistant")
        geometry = settings.value(f"geometry/{self.widget_id}")
        if geometry:
            self.setGeometry(geometry)
    
    def save_geometry(self):
        """Save current position and size"""
        settings = QSettings("PowerPlay", "MeetingAssistant")
        settings.setValue(f"geometry/{self.widget_id}", self.geometry())
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if click is in resize area
            pos = event.pos()
            rect = self.rect()
            
            # Determine if click is on an edge
            on_right = abs(rect.right() - pos.x()) <= self.resize_margin
            on_bottom = abs(rect.bottom() - pos.y()) <= self.resize_margin
            
            if on_right and on_bottom:
                self.resizing = True
                self.resize_start = event.pos()
                self.start_geometry = self.geometry()
            else:
                # Handle dragging as before
                self.dragging = True
                self.drag_start = event.pos()
                self.start_geometry = self.geometry()
            
            event.accept()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.resizing = False
            self.save_geometry()
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
    
    def mouseMoveEvent(self, event):
        if self.resizing:
            delta = event.pos() - self.resize_start
            new_width = max(self.minimumWidth(), self.start_geometry.width() + delta.x())
            new_height = max(self.minimumHeight(), self.start_geometry.height() + delta.y())
            self.resize(new_width, new_height)
            event.accept()
        elif self.dragging:
            delta = event.pos() - self.drag_start
            new_pos = self.mapToParent(delta)
            self.move(new_pos)
            event.accept()
        else:
            # Update cursor based on position
            pos = event.pos()
            rect = self.rect()
            on_right = abs(rect.right() - pos.x()) <= self.resize_margin
            on_bottom = abs(rect.bottom() - pos.y()) <= self.resize_margin
            
            if on_right and on_bottom:
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def toggle_float(self):
        self.floating = not self.floating
        self.float_btn.setText("🗗" if self.floating else "🗖")
        # Implement floating behavior
    
    def toggle_minimize(self):
        if not self.minimized:
            self.restore_geometry = self.geometry()
            self.setFixedHeight(self.title_label.height() + 10)
            self.content.hide()
            self.min_btn.setText("🗖")
        else:
            self.setGeometry(self.restore_geometry)
            self.setMinimumHeight(150)
            self.setMaximumHeight(16777215)
            self.content.show()
            self.min_btn.setText("🗕")
        self.minimized = not self.minimized
        self.save_geometry()
