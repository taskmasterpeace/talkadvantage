from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QLineEdit, QTextEdit, QListWidget,
    QMessageBox, QGroupBox, QComboBox, QListWidgetItem,
    QWidget, QFileDialog, QFormLayout, QRadioButton,
    QStackedWidget, QSizePolicy, QApplication, QCheckBox,
    QMenu, QSplitter, QTabWidget, QScrollArea
)

class BookmarkDialog(QDialog):
    """Dialog for editing bookmark details"""
    
    def __init__(self, parent=None, bookmark=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Bookmark" if bookmark else "Add Bookmark")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # Bookmark type selection
        type_group = QGroupBox("🏷️ Bookmark Type")
        type_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ccc;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
        """)
        type_layout = QVBoxLayout()
        type_layout.setSpacing(8)
        
        self.type_marker = QRadioButton("📍 Marker (Insert text at position)")
        self.type_voice = QRadioButton("🎤 Voice Command (Execute action)")
        
        # Style radio buttons
        radio_style = """
            QRadioButton {
                padding: 6px;
                border-radius: 4px;
            }
            QRadioButton:hover {
                background-color: #f0f0f0;
            }
        """
        self.type_marker.setStyleSheet(radio_style)
        self.type_voice.setStyleSheet(radio_style)
        if bookmark:
            self.type_marker.setChecked(bookmark["bookmark_type"] == "marker")
            self.type_voice.setChecked(bookmark["bookmark_type"] == "voice_command")
        else:
            self.type_marker.setChecked(True)
        type_layout.addWidget(self.type_marker)
        type_layout.addWidget(self.type_voice)
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # Form for other fields
        form = QFormLayout()
        form.setSpacing(10)
        
        # Style for input fields
        input_style = """
            QLineEdit, QTextEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #f8f9fa;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #007bff;
                background-color: white;
            }
        """
        
        # Name field
        self.name_edit = QLineEdit()
        self.name_edit.setStyleSheet(input_style)
        self.name_edit.setPlaceholderText("Enter bookmark name...")
        if bookmark:
            self.name_edit.setText(bookmark["name"])
        form.addRow("Name:", self.name_edit)
        
        # Key shortcut field
        self.shortcut_edit = QLineEdit()
        self.shortcut_edit.setStyleSheet(input_style)
        self.shortcut_edit.setPlaceholderText("e.g., Ctrl+1, Alt+M...")
        if bookmark:
            self.shortcut_edit.setText(bookmark["key_shortcut"])
        form.addRow("Key Shortcut:", self.shortcut_edit)
        
        # Voice trigger field
        self.trigger_edit = QLineEdit()
        self.trigger_edit.setStyleSheet(input_style)
        self.trigger_edit.setPlaceholderText("e.g., mark decision, new topic...")
        if bookmark:
            self.trigger_edit.setText(bookmark["voice_trigger"])
        form.addRow("Voice Trigger:", self.trigger_edit)
        
        # Content/Action fields (switched based on type)
        self.content_stack = QStackedWidget()
        
        # Marker content widget
        self.content_edit = QTextEdit()
        self.content_edit.setStyleSheet(input_style)
        self.content_edit.setMinimumHeight(80)
        self.content_edit.setMaximumHeight(120)
        self.content_edit.setPlaceholderText("Enter the text that will be inserted at the marker position...")
        if bookmark and bookmark.get("bookmark_type") == "marker":
            self.content_edit.setText(bookmark.get("content", ""))
        
        # Voice command action widget
        self.action_combo = QComboBox()
        self.action_combo.setStyleSheet(input_style)
        self.action_combo.addItems([
            "start_recording",
            "stop_recording",
            "pause_recording",
            "resume_recording",
            "new_section",
            "mark_important",
            "add_note"
        ])
        if bookmark and bookmark.get("bookmark_type") == "voice_command":
            self.action_combo.setCurrentText(bookmark.get("action", ""))
            
        # Add widgets to stack
        content_page = QWidget()
        content_layout = QFormLayout()
        content_layout.addRow("Marker Text:", self.content_edit)
        content_page.setLayout(content_layout)
        
        action_page = QWidget()
        action_layout = QFormLayout()
        action_layout.addRow("Command Action:", self.action_combo)
        action_page.setLayout(action_layout)
        
        self.content_stack.addWidget(content_page)
        self.content_stack.addWidget(action_page)
        
        # Set initial stack page based on type
        self.content_stack.setCurrentIndex(0 if self.type_marker.isChecked() else 1)
        
        # Connect radio buttons to stack switching
        self.type_marker.toggled.connect(lambda checked: self.content_stack.setCurrentIndex(0) if checked else None)
        self.type_voice.toggled.connect(lambda checked: self.content_stack.setCurrentIndex(1) if checked else None)
        
        form.addRow("", self.content_stack)
        
        # Description field (smaller)
        self.description_edit = QTextEdit()
        self.description_edit.setStyleSheet(input_style)
        self.description_edit.setMinimumHeight(40)
        self.description_edit.setMaximumHeight(60)
        self.description_edit.setPlaceholderText("Add a helpful description of when to use this bookmark...")
        if bookmark:
            self.description_edit.setText(bookmark.get("description", ""))
        form.addRow("Description:", self.description_edit)
        
        # Special bookmark types section
        special_group = QGroupBox("🌟 Special Bookmark Types")
        special_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ccc;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
        """)
        special_layout = QVBoxLayout()

        # User Speaking checkbox
        self.user_speaking_check = QCheckBox("👤 User Speaking - Mark when the user is speaking")
        self.user_speaking_check.setStyleSheet("""
            QCheckBox {
                padding: 6px;
                border-radius: 4px;
            }
            QCheckBox:hover {
                background-color: #f0f0f0;
            }
        """)
        if bookmark and bookmark.get("is_user_speaking"):
            self.user_speaking_check.setChecked(True)
        special_layout.addWidget(self.user_speaking_check)

        # Decision Point checkbox
        self.decision_point_check = QCheckBox("🔍 Decision Point - Mark important decisions")
        self.decision_point_check.setStyleSheet("""
            QCheckBox {
                padding: 6px;
                border-radius: 4px;
            }
            QCheckBox:hover {
                background-color: #f0f0f0;
            }
        """)
        if bookmark and bookmark.get("is_decision_point"):
            self.decision_point_check.setChecked(True)
        special_layout.addWidget(self.decision_point_check)

        # Action Item checkbox
        self.action_item_check = QCheckBox("✅ Action Item - Mark tasks and assignments")
        self.action_item_check.setStyleSheet("""
            QCheckBox {
                padding: 6px;
                border-radius: 4px;
            }
            QCheckBox:hover {
                background-color: #f0f0f0;
            }
        """)
        if bookmark and bookmark.get("is_action_item"):
            self.action_item_check.setChecked(True)
        special_layout.addWidget(self.action_item_check)

        special_group.setLayout(special_layout)
        layout.addWidget(special_group)
        
        # Add form to layout
        layout.addLayout(form)
        
        # Buttons with styling
        button_box = QHBoxLayout()
        button_box.setSpacing(8)
        
        save_btn = QPushButton("💾 Save")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        save_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        button_box.addWidget(save_btn)
        button_box.addWidget(cancel_btn)
        
        # Add buttons to layout
        button_widget = QWidget()
        button_widget.setLayout(button_box)
        layout.addWidget(button_widget)
        
        self.setLayout(layout)
        
    def get_bookmark(self):
        """Return the bookmark data"""
        is_marker = self.type_marker.isChecked()
        return {
            "name": self.name_edit.text(),
            "bookmark_type": "marker" if is_marker else "voice_command",
            "key_shortcut": self.shortcut_edit.text(),
            "voice_trigger": self.trigger_edit.text(),
            "content": self.content_edit.toPlainText() if is_marker else "",
            "action": "" if is_marker else self.action_combo.currentText(),
            "description": self.description_edit.toPlainText(),
            # Special bookmark types
            "is_user_speaking": self.user_speaking_check.isChecked(),
            "is_decision_point": self.decision_point_check.isChecked(),
            "is_action_item": self.action_item_check.isChecked()
        }
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QColor
import os
import json
from services.template_manager import TemplateManager
from .template_wizard_qt import TemplateWizardDialog

