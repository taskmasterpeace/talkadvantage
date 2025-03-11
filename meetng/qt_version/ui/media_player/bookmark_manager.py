from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QListWidget, QListWidgetItem, QDialog,
    QFormLayout, QLineEdit, QTextEdit, QDialogButtonBox,
    QStyledItemDelegate, QStyle, QSizePolicy, QMenu,
    QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPainter, QColor
import json
import os

class BookmarkDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if not index.isValid():
            return
            
        bookmark = index.data(Qt.ItemDataRole.UserRole)
        rect = option.rect
        
        # Draw selection background if selected
        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(rect, option.palette.highlight())
            
        # Create display text with special indicators
        display_text = f"[{bookmark['timestamp']}] {bookmark['title']}"
        
        # Add special indicators if not already in title
        if bookmark.get('is_user_speaking') and "👤" not in display_text:
            display_text = f"👤 {display_text}"
        elif bookmark.get('is_decision_point') and "🔍" not in display_text:
            display_text = f"🔍 {display_text}"
        elif bookmark.get('is_action_item') and "✅" not in display_text:
            display_text = f"✅ {display_text}"
            
        # Draw timestamp and title compactly
        painter.drawText(
            rect.adjusted(4, 2, -4, -2),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            display_text
        )
        
    def sizeHint(self, option, index):
        return QSize(0, 24)  # Compact height

