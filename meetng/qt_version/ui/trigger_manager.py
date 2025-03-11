from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QTableWidget, QTableWidgetItem, QCheckBox,
    QGroupBox, QStyledItemDelegate, QTabWidget, QWidget
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QColor

class ReadOnlyDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        return None

class TriggerManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Voice Command Manager")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        # Load existing settings
        self.settings = QSettings("PowerPlay", "MeetingAssistant")
        print("\n=== Initializing Trigger Manager ===")
        
        layout = QVBoxLayout()
        
        # Main tab widget
        tabs = QTabWidget()
        
        # === Built-in Commands Tab ===
        built_in_widget = QWidget()
        built_in_layout = QVBoxLayout()
        
        # System commands group
        system_group = QGroupBox("System Commands")
        system_layout = QVBoxLayout()
        
        self.system_table = QTableWidget()
        self.system_table.setColumnCount(4)
        self.system_table.setHorizontalHeaderLabels([
            "Action (Fixed)", 
            "Trigger Phrase",
            "Bookmark Name",
            "Active"
        ])
        
        # Set column properties
        self.system_table.setColumnWidth(0, 200)
        self.system_table.setColumnWidth(1, 200)
        self.system_table.setColumnWidth(2, 200)
        
        # Make first column non-editable
        self.system_table.setItemDelegateForColumn(0, ReadOnlyDelegate())
        
        # Set column properties
        self.system_table.setColumnWidth(0, 200)
        self.system_table.setColumnWidth(1, 200)
        self.system_table.setColumnWidth(2, 200)
        self.system_table.setItemDelegateForColumn(0, ReadOnlyDelegate())
        
        # Load saved triggers or defaults
        self.load_saved_triggers()
        
        # Add "Reset to Defaults" button
        reset_btn = QPushButton("Reset to Default Phrases")
        reset_btn.clicked.connect(self.reset_default_triggers)
        
        system_layout.addWidget(self.system_table)
        system_layout.addWidget(reset_btn)
        
        # Add help text
        help_text = QLabel(
            "• Customize trigger phrases to use your preferred words\n"
            "• For bookmarks, you can set both the trigger phrase and the bookmark name\n"
            "• Example: Trigger 'mark unicorn' could create a bookmark named 'Magical Moment'"
        )
        help_text.setStyleSheet("color: #666; font-style: italic;")
        system_layout.addWidget(help_text)
        
        system_group.setLayout(system_layout)
        built_in_layout.addWidget(system_group)
        
        built_in_widget.setLayout(built_in_layout)
        tabs.addTab(built_in_widget, "Built-in Commands")
        
        layout.addWidget(tabs)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.save_changes)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

    def save_changes(self):
        """Save all changes to settings"""
        print("\n=== Saving Triggers ===")
        
        # Save system command triggers
        system_triggers = []
        for row in range(self.system_table.rowCount()):
            trigger = {
                'action': self.system_table.item(row, 0).text(),
                'trigger_phrase': self.system_table.item(row, 1).text(),
                'bookmark_name': self.system_table.item(row, 2).text(),
                'active': self.system_table.cellWidget(row, 3).isChecked()
            }
            system_triggers.append(trigger)
            print(f"Saving trigger: {trigger}")

        # Save to settings
        self.settings.beginWriteArray('system_triggers')
        for i, trigger in enumerate(system_triggers):
            self.settings.setArrayIndex(i)
            for key, value in trigger.items():
                self.settings.setValue(key, value)
        self.settings.endArray()
        self.settings.sync()
        
        # Verify save
        print("\nVerification - Saved triggers:")
        size = self.settings.beginReadArray('system_triggers')
        for i in range(size):
            self.settings.setArrayIndex(i)
            trigger = {
                'action': self.settings.value('action'),
                'trigger_phrase': self.settings.value('trigger_phrase'),
                'bookmark_name': self.settings.value('bookmark_name'),
                'active': self.settings.value('active', type=bool)
            }
            print(f"  {trigger}")
        self.settings.endArray()
        
        # Update parent's triggers
        if self.parent():
            print("\nUpdating parent's triggers")
            self.parent().load_triggers_from_settings()
            
        print("\n=== Save Complete ===")
        self.accept()

    def reset_default_triggers(self):
        """Reset trigger phrases to defaults"""
        default_commands = [
            ("Create Quick Bookmark", "bookmark this", "Quick Mark"),
            ("Create Named Bookmark", "mark important", "Important Point"),
            ("Create Named Bookmark", "mark todo", "TODO Item"),
            ("Create Named Bookmark", "mark decision", "Decision Made"),
            ("Process Current Section", "chunk now", ""),
            ("Pause/Resume Recording", "pause recording", ""),
            ("Stop Recording Session", "stop recording", "")
        ]
        
        for row, (action, trigger, bookmark_name) in enumerate(default_commands):
            self.system_table.item(row, 1).setText(trigger)
            self.system_table.item(row, 2).setText(bookmark_name)
    def load_saved_triggers(self):
        """Load saved triggers from settings"""
        print("\n=== Loading Saved Triggers ===")
        
        # Define default commands
        default_commands = [
            ("Create Quick Bookmark", "bookmark this", "Quick Mark", True),
            ("Create Named Bookmark", "mark important", "Important Point", True),
            ("Create Named Bookmark", "mark todo", "TODO Item", True),
            ("Create Named Bookmark", "mark decision", "Decision Made", True),
            ("Process Current Section", "chunk now", "", True),
            ("Pause/Resume Recording", "pause recording", "", True),
            ("Stop Recording Session", "stop recording", "", True)
        ]
        
        # Read saved triggers
        saved_triggers = []
        size = self.settings.beginReadArray('system_triggers')
        for i in range(size):
            self.settings.setArrayIndex(i)
            trigger = {
                'action': self.settings.value('action'),
                'trigger_phrase': self.settings.value('trigger_phrase'),
                'bookmark_name': self.settings.value('bookmark_name'),
                'active': self.settings.value('active', type=bool)
            }
            saved_triggers.append(trigger)
            print(f"Loaded saved trigger: {trigger['action']} = {trigger}")
        self.settings.endArray()
        
        # Populate table
        self.system_table.setRowCount(len(default_commands))
        for i, (action, default_trigger, default_bookmark, default_active) in enumerate(default_commands):
            # Find matching saved trigger if it exists
            saved = next((t for t in saved_triggers if t['action'] == action), None)
            
            # Use saved values if found, otherwise use defaults
            trigger_phrase = saved['trigger_phrase'] if saved else default_trigger
            bookmark_name = saved['bookmark_name'] if saved else default_bookmark
            is_active = saved['active'] if saved else default_active
            
            print(f"Setting row {i}: {action} = {trigger_phrase}, {bookmark_name}, {is_active}")
            
            # Action (non-editable)
            action_item = QTableWidgetItem(action)
            action_item.setFlags(action_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.system_table.setItem(i, 0, action_item)
            
            # Trigger phrase (editable)
            trigger_item = QTableWidgetItem(trigger_phrase)
            trigger_item.setToolTip("Enter one or more trigger phrases separated by semicolons (;)\n"
                                  "Example: 'bookmark this; mark this; remember this'\n"
                                  "Triggers are case-insensitive")
            self.system_table.setItem(i, 1, trigger_item)
            
            # Bookmark name (editable for bookmark actions)
            bookmark_item = QTableWidgetItem(bookmark_name)
            if "Bookmark" not in action:
                bookmark_item.setFlags(bookmark_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                bookmark_item.setBackground(QColor("#f0f0f0"))
            self.system_table.setItem(i, 2, bookmark_item)
            
            # Active checkbox
            checkbox = QCheckBox()
            checkbox.setChecked(is_active)
            self.system_table.setCellWidget(i, 3, checkbox)