class TemplateEditorQt(QDialog):
    """Dialog for editing templates with a two-column layout and tabbed interface"""
    
    template_saved = pyqtSignal(dict)
    
    def __init__(self, parent=None, template_manager=None):
        super().__init__(parent)
        self.setWindowTitle("Analysis Profile Editor")
        self.setMinimumSize(1200, 800)
        
        # Store template manager
        self.template_manager = template_manager
        
        # Store app reference from parent
        self.app = parent.app if parent and hasattr(parent, 'app') else None
        
        # Ensure we have a template manager
        if self.template_manager is None and self.app and hasattr(self.app, 'langchain_service'):
            print("No template manager provided, using one from langchain_service")
            self.template_manager = self.app.langchain_service.template_manager
        
        # Initialize attributes
        self.templates = []
        self.current_template = None
        self.has_unsaved_changes = False
        self.original_values = {}
        self._debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        
        # Create layout - IMPORTANT: Use self as parent for the layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Setup UI components
        self.setup_ui(self.main_layout)
        
        # Load templates
        self.load_templates()
        
        # Force update
        self.update()
        QApplication.processEvents()
        
    def setup_ui(self, layout):
        """Set up the user interface with two-column layout"""
        # Create a splitter for the two-column layout
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(self.splitter)
        
        # Left panel - Template List and Controls
        self.left_panel = QWidget()
        self.left_panel.setMinimumWidth(250)  # Ensure left panel doesn't get too narrow
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)
        
        # Template list group
        template_group = QGroupBox("Templates")
        template_layout = QVBoxLayout()
        template_layout.setSpacing(8)
        
        # Template list with search
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Filter templates...")
        self.search_edit.textChanged.connect(self.filter_templates)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        template_layout.addLayout(search_layout)
        
        # Template list
        self.template_list = QListWidget()
        self.template_list.setMinimumHeight(300)
        self.template_list.currentRowChanged.connect(self.on_list_selection_changed)
        template_layout.addWidget(self.template_list)
        
        # Template controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(6)
        
        self.new_btn = QPushButton("New")
        self.new_btn.clicked.connect(self.new_template)
        
        self.duplicate_btn = QPushButton("Duplicate")  # New duplicate button
        self.duplicate_btn.clicked.connect(self.duplicate_template)
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete_template)
        
        controls_layout.addWidget(self.new_btn)
        controls_layout.addWidget(self.duplicate_btn)  # Add duplicate button
        controls_layout.addWidget(self.delete_btn)
        template_layout.addLayout(controls_layout)
        
        # Second row of controls
        second_controls = QHBoxLayout()
        second_controls.setSpacing(6)
        
        self.wizard_btn = QPushButton("AI Wizard")
        self.wizard_btn.clicked.connect(self.show_wizard)
        self.wizard_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        
        # Import/Export
        self.import_btn = QPushButton("Import")
        self.import_btn.clicked.connect(self.import_template)
        
        self.export_btn = QPushButton("Export")
        self.export_btn.clicked.connect(self.export_template)
        
        second_controls.addWidget(self.wizard_btn)
        second_controls.addWidget(self.import_btn)
        second_controls.addWidget(self.export_btn)
        template_layout.addLayout(second_controls)
        
        template_group.setLayout(template_layout)
        left_layout.addWidget(template_group)
        
        # Template statistics
        stats_group = QGroupBox("Usage Statistics")
        stats_layout = QVBoxLayout()
        self.stats_label = QLabel("Select a template to view statistics")
        stats_layout.addWidget(self.stats_label)
        stats_group.setLayout(stats_layout)
        left_layout.addWidget(stats_group)
        
        # Right panel - Template Editor
        self.right_panel = QWidget()
        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)
        
        # Header with template name
        self.header_label = QLabel("Select or create a template")
        self.header_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
        right_layout.addWidget(self.header_label)
        
        # Tab widget for template components
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.create_basic_info_tab()
        self.create_prompts_tab()
        self.create_bookmarks_tab()
        self.create_advanced_tab()
        self.create_preview_tab()
        
        right_layout.addWidget(self.tab_widget)
        
        # Save button
        self.save_btn = QPushButton("Save Template")
        self.save_btn.clicked.connect(self.save_template)
        self.save_btn.setEnabled(False)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        right_layout.addWidget(self.save_btn)
        
        # Add panels to splitter
        self.splitter.addWidget(self.left_panel)
        self.splitter.addWidget(self.right_panel)
        
        # Set initial splitter sizes (30% left, 70% right)
        total_width = self.width()
        self.splitter.setSizes([int(total_width * 0.3), int(total_width * 0.7)])
        
        # Force update
        self.splitter.update()
        self.left_panel.update()
        self.right_panel.update()
        
        # Ensure the template list is populated immediately
        QApplication.processEvents()

    def create_basic_info_tab(self):
        """Create the Basic Info tab with guidance"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Name field with guidance
        name_group = QGroupBox("Template Name")
        name_layout = QVBoxLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter a descriptive name...")
        self.name_edit.textChanged.connect(self.on_field_changed)
        
        name_help = QLabel("Choose a clear, descriptive name that indicates the template's purpose.")
        name_help.setStyleSheet("color: #666; font-style: italic;")
        
        name_layout.addWidget(self.name_edit)
        name_layout.addWidget(name_help)
        name_group.setLayout(name_layout)
        layout.addWidget(name_group)
        
        # Description field with guidance
        desc_group = QGroupBox("Description")
        desc_layout = QVBoxLayout()
        
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Explain when and how to use this template...")
        self.description_edit.setMaximumHeight(150)
        self.description_edit.textChanged.connect(self.on_field_changed)
        
        desc_help = QLabel("Provide a brief explanation of what this template does and when to use it.")
        desc_help.setStyleSheet("color: #666; font-style: italic;")
        
        desc_example = QLabel("<b>Example:</b> \"Analyzes meeting transcripts to extract action items, decisions, and follow-ups.\"")
        desc_example.setStyleSheet("color: #28a745; font-style: italic;")
        
        desc_layout.addWidget(self.description_edit)
        desc_layout.addWidget(desc_help)
        desc_layout.addWidget(desc_example)
        desc_group.setLayout(desc_layout)
        layout.addWidget(desc_group)
        
        # Add spacer at the bottom
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Basic Info")

    def create_prompts_tab(self):
        """Create the Prompts tab with guidance"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # User Context field with guidance
        user_group = QGroupBox("User Context (WHO)")
        user_layout = QVBoxLayout()
        
        user_help = QLabel("Define your perspective and role. This sets WHO you are in relation to the content.")
        user_help.setStyleSheet("color: #666; font-style: italic;")
        user_layout.addWidget(user_help)
        
        self.user_edit = QTextEdit()
        self.user_edit.setPlaceholderText("As a [your role]...")
        self.user_edit.setMinimumHeight(80)
        self.user_edit.textChanged.connect(self.on_field_changed)
        user_layout.addWidget(self.user_edit)
        
        user_example = QLabel("<b>Example:</b> \"As a project manager reviewing a team meeting...\"")
        user_example.setStyleSheet("color: #28a745; font-style: italic;")
        user_layout.addWidget(user_example)
        
        user_group.setLayout(user_layout)
        layout.addWidget(user_group)
        
        # System Prompt field with guidance
        system_group = QGroupBox("System Prompt (ROLE)")
        system_layout = QVBoxLayout()
        
        system_help = QLabel("Define the AI's behavior and capabilities. This sets the AI's ROLE and approach.")
        system_help.setStyleSheet("color: #666; font-style: italic;")
        system_layout.addWidget(system_help)
        
        self.system_prompt_edit = QTextEdit()
        self.system_prompt_edit.setPlaceholderText("You are an AI assistant that...")
        self.system_prompt_edit.setMinimumHeight(120)
        self.system_prompt_edit.textChanged.connect(self.on_field_changed)
        system_layout.addWidget(self.system_prompt_edit)
        
        system_example = QLabel("<b>Example:</b> \"You are an AI assistant specializing in project management. Your role is to:\n1. Identify action items and owners\n2. Extract key decisions\n3. Highlight risks and issues\"")
        system_example.setStyleSheet("color: #28a745; font-style: italic;")
        system_layout.addWidget(system_example)
        
        system_group.setLayout(system_layout)
        layout.addWidget(system_group)
        
        # Analysis Instructions field with guidance
        template_group = QGroupBox("Analysis Instructions (HOW)")
        template_layout = QVBoxLayout()
        
        template_help = QLabel("Define the specific format and requirements for the analysis. This sets HOW the content should be analyzed.")
        template_help.setStyleSheet("color: #666; font-style: italic;")
        template_layout.addWidget(template_help)
        
        self.template_edit = QTextEdit()
        self.template_edit.setPlaceholderText("Please analyze this content by...")
        self.template_edit.setMinimumHeight(150)
        self.template_edit.textChanged.connect(self.on_field_changed)
        template_layout.addWidget(self.template_edit)
        
        template_example = QLabel("<b>Example:</b> \"Please provide a meeting analysis with these sections:\n1. Action Items (with owners and deadlines)\n2. Decisions Made\n3. Key Discussion Points\"")
        template_example.setStyleSheet("color: #28a745; font-style: italic;")
        template_layout.addWidget(template_example)
        
        template_group.setLayout(template_layout)
        layout.addWidget(template_group)
        
        # Add scrollable area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_content.setLayout(layout)
        scroll_area.setWidget(scroll_content)
        
        tab_layout = QVBoxLayout()
        tab_layout.addWidget(scroll_area)
        tab.setLayout(tab_layout)
        
        self.tab_widget.addTab(tab, "Prompts")

    def create_bookmarks_tab(self):
        """Create the Bookmarks tab with guidance"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Bookmark explanation
        bookmark_help = QLabel("Bookmarks help mark important points in conversations. Templates can include predefined bookmarks relevant to specific conversation types.")
        bookmark_help.setStyleSheet("color: #666; font-style: italic;")
        bookmark_help.setWordWrap(True)
        layout.addWidget(bookmark_help)
        
        # Split into two columns with styling
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(10)  # Add space between columns
        
        # Markers column
        markers_group = QGroupBox("📍 Markers")
        markers_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ccc;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
        """)
        markers_layout = QVBoxLayout()
        
        markers_help = QLabel("Markers are visual indicators in the transcript (e.g., \"[DECISION]\").")
        markers_help.setStyleSheet("color: #666; font-style: italic;")
        markers_help.setWordWrap(True)
        markers_layout.addWidget(markers_help)
        
        self.markers_list = QListWidget()
        self.markers_list.setMinimumHeight(200)
        self.markers_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
                background-color: #f8f9fa;
            }
            QListWidget::item {
                border-bottom: 1px solid #eee;
                padding: 4px;
                margin: 2px 0;
            }
            QListWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
        """)
        markers_layout.addWidget(self.markers_list)
        markers_group.setLayout(markers_layout)
        columns_layout.addWidget(markers_group)
        
        # Voice Commands column
        commands_group = QGroupBox("🎤 Voice Commands")
        commands_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ccc;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
        """)
        commands_layout = QVBoxLayout()
        
        commands_help = QLabel("Voice commands are spoken triggers that create bookmarks (e.g., \"mark decision\").")
        commands_help.setStyleSheet("color: #666; font-style: italic;")
        commands_help.setWordWrap(True)
        commands_layout.addWidget(commands_help)
        
        self.commands_list = QListWidget()
        self.commands_list.setMinimumHeight(200)
        self.commands_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
                background-color: #f8f9fa;
            }
            QListWidget::item {
                border-bottom: 1px solid #eee;
                padding: 4px;
                margin: 2px 0;
            }
            QListWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
        """)
        commands_layout.addWidget(self.commands_list)
        commands_group.setLayout(commands_layout)
        columns_layout.addWidget(commands_group)
        
        layout.addLayout(columns_layout)
        
        # Buttons below both columns with styling
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)  # Add space between buttons
        
        self.add_bookmark_btn = QPushButton("➕ Add")
        self.add_bookmark_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.add_bookmark_btn.clicked.connect(self.add_bookmark)
        
        self.edit_bookmark_btn = QPushButton("✏️ Edit")
        self.edit_bookmark_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.edit_bookmark_btn.clicked.connect(self.edit_bookmark)
        
        self.delete_bookmark_btn = QPushButton("🗑️ Delete")
        self.delete_bookmark_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.delete_bookmark_btn.clicked.connect(self.delete_bookmark)
        
        # Quick Add button with dropdown menu
        self.quick_add_btn = QPushButton("⚡ Quick Add")
        self.quick_add_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #138496;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.quick_add_btn.clicked.connect(self.show_quick_add_menu)
        
        buttons_layout.addWidget(self.add_bookmark_btn)
        buttons_layout.addWidget(self.edit_bookmark_btn)
        buttons_layout.addWidget(self.delete_bookmark_btn)
        buttons_layout.addWidget(self.quick_add_btn)
        
        # Add selection handling for bookmark lists
        self.markers_list.itemSelectionChanged.connect(self.on_bookmark_selection_changed)
        self.commands_list.itemSelectionChanged.connect(self.on_bookmark_selection_changed)
        
        layout.addLayout(buttons_layout)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Bookmarks")

    def create_advanced_tab(self):
        """Create the Advanced tab with guidance"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Curiosity Engine Prompt
        curiosity_group = QGroupBox("Curiosity Engine Prompt")
        curiosity_layout = QVBoxLayout()
        
        curiosity_help = QLabel("Define custom prompt for generating contextual questions. The Curiosity Engine generates questions about the conversation to help uncover additional context.")
        curiosity_help.setStyleSheet("color: #666; font-style: italic;")
        curiosity_help.setWordWrap(True)
        curiosity_layout.addWidget(curiosity_help)
        
        self.curiosity_prompt_edit = QTextEdit()
        self.curiosity_prompt_edit.setPlaceholderText("Custom prompt for the Curiosity Engine...")
        self.curiosity_prompt_edit.setMinimumHeight(200)
        self.curiosity_prompt_edit.textChanged.connect(self.on_field_changed)
        curiosity_layout.addWidget(self.curiosity_prompt_edit)
        
        curiosity_example = QLabel("<b>Tip:</b> Focus on the [CUSTOMIZABLE GUIDELINES] section to specify what types of questions should be generated.")
        curiosity_example.setStyleSheet("color: #28a745; font-style: italic;")
        curiosity_layout.addWidget(curiosity_example)
        
        curiosity_group.setLayout(curiosity_layout)
        layout.addWidget(curiosity_group)
        
        # Conversation Mode
        mode_group = QGroupBox("Conversation Mode")
        mode_layout = QVBoxLayout()
        
        mode_help = QLabel("Select how the Conversation Compass should work with this template.")
        mode_help.setStyleSheet("color: #666; font-style: italic;")
        mode_help.setWordWrap(True)
        mode_layout.addWidget(mode_help)
        
        mode_options = QHBoxLayout()
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["tracking", "guided"])
        self.mode_combo.setToolTip("tracking: follows conversation flow, guided: suggests paths")
        self.mode_combo.currentTextChanged.connect(self.on_field_changed)
        
        mode_options.addWidget(QLabel("Mode:"))
        mode_options.addWidget(self.mode_combo)
        mode_options.addStretch()
        
        mode_layout.addLayout(mode_options)
        
        # Mode explanation
        mode_explanation = QLabel("""
        <b>Tracking Mode:</b> Follows the natural flow of conversation without predetermined paths. Best for open discussions, brainstorming, or exploratory conversations.<br><br>
        <b>Guided Mode:</b> Helps direct the conversation toward specific goals with suggested paths. Best for interviews, negotiations, or structured discussions.
        """)
        mode_explanation.setStyleSheet("color: #666; font-style: italic;")
        mode_explanation.setWordWrap(True)
        mode_layout.addWidget(mode_explanation)
        
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)
        
        # Visualization Settings
        vis_group = QGroupBox("Visualization Settings")
        vis_layout = QVBoxLayout()
        
        vis_help = QLabel("Configure how conversation trees and other visualizations appear.")
        vis_help.setStyleSheet("color: #666; font-style: italic;")
        vis_help.setWordWrap(True)
        vis_layout.addWidget(vis_help)
        
        layout_options = QHBoxLayout()
        layout_options.addWidget(QLabel("Default Layout:"))
        
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(["radial", "hierarchical", "force-directed"])
        self.layout_combo.setToolTip("radial: circular layout, hierarchical: tree layout, force-directed: dynamic layout")
        layout_options.addWidget(self.layout_combo)
        layout_options.addStretch()
        
        vis_layout.addLayout(layout_options)
        
        # Highlight options
        highlight_options = QVBoxLayout()
        
        self.highlight_decisions = QCheckBox("Highlight decision points")
        self.highlight_decisions.setChecked(True)
        self.highlight_decisions.setToolTip("Visually emphasize decision points in the conversation tree")
        
        self.highlight_questions = QCheckBox("Highlight questions")
        self.highlight_questions.setChecked(True)
        self.highlight_questions.setToolTip("Visually emphasize questions in the conversation tree")
        
        highlight_options.addWidget(self.highlight_decisions)
        highlight_options.addWidget(self.highlight_questions)
        
        vis_layout.addLayout(highlight_options)
        
        vis_group.setLayout(vis_layout)
        layout.addWidget(vis_group)
        
        # Add scrollable area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_content.setLayout(layout)
        scroll_area.setWidget(scroll_content)
        
        tab_layout = QVBoxLayout()
        tab_layout.addWidget(scroll_area)
        tab.setLayout(tab_layout)
        
        self.tab_widget.addTab(tab, "Advanced")

    def create_preview_tab(self):
        """Create a preview tab to show how the template will look"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Preview header
        preview_header = QLabel("Template Preview")
        preview_header.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(preview_header)
        
        # Preview description
        preview_desc = QLabel("This shows how your template will look when applied to a transcript.")
        preview_desc.setStyleSheet("color: #666; font-style: italic;")
        preview_desc.setWordWrap(True)
        layout.addWidget(preview_desc)
        
        # Preview content
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMinimumHeight(400)
        layout.addWidget(self.preview_text)
        
        # Update preview button
        update_btn = QPushButton("Update Preview")
        update_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        update_btn.clicked.connect(self.update_preview)
        layout.addWidget(update_btn)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Preview")

    def update_preview(self):
        """Update the template preview based on current values"""
        try:
            # Get current template values
            name = self.name_edit.text()
            description = self.description_edit.toPlainText()
            user_prompt = self.user_edit.toPlainText()
            system_prompt = self.system_prompt_edit.toPlainText()
            template_prompt = self.template_edit.toPlainText()
            
            # Get bookmarks
            bookmarks = []
            for i in range(self.markers_list.count()):
                bookmark = self.markers_list.item(i).data(Qt.ItemDataRole.UserRole)
                bookmarks.append(bookmark)
            
            # Create preview HTML
            preview_html = f"""
            <h2>Template: {name}</h2>
            <p><i>{description}</i></p>
            
            <h3>User Context</h3>
            <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px;">
                {user_prompt.replace('\n', '<br>')}
            </div>
            
            <h3>System Prompt</h3>
            <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px;">
                {system_prompt.replace('\n', '<br>')}
            </div>
            
            <h3>Analysis Instructions</h3>
            <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px;">
                {template_prompt.replace('\n', '<br>')}
            </div>
            """
            
            # Add bookmarks if available
            if bookmarks:
                preview_html += """
                <h3>Bookmarks</h3>
                <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px;">
                    <ul>
                """
                
                for bookmark in bookmarks:
                    # Add icon based on bookmark type
                    icon = "📌"
                    if bookmark.get("is_user_speaking"):
                        icon = "👤"
                    elif bookmark.get("is_decision_point"):
                        icon = "🔍"
                    elif bookmark.get("is_action_item"):
                        icon = "✅"
                    
                    preview_html += f"""
                    <li><b>{icon} {bookmark['name']}</b> - {bookmark.get('description', '')}</li>
                    """
                    
                preview_html += """
                    </ul>
                </div>
                """
            
            # Add sample output
            preview_html += """
            <h3>Sample Output</h3>
            <div style="background-color: #e9f7ef; padding: 10px; border-radius: 5px; border-left: 4px solid #28a745;">
                <p><b>Analysis Results:</b></p>
                <p>This is where the AI-generated analysis would appear, following the format specified in your Analysis Instructions.</p>
            </div>
            """
            
            # Set preview text
            self.preview_text.setHtml(preview_html)
            
        except Exception as e:
            self.preview_text.setHtml(f"<p>Error generating preview: {str(e)}</p>")

    def filter_templates(self):
        """Filter templates based on search text"""
        search_text = self.search_edit.text().lower()
        
        for i in range(self.template_list.count()):
            item = self.template_list.item(i)
            template = item.data(Qt.ItemDataRole.UserRole)
            
            # Get description, handling both string and dict cases
            description = template.get("description", "")
            if isinstance(description, dict):
                # Convert dict to string for searching
                description_text = " ".join(str(v) for v in description.values())
            else:
                description_text = str(description)
            
            # Check if template name or description contains search text
            if (search_text in template["name"].lower() or 
                search_text in description_text.lower()):
                item.setHidden(False)
            else:
                item.setHidden(True)

    def on_bookmark_selection_changed(self):
        """Handle bookmark selection changes"""
        # Check if a marker is selected
        marker_selected = self.markers_list.currentItem() is not None
        
        # Check if a command is selected
        command_selected = self.commands_list.currentItem() is not None
        
        # Enable/disable edit and delete buttons based on selection
        self.edit_bookmark_btn.setEnabled(marker_selected or command_selected)
        self.delete_bookmark_btn.setEnabled(marker_selected or command_selected)

    def update_template_stats(self, template_name):
        """Update the template statistics display"""
        if not template_name:
            self.stats_label.setText("Select a template to view statistics")
            return
            
        # Get template statistics from LangChain service
        stats = None
        parent = self.parent()
        if parent and hasattr(parent, 'app') and parent.app and hasattr(parent.app, 'langchain_service'):
            stats = parent.app.langchain_service.get_template_stats(template_name)
            
        if not stats:
            self.stats_label.setText(f"No usage statistics available for '{template_name}'")
            return
            
        # Format statistics
        stats_text = f"""
        <b>Template:</b> {template_name}<br>
        <b>Uses:</b> {stats.get('uses', 0)}<br>
        <b>First Used:</b> {stats.get('first_used', 'Never')}<br>
        <b>Last Used:</b> {stats.get('last_used', 'Never')}<br>
        <b>Avg. Response Time:</b> {stats.get('avg_response_time', 0):.2f}s<br>
        <b>Avg. Response Length:</b> {stats.get('avg_length', 0)} chars
        """
        
        self.stats_label.setText(stats_text)
        
    def on_list_selection_changed(self, row):
        """Handle template list selection when a row is selected"""
        if row < 0:
            return
            
        # Reset styling on all fields
        for widget in [self.name_edit, self.description_edit, self.user_edit, 
                      self.template_edit, self.system_prompt_edit, 
                      self.curiosity_prompt_edit]:
            widget.setStyleSheet("")
            
        # Clear and disable bookmark lists
        self.markers_list.clear()
        self.commands_list.clear()
        self.edit_bookmark_btn.setEnabled(False)
        self.delete_bookmark_btn.setEnabled(False)
            
        current_item = self.template_list.item(row)
        if not current_item:
            return
            
        template = current_item.data(Qt.ItemDataRole.UserRole)
        if not template:
            return
            
        # Update header with template name
        self.header_label.setText(template["name"])
            
        # Set basic template fields
        self.name_edit.setText(template["name"])
        
        # Handle description that might be a dict or string
        description = template.get('description', '')
        if isinstance(description, dict):
            # Convert dict to formatted string
            desc_text = "\n".join([
                f"{key}: {value}"
                for key, value in description.items()
            ])
            self.description_edit.setText(desc_text)
        else:
            self.description_edit.setText(str(description))
            
        # Handle user field that might be a dict or string
        user = template.get('user_prompt', template.get('user', ''))
        if isinstance(user, dict):
            user_text = "\n".join([
                f"{key}: {value}"
                for key, value in user.items()
            ])
            self.user_edit.setText(user_text)
        else:
            self.user_edit.setText(str(user))
            
        # Handle system prompt that might be a dict or string
        system_prompt = template.get('system_prompt', '')
        if isinstance(system_prompt, dict):
            prompt_text = system_prompt.get('content', '')
            self.system_prompt_edit.setText(prompt_text)
        else:
            self.system_prompt_edit.setText(str(system_prompt))
            
        # Handle template that might be a dict or string
        template_content = template.get('template_prompt', template.get('template', ''))
        if isinstance(template_content, dict):
            template_text = "\n".join([
                f"{key}: {value}"
                for key, value in template_content.items()
            ])
            self.template_edit.setText(template_text)
        else:
            self.template_edit.setText(str(template_content))
        
        # Store original values for change tracking
        self.original_values = {
            'name': template["name"],
            'description': template.get("description", ""),
            'user': user,
            'template': template_content,
            'system_prompt': system_prompt if isinstance(system_prompt, str) else system_prompt.get('content', ''),
            'curiosity_prompt': template.get("curiosity_prompt", ""),
            'conversation_mode': template.get("conversation_mode", "tracking")
        }
        
        # Set curiosity prompt
        self.curiosity_prompt_edit.setText(template.get("curiosity_prompt", ""))
        
        # Set conversation mode
        mode = template.get("conversation_mode", "tracking")
        index = self.mode_combo.findText(mode)
        if index >= 0:
            self.mode_combo.setCurrentIndex(index)
        
        # Set visualization settings if available
        vis_settings = template.get("visualization", {})
        if vis_settings:
            # Set layout
            layout_type = vis_settings.get("default_layout", "radial")
            layout_index = self.layout_combo.findText(layout_type)
            if layout_index >= 0:
                self.layout_combo.setCurrentIndex(layout_index)
                
            # Set checkboxes
            self.highlight_decisions.setChecked(vis_settings.get("highlight_decisions", True))
            self.highlight_questions.setChecked(vis_settings.get("highlight_questions", True))
        
        # Load bookmarks into appropriate lists
        self.markers_list.clear()
        self.commands_list.clear()
        
        for bookmark in template.get("bookmarks", []):
            display_text = f"{bookmark['name']}\n[{bookmark.get('key_shortcut', '')}]"
            
            # Add special indicators
            special_indicators = []
            if bookmark.get("is_user_speaking"):
                special_indicators.append("👤")
            if bookmark.get("is_decision_point"):
                special_indicators.append("🔍")
            if bookmark.get("is_action_item"):
                special_indicators.append("✅")
                
            if special_indicators:
                display_text += f" {' '.join(special_indicators)}"
            
            if bookmark.get("bookmark_type") == "marker":
                display_text += f"\n→ {bookmark.get('content', '')[:30]}..."
                item = QListWidgetItem(display_text)
                item.setData(Qt.ItemDataRole.UserRole, bookmark)
                
                # Add special styling for special bookmark types
                if bookmark.get("is_user_speaking"):
                    item.setBackground(QColor(230, 247, 255))  # Light blue
                elif bookmark.get("is_decision_point"):
                    item.setBackground(QColor(255, 243, 224))  # Light orange
                elif bookmark.get("is_action_item"):
                    item.setBackground(QColor(232, 245, 233))  # Light green
                    
                self.markers_list.addItem(item)
            else:  # voice_command
                display_text += f"\n📢 \"{bookmark.get('voice_trigger', '')}\""
                item = QListWidgetItem(display_text)
                item.setData(Qt.ItemDataRole.UserRole, bookmark)
                self.commands_list.addItem(item)
        
        # Update template stats
        self.update_template_stats(template["name"])
            
        # Enable/disable bookmark buttons based on template protection
        is_protected = template["name"].startswith("*")
        self.add_bookmark_btn.setEnabled(not is_protected)
        self.edit_bookmark_btn.setEnabled(not is_protected)
        self.delete_bookmark_btn.setEnabled(not is_protected)
        self.quick_add_btn.setEnabled(not is_protected)
        
        # Reset unsaved changes flag
        self.has_unsaved_changes = False
        self.save_btn.setEnabled(False)
        
        # Update preview
        self.update_preview()
        
    def on_field_changed(self):
        """Handle field changes to enable save button"""
        self.has_unsaved_changes = True
        self.save_btn.setEnabled(True)
        
    def load_templates(self):
        """Load templates from service"""
        try:
            # Clear template list
            self.template_list.clear()
            
            # Get templates from service
            if not hasattr(self, 'app') or not self.app:
                # Try to get app reference from parent
                if hasattr(self, 'parent') and self.parent() and hasattr(self.parent(), 'app') and self.parent().app:
                    self.app = self.parent().app
                    print(f"Retrieved app reference from parent: {self.app}")
                else:
                    print("No app reference available from self or parent")
                    raise ValueError("No app reference available")
                    
            print(f"Using app reference: {self.app}")
            
            if not hasattr(self.app, 'langchain_service'):
                print(f"App has no langchain_service attribute")
                raise ValueError("App has no langchain_service attribute")
                
            print(f"Using langchain_service: {self.app.langchain_service}")
            
            service = self.app.langchain_service
            self.templates = service.get_available_templates()
            
            # Check if templates were loaded
            if not self.templates:
                print("Warning: No templates returned from get_available_templates()")
                # Try to load default templates
                if hasattr(service, 'template_manager') and hasattr(service.template_manager, 'get_default_templates'):
                    print("Attempting to load default templates")
                    self.templates = service.template_manager.get_default_templates()
                else:
                    print("No default templates available")
                    self.templates = []
            
            print(f"Loaded {len(self.templates)} templates")
            
            # Add templates to list
            for template in self.templates:
                item = QListWidgetItem(template["name"])
                item.setData(Qt.ItemDataRole.UserRole, template)
                
                # Add special styling for built-in templates
                if template["name"].startswith("*"):
                    item.setBackground(QColor(240, 240, 240))
                    
                self.template_list.addItem(item)
                
            print(f"Added {self.template_list.count()} templates to list")
                
        except Exception as e:
            error_msg = f"Failed to load templates: {str(e)}"
            print(f"ERROR: {error_msg}")  # Print to console for debugging
            import traceback
            traceback.print_exc()  # Print full traceback
            QMessageBox.critical(self, "Error", error_msg)
            
    def new_template(self):
        """Create a new template"""
        # Check for unsaved changes
        if self.has_unsaved_changes:
            response = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save them first?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            
            if response == QMessageBox.StandardButton.Cancel:
                return
            elif response == QMessageBox.StandardButton.Yes:
                self.save_template()
                
        # Create new template
        template = {
            "name": "New Template",
            "description": "Description of the new template",
            "user_prompt": "As a user reviewing this content...",
            "template_prompt": "Please analyze this content by...",
            "system_prompt": "You are an AI assistant analyzing content...",
            "bookmarks": [],
            "curiosity_prompt": """[SYSTEM INSTRUCTIONS - DO NOT MODIFY THIS SECTION]