class BookmarkEditDialog(QDialog):
    def __init__(self, bookmark, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Bookmark")
        self.bookmark = bookmark.copy()
        
        layout = QFormLayout(self)
        
        # Title field
        self.title_edit = QLineEdit(bookmark['title'])
        layout.addRow("Title:", self.title_edit)
        
        # Notes field (optional, expandable)
        self.notes_edit = QTextEdit()
        self.notes_edit.setText(bookmark.get('notes', ''))
        self.notes_edit.setMaximumHeight(100)
        layout.addRow("Notes:", self.notes_edit)
        
        # Special bookmark types
        self.user_speaking_check = QCheckBox("👤 User Speaking")
        self.user_speaking_check.setChecked(bookmark.get('is_user_speaking', False))
        layout.addRow("", self.user_speaking_check)
        
        self.decision_point_check = QCheckBox("🔍 Decision Point")
        self.decision_point_check.setChecked(bookmark.get('is_decision_point', False))
        layout.addRow("", self.decision_point_check)
        
        self.action_item_check = QCheckBox("✅ Action Item")
        self.action_item_check.setChecked(bookmark.get('is_action_item', False))
        layout.addRow("", self.action_item_check)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
    def accept(self):
        self.bookmark['title'] = self.title_edit.text()
        self.bookmark['notes'] = self.notes_edit.toPlainText()
        self.bookmark['is_user_speaking'] = self.user_speaking_check.isChecked()
        self.bookmark['is_decision_point'] = self.decision_point_check.isChecked()
        self.bookmark['is_action_item'] = self.action_item_check.isChecked()
        super().accept()

class BookmarkManager(QWidget):
    seek_to_timestamp = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bookmarks")
        
        # Make window resizable
        self.setMinimumSize(200, 100)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        layout = QVBoxLayout(self)
        
        # Bookmark list with custom delegate for compact display
        self.bookmark_list = QListWidget()
        self.bookmark_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.bookmark_list.itemDoubleClicked.connect(self.edit_bookmark)
        self.bookmark_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.bookmark_list.customContextMenuRequested.connect(self.show_context_menu)
        self.bookmark_list.setItemDelegate(BookmarkDelegate())
        layout.addWidget(self.bookmark_list)
        
        # Compact controls
        controls = QHBoxLayout()
        self.add_btn = QPushButton("+")
        self.add_btn.setMaximumWidth(30)
        self.add_btn.clicked.connect(self.add_bookmark)
        self.delete_btn = QPushButton("-")
        self.delete_btn.setMaximumWidth(30)
        self.delete_btn.clicked.connect(self.delete_bookmark)
        self.prev_btn = QPushButton("◀")
        self.prev_btn.setMaximumWidth(30)
        self.prev_btn.clicked.connect(lambda: self.navigate_bookmarks(-1))
        self.next_btn = QPushButton("▶")
        self.next_btn.setMaximumWidth(30)
        self.next_btn.clicked.connect(lambda: self.navigate_bookmarks(1))
        
        controls.addWidget(self.add_btn)
        controls.addWidget(self.delete_btn)
        controls.addSpacing(10)
        controls.addWidget(self.prev_btn)
        controls.addWidget(self.next_btn)
        controls.addStretch()
        
        layout.addLayout(controls)
        
        # Load existing bookmarks
        self.load_bookmarks()
        
    def add_bookmark(self, timestamp: str = "00:00", title: str = None, bookmark_type: str = None, is_user_speaking: bool = False, is_decision_point: bool = False, is_action_item: bool = False):
        """Add a new bookmark with optional special type flags"""
        if not title:
            title = f"Bookmark at {timestamp}"
            
            # Add indicator for special bookmark types
            if is_user_speaking:
                title = f"👤 User: {title}"
            elif is_decision_point:
                title = f"🔍 Decision: {title}"
            elif is_action_item:
                title = f"✅ Action: {title}"
                
        bookmark = {
            'timestamp': timestamp,
            'title': title,
            'notes': '',
            'is_user_speaking': is_user_speaking,
            'is_decision_point': is_decision_point,
            'is_action_item': is_action_item
        }
        
        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, bookmark)
        
        # Apply special styling based on bookmark type
        if is_user_speaking:
            item.setBackground(QColor(230, 247, 255))  # Light blue
        elif is_decision_point:
            item.setBackground(QColor(255, 243, 224))  # Light orange
        elif is_action_item:
            item.setBackground(QColor(232, 245, 233))  # Light green
            
        self.bookmark_list.addItem(item)
        self.save_bookmarks()

    def edit_bookmark(self, item):
        """Edit existing bookmark"""
        bookmark = item.data(Qt.ItemDataRole.UserRole)
        dialog = BookmarkEditDialog(bookmark, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            item.setData(Qt.ItemDataRole.UserRole, dialog.bookmark)
            self.save_bookmarks()

    def delete_bookmark(self):
        """Delete selected bookmark"""
        current = self.bookmark_list.currentItem()
        if current:
            self.bookmark_list.takeItem(self.bookmark_list.row(current))
            self.save_bookmarks()

    def navigate_bookmarks(self, direction: int):
        """Navigate between bookmarks"""
        current_row = self.bookmark_list.currentRow()
        new_row = current_row + direction
        
        if 0 <= new_row < self.bookmark_list.count():
            self.bookmark_list.setCurrentRow(new_row)
            item = self.bookmark_list.item(new_row)
            bookmark = item.data(Qt.ItemDataRole.UserRole)
            self.seek_to_timestamp.emit(bookmark['timestamp'])

    def show_context_menu(self, position):
        """Show context menu for bookmark item"""
        menu = QMenu(self)
        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Delete")
        
        action = menu.exec(self.bookmark_list.mapToGlobal(position))
        if action == edit_action:
            self.edit_bookmark(self.bookmark_list.itemAt(position))
        elif action == delete_action:
            self.delete_bookmark()

    def save_bookmarks(self):
        """Save bookmarks to file"""
        bookmarks = []
        for i in range(self.bookmark_list.count()):
            item = self.bookmark_list.item(i)
            bookmarks.append(item.data(Qt.ItemDataRole.UserRole))
            
        filepath = self.get_bookmark_filepath()
        with open(filepath, 'w') as f:
            json.dump(bookmarks, f)

    def load_bookmarks(self):
        """Load bookmarks from file"""
        filepath = self.get_bookmark_filepath()
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                bookmarks = json.load(f)
                
            self.bookmark_list.clear()
            for bookmark in bookmarks:
                item = QListWidgetItem()
                item.setData(Qt.ItemDataRole.UserRole, bookmark)
                self.bookmark_list.addItem(item)

    def get_bookmark_filepath(self):
        """Get path for bookmark storage"""
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                          "bookmarks.json")
                          
    def set_template(self, template: dict):
        """Set the template for the bookmark manager
        
        Args:
            template: The template dictionary
        """
        self.current_template = template
        print(f"Bookmark Manager: Template set to '{template.get('name', 'unknown')}'")
        
        # Add template-specific bookmarks to the quick add menu
        if "bookmarks" in template:
            special_bookmarks = [b for b in template["bookmarks"] if 
                                b.get("is_user_speaking") or 
                                b.get("is_decision_point") or 
                                b.get("is_action_item")]
            
            if special_bookmarks:
                print(f"Found {len(special_bookmarks)} special bookmarks in template")
