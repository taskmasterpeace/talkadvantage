from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QGroupBox, QTextEdit,
    QFrame, QMessageBox, QComboBox, QCheckBox,
    QTabWidget, QWidget, QScrollArea, QFormLayout,
    QListWidget
)
from PyQt6.QtGui import QFont, QColor, QTextCharFormat, QTextCursor
from qt_version.utils.settings_manager import SettingsManager
from qt_version.utils.theme_manager import ThemeType
from PyQt6.QtCore import Qt
from dotenv import load_dotenv, set_key
import os
from pathlib import Path

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumSize(700, 600)  # Increased minimum size for better usability
        self.resize(800, 650)  # Set a default size that's comfortable
        
        # Initialize settings manager and debug mode
        self.settings_manager = SettingsManager()
        self._debug_mode = self.settings_manager.get_setting('debug_mode', 'false').lower() == 'true'
        
        # Available themes
        self.themes = {
            "modern_light": "Modern Light",
            "modern_dark": "Modern Dark",
            "classic_light": "Classic Light",
            "classic_dark": "Classic Dark",
            "high_contrast": "High Contrast"
        }
        
        # Load current values
        self.current_openai_key = self.settings_manager.get_setting('OPENAI_API_KEY', '')
        self.current_assemblyai_key = self.settings_manager.get_setting('ASSEMBLYAI_API_KEY', '')
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.create_api_tab()
        self.create_appearance_tab()
        self.create_model_tab()
        self.create_curiosity_tab()
        self.create_advanced_tab()
        
        main_layout.addWidget(self.tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def create_api_tab(self):
        """Create the Configuration tab with API Keys and File Locations"""
        config_tab = QWidget()
        config_layout = QVBoxLayout(config_tab)
        
        # API Keys group
        api_group = QGroupBox("API Keys")
        api_keys_layout = QVBoxLayout()
        
        # OpenAI Key
        api_keys_layout.addWidget(QLabel("OpenAI API Key:"))
        self.openai_key = QLineEdit()
        self.openai_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.openai_key.setText(self.current_openai_key)
        api_keys_layout.addWidget(self.openai_key)
        
        # AssemblyAI Key
        api_keys_layout.addWidget(QLabel("AssemblyAI API Key:"))
        self.assemblyai_key = QLineEdit()
        self.assemblyai_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.assemblyai_key.setText(self.current_assemblyai_key)
        api_keys_layout.addWidget(self.assemblyai_key)
        
        # LangSmith Key
        api_keys_layout.addWidget(QLabel("LangSmith API Key:"))
        self.langsmith_key = QLineEdit()
        self.langsmith_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.langsmith_key.setText(self.settings_manager.get_setting('LANGSMITH_API_KEY', ''))
        api_keys_layout.addWidget(self.langsmith_key)
        
        api_group.setLayout(api_keys_layout)
        config_layout.addWidget(api_group)
        
        # File Locations group
        file_group = QGroupBox("File Locations")
        file_layout = QVBoxLayout()
        
        # Workspace directory (primary location for recordings and transcripts)
        file_layout.addWidget(QLabel("Workspace Directory:"))
        self.workspace_dir = QLineEdit()
        self.workspace_dir.setText(self.settings_manager.get_setting('workspace_dir', ''))
        self.workspace_dir.setToolTip("Location for recordings and transcripts")
        browse_workspace_btn = QPushButton("Browse...")
        browse_workspace_btn.clicked.connect(lambda: self.browse_directory(self.workspace_dir))
        
        workspace_layout = QHBoxLayout()
        workspace_layout.addWidget(self.workspace_dir)
        workspace_layout.addWidget(browse_workspace_btn)
        file_layout.addLayout(workspace_layout)
        
        # Templates directory
        file_layout.addWidget(QLabel("Templates Directory:"))
        self.templates_dir = QLineEdit()
        self.templates_dir.setText(self.settings_manager.get_setting('templates_dir', ''))
        browse_templates_btn = QPushButton("Browse...")
        browse_templates_btn.clicked.connect(lambda: self.browse_directory(self.templates_dir))
        
        templates_layout = QHBoxLayout()
        templates_layout.addWidget(self.templates_dir)
        templates_layout.addWidget(browse_templates_btn)
        file_layout.addLayout(templates_layout)
        
        file_group.setLayout(file_layout)
        config_layout.addWidget(file_group)
        
        # Add stretch to push everything to the top
        config_layout.addStretch()
        
        self.tab_widget.addTab(config_tab, "Configuration")
    
    def create_appearance_tab(self):
        """Create the Appearance tab"""
        appearance_tab = QWidget()
        appearance_layout = QVBoxLayout(appearance_tab)
        
        # Theme group
        theme_group = QGroupBox("Theme Settings")
        theme_layout = QFormLayout()
        
        # Theme selection dropdown
        theme_layout.addRow(QLabel("Theme:"), QLabel(""))  # Spacer row
        self.theme_combo = QComboBox()
        
        # Get available themes from theme manager
        if hasattr(self.parent(), 'app') and hasattr(self.parent().app, 'theme_manager'):
            theme_manager = self.parent().app.theme_manager
            available_themes = theme_manager.get_available_themes()
            for theme_id, theme_name in available_themes.items():
                self.theme_combo.addItem(theme_name, theme_id)
        else:
            # Fallback if theme manager not available
            for theme_id, theme_name in self.themes.items():
                self.theme_combo.addItem(theme_name, theme_id)
        
        # Set current theme from settings
        current_theme = self.settings_manager.get_setting('theme', 'modern_light')
        index = self.theme_combo.findData(current_theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        self.theme_combo.setToolTip("Select the application theme")
        theme_layout.addRow("Theme Style:", self.theme_combo)
        
        # Add import/export theme buttons
        theme_buttons_layout = QHBoxLayout()
        
        import_theme_btn = QPushButton("Import Theme")
        import_theme_btn.setToolTip("Import a theme from a JSON file")
        import_theme_btn.clicked.connect(self.import_theme)
        theme_buttons_layout.addWidget(import_theme_btn)
        
        export_theme_btn = QPushButton("Export Theme")
        export_theme_btn.setToolTip("Export the current theme to a JSON file")
        export_theme_btn.clicked.connect(self.export_theme)
        theme_buttons_layout.addWidget(export_theme_btn)
        
        theme_layout.addRow("", theme_buttons_layout)
        
        # Theme type indicator
        theme_type_label = QLabel("Theme type will be determined by the selected theme")
        theme_type_label.setStyleSheet("font-style: italic; color: gray;")
        theme_layout.addRow("", theme_type_label)
        
        # Theme preview with sample UI elements
        preview_frame = QFrame()
        preview_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Sunken)
        preview_frame.setMinimumHeight(150)
        
        preview_layout = QVBoxLayout(preview_frame)
        
        # Add sample elements to preview
        preview_title = QLabel("Theme Preview")
        preview_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        preview_layout.addWidget(preview_title)
        
        # Sample button row
        button_row = QHBoxLayout()
        primary_btn = QPushButton("Primary")
        primary_btn.setProperty("class", "primary")
        button_row.addWidget(primary_btn)
        
        secondary_btn = QPushButton("Secondary")
        secondary_btn.setProperty("class", "secondary")
        button_row.addWidget(secondary_btn)
        
        warning_btn = QPushButton("Warning")
        warning_btn.setProperty("class", "warning")
        button_row.addWidget(warning_btn)
        
        preview_layout.addLayout(button_row)
        
        # Sample input
        sample_input = QLineEdit()
        sample_input.setPlaceholderText("Sample input field")
        preview_layout.addWidget(sample_input)
        
        # Sample list widget
        sample_list = QListWidget()
        sample_list.addItem("Sample list item 1")
        sample_list.addItem("Sample list item 2")
        sample_list.setMaximumHeight(60)
        preview_layout.addWidget(sample_list)
        
        # Update preview when theme changes
        self.theme_combo.currentIndexChanged.connect(self.update_theme_preview)
        
        theme_layout.addRow("Preview:", preview_frame)
        
        theme_group.setLayout(theme_layout)
        appearance_layout.addWidget(theme_group)
        
        # Add stretch to push everything to the top
        appearance_layout.addStretch()
        
        self.tab_widget.addTab(appearance_tab, "Appearance")
    
    def create_model_tab(self):
        """Create the Model Selection tab"""
        model_tab = QWidget()
        model_layout = QVBoxLayout(model_tab)
        
        # Model Selection
        model_group = QGroupBox("Model Selection")
        model_group_layout = QVBoxLayout()
        
        # Model description
        model_desc = QLabel("Select the OpenAI model to use:")
        model_desc.setWordWrap(True)
        model_group_layout.addWidget(model_desc)
        
        # Model combo box
        self.model_combo = QComboBox()
        self.models = {
            "gpt-4o-mini": "GPT-4o Mini (Default, optimized for general use)",
            "gpt-4o": "GPT-4o (Full capabilities)",
            "gpt-o1": "GPT-o1 (Complex reasoning)"
        }
        for model_id, desc in self.models.items():
            self.model_combo.addItem(desc, model_id)
        
        # Set current model from settings
        current_model = self.settings_manager.get_setting('llm_model', 'gpt-4o-mini')
        index = self.model_combo.findData(current_model)
        if index >= 0:
            self.model_combo.setCurrentIndex(index)
            
        model_group_layout.addWidget(self.model_combo)
        model_group.setLayout(model_group_layout)
        model_layout.addWidget(model_group)
        
        # Add stretch to push everything to the top
        model_layout.addStretch()
        
        self.tab_widget.addTab(model_tab, "Models")
    
    def create_curiosity_tab(self):
        """Create the Curiosity Engine tab"""
        curiosity_tab = QWidget()
        
        # Use a scroll area to handle large content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        curiosity_layout = QVBoxLayout(scroll_content)
        
        # Create Curiosity Engine group
        curiosity_group = QGroupBox("Curiosity Engine Settings")
        curiosity_group_layout = QVBoxLayout()

        # Add explanation
        explanation = QLabel(
            "The Curiosity Engine generates questions about your transcript to help gain deeper insights. "
            "You can customize how these questions are generated by editing the prompt below."
        )
        explanation.setWordWrap(True)
        curiosity_group_layout.addWidget(explanation)

        # Add warning
        warning = QLabel(
            "⚠️ WARNING: Sections marked 'DO NOT MODIFY' contain critical instructions for proper functioning. "
            "Only edit the 'CUSTOMIZABLE GUIDELINES' section unless you understand prompt engineering."
        )
        warning.setWordWrap(True)
        warning.setStyleSheet("color: #e74c3c; font-weight: bold;")
        curiosity_group_layout.addWidget(warning)

        # Add the prompt editor with increased height
        self.curiosity_prompt = QTextEdit()
        self.curiosity_prompt.setMinimumHeight(350)  # Increased height
        self.curiosity_prompt.setFont(QFont("Courier New", 10))
        self.curiosity_prompt.setText(self.settings_manager.get_setting('curiosity_engine_prompt', ''))
        
        # Add syntax highlighting for the prompt sections
        cursor = self.curiosity_prompt.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        
        # Function to highlight sections
        def highlight_section(text, color):
            cursor = self.curiosity_prompt.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            while True:
                cursor = self.curiosity_prompt.document().find(text, cursor)
                if cursor.isNull():
                    break
                    
                format = QTextCharFormat()
                format.setForeground(QColor(color))
                format.setFontWeight(700)  # Bold
                cursor.mergeCharFormat(format)
        
        # Highlight different sections
        highlight_section("[SYSTEM INSTRUCTIONS - DO NOT MODIFY THIS SECTION]", "#e74c3c")  # Red
        highlight_section("[QUESTION TYPES - DO NOT MODIFY THESE TYPES]", "#e74c3c")  # Red
        highlight_section("[CUSTOMIZABLE GUIDELINES - YOU CAN MODIFY THIS SECTION]", "#27ae60")  # Green
        highlight_section("[OUTPUT FORMAT - DO NOT MODIFY THIS SECTION]", "#e74c3c")  # Red

        # Add the text editor
        curiosity_group_layout.addWidget(self.curiosity_prompt)

        # Add reset button
        reset_prompt_btn = QPushButton("Reset to Default")
        reset_prompt_btn.clicked.connect(self.reset_curiosity_prompt)
        curiosity_group_layout.addWidget(reset_prompt_btn)

        curiosity_group.setLayout(curiosity_group_layout)
        curiosity_layout.addWidget(curiosity_group)
        
        scroll_area.setWidget(scroll_content)
        
        # Create tab layout and add scroll area
        tab_layout = QVBoxLayout(curiosity_tab)
        tab_layout.addWidget(scroll_area)
        
        self.tab_widget.addTab(curiosity_tab, "Curiosity Engine")
    
    def create_advanced_tab(self):
        """Create the Advanced tab"""
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)
        
        # Debug Settings
        debug_group = QGroupBox("Debug Settings")
        debug_layout = QVBoxLayout()
        
        self.debug_mode = QCheckBox("Enable Debug Logging")
        self.debug_mode.setChecked(self._debug_mode)
        self.debug_mode.setToolTip("Enable detailed debug output in console")
        debug_layout.addWidget(self.debug_mode)
        
        debug_group.setLayout(debug_layout)
        advanced_layout.addWidget(debug_group)
        
        # Add Statistics Reset section
        stats_group = QGroupBox("Template Statistics")
        stats_layout = QVBoxLayout()
        
        reset_btn = QPushButton("Reset Template Statistics")
        reset_btn.clicked.connect(self.reset_statistics)
        stats_layout.addWidget(reset_btn)
        
        # Add test button
        test_btn = QPushButton("Test Settings Persistence")
        test_btn.clicked.connect(self.test_settings)
        stats_layout.addWidget(test_btn)
        
        stats_group.setLayout(stats_layout)
        advanced_layout.addWidget(stats_group)
        
        # Add stretch to push everything to the top
        advanced_layout.addStretch()
        
        self.tab_widget.addTab(advanced_tab, "Advanced")
        
    def reset_statistics(self):
        """Reset template usage statistics"""
        reply = QMessageBox.question(
            self, "Confirm Reset",
            "Are you sure you want to reset all template statistics?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.parent().app.service_adapter.langchain_service.reset_template_stats()
            QMessageBox.information(self, "Success", "Template statistics have been reset")
        
    def reset_curiosity_prompt(self):
        """Reset the curiosity prompt to default"""
        default_prompt = '''[SYSTEM INSTRUCTIONS - DO NOT MODIFY THIS SECTION]
You are an expert active listener analyzing meeting transcripts. 
Generate 2-3 insightful questions that would help understand the context better.

[QUESTION TYPES - DO NOT MODIFY THESE TYPES]
Question types:
- YES_NO: Simple yes/no questions
- MULTIPLE_CHOICE: Questions with predefined options (provide 3-4 choices)
- MULTIPLE_CHOICE_FILL: Multiple choice with an "other" option (provide 3-4 choices)

[CUSTOMIZABLE GUIDELINES - YOU CAN MODIFY THIS SECTION]
Generate questions that:
- Are relevant to the transcript content
- Help clarify important points
- Uncover underlying context
- Are concise and clear
- Have meaningful multiple choice options when applicable

[OUTPUT FORMAT - DO NOT MODIFY THIS SECTION]
Return a list of questions in the specified format.'''
        
        self.curiosity_prompt.setText(default_prompt)
        QMessageBox.information(self, "Reset Complete", "Curiosity Engine prompt has been reset to default.")
        
    def accept(self):
        """Save settings securely to database and close dialog"""
        try:
            # No dark mode setting anymore - theme type is determined by the theme itself
            
            # Save debug mode setting
            self.settings_manager.save_setting('debug_mode', str(self.debug_mode.isChecked()).lower())
            
            # Only validate and save API keys if they've been modified
            openai_key = self.openai_key.text().strip()
            assemblyai_key = self.assemblyai_key.text().strip()
            langsmith_key = self.langsmith_key.text().strip()
            
            if openai_key or assemblyai_key:  # Only if keys were entered
                if not openai_key or not assemblyai_key:
                    QMessageBox.warning(self, "Validation Error", "Both API keys are required")
                    return
                    
                # Save to settings database
                self.settings_manager.save_setting('OPENAI_API_KEY', openai_key)
                self.settings_manager.save_setting('ASSEMBLYAI_API_KEY', assemblyai_key)
                
                # Update environment variables
                os.environ['OPENAI_API_KEY'] = openai_key
                os.environ['ASSEMBLYAI_API_KEY'] = assemblyai_key
                
                # Update main window keys if they exist
                if self.parent():
                    self.parent().openai_key = openai_key
                    self.parent().assemblyai_key = assemblyai_key
                    
                    # Initialize services with new keys if app exists
                    if hasattr(self.parent(), 'app') and self.parent().app:
                        success, message = self.parent().app.service_adapter.setup_services(
                            openai_key,
                            assemblyai_key
                        )
                        if not success:
                            raise ValueError(f"Failed to initialize services: {message}")
            
            # Save LangSmith key if provided
            if langsmith_key:
                self.settings_manager.save_setting('LANGSMITH_API_KEY', langsmith_key)
                os.environ['LANGSMITH_API_KEY'] = langsmith_key
            
            # Save directory paths
            workspace_dir = self.workspace_dir.text().strip()
            templates_dir = self.templates_dir.text().strip()
            
            if workspace_dir:
                self.settings_manager.save_setting('workspace_dir', workspace_dir)
                # Create directory if it doesn't exist
                os.makedirs(workspace_dir, exist_ok=True)
                
            if templates_dir:
                self.settings_manager.save_setting('templates_dir', templates_dir)
                # Create directory if it doesn't exist
                os.makedirs(templates_dir, exist_ok=True)
            
            # Save model selection
            selected_model = self.model_combo.currentData()
            self.settings_manager.save_setting('llm_model', selected_model)
            
            # Save the curiosity engine prompt
            curiosity_prompt = self.curiosity_prompt.toPlainText()
            if curiosity_prompt:
                self.settings_manager.save_setting('curiosity_engine_prompt', curiosity_prompt)

            # Save theme selection
            selected_theme = self.theme_combo.currentData()
            self.settings_manager.save_setting('theme', selected_theme)
            
            # Apply theme immediately - ensure it works
            if self.parent() and hasattr(self.parent(), 'app') and hasattr(self.parent().app, 'theme_manager'):
                print(f"Applying theme: {selected_theme}")
                self.parent().app.theme_manager.apply_theme(selected_theme)
                
                # Force update of the application style
                from PyQt6.QtCore import QCoreApplication
                QCoreApplication.processEvents()
                self.parent().update()

            # Show success message
            QMessageBox.information(self, "Success", "Settings saved successfully")
            
            # Refresh library tab if workspace directory changed
            if workspace_dir and hasattr(self.parent(), 'library_tab'):
                self.parent().library_tab.load_workspace_files()
            elif workspace_dir and hasattr(self.parent(), 'app') and hasattr(self.parent().app, 'main_window'):
                if hasattr(self.parent().app.main_window, 'library_tab'):
                    self.parent().app.main_window.library_tab.load_workspace_files()
            
            super().accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
            
    def set_values(self, openai_key: str, assemblyai_key: str):
        """Set current values"""
        self.openai_key.setText(openai_key)
        self.assemblyai_key.setText(assemblyai_key)
        
    def get_values(self) -> tuple[str, str]:
        """Get entered values"""
        return (
            self.openai_key.text(),
            self.assemblyai_key.text()
        )
            
    def test_settings(self):
        """Test settings persistence"""
        if self.settings_manager.test_persistence():
            QMessageBox.information(self, "Test Result", "Settings persistence test passed!")
        else:
            QMessageBox.warning(self, "Test Result", "Settings persistence test failed. Check console for details.")
            
    def browse_directory(self, line_edit):
        """Open directory browser and update the line edit with selected path"""
        from PyQt6.QtWidgets import QFileDialog
        
        # Get current directory from line edit or use home directory
        current_dir = line_edit.text() or str(Path.home())
        
        # Open directory dialog
        directory = QFileDialog.getExistingDirectory(
            self, "Select Directory", current_dir, 
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks
        )
        
        # Update line edit if directory was selected
        if directory:
            line_edit.setText(directory)
            
    def update_theme_preview(self):
        """Update the theme preview based on current selection"""
        if not hasattr(self.parent(), 'app') or not hasattr(self.parent().app, 'theme_manager'):
            return
            
        # Get selected theme
        theme_id = self.theme_combo.currentData()
        
        # Get theme from theme manager
        theme_manager = self.parent().app.theme_manager
        theme = theme_manager.get_theme(theme_id)
        
        if theme is None:
            return
            
        # Create stylesheet for preview elements only
        stylesheet = f"""
            QFrame {{
                background-color: {theme.background};
                color: {theme.text};
            }}
            
            QPushButton[class="primary"] {{
                background: {theme.primary};
                color: {theme_manager.get_contrasting_text_color(theme.primary)};
                border: none;
                padding: 5px;
                border-radius: {theme.border_radius}px;
            }}
            
            QPushButton[class="secondary"] {{
                background: {theme.secondary};
                color: {theme_manager.get_contrasting_text_color(theme.secondary)};
                border: none;
                padding: 5px;
                border-radius: {theme.border_radius}px;
            }}
            
            QPushButton[class="warning"] {{
                background: {theme.warning};
                color: {theme_manager.get_contrasting_text_color(theme.warning)};
                border: none;
                padding: 5px;
                border-radius: {theme.border_radius}px;
            }}
            
            QLineEdit {{
                background-color: {theme.input_background};
                color: {theme_manager.get_contrasting_text_color(theme.input_background)};
                border: 1px solid {theme.primary};
                border-radius: {theme.border_radius}px;
                padding: 5px;
            }}
            
            QListWidget {{
                background-color: {theme.input_background};
                color: {theme_manager.get_contrasting_text_color(theme.input_background)};
                border: 1px solid {theme.primary};
                border-radius: {theme.border_radius}px;
                padding: 2px;
            }}
            
            QListWidget::item {{
                padding: 2px;
                color: {theme_manager.get_contrasting_text_color(theme.input_background)};
            }}
            
            QLabel {{
                color: {theme.text};
            }}
        """
        
        # Find the preview frame and apply stylesheet
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == "Appearance":
                tab = self.tab_widget.widget(i)
                for child in tab.findChildren(QFrame):
                    if child.frameStyle() == (QFrame.Shape.Box | QFrame.Shadow.Sunken):
                        child.setStyleSheet(stylesheet)
                        break
                break
                
    def import_theme(self):
        """Import a theme from a JSON file"""
        from PyQt6.QtWidgets import QFileDialog
        
        # Open file dialog to select JSON file
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Theme", "", "JSON Files (*.json);;All Files (*)"
        )
        
        if not file_path:
            return
            
        # Import theme using theme manager
        if hasattr(self.parent(), 'app') and hasattr(self.parent().app, 'theme_manager'):
            theme_manager = self.parent().app.theme_manager
            theme_id = theme_manager.import_theme(file_path)
            
            if theme_id:
                # Refresh theme combo box
                self.theme_combo.clear()
                available_themes = theme_manager.get_available_themes()
                for tid, theme_name in available_themes.items():
                    self.theme_combo.addItem(theme_name, tid)
                    
                # Select the imported theme
                index = self.theme_combo.findData(theme_id)
                if index >= 0:
                    self.theme_combo.setCurrentIndex(index)
                    
                QMessageBox.information(self, "Theme Imported", f"Theme '{self.theme_combo.currentText()}' imported successfully")
            else:
                QMessageBox.warning(self, "Import Failed", "Failed to import theme. Check console for details.")
        else:
            QMessageBox.warning(self, "Import Failed", "Theme manager not available")
            
    def export_theme(self):
        """Export the current theme to a JSON file"""
        from PyQt6.QtWidgets import QFileDialog
        
        # Get selected theme
        theme_id = self.theme_combo.currentData()
        theme_name = self.theme_combo.currentText()
        
        if not theme_id:
            return
            
        # Open file dialog to select save location
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Theme", f"{theme_name}.json", "JSON Files (*.json);;All Files (*)"
        )
        
        if not file_path:
            return
            
        # Export theme using theme manager
        if hasattr(self.parent(), 'app') and hasattr(self.parent().app, 'theme_manager'):
            theme_manager = self.parent().app.theme_manager
            success = theme_manager.export_theme(theme_id, file_path)
            
            if success:
                QMessageBox.information(self, "Theme Exported", f"Theme '{theme_name}' exported successfully")
            else:
                QMessageBox.warning(self, "Export Failed", "Failed to export theme. Check console for details.")
        else:
            QMessageBox.warning(self, "Export Failed", "Theme manager not available")
