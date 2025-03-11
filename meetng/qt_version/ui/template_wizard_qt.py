from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QTextEdit, QProgressBar, QWidget,
    QMessageBox, QStackedWidget, QApplication,
    QListWidget, QSplitter, QTabWidget, QLineEdit
)
from PyQt6.QtCore import Qt, QTimer
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
import json
import os

class WizardQuestionPage(QWidget):
    """Widget for displaying a single wizard question"""
    
    def __init__(self, question_data: dict, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        
        # Extract question text from the dictionary
        question = question_data["question"]
        
        # Question label with styling
        question_label = QLabel(question)
        question_label.setWordWrap(True)
        question_label.setStyleSheet("""
            QLabel {
                font-size: 12pt;
                color: #2c3e50;
                margin-bottom: 10px;
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 5px;
            }
        """)
        layout.addWidget(question_label)
        
        # Add description if available
        if "description" in question_data:
            description_label = QLabel(question_data["description"])
            description_label.setWordWrap(True)
            description_label.setStyleSheet("""
                QLabel {
                    font-size: 10pt;
                    color: #7f8c8d;
                    margin-bottom: 10px;
                }
            """)
            layout.addWidget(description_label)
        
        # Add examples if available
        if "examples" in question_data and question_data["examples"]:
            examples_text = "Examples:\n• " + "\n• ".join(question_data["examples"])
            examples_label = QLabel(examples_text)
            examples_label.setWordWrap(True)
            examples_label.setStyleSheet("""
                QLabel {
                    font-size: 9pt;
                    color: #95a5a6;
                    font-style: italic;
                    margin-bottom: 10px;
                    padding: 5px;
                    background-color: #f0f0f0;
                    border-radius: 3px;
                }
            """)
            layout.addWidget(examples_label)
        
        # Answer text area
        self.answer_edit = QTextEdit()
        self.answer_edit.setPlaceholderText("Type your answer here...")
        self.answer_edit.setStyleSheet("""
            QTextEdit {
                border: 2px solid #ddd;
                border-radius: 5px;
                padding: 8px;
                background-color: white;
                min-height: 100px;
            }
            QTextEdit:focus {
                border-color: #3498db;
            }
        """)
        layout.addWidget(self.answer_edit)
        
        self.setLayout(layout)
        
    def get_answer(self) -> str:
        return self.answer_edit.toPlainText().strip()

class TemplateWizardDialog(QDialog):
    """Dialog for AI-assisted template creation wizard"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🧙‍♂️ AI Assistant Profile Wizard")
        self.setModal(True)
        self.setMinimumSize(1200, 700)  # Increased width for two-column layout
        self._debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        
        # Initialize attributes
        self.questions = [
            {
                "question": "Which type of expert would be most helpful for your needs?",
                "description": "Choose the primary expertise needed:",
                "examples": [
                    "Meeting Analyst - For capturing decisions and action items",
                    "Executive Coach - For leadership and team dynamics",
                    "Strategic Advisor - For business strategy and planning",
                    "Innovation Expert - For creative problem-solving",
                    "Risk Manager - For compliance and risk assessment",
                    "Technical Architect - For system design and integration",
                    "Change Manager - For organizational transformation",
                    "Behavioral Expert - For group dynamics and psychology",
                    "Negotiation Expert - For deal-making and conflict resolution"
                ]
            },
            {
                "question": "What specific outcomes do you want to achieve?",
                "description": "Describe your ideal end results:",
                "examples": [
                    "Clear action items and ownership",
                    "Strategic recommendations",
                    "Risk assessment and mitigation plans",
                    "Technical architecture decisions",
                    "Behavioral insights and suggestions"
                ]
            },
            {
                "question": "How should the AI expert engage with the content?",
                "description": "Define the interaction style:",
                "examples": [
                    "Analytical and objective",
                    "Probing and investigative",
                    "Supportive and coaching",
                    "Strategic and advisory",
                    "Technical and precise"
                ]
            },
            {
                "question": "What specific elements need special attention?",
                "description": "Identify key focus areas:",
                "examples": [
                    "Decision points and rationale",
                    "Team dynamics and relationships",
                    "Technical constraints and dependencies",
                    "Risk factors and compliance issues",
                    "Change impact and readiness"
                ]
            },
            {
                "question": "What type of recommendations would be most valuable?",
                "description": "Define the guidance needed:",
                "examples": [
                    "Immediate action items",
                    "Strategic insights",
                    "Process improvements",
                    "Technical solutions",
                    "Behavioral adjustments"
                ]
            },
            # New questions for enhanced templates
            {
                "question": "Which conversation mode would be most appropriate?",
                "description": "Choose how the Conversation Compass should work:",
                "examples": [
                    "Tracking Mode - Follow the natural flow of conversation (best for open discussions, brainstorming)",
                    "Guided Mode - Help direct the conversation toward specific goals (best for interviews, negotiations)"
                ]
            },
            {
                "question": "Which special bookmark types would be useful?",
                "description": "Select bookmark types that would help analyze this content:",
                "examples": [
                    "User Speaking - Mark when you are speaking (useful for identifying your contributions)",
                    "Decision Points - Mark important decisions (useful for tracking key choices)",
                    "Action Items - Mark tasks and assignments (useful for follow-up tracking)"
                ]
            },
            {
                "question": "What should the Curiosity Engine focus on?",
                "description": "The Curiosity Engine generates questions about the conversation:",
                "examples": [
                    "Context clarification - Questions about unclear points",
                    "Decision making - Questions about how decisions were reached",
                    "Action items - Questions about tasks and responsibilities",
                    "Participant roles - Questions about who said what",
                    "Meeting type - Questions about the nature of the conversation"
                ]
            }
        ]
        self.current_question = 0
        self.answers = []
        self.generated_templates = []
        
        # Setup UI with two-column layout
        main_layout = QVBoxLayout()
        
        # Header
        header = QLabel("AI Assistant Profile Creator")
        header.setStyleSheet("""
            QLabel {
                font-size: 18pt;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
            }
        """)
        main_layout.addWidget(header)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #9b59b6;
            }
        """)
        main_layout.addWidget(self.progress)
        
        # Create a splitter for the two-column layout
        splitter = QSplitter()
        splitter.setChildrenCollapsible(False)
        main_layout.addWidget(splitter, 1)  # Give it a stretch factor
        
        # Left panel - Question navigation
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)
        
        # Question list
        question_list_label = QLabel("Profile Questions:")
        question_list_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        left_layout.addWidget(question_list_label)
        
        self.question_list = QListWidget()
        for i, question in enumerate(self.questions):
            self.question_list.addItem(f"Q{i+1}: {question['question'][:30]}...")
        self.question_list.currentRowChanged.connect(self.on_question_selected)
        left_layout.addWidget(self.question_list, 1)  # Give it stretch
        
        # Right panel - Question content
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)
        
        # Stacked widget for questions
        self.question_stack = QStackedWidget()
        for question in self.questions:
            page = WizardQuestionPage(question)
            self.question_stack.addWidget(page)
        right_layout.addWidget(self.question_stack, 1)  # Give it stretch
        
        # Navigation buttons
        button_layout = QHBoxLayout()
        
        self.back_btn = QPushButton("⬅️ Back")
        self.back_btn.clicked.connect(self.previous_question)
        self.back_btn.setEnabled(False)
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        
        self.next_btn = QPushButton("Next ➡️")
        self.next_btn.clicked.connect(self.next_question)
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        
        button_layout.addWidget(self.back_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.next_btn)
        
        right_layout.addLayout(button_layout)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        # Set initial splitter sizes (30% left, 70% right)
        splitter.setSizes([300, 700])
        
        self.setLayout(main_layout)
        
        # Update progress and select first question
        self.update_progress()
        self.question_list.setCurrentRow(0)
        
    def update_progress(self):
        """Update progress bar and button states"""
        progress = ((self.current_question + 1) / (len(self.questions) + 1)) * 100
        self.progress.setValue(int(progress))
        
        self.back_btn.setEnabled(self.current_question > 0)
        self.next_btn.setText("Generate Templates ✨" if self.current_question == len(self.questions) - 1 else "Next ➡️")
        
        # Update question list selection
        self.question_list.setCurrentRow(self.current_question)
        
    def on_question_selected(self, index):
        """Handle question selection from list"""
        if index >= 0 and index < len(self.questions):
            # Save current answer before switching
            if self.current_question >= 0 and self.current_question < len(self.questions):
                current_page = self.question_stack.widget(self.current_question)
                answer = current_page.get_answer()
                if answer:  # Only save if there's an answer
                    if len(self.answers) <= self.current_question:
                        self.answers.append(answer)
                    else:
                        self.answers[self.current_question] = answer
            
            # Switch to selected question
            self.current_question = index
            self.question_stack.setCurrentIndex(index)
            self.update_progress()
        
    def previous_question(self):
        """Go to previous question"""
        if self.current_question > 0:
            self.current_question -= 1
            self.question_stack.setCurrentIndex(self.current_question)
            self.question_list.setCurrentRow(self.current_question)
            self.update_progress()
            
    def next_question(self):
        """Handle next button click"""
        current_page = self.question_stack.currentWidget()
        answer = current_page.get_answer()
        
        if not answer:
            QMessageBox.warning(self, "Input Required", "Please answer the question before continuing.")
            return
            
        # Store answer if we haven't already
        if len(self.answers) <= self.current_question:
            self.answers.append(answer)
        else:
            self.answers[self.current_question] = answer
            
        if self.current_question < len(self.questions) - 1:
            self.current_question += 1
            self.question_stack.setCurrentIndex(self.current_question)
            self.question_list.setCurrentRow(self.current_question)
            self.update_progress()
        else:
            self.generate_templates()
            
    def generate_templates(self):
        """Generate templates using LangChain"""
        try:
            # Update UI to show generation in progress
            self.progress.setMaximum(0)  # Show indeterminate progress
            self.next_btn.setEnabled(False)
            self.back_btn.setEnabled(False)
            self.next_btn.setText("Generating... ⚡")
            
            # Prepare the context from answers
            context = "\n".join([
                f"Q: {q['question']}\nA: {a}" 
                for q, a in zip(self.questions, self.answers)
            ])
            
            # Create progress dialog with output display
            progress_dialog = QDialog(self)
            progress_dialog.setWindowTitle("Generating Templates")
            progress_dialog.setModal(True)
            progress_dialog.setMinimumSize(800, 500)  # Increased size
            
            layout = QVBoxLayout()
            
            # Status label
            status_label = QLabel("Starting template generation...")
            status_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
            layout.addWidget(status_label)
            
            # Progress display
            output_display = QTextEdit()
            output_display.setReadOnly(True)
            output_display.setMinimumHeight(400)  # Increased height
            output_display.setAcceptRichText(True)
            output_display.setStyleSheet("""
                QTextEdit {
                    font-family: system-ui;
                    line-height: 1.4;
                    padding: 10px;
                }
                QTextEdit p {
                    margin: 0;
                    padding: 0;
                    text-align: left;
                }
            """)
            layout.addWidget(output_display)
            
            progress_dialog.setLayout(layout)
            progress_dialog.show()
            
            # Prepare context
            context = "\n".join([
                f"Q: {q}\nA: {a}" 
                for q, a in zip(self.questions, self.answers)
            ])
            
            # Create and run chain
            from qt_version.services.template_chain_service import TemplateChainService
            chain_service = TemplateChainService()
            
            def update_progress(message):
                output_display.append(message)
                # Scroll to bottom
                cursor = output_display.textCursor()
                cursor.movePosition(cursor.MoveOperation.End)
                output_display.setTextCursor(cursor)
                QApplication.processEvents()
            
            # Generate templates
            self.generated_templates = chain_service.generate_templates(
                context, 
                progress_callback=update_progress
            )
            
            if self._debug_mode:
                print("\nGenerated templates:")
                print(self.generated_templates)
            
            try:
                # Validate the templates
                if not isinstance(self.generated_templates, list):
                    self.generated_templates = [self.generated_templates]
            
                # Validate the response structure
                if not isinstance(self.generated_templates, list):
                    raise ValueError("Response must be a JSON array")
                if not all(isinstance(t, dict) for t in self.generated_templates):
                    raise ValueError("Each template must be a JSON object")
                
                # Check for required fields
                required_fields = ["name", "description", "system_prompt"]
                for template in self.generated_templates:
                    missing = [f for f in required_fields if f not in template]
                    if missing:
                        update_progress(f"⚠️ Template missing required fields: {', '.join(missing)}")
                    
                    # Ensure new fields are present
                    if "curiosity_prompt" not in template:
                        update_progress("⚠️ Adding default curiosity prompt")
                        # Create a default curiosity prompt
                        template["curiosity_prompt"] = """[SYSTEM INSTRUCTIONS - DO NOT MODIFY THIS SECTION]
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
    Return a list of questions in the specified format."""
                    
                    if "conversation_mode" not in template:
                        update_progress("⚠️ Adding default conversation mode (tracking)")
                        template["conversation_mode"] = "tracking"
                    
                    if "version" not in template:
                        template["version"] = 2
                    
                    # Ensure template has visualization settings
                    if "visualization" not in template:
                        template["visualization"] = {
                            "default_layout": "radial",
                            "node_color_scheme": "default",
                            "highlight_decisions": True,
                            "highlight_questions": True,
                            "expand_level": 1
                        }
                
                # Close dialog with success
                self.accept()
                
            except Exception as e:
                raise ValueError(f"Invalid template format: {str(e)}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate templates: {str(e)}")
            self.next_btn.setEnabled(True)
            self.back_btn.setEnabled(True)
            
    def get_generated_templates(self) -> list:
        """Return the generated templates"""
        return self.generated_templates
        
    def apply_template_to_components(self, template_name: str, components: dict):
        """Apply template settings to various components
        
        Args:
            template_name: Name of the template to apply
            components: Dictionary of components to apply settings to
        """
        try:
            # Get the template
            template = None
            for t in self.generated_templates:
                if t.get("name") == template_name:
                    template = t
                    break
                    
            if not template:
                print(f"Template not found: {template_name}")
                return
                
            # Apply to Curiosity Engine
            if "curiosity_engine" in components:
                print(f"Applying template '{template_name}' to Curiosity Engine")
                components["curiosity_engine"].set_template(template)
                
            # Apply to Conversation Compass
            if "conversation_tree_service" in components:
                print(f"Applying template '{template_name}' to Conversation Compass")
                components["conversation_tree_service"].set_template(template)
                
            # Apply to Bookmark Manager
            if "bookmark_manager" in components:
                print(f"Applying template '{template_name}' to Bookmark Manager")
                components["bookmark_manager"].set_template(template)
                
            print(f"Template '{template_name}' applied to all components")
            
        except Exception as e:
            print(f"Error applying template settings: {str(e)}")
            import traceback
            traceback.print_exc()