You are an expert active listener analyzing conversation transcripts. 
Generate 2-3 insightful questions that would help understand the context better.

[QUESTION TYPES - DO NOT MODIFY THESE TYPES]
Question types:
- YES_NO: Simple yes/no questions
- MULTIPLE_CHOICE: Questions with predefined options (provide 3-4 choices)
- MULTIPLE_CHOICE_FILL: Multiple choice with an "other" option (provide 3-4 choices)
- SPEAKER_IDENTIFICATION: Questions about who said specific statements
- MEETING_TYPE: Questions about the type of meeting/conversation

[CUSTOMIZABLE GUIDELINES - YOU CAN MODIFY THIS SECTION]
Generate questions that:
- Are relevant to the transcript content
- Help clarify important points
- Uncover underlying context
- Are concise and clear
- Have meaningful multiple choice options when applicable

[OUTPUT FORMAT - DO NOT MODIFY THIS SECTION]
Return a list of questions in the specified format.""",
            "conversation_mode": "tracking",
            "visualization": {
                "default_layout": "radial",
                "node_color_scheme": "default",
                "highlight_decisions": True,
                "highlight_questions": True,
                "expand_level": 1
            },
            "version": 2
        }
        
        # Add to list
        item = QListWidgetItem(template["name"])
        item.setData(Qt.ItemDataRole.UserRole, template)
        self.template_list.addItem(item)
        
        # Select new template
        self.template_list.setCurrentItem(item)
        
        # Set focus to name field
        self.name_edit.setFocus()
        self.name_edit.selectAll()
        
        # Set unsaved changes flag
        self.has_unsaved_changes = True
        self.save_btn.setEnabled(True)
        
    def show_wizard(self):
        """Show template wizard dialog"""
        wizard = TemplateWizardDialog(self)
        if wizard.exec():
            # Get generated templates
            templates = wizard.get_generated_templates()
            
            if templates:
                # Add templates to list
                for template in templates:
                    # Check if template already exists
                    exists = False
                    for i in range(self.template_list.count()):
                        item = self.template_list.item(i)
                        if item.text() == template["name"]:
                            exists = True
                            break
                            
                    if not exists:
                        item = QListWidgetItem(template["name"])
                        item.setData(Qt.ItemDataRole.UserRole, template)
                        self.template_list.addItem(item)
                        
                # Select first template
                if templates:
                    for i in range(self.template_list.count()):
                        item = self.template_list.item(i)
                        if item.text() == templates[0]["name"]:
                            self.template_list.setCurrentItem(item)
                            break
                            
                # Save templates
                service = self.parent().app.langchain_service
                for template in templates:
                    service.save_template(template)
                    
                QMessageBox.information(
                    self,
                    "Templates Created",
                    f"Successfully created {len(templates)} templates"
                )
                
    def delete_template(self):
        """Delete the selected template"""
        current_item = self.template_list.currentItem()
        if not current_item:
            return
            
        template = current_item.data(Qt.ItemDataRole.UserRole)
        
        # Check if template is built-in
        if template["name"].startswith("*"):
            QMessageBox.warning(
                self,
                "Cannot Delete",
                "Built-in templates cannot be deleted"
            )
            return
            
        # Confirm deletion
        response = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the template '{template['name']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if response == QMessageBox.StandardButton.No:
            return
            
        # Delete template
        service = self.parent().app.langchain_service
        if service.delete_template(template["name"]):
            # Remove from list
            row = self.template_list.row(current_item)
            self.template_list.takeItem(row)
            
            QMessageBox.information(
                self,
                "Template Deleted",
                f"Template '{template['name']}' deleted successfully"
            )
        else:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to delete template '{template['name']}'"
            )
            
    def import_template(self):
        """Import a template from a JSON file"""
        from PyQt6.QtWidgets import QFileDialog
        
        # Get file path
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Template",
            "",
            "JSON Files (*.json)"
        )
        
        if not file_path:
            return
            
        try:
            # Load template from file
            with open(file_path, 'r') as f:
                template = json.load(f)
                
            # Validate template
            if not isinstance(template, dict):
                raise ValueError("Invalid template format: not a JSON object")
                
            required_fields = ["name", "user_prompt", "template_prompt", "system_prompt"]
            for field in required_fields:
                if field not in template and field.replace("_prompt", "") not in template:
                    raise ValueError(f"Invalid template format: missing required field '{field}'")
                    
            # Add version if not present
            if "version" not in template:
                template["version"] = 2
                
            # Add to list
            item = QListWidgetItem(template["name"])
            item.setData(Qt.ItemDataRole.UserRole, template)
            self.template_list.addItem(item)
            
            # Select imported template
            self.template_list.setCurrentItem(item)
            
            # Save template
            parent = self.parent()
            if not parent or not hasattr(parent, 'app') or not parent.app:
                raise ValueError("No app reference available")
                
            service = parent.app.langchain_service
            if service.save_template(template):
                QMessageBox.information(
                    self,
                    "Template Imported",
                    f"Template '{template['name']}' imported successfully"
                )
            else:
                raise ValueError("Failed to save imported template")
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Import Error",
                f"Failed to import template: {str(e)}"
            )
            
    def export_template(self):
        """Export the selected template to a JSON file"""
        current_item = self.template_list.currentItem()
        if not current_item:
            return
            
        template = current_item.data(Qt.ItemDataRole.UserRole)
        
        from PyQt6.QtWidgets import QFileDialog
        
        # Get file path
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Template",
            f"{template['name'].replace('*', '')}.json",
            "JSON Files (*.json)"
        )
        
        if not file_path:
            return
            
        try:
            # Save template to file
            with open(file_path, 'w') as f:
                json.dump(template, f, indent=2)
                
            QMessageBox.information(
                self,
                "Template Exported",
                f"Template '{template['name']}' exported successfully"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"Failed to export template: {str(e)}"
            )
            
    def add_bookmark(self):
        """Add a new bookmark"""
        dialog = BookmarkDialog(self)
        if dialog.exec():
            bookmark = dialog.get_bookmark()
            
            # Add to appropriate list
            if bookmark["bookmark_type"] == "marker":
                display_text = f"{bookmark['name']}\n[{bookmark.get('key_shortcut', '')}]"
                
                # Add special indicators
                special_indicators = []
                if bookmark.get("is_user_speaking"):
                    special_indicators.append("👤")
                if bookmark.get("is_decision_point"):
                    special_indicators.append("🔍")
                if bookmark.get("is_action_item"):
                    special_indicators.append("✅")
                    
                if special_indicators:
                    display_text += f" {' '.join(special_indicators)}"
                    
                display_text += f"\n→ {bookmark.get('content', '')[:30]}..."
                item = QListWidgetItem(display_text)
                item.setData(Qt.ItemDataRole.UserRole, bookmark)
                
                # Add special styling for special bookmark types
                if bookmark.get("is_user_speaking"):
                    item.setBackground(QColor(230, 247, 255))  # Light blue
                elif bookmark.get("is_decision_point"):
                    item.setBackground(QColor(255, 243, 224))  # Light orange
                elif bookmark.get("is_action_item"):
                    item.setBackground(QColor(232, 245, 233))  # Light green
                    
                self.markers_list.addItem(item)
            else:  # voice_command
                display_text = f"{bookmark['name']}\n[{bookmark.get('key_shortcut', '')}]"
                display_text += f"\n📢 \"{bookmark.get('voice_trigger', '')}\""
                item = QListWidgetItem(display_text)
                item.setData(Qt.ItemDataRole.UserRole, bookmark)
                self.commands_list.addItem(item)
                
            # Set unsaved changes flag
            self.has_unsaved_changes = True
            self.save_btn.setEnabled(True)
            
    def edit_bookmark(self):
        """Edit the selected bookmark"""
        # Check which list has selection
        if self.markers_list.currentItem():
            current_item = self.markers_list.currentItem()
            current_list = self.markers_list
        elif self.commands_list.currentItem():
            current_item = self.commands_list.currentItem()
            current_list = self.commands_list
        else:
            return
            
        bookmark = current_item.data(Qt.ItemDataRole.UserRole)
        
        dialog = BookmarkDialog(self, bookmark)
        if dialog.exec():
            updated_bookmark = dialog.get_bookmark()
            
            # Remove from current list
            row = current_list.row(current_item)
            current_list.takeItem(row)
            
            # Add to appropriate list
            if updated_bookmark["bookmark_type"] == "marker":
                display_text = f"{updated_bookmark['name']}\n[{updated_bookmark.get('key_shortcut', '')}]"
                
                # Add special indicators
                special_indicators = []
                if updated_bookmark.get("is_user_speaking"):
                    special_indicators.append("👤")
                if updated_bookmark.get("is_decision_point"):
                    special_indicators.append("🔍")
                if updated_bookmark.get("is_action_item"):
                    special_indicators.append("✅")
                    
                if special_indicators:
                    display_text += f" {' '.join(special_indicators)}"
                    
                display_text += f"\n→ {updated_bookmark.get('content', '')[:30]}..."
                item = QListWidgetItem(display_text)
                item.setData(Qt.ItemDataRole.UserRole, updated_bookmark)
                
                # Add special styling for special bookmark types
                if updated_bookmark.get("is_user_speaking"):
                    item.setBackground(QColor(230, 247, 255))  # Light blue
                elif updated_bookmark.get("is_decision_point"):
                    item.setBackground(QColor(255, 243, 224))  # Light orange
                elif updated_bookmark.get("is_action_item"):
                    item.setBackground(QColor(232, 245, 233))  # Light green
                    
                self.markers_list.addItem(item)
            else:  # voice_command
                display_text = f"{updated_bookmark['name']}\n[{updated_bookmark.get('key_shortcut', '')}]"
                display_text += f"\n📢 \"{updated_bookmark.get('voice_trigger', '')}\""
                item = QListWidgetItem(display_text)
                item.setData(Qt.ItemDataRole.UserRole, updated_bookmark)
                self.commands_list.addItem(item)
                
            # Set unsaved changes flag
            self.has_unsaved_changes = True
            self.save_btn.setEnabled(True)
            
    def delete_bookmark(self):
        """Delete the selected bookmark"""
        # Check which list has selection
        if self.markers_list.currentItem():
            current_item = self.markers_list.currentItem()
            current_list = self.markers_list
        elif self.commands_list.currentItem():
            current_item = self.commands_list.currentItem()
            current_list = self.commands_list
        else:
            return
            
        # Remove from list
        row = current_list.row(current_item)
        current_list.takeItem(row)
        
        # Set unsaved changes flag
        self.has_unsaved_changes = True
        self.save_btn.setEnabled(True)
        
    def duplicate_template(self):
        """Create a duplicate of the selected template"""
        current_item = self.template_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Template Selected", "Please select a template to duplicate.")
            return
            
        template = current_item.data(Qt.ItemDataRole.UserRole)
        
        # Create a deep copy of the template
        import copy
        duplicate = copy.deepcopy(template)
        
        # Modify the name to indicate it's a copy
        duplicate["name"] = f"{template['name']} (Copy)"
        
        # Add to list
        item = QListWidgetItem(duplicate["name"])
        item.setData(Qt.ItemDataRole.UserRole, duplicate)
        self.template_list.addItem(item)
        
        # Select the new item
        self.template_list.setCurrentItem(item)
        
        # Set focus to name field for easy renaming
        self.name_edit.setFocus()
        self.name_edit.selectAll()
        
        # Mark as unsaved
        self.has_unsaved_changes = True
        self.save_btn.setEnabled(True)
        
        QMessageBox.information(
            self,
            "Template Duplicated",
            f"Created a copy of '{template['name']}'. You can now modify and save it."
        )
        
    def show_quick_add_menu(self):
        """Show quick add menu for common bookmark types"""
        menu = QMenu(self)
        
        # User Speaking bookmark
        user_speaking_action = menu.addAction("👤 User Speaking")
        user_speaking_action.triggered.connect(lambda: self.quick_add_bookmark("user_speaking"))
        
        # Decision Point bookmark
        decision_action = menu.addAction("🔍 Decision Point")
        decision_action.triggered.connect(lambda: self.quick_add_bookmark("decision_point"))
        
        # Action Item bookmark
        action_item_action = menu.addAction("✅ Action Item")
        action_item_action.triggered.connect(lambda: self.quick_add_bookmark("action_item"))
        
        # New Topic bookmark
        new_topic_action = menu.addAction("📌 New Topic")
        new_topic_action.triggered.connect(lambda: self.quick_add_bookmark("new_topic"))
        
        # Show the menu
        menu.exec(self.quick_add_btn.mapToGlobal(self.quick_add_btn.rect().bottomLeft()))
        
    def save_template(self):
        """Save current template"""
        try:
            # Validate all required fields
            validation_errors = []
            
            name = self.name_edit.text().strip()
            if not name:
                validation_errors.append("Template name is required")
            elif len(name) < 3:
                validation_errors.append("Template name must be at least 3 characters")
                
            description = self.description_edit.toPlainText().strip()
            if not description:
                validation_errors.append("Description is required")
                
            user_prompt = self.user_edit.toPlainText().strip()
            if not user_prompt:
                validation_errors.append("User prompt is required")
                
            template_prompt = self.template_edit.toPlainText().strip()
            if not template_prompt:
                validation_errors.append("Template instructions are required")
                
            system_prompt = self.system_prompt_edit.toPlainText().strip()
            if not system_prompt:
                validation_errors.append("System prompt is required")
                
            # Curiosity prompt is optional, no validation needed
            
            # Conversation mode validation
            conversation_mode = self.mode_combo.currentText()
            if conversation_mode not in ["tracking", "guided"]:
                validation_errors.append("Conversation mode must be 'tracking' or 'guided'")
                
            if validation_errors:
                QMessageBox.warning(
                    self,
                    "Validation Error",
                    "Please correct the following:\n• " + "\n• ".join(validation_errors)
                )
                return

            # Collect bookmarks from both lists
            bookmarks = []
            # Add markers
            for i in range(self.markers_list.count()):
                item = self.markers_list.item(i)
                bookmarks.append(item.data(Qt.ItemDataRole.UserRole))
            # Add voice commands
            for i in range(self.commands_list.count()):
                item = self.commands_list.item(i)
                bookmarks.append(item.data(Qt.ItemDataRole.UserRole))

            # Collect visualization settings
            visualization = {
                "default_layout": self.layout_combo.currentText(),
                "node_color_scheme": "default",  # Default for now
                "highlight_decisions": self.highlight_decisions.isChecked(),
                "highlight_questions": self.highlight_questions.isChecked(),
                "expand_level": 1  # Default for now
            }

            template = {
                "name": name,
                "description": description,
                "user_prompt": user_prompt,
                "template_prompt": template_prompt,
                "system_prompt": system_prompt,
                "bookmarks": bookmarks,
                "curiosity_prompt": self.curiosity_prompt_edit.toPlainText().strip(),
                "conversation_mode": self.mode_combo.currentText(),
                "visualization": visualization,
                "version": 2  # Set version to current format
            }

            # Debug output
            print(f"Attempting to save template: {name}")
            print(f"Template data: {template.keys()}")
            
            # Print template structure for debugging
            import json
            print(f"Template structure: {json.dumps(template, indent=2, default=str)}")
            
            # Save template
            success = False
            if hasattr(self, 'template_manager') and self.template_manager:
                # Use directly available template manager
                print(f"Saving template using template_manager: {self.template_manager}")
                if hasattr(self.template_manager, 'save_template'):
                    try:
                        # Create a Template object if the save_template method expects one
                        from services.template_manager import Template
                        template_obj = Template(
                            name=template["name"],
                            description=template["description"],
                            user_prompt=template["user_prompt"],
                            template_prompt=template["template_prompt"],
                            system_prompt=template["system_prompt"],
                            bookmarks=template["bookmarks"],
                            curiosity_prompt=template["curiosity_prompt"],
                            conversation_mode=template["conversation_mode"],
                            visualization=template["visualization"],
                            version=template["version"]
                        )
                        success = self.template_manager.save_template(template_obj)
                        print(f"Template manager save result: {success}")
                    except ImportError:
                        # If Template class is not available, try with dictionary
                        try:
                            success = self.template_manager.save_template(template)
                            print(f"Template manager save result with dict: {success}")
                        except Exception as dict_error:
                            print(f"Template manager save error with dict: {str(dict_error)}")
                            import traceback
                            traceback.print_exc()
                            raise
                    except Exception as tm_error:
                        print(f"Template manager save error: {str(tm_error)}")
                        import traceback
                        traceback.print_exc()
                        raise
                else:
                    error_msg = "template_manager has no save_template method"
                    print(f"Error: {error_msg}")
                    raise AttributeError(error_msg)
            elif self.parent() and hasattr(self.parent(), 'app') and self.parent().app and hasattr(self.parent().app, 'langchain_service'):
                # Use parent's app's langchain service
                service = self.parent().app.langchain_service
                print(f"Saving template using langchain_service: {service}")
                if hasattr(service, 'save_template'):
                    try:
                        # Try with Template object first
                        try:
                            from services.template_manager import Template
                            template_obj = Template(
                                name=template["name"],
                                description=template["description"],
                                user_prompt=template["user_prompt"],
                                template_prompt=template["template_prompt"],
                                system_prompt=template["system_prompt"],
                                bookmarks=template["bookmarks"],
                                curiosity_prompt=template["curiosity_prompt"],
                                conversation_mode=template["conversation_mode"],
                                visualization=template["visualization"],
                                version=template["version"]
                            )
                            success = service.save_template(template_obj)
                        except ImportError:
                            # Fall back to dictionary if Template class not available
                            success = service.save_template(template)
                        print(f"LangChain service save result: {success}")
                    except Exception as lc_error:
                        print(f"LangChain service save error: {str(lc_error)}")
                        import traceback
                        traceback.print_exc()
                        raise
                else:
                    error_msg = "langchain_service has no save_template method"
                    print(f"Error: {error_msg}")
                    raise AttributeError(error_msg)
            else:
                error_msg = "No template manager or langchain service available"
                print(f"Error: {error_msg}")
                raise ValueError(error_msg)
                
            if success:
                print("Template saved successfully, now reloading templates")
                # Force reload templates
                reload_success = False
                if hasattr(self, 'template_manager') and self.template_manager and hasattr(self.template_manager, 'reload_templates'):
                    print("Reloading templates via template_manager.reload_templates()")
                    try:
                        self.template_manager.reload_templates()
                        reload_success = True
                    except Exception as reload_error:
                        print(f"Error reloading templates via template_manager: {str(reload_error)}")
                        import traceback
                        traceback.print_exc()
                elif hasattr(self.parent(), 'app') and self.parent().app and hasattr(self.parent().app, 'langchain_service') and hasattr(self.parent().app.langchain_service, 'template_manager') and hasattr(self.parent().app.langchain_service.template_manager, 'reload_templates'):
                    print("Reloading templates via langchain_service.template_manager.reload_templates()")
                    try:
                        self.parent().app.langchain_service.template_manager.reload_templates()
                        reload_success = True
                    except Exception as reload_error:
                        print(f"Error reloading templates via langchain_service: {str(reload_error)}")
                        import traceback
                        traceback.print_exc()
                else:
                    # Fallback to recreating the template manager
                    print("Creating new TemplateManager instance")
                    try:
                        from services.template_manager import TemplateManager
                        self.parent().app.langchain_service.template_manager = TemplateManager()
                        reload_success = True
                    except Exception as new_tm_error:
                        print(f"Error creating new TemplateManager: {str(new_tm_error)}")
                        import traceback
                        traceback.print_exc()
                
                # Notify any dependent components that templates have changed
                if hasattr(self.parent(), 'app') and self.parent().app and hasattr(self.parent().app, 'notify_template_change'):
                    print("Notifying app of template change")
                    try:
                        self.parent().app.notify_template_change()
                    except Exception as notify_error:
                        print(f"Error notifying template change: {str(notify_error)}")
                        import traceback
                        traceback.print_exc()
                
                # Refresh the template list
                print("Refreshing template list")
                try:
                    self.load_templates()  # Refresh the list
                except Exception as load_error:
                    print(f"Error loading templates: {str(load_error)}")
                    import traceback
                    traceback.print_exc()
                
                # Select the newly saved template
                try:
                    for i in range(self.template_list.count()):
                        item = self.template_list.item(i)
                        template_data = item.data(Qt.ItemDataRole.UserRole)
                        if template_data["name"] == name:
                            self.template_list.setCurrentItem(item)
                            break
                except Exception as select_error:
                    print(f"Error selecting template: {str(select_error)}")
                    import traceback
                    traceback.print_exc()
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"Template '{name}' saved successfully"
                )
                
                # Reset unsaved changes flag
                self.has_unsaved_changes = False
                self.save_btn.setEnabled(False)
            else:
                error_msg = "Failed to save template (save_template returned False)"
                print(f"Error: {error_msg}")
                raise Exception(error_msg)

        except Exception as e:
            error_msg = f"Failed to save template: {str(e)}"
            print(f"ERROR: {error_msg}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", error_msg)
            
    def closeEvent(self, event):
        """Handle dialog close event"""
        if self.has_unsaved_changes:
            response = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save them first?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            
            if response == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
            elif response == QMessageBox.StandardButton.Yes:
                self.save_template()
        
        # If this is a standalone window, accept the event
        # If this is embedded in a dialog, let the parent handle it
        if self.parent() and isinstance(self.parent(), QDialog):
            # Let the parent dialog handle the close event
            self.parent().accept()
            event.ignore()
        else:
            # This is a standalone window, accept the event
            event.accept()
    def create_basic_info_tab(self):
        """Create the Basic Info tab with guidance"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Name field with guidance
        name_group = QGroupBox("Template Name")
        name_layout = QVBoxLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter a descriptive name...")
        self.name_edit.textChanged.connect(self.on_field_changed)
        
        name_help = QLabel("Choose a clear, descriptive name that indicates the template's purpose.")
        name_help.setStyleSheet("color: #666; font-style: italic;")
        
        name_layout.addWidget(self.name_edit)
        name_layout.addWidget(name_help)
        name_group.setLayout(name_layout)
        layout.addWidget(name_group)
        
        # Description field with guidance
        desc_group = QGroupBox("Description")
        desc_layout = QVBoxLayout()
        
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Explain when and how to use this template...")
        self.description_edit.setMaximumHeight(150)
        self.description_edit.textChanged.connect(self.on_field_changed)
        
        desc_help = QLabel("Provide a brief explanation of what this template does and when to use it.")
        desc_help.setStyleSheet("color: #666; font-style: italic;")
        
        desc_example = QLabel("<b>Example:</b> \"Analyzes meeting transcripts to extract action items, decisions, and follow-ups.\"")
        desc_example.setStyleSheet("color: #28a745; font-style: italic;")
        
        desc_layout.addWidget(self.description_edit)
        desc_layout.addWidget(desc_help)
        desc_layout.addWidget(desc_example)
        desc_group.setLayout(desc_layout)
        layout.addWidget(desc_group)
        
        # Add spacer at the bottom
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Basic Info")
        
    def create_prompts_tab(self):
        """Create the Prompts tab with guidance"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # User Context field with guidance
        user_group = QGroupBox("User Context (WHO)")
        user_layout = QVBoxLayout()
        
        user_help = QLabel("Define your perspective and role. This sets WHO you are in relation to the content.")
        user_help.setStyleSheet("color: #666; font-style: italic;")
        user_layout.addWidget(user_help)
        
        self.user_edit = QTextEdit()
        self.user_edit.setPlaceholderText("As a [your role]...")
        self.user_edit.setMinimumHeight(80)
        self.user_edit.textChanged.connect(self.on_field_changed)
        user_layout.addWidget(self.user_edit)
        
        user_example = QLabel("<b>Example:</b> \"As a project manager reviewing a team meeting...\"")
        user_example.setStyleSheet("color: #28a745; font-style: italic;")
        user_layout.addWidget(user_example)
        
        user_group.setLayout(user_layout)
        layout.addWidget(user_group)
        
        # System Prompt field with guidance
        system_group = QGroupBox("System Prompt (ROLE)")
        system_layout = QVBoxLayout()
        
        system_help = QLabel("Define the AI's behavior and capabilities. This sets the AI's ROLE and approach.")
        system_help.setStyleSheet("color: #666; font-style: italic;")
        system_layout.addWidget(system_help)
        
        self.system_prompt_edit = QTextEdit()
        self.system_prompt_edit.setPlaceholderText("You are an AI assistant that...")
        self.system_prompt_edit.setMinimumHeight(120)
        self.system_prompt_edit.textChanged.connect(self.on_field_changed)
        system_layout.addWidget(self.system_prompt_edit)
        
        system_example = QLabel("<b>Example:</b> \"You are an AI assistant specializing in project management. Your role is to:\n1. Identify action items and owners\n2. Extract key decisions\n3. Highlight risks and issues\"")
        system_example.setStyleSheet("color: #28a745; font-style: italic;")
        system_layout.addWidget(system_example)
        
        system_group.setLayout(system_layout)
        layout.addWidget(system_group)
        
        # Analysis Instructions field with guidance
        template_group = QGroupBox("Analysis Instructions (HOW)")
        template_layout = QVBoxLayout()
        
        template_help = QLabel("Define the specific format and requirements for the analysis. This sets HOW the content should be analyzed.")
        template_help.setStyleSheet("color: #666; font-style: italic;")
        template_layout.addWidget(template_help)
        
        self.template_edit = QTextEdit()
        self.template_edit.setPlaceholderText("Please analyze this content by...")
        self.template_edit.setMinimumHeight(150)
        self.template_edit.textChanged.connect(self.on_field_changed)
        template_layout.addWidget(self.template_edit)
        
        template_example = QLabel("<b>Example:</b> \"Please provide a meeting analysis with these sections:\n1. Action Items (with owners and deadlines)\n2. Decisions Made\n3. Key Discussion Points\"")
        template_example.setStyleSheet("color: #28a745; font-style: italic;")
        template_layout.addWidget(template_example)
        
        template_group.setLayout(template_layout)
        layout.addWidget(template_group)
        
        # Add scrollable area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_content.setLayout(layout)
        scroll_area.setWidget(scroll_content)
        
        tab_layout = QVBoxLayout()
        tab_layout.addWidget(scroll_area)
        tab.setLayout(tab_layout)
        
        self.tab_widget.addTab(tab, "Prompts")
        
    def create_bookmarks_tab(self):
        """Create the Bookmarks tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Bookmarks explanation
        bookmarks_help = QLabel("Bookmarks are special markers that can be inserted into transcripts to highlight important points.")
        bookmarks_help.setWordWrap(True)
        bookmarks_help.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(bookmarks_help)
        
        # Split into two columns with styling
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(10)  # Add space between columns
        
        # Markers column
        markers_group = QGroupBox("📍 Markers")
        markers_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ccc;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
        """)
        markers_layout = QVBoxLayout()
        self.markers_list = QListWidget()
        self.markers_list.setMinimumHeight(200)
        self.markers_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
                background-color: #f8f9fa;
            }
            QListWidget::item {
                border-bottom: 1px solid #eee;
                padding: 4px;
                margin: 2px 0;
            }
            QListWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
        """)
        markers_layout.addWidget(self.markers_list)
        markers_group.setLayout(markers_layout)
        columns_layout.addWidget(markers_group)
        
        # Voice Commands column
        commands_group = QGroupBox("🎤 Voice Commands")
        commands_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ccc;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
        """)
        commands_layout = QVBoxLayout()
        self.commands_list = QListWidget()
        self.commands_list.setMinimumHeight(200)
        self.commands_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
                background-color: #f8f9fa;
            }
            QListWidget::item {
                border-bottom: 1px solid #eee;
                padding: 4px;
                margin: 2px 0;
            }
            QListWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
        """)
        commands_layout.addWidget(self.commands_list)
        commands_group.setLayout(commands_layout)
        columns_layout.addWidget(commands_group)
        
        layout.addLayout(columns_layout)
        
        # Buttons below both columns with styling
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)  # Add space between buttons
        
        self.add_bookmark_btn = QPushButton("➕ Add")
        self.add_bookmark_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.add_bookmark_btn.clicked.connect(self.add_bookmark)
        
        self.edit_bookmark_btn = QPushButton("✏️ Edit")
        self.edit_bookmark_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.edit_bookmark_btn.clicked.connect(self.edit_bookmark)
        
        self.delete_bookmark_btn = QPushButton("🗑️ Delete")
        self.delete_bookmark_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.delete_bookmark_btn.clicked.connect(self.delete_bookmark)
        
        # Quick Add button with dropdown menu
        self.quick_add_btn = QPushButton("⚡ Quick Add")
        self.quick_add_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #138496;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.quick_add_btn.clicked.connect(self.show_quick_add_menu)
        
        buttons_layout.addWidget(self.add_bookmark_btn)
        buttons_layout.addWidget(self.edit_bookmark_btn)
        buttons_layout.addWidget(self.delete_bookmark_btn)
        buttons_layout.addWidget(self.quick_add_btn)
        
        # Add selection handling for bookmark lists
        self.markers_list.itemSelectionChanged.connect(self.on_bookmark_selection_changed)
        self.commands_list.itemSelectionChanged.connect(self.on_bookmark_selection_changed)
        
        layout.addLayout(buttons_layout)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Bookmarks")
        
    def create_advanced_tab(self):
        """Create the Advanced tab with guidance"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Curiosity Engine Prompt
        curiosity_group = QGroupBox("Curiosity Engine Prompt")
        curiosity_layout = QVBoxLayout()
        
        curiosity_help = QLabel("Define custom prompt for generating contextual questions. The Curiosity Engine generates questions about the conversation to help uncover additional context.")
        curiosity_help.setStyleSheet("color: #666; font-style: italic;")
        curiosity_help.setWordWrap(True)
        curiosity_layout.addWidget(curiosity_help)
        
        self.curiosity_prompt_edit = QTextEdit()
        self.curiosity_prompt_edit.setPlaceholderText("Custom prompt for the Curiosity Engine...")
        self.curiosity_prompt_edit.setMinimumHeight(200)
        self.curiosity_prompt_edit.textChanged.connect(self.on_field_changed)
        curiosity_layout.addWidget(self.curiosity_prompt_edit)
        
        curiosity_example = QLabel("<b>Tip:</b> Focus on the [CUSTOMIZABLE GUIDELINES] section to specify what types of questions should be generated.")
        curiosity_example.setStyleSheet("color: #28a745; font-style: italic;")
        curiosity_layout.addWidget(curiosity_example)
        
        curiosity_group.setLayout(curiosity_layout)
        layout.addWidget(curiosity_group)
        
        # Conversation Mode
        mode_group = QGroupBox("Conversation Mode")
        mode_layout = QVBoxLayout()
        
        mode_help = QLabel("Select how the Conversation Compass should work with this template.")
        mode_help.setStyleSheet("color: #666; font-style: italic;")
        mode_help.setWordWrap(True)
        mode_layout.addWidget(mode_help)
        
        mode_options = QHBoxLayout()
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["tracking", "guided"])
        self.mode_combo.setToolTip("tracking: follows conversation flow, guided: suggests paths")
        self.mode_combo.currentTextChanged.connect(self.on_field_changed)
        
        mode_options.addWidget(QLabel("Mode:"))
        mode_options.addWidget(self.mode_combo)
        mode_options.addStretch()
        
        mode_layout.addLayout(mode_options)
        
        # Mode explanation
        mode_explanation = QLabel("""
        <b>Tracking Mode:</b> Follows the natural flow of conversation without predetermined paths. Best for open discussions, brainstorming, or exploratory conversations.<br><br>
        <b>Guided Mode:</b> Helps direct the conversation toward specific goals with suggested paths. Best for interviews, negotiations, or structured discussions.
        """)
        mode_explanation.setStyleSheet("color: #666; font-style: italic;")
        mode_explanation.setWordWrap(True)
        mode_layout.addWidget(mode_explanation)
        
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)
        
        # Visualization Settings
        vis_group = QGroupBox("Visualization Settings")
        vis_layout = QVBoxLayout()
        
        vis_help = QLabel("Configure how conversation trees and other visualizations appear.")
        vis_help.setStyleSheet("color: #666; font-style: italic;")
        vis_help.setWordWrap(True)
        vis_layout.addWidget(vis_help)
        
        layout_options = QHBoxLayout()
        layout_options.addWidget(QLabel("Default Layout:"))
        
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(["radial", "hierarchical", "force-directed"])
        self.layout_combo.setToolTip("radial: circular layout, hierarchical: tree layout, force-directed: dynamic layout")
        layout_options.addWidget(self.layout_combo)
        layout_options.addStretch()
        
        vis_layout.addLayout(layout_options)
        
        # Highlight options
        highlight_options = QVBoxLayout()
        
        self.highlight_decisions = QCheckBox("Highlight decision points")
        self.highlight_decisions.setChecked(True)
        self.highlight_decisions.setToolTip("Visually emphasize decision points in the conversation tree")
        
        self.highlight_questions = QCheckBox("Highlight questions")
        self.highlight_questions.setChecked(True)
        self.highlight_questions.setToolTip("Visually emphasize questions in the conversation tree")
        
        highlight_options.addWidget(self.highlight_decisions)
        highlight_options.addWidget(self.highlight_questions)
        
        vis_layout.addLayout(highlight_options)
        
        vis_group.setLayout(vis_layout)
        layout.addWidget(vis_group)
        
        # Add scrollable area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_content.setLayout(layout)
        scroll_area.setWidget(scroll_content)
        
        tab_layout = QVBoxLayout()
        tab_layout.addWidget(scroll_area)
        tab.setLayout(tab_layout)
        
        self.tab_widget.addTab(tab, "Advanced")

    def create_preview_tab(self):
        """Create a preview tab to show how the template will look"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Preview header
        preview_header = QLabel("Template Preview")
        preview_header.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(preview_header)
        
        # Preview description
        preview_desc = QLabel("This shows how your template will look when applied to a transcript.")
        preview_desc.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(preview_desc)
        
        # Preview content
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMinimumHeight(400)
        layout.addWidget(self.preview_text)
        
        # Update preview button
        update_btn = QPushButton("Update Preview")
        update_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        update_btn.clicked.connect(self.update_preview)
        layout.addWidget(update_btn)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Preview")
