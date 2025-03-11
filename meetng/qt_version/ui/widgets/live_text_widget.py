from .floating_widget import FloatingWidget
from PyQt6.QtWidgets import QTextEdit, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMenu
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QTextCursor, QTextCharFormat, QColor
from ..components.font_control import FontControlPanel

class LiveTextWidget(FloatingWidget):
    """Widget for displaying live text with formatting options"""
    
    textChanged = pyqtSignal(str)  # Signal emitted when text content changes
    
    def __init__(self, parent=None):
        super().__init__(parent, title="Live Text", widget_id="live_text")
        
        # Controls
        controls = QHBoxLayout()
        
        # Font control
        self.font_control = FontControlPanel(settings_key="live_text_font")
        controls.addWidget(self.font_control)
        
        # Copy button
        self.copy_btn = QPushButton("📋 Copy")
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        controls.addWidget(self.copy_btn)
        
        # Search button
        self.search_btn = QPushButton("🔍 Search")
        self.search_btn.clicked.connect(self.show_search_dialog)
        controls.addWidget(self.search_btn)
        
        self.content_layout.addLayout(controls)
        
        # Text area
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.text_edit.customContextMenuRequested.connect(self.show_context_menu)
        self.font_control.fontChanged.connect(lambda f: self.text_edit.setFont(f))
        self.content_layout.addWidget(self.text_edit)
        
        # Initialize search variables
        self.current_search_text = ""
        self.current_search_position = 0
    
    def set_text(self, text):
        """Set the text content"""
        self.text_edit.setText(text)
        self.textChanged.emit(text)
    
    def append_text(self, text):
        """Append text to the current content"""
        self.text_edit.append(text)
        self.textChanged.emit(self.text_edit.toPlainText())
    
    def get_text(self):
        """Get the current text content"""
        return self.text_edit.toPlainText()
    
    def copy_to_clipboard(self):
        """Copy text to clipboard with visual feedback"""
        from PyQt6.QtWidgets import QApplication
        
        text = self.text_edit.toPlainText()
        QApplication.clipboard().setText(text)
        
        # Show temporary feedback
        cursor_pos = self.text_edit.textCursor().position()
        self.show_temporary_message("Copied to clipboard!", 1500)
    
    def show_temporary_message(self, message, duration=1500):
        """Show a temporary message overlay"""
        from PyQt6.QtWidgets import QLabel
        from PyQt6.QtCore import QTimer
        
        feedback = QLabel(message, self.text_edit)
        feedback.setStyleSheet("""
            background-color: rgba(70, 70, 70, 0.8);
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            font-weight: bold;
        """)
        feedback.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Position in the center of the text widget
        feedback.adjustSize()
        x = (self.text_edit.width() - feedback.width()) // 2
        y = (self.text_edit.height() - feedback.height()) // 2
        feedback.move(x, y)
        
        # Show and auto-hide after specified duration
        feedback.show()
        QTimer.singleShot(duration, feedback.deleteLater)
    
    def show_context_menu(self, position):
        """Show custom context menu"""
        menu = QMenu()
        
        # Add standard actions
        copy_action = menu.addAction("Copy")
        copy_action.triggered.connect(self.copy_to_clipboard)
        
        select_all_action = menu.addAction("Select All")
        select_all_action.triggered.connect(self.text_edit.selectAll)
        
        menu.addSeparator()
        
        # Add search action
        search_action = menu.addAction("Search...")
        search_action.triggered.connect(self.show_search_dialog)
        
        # Execute the menu
        menu.exec(self.text_edit.mapToGlobal(position))
    
    def show_search_dialog(self):
        """Show search dialog"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Search Text")
        dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout(dialog)
        
        # Search input
        search_layout = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setPlaceholderText("Enter search text...")
        if self.current_search_text:
            search_input.setText(self.current_search_text)
        search_layout.addWidget(search_input)
        layout.addLayout(search_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        find_next_btn = QPushButton("Find Next")
        find_prev_btn = QPushButton("Find Previous")
        close_btn = QPushButton("Close")
        
        find_next_btn.clicked.connect(lambda: self.find_text(search_input.text(), forward=True))
        find_prev_btn.clicked.connect(lambda: self.find_text(search_input.text(), forward=False))
        close_btn.clicked.connect(dialog.close)
        
        button_layout.addWidget(find_next_btn)
        button_layout.addWidget(find_prev_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        # Connect enter key to find next
        search_input.returnPressed.connect(lambda: self.find_text(search_input.text(), forward=True))
        
        dialog.exec()
    
    def find_text(self, text, forward=True):
        """Find and highlight text in the document"""
        if not text:
            return False
            
        # Store current search text
        self.current_search_text = text
        
        # Get current cursor
        cursor = self.text_edit.textCursor()
        
        # Create format for highlighting
        format = QTextCharFormat()
        format.setBackground(QColor(255, 255, 0, 100))  # Light yellow highlight
        
        # Set search flags
        flags = QTextDocument.FindFlag(0)
        if not forward:
            flags |= QTextDocument.FindFlag.FindBackward
        
        # Find the text
        found = self.text_edit.find(text, flags)
        
        if not found and self.current_search_position > 0:
            # If not found and we're not at the beginning, wrap around
            cursor.setPosition(0 if forward else len(self.text_edit.toPlainText()))
            self.text_edit.setTextCursor(cursor)
            found = self.text_edit.find(text, flags)
        
        # Update position if found
        if found:
            self.current_search_position = cursor.position()
            return True
        else:
            self.show_temporary_message(f"Text '{text}' not found", 1500)
            return False
