from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QComboBox, QLineEdit, QTextEdit, QStackedWidget, QFormLayout,
    QGroupBox, QRadioButton, QButtonGroup, QCheckBox, QListWidget,
    QListWidgetItem, QDialogButtonBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QSettings

class ConversationCompassSetupDialog(QDialog):
    """Dialog for setting up a new Conversation Compass session"""
    
    def __init__(self, parent=None, langchain_service=None):
        super().__init__(parent)
        self.setWindowTitle("New Conversation Compass")
        self.setMinimumSize(600, 500)
        self.langchain_service = langchain_service
        self.setup_result = {}
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create step widget
        self.steps = QStackedWidget()
        
        # Add steps
        self.add_type_selection_step()
        self.add_context_input_step()
        self.add_mode_selection_step()
        self.add_visualization_config_step()
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        self.back_btn = QPushButton("Back")
        self.next_btn = QPushButton("Next")
        self.finish_btn = QPushButton("Start Compass")
        self.finish_btn.setVisible(False)
        
        nav_layout.addWidget(self.back_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.next_btn)
        nav_layout.addWidget(self.finish_btn)
        
        # Add to main layout
        layout.addWidget(self.steps)
        layout.addLayout(nav_layout)
        
        # Connect signals
        self.back_btn.clicked.connect(self.go_previous_step)
        self.next_btn.clicked.connect(self.go_next_step)
        self.finish_btn.clicked.connect(self.finish_setup)
        
        # Initialize state
        self.current_step = 0
        self.update_navigation_buttons()
    
    def add_type_selection_step(self):
        """Add conversation type selection step"""
        step_widget = QGroupBox("Conversation Type")
        layout = QVBoxLayout(step_widget)
        
        # Description
        layout.addWidget(QLabel("What kind of conversation are you having?"))
        
        # Conversation type selection
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Sales Conversation",
            "Job Interview",
            "Customer Support",
            "Negotiation",
            "Information Gathering",
            "General Discussion",
            "Custom"
        ])
        layout.addWidget(self.type_combo)
        
        # Custom type input (only visible when Custom is selected)
        self.custom_type_input = QLineEdit()
        self.custom_type_input.setPlaceholderText("Enter custom conversation type...")
        self.custom_type_input.setVisible(False)
        layout.addWidget(self.custom_type_input)
        
        # Connect signals
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        
        layout.addStretch()
        self.steps.addWidget(step_widget)
    
    def add_context_input_step(self):
        """Add context input step"""
        step_widget = QGroupBox("Conversation Context")
        layout = QVBoxLayout(step_widget)
        
        # Description
        layout.addWidget(QLabel("Provide context for your conversation:"))
        
        # Goal input
        form_layout = QFormLayout()
        self.goal_input = QLineEdit()
        self.goal_input.setPlaceholderText("What do you want to achieve in this conversation?")
        form_layout.addRow("Goal:", self.goal_input)
        
        # Topics input
        self.topics_input = QLineEdit()
        self.topics_input.setPlaceholderText("Key topics to cover (comma separated)")
        form_layout.addRow("Topics:", self.topics_input)
        
        # Duration input
        self.duration_combo = QComboBox()
        self.duration_combo.addItems(["Short (< 15 min)", "Medium (15-30 min)", "Long (> 30 min)"])
        form_layout.addRow("Duration:", self.duration_combo)
        
        layout.addLayout(form_layout)
        
        # Additional context
        layout.addWidget(QLabel("Additional Context (optional):"))
        self.additional_context = QTextEdit()
        self.additional_context.setPlaceholderText("Add any other relevant information about the conversation...")
        self.additional_context.setMaximumHeight(150)
        layout.addWidget(self.additional_context)
        
        layout.addStretch()
        self.steps.addWidget(step_widget)
    
    def add_mode_selection_step(self):
        """Add mode selection step"""
        step_widget = QGroupBox("Compass Mode")
        layout = QVBoxLayout(step_widget)
        
        # Description
        layout.addWidget(QLabel("How would you like the Conversation Compass to function?"))
        
        # Mode selection
        self.mode_group = QButtonGroup(self)
        
        # Create a more prominent mode selection with descriptions
        mode_frame = QFrame()
        mode_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        mode_frame.setStyleSheet("QFrame { background-color: #f5f5f5; border-radius: 5px; }")
        mode_layout = QVBoxLayout(mode_frame)
        
        # Tracking mode
        tracking_layout = QHBoxLayout()
        tracking_mode = QRadioButton("Tracking Mode")
        tracking_mode.setStyleSheet("font-weight: bold;")
        self.mode_group.addButton(tracking_mode, 0)
        tracking_layout.addWidget(tracking_mode)
        tracking_layout.addWidget(QLabel("- Follows your actual conversation without pre-generating paths"))
        mode_layout.addLayout(tracking_layout)
        
        # Guidance mode
        guidance_layout = QHBoxLayout()
        guidance_mode = QRadioButton("Guidance Mode")
        guidance_mode.setStyleSheet("font-weight: bold;")
        self.mode_group.addButton(guidance_mode, 1)
        guidance_layout.addWidget(guidance_mode)
        guidance_layout.addWidget(QLabel("- Pre-generates potential conversation paths and suggests responses"))
        mode_layout.addLayout(guidance_layout)
        
        # Preparation mode
        preparation_layout = QHBoxLayout()
        preparation_mode = QRadioButton("Preparation Mode")
        preparation_mode.setStyleSheet("font-weight: bold;")
        self.mode_group.addButton(preparation_mode, 2)
        preparation_layout.addWidget(preparation_mode)
        preparation_layout.addWidget(QLabel("- Creates a complete conversation map before you start talking"))
        mode_layout.addLayout(preparation_layout)
        
        # Analysis mode
        analysis_layout = QHBoxLayout()
        analysis_mode = QRadioButton("Analysis Mode")
        analysis_mode.setStyleSheet("font-weight: bold;")
        self.mode_group.addButton(analysis_mode, 3)
        analysis_layout.addWidget(analysis_mode)
        analysis_layout.addWidget(QLabel("- Works with existing transcripts to show what happened and alternatives"))
        mode_layout.addLayout(analysis_layout)
        
        # Set default
        tracking_mode.setChecked(True)
        
        layout.addWidget(mode_frame)
        layout.addStretch()
        self.steps.addWidget(step_widget)
    
    def add_visualization_config_step(self):
        """Add visualization configuration step"""
        step_widget = QGroupBox("Visualization Settings")
        layout = QVBoxLayout(step_widget)
        
        # Description
        layout.addWidget(QLabel("Configure how the conversation tree will be displayed:"))
        
        # Detail level
        form_layout = QFormLayout()
        self.detail_combo = QComboBox()
        self.detail_combo.addItems(["Low", "Medium", "High"])
        self.detail_combo.setCurrentText("Medium")
        form_layout.addRow("Detail Level:", self.detail_combo)
        
        # Layout type
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(["Radial", "Hierarchical", "Force-Directed"])
        self.layout_combo.setCurrentText("Radial")
        form_layout.addRow("Layout Type:", self.layout_combo)
        
        # Focus areas
        layout.addLayout(form_layout)
        layout.addWidget(QLabel("Focus Areas:"))
        
        self.focus_questions = QCheckBox("Questions")
        self.focus_questions.setChecked(True)
        layout.addWidget(self.focus_questions)
        
        self.focus_objections = QCheckBox("Objections/Concerns")
        self.focus_objections.setChecked(True)
        layout.addWidget(self.focus_objections)
        
        self.focus_decisions = QCheckBox("Decision Points")
        self.focus_decisions.setChecked(True)
        layout.addWidget(self.focus_decisions)
        
        # Expand/collapse options
        layout.addWidget(QLabel("Initial Tree State:"))
        
        self.expand_all_radio = QRadioButton("Expand All")
        self.expand_first_level_radio = QRadioButton("Expand First Level Only")
        self.expand_first_level_radio.setChecked(True)
        self.collapse_all_radio = QRadioButton("Collapse All")
        
        expand_group = QButtonGroup(self)
        expand_group.addButton(self.expand_all_radio)
        expand_group.addButton(self.expand_first_level_radio)
        expand_group.addButton(self.collapse_all_radio)
        
        layout.addWidget(self.expand_all_radio)
        layout.addWidget(self.expand_first_level_radio)
        layout.addWidget(self.collapse_all_radio)
        
        # Template selection
        layout.addWidget(QLabel("Starting Templates:"))
        self.templates_list = QListWidget()
        self.load_templates()
        layout.addWidget(self.templates_list)
        
        layout.addStretch()
        self.steps.addWidget(step_widget)
    
    def load_templates(self):
        """Load available templates for conversation compass"""
        # This would normally load from a template service
        # For now, we'll add some sample templates
        templates = [
            "Sales - Discovery Call",
            "Sales - Product Demo",
            "Interview - Technical",
            "Interview - Behavioral",
            "Support - Problem Resolution",
            "Negotiation - Salary",
            "General - Information Gathering"
        ]
        
        for template in templates:
            item = QListWidgetItem(template)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.templates_list.addItem(item)
    
    def on_type_changed(self, text):
        """Handle conversation type change"""
        self.custom_type_input.setVisible(text == "Custom")
    
    def go_previous_step(self):
        """Go to previous step"""
        if self.current_step > 0:
            self.current_step -= 1
            self.steps.setCurrentIndex(self.current_step)
            self.update_navigation_buttons()
    
    def go_next_step(self):
        """Go to next step"""
        if self.current_step < self.steps.count() - 1:
            self.current_step += 1
            self.steps.setCurrentIndex(self.current_step)
            self.update_navigation_buttons()
    
    def update_navigation_buttons(self):
        """Update navigation button states"""
        self.back_btn.setEnabled(self.current_step > 0)
        
        is_last_step = self.current_step == self.steps.count() - 1
        self.next_btn.setVisible(not is_last_step)
        self.finish_btn.setVisible(is_last_step)
    
    def finish_setup(self):
        """Complete setup and return results"""
        # Gather all settings
        self.setup_result = {
            # Step 1: Conversation Type
            'conversation_type': self.type_combo.currentText(),
            'custom_type': self.custom_type_input.text() if self.type_combo.currentText() == "Custom" else "",
            
            # Step 2: Context
            'goal': self.goal_input.text(),
            'topics': self.topics_input.text(),
            'duration': self.duration_combo.currentText(),
            'additional_context': self.additional_context.toPlainText(),
            
            # Step 3: Mode - Explicitly include the mode selection
            'mode': self.mode_group.checkedId(),
            
            # Step 4: Visualization
            'detail_level': self.detail_combo.currentText(),
            'layout_type': self.layout_combo.currentText(),
            'focus_questions': self.focus_questions.isChecked(),
            'focus_objections': self.focus_objections.isChecked(),
            'focus_decisions': self.focus_decisions.isChecked(),
            'initial_tree_state': 'expand_all' if self.expand_all_radio.isChecked() else 
                                ('expand_first_level' if self.expand_first_level_radio.isChecked() else 'collapse_all'),
            'templates': [
                self.templates_list.item(i).text() 
                for i in range(self.templates_list.count()) 
                if self.templates_list.item(i).checkState() == Qt.CheckState.Checked
            ]
        }
        
        # Add template information if a template is selected
        selected_templates = self.setup_result['templates']
        if selected_templates:
            # Get the first selected template (for now we'll just use one)
            template_name = selected_templates[0]
            
            # Get template details from service
            if self.langchain_service:
                template = self.langchain_service.get_template(template_name)
                if template:
                    # Add template info to context
                    self.setup_result['template'] = template
                    
                    # Override mode based on template's conversation_mode if available
                    if "conversation_mode" in template:
                        print(f"Using template conversation mode: {template['conversation_mode']}")
                        # Map string mode to numeric mode ID
                        mode_mapping = {"tracking": 0, "guided": 1}
                        if template['conversation_mode'] in mode_mapping:
                            self.setup_result['mode'] = mode_mapping[template['conversation_mode']]
        
        self.accept()
    
    def get_setup_result(self):
        """Get the setup result"""
        return self.setup_result
