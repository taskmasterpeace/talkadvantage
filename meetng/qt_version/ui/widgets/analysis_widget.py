from .floating_widget import FloatingWidget
from langchain_openai import ChatOpenAI
from ..components.processing_indicator import ProcessingIndicator
from PyQt6.QtWidgets import (
    QTextEdit, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QComboBox, QApplication, QSizePolicy,
    QColorDialog
)
from PyQt6.QtGui import QTextCursor, QTextCharFormat
from ..components.font_control import FontControlPanel
from PyQt6.QtCore import QDateTime
import markdown

class AnalysisWidget(FloatingWidget):
    def __init__(self, parent=None, template_name="", widget_id=None):
        widget_id = widget_id or f"analysis_{template_name.lower().replace(' ', '_')}"
        super().__init__(parent, title=f"Analysis: {template_name}", widget_id=widget_id)
        
        # Store reference to parent for accessing services
        self.parent = parent
        
        # Set larger minimum and default size
        self.setMinimumSize(400, 300)
        self.resize(600, 500)
        
        # Add margins to content layout
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setSpacing(10)
        
        # Template controls
        template_layout = QHBoxLayout()
        template_layout.addWidget(QLabel("Template:"))
        
        self.template_combo = QComboBox()
        self.load_templates(current_template=template_name)
        self.template_combo.currentTextChanged.connect(self.on_template_changed)
        template_layout.addWidget(self.template_combo)
        
        self.content_layout.addLayout(template_layout)
        
        # Analysis controls
        controls = QHBoxLayout()
        
        # Font control
        self.font_control = FontControlPanel(settings_key=f"analysis_font_{widget_id}")
        controls.addWidget(self.font_control)
        
        # Copy button
        self.copy_btn = QPushButton("📋 Copy")
        self.copy_btn.clicked.connect(self.copy_text)
        controls.addWidget(self.copy_btn)
        
        self.content_layout.addLayout(controls)
        
        # Add processing indicator
        self.processing_indicator = ProcessingIndicator()
        self.content_layout.addWidget(self.processing_indicator)
        
        # Text area
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.font_control.fontChanged.connect(lambda f: self.text_edit.setFont(f))
        self.text_edit.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.content_layout.addWidget(self.text_edit)

    def load_templates(self, current_template=None):
        """Load all available templates"""
        try:
            # Get templates from service
            templates = self.parent.app.service_adapter.langchain_service.get_available_templates()
            
            # Store templates in cache
            self._templates_cache = templates
            
            # Update combo box
            self.template_combo.clear()
            for template in templates:
                self.template_combo.addItem(template["name"])
                
            # Set current template if specified
            if current_template:
                index = self.template_combo.findText(current_template)
                if index >= 0:
                    self.template_combo.setCurrentIndex(index)
                    
        except Exception as e:
            self.text_edit.setText(f"Error loading templates: {str(e)}")

    def on_template_changed(self):
        """Handle template selection change"""
        self.setWindowTitle(f"Analysis: {self.template_combo.currentText()}")

    def copy_text(self):
        """Copy analysis text to clipboard"""
        QApplication.clipboard().setText(self.text_edit.toPlainText())
        
    def process_text(self, text: str):
        """Process text using this widget's selected template"""
        try:
            self.processing_indicator.start()  # Start timer
            # Get current template
            template_name = self.template_combo.currentText()
            template = next((t for t in self._templates_cache if t["name"] == template_name), None)
            
            if not template:
                raise ValueError(f"Template '{template_name}' not found")
            
            # Use the existing LangChain service
            result = self.parent.app.service_adapter.langchain_service.process_chunk(
                text,
                template,
                is_full_analysis=False
            )
            
            # Format and display result
            current_time = QDateTime.currentDateTime().toString("hh:mm:ss")
            
            html_content = f"""
    <div class="message-container" style="margin: 15px 10px;">
        <!-- Global style overrides -->
        <style>
            /* Universal reset for all elements inside container */
            .message-container * {{
                background: transparent !important;
                margin: 0 !important;
                padding: 0 !important;
            }}
            
            /* Specific element adjustments */
            .message-container p {{ margin-bottom: 8px !important; }}
            .message-container ul, 
            .message-container ol {{ 
                margin: 4px 0 !important;
                padding-left: 20px !important;
            }}
            .message-container blockquote {{
                border-left: 3px solid #ccc !important;
                margin-left: 0 !important;
                padding-left: 10px !important;
            }}
            .message-container table {{
                border-collapse: collapse !important;
                margin: 8px 0 !important;
            }}
            .message-container th,
            .message-container td {{
                border: 1px solid #ddd !important;
                padding: 6px !important;
            }}
        </style>
        
        <!-- Header -->
        <div style="margin-bottom: 5px;">
            <span style="color: #666; font-size: 0.9em;">{current_time}</span>
            <span style="color: #2196F3; margin-left: 10px; font-weight: bold;">{template_name}</span>
        </div>
        
        <!-- Message Bubble -->
        <div style="
            background-color: #2C3E50;
            border-radius: 15px;
            padding: 15px;
            margin: 5px 0;
            color: #FFFFFF;
            line-height: 1.6;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        ">
            <div style="color: #FFFFFF;">
                {markdown.markdown(result, extensions=['tables'])}
            </div>
        </div>
    </div>
        """
        
            # Clear any existing formatting
            cursor = self.text_edit.textCursor()
            cursor.select(QTextCursor.SelectionType.Document)
            cursor.setCharFormat(QTextCharFormat())
            self.text_edit.setTextCursor(cursor)
            
            # Debug print
            print("\nDebug: Generated HTML Content:")
            print(html_content)
            
            self.text_edit.append(html_content)
            self.processing_indicator.stop()  # Stop timer
            
        except Exception as e:
            self.processing_indicator.stop()  # Stop timer on error
            error_html = f"""
        <div style="
            margin: 10px;
            padding: 10px;
            background-color: #DC3545;
            border-radius: 15px;
            color: white;
        ">
            Error: {str(e)}
        </div>
        """
            self.text_edit.append(error_html)
