from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, 
    QPushButton, QButtonGroup, QRadioButton,
    QLineEdit, QHBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QDateTime
from ..floating_widget import FloatingWidget
from qt_version.services.curiosity_engine import CuriosityQuestion, QuestionType

class BaseCuriosityWidget(FloatingWidget):
    """Base class for all curiosity widgets"""
    widget_type = "base"
    icon = "❓"  # Default icon
    purpose = "Base curiosity widget"
    
    answer_submitted = pyqtSignal(CuriosityQuestion, object)
    
    def __init__(self, parent=None, question_type=None, widget_id=None):
        # Stage 1: Initialize basic widget properties
        self.question_type = question_type
        widget_id = widget_id or f"curiosity_{self.question_type.lower() if question_type else 'base'}"
        super().__init__(parent, title=f"{self.icon} {self.widget_type}", widget_id=widget_id)
        
        # Stage 2: Initialize question handling
        self.questions = []
        self.current_question_index = 0
        self.answers = []
        
        # Stage 3: Initialize button group
        self.button_group = QButtonGroup(self)
        self.button_group.buttonClicked.connect(self.handle_answer)
        
        # Stage 4: Setup UI components
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the widget UI"""
        # Question display
        self.question_label = QLabel()
        self.question_label.setWordWrap(True)
        self.question_label.setStyleSheet("""
            QLabel {
                font-size: 12pt;
                color: white;
                padding: 15px;
                background-color: #2C3E50;
                border-radius: 10px;
            }
        """)
        self.content_layout.addWidget(self.question_label)
        
        # Answer area - implemented by subclasses
        self.answer_area = QWidget()
        self.answer_layout = QVBoxLayout(self.answer_area)
        self.content_layout.addWidget(self.answer_area)
        
        # Progress indicator
        self.progress_label = QLabel()
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(self.progress_label)
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        
        self.prev_btn = QPushButton("← Previous")
        self.prev_btn.clicked.connect(self.previous_question)
        nav_layout.addWidget(self.prev_btn)
        
        self.next_btn = QPushButton("Next →")
        self.next_btn.clicked.connect(self.next_question)
        nav_layout.addWidget(self.next_btn)
        
        self.content_layout.addLayout(nav_layout)
        
        self.update_navigation()
        
    def set_questions(self, questions):
        """Set the list of questions and show first one"""
        self.questions = questions
        self.current_question_index = 0
        self.answers = [None] * len(questions)
        self.show_current_question()
        
    def show_current_question(self):
        """Display current question and update UI"""
        if not self.questions:
            self.question_label.setText("No questions available")
            return
            
        question = self.questions[self.current_question_index]
        self.question_label.setText(question.text)
        self.setup_answer_widget(question)
        self.update_navigation()
        
    def setup_answer_widget(self, question):
        """Setup answer widget based on question type"""
        # Clear previous buttons
        for button in self.button_group.buttons():
            self.button_group.removeButton(button)
            button.deleteLater()
        
        # Clear previous layout properly
        while self.answer_layout.count():
            item = self.answer_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Debug output to see what choices we have
        print(f"Setting up answer widget for question type: {question.type}")
        print(f"Question text: {question.text}")
        print(f"Choices: {question.choices}")
        
        if question.type == QuestionType.YES_NO:
            options = ["Yes", "No", "Not Sure", "Skip"]
        elif question.type in [QuestionType.MULTIPLE_CHOICE, QuestionType.SPEAKER_IDENTIFICATION, QuestionType.MEETING_TYPE]:
            # Ensure we have choices to display
            if not question.choices or len(question.choices) < 2:
                print(f"Warning: No choices for question: {question.text}")
                # Add default choices based on question type
                if question.type == QuestionType.SPEAKER_IDENTIFICATION:
                    question.choices = ["Me (User)", "Another Person", "Multiple People", "Unknown"]
                elif question.type == QuestionType.MEETING_TYPE:
                    question.choices = ["Discussion", "Presentation", "Negotiation", "Interview", "Other"]
                else:
                    question.choices = ["Option 1", "Option 2", "Option 3"]
            
            options = question.choices + ["Skip"]
        else:
            options = ["Skip"]
        
        for option in options:
            radio = QRadioButton(option)
            radio.setStyleSheet("""
                QRadioButton {
                    padding: 10px;
                    margin: 5px;
                    min-height: 20px;
                    background-color: #2C3E50;
                    color: white;
                    border-radius: 5px;
                }
                QRadioButton:hover {
                    background-color: #34495E;
                }
            """)
            self.button_group.addButton(radio)
            self.answer_layout.addWidget(radio)
            
    def setup_yes_no_widget(self):
        """Setup yes/no answer widget"""
        self.button_group = QButtonGroup()
        for option in ["Yes", "No", "I don't know"]:
            radio = QRadioButton(option)
            self.button_group.addButton(radio)
            self.answer_layout.addWidget(radio)
            
    def setup_multiple_choice_widget(self, choices):
        """Setup multiple choice answer widget"""
        self.button_group = QButtonGroup()
        for choice in choices:
            radio = QRadioButton(choice)
            self.button_group.addButton(radio)
            self.answer_layout.addWidget(radio)
            
    def setup_multiple_choice_fill_widget(self, choices):
        """Setup multiple choice with custom answer widget"""
        self.button_group = QButtonGroup()
        
        # Add standard choices
        for choice in choices:
            radio = QRadioButton(choice)
            self.button_group.addButton(radio)
            self.answer_layout.addWidget(radio)
            
        # Add custom option
        custom_layout = QHBoxLayout()
        custom_radio = QRadioButton("Other:")
        self.button_group.addButton(custom_radio)
        custom_layout.addWidget(custom_radio)
        
        self.custom_input = QLineEdit()
        self.custom_input.setEnabled(False)
        custom_radio.toggled.connect(self.custom_input.setEnabled)
        custom_layout.addWidget(self.custom_input)
        
        self.answer_layout.addLayout(custom_layout)
        
    def get_current_answer(self):
        """Get the current answer value"""
        if not self.button_group:
            return None
            
        selected = self.button_group.checkedButton()
        if not selected:
            return None
            
        if hasattr(self, 'custom_input') and selected.text() == "Other:":
            return self.custom_input.text()
        return selected.text()
        
    def handle_answer(self, button):
        """Handle answer selection"""
        if not button or not self.questions:
            return
            
        answer = button.text()
        current_question = self.questions[self.current_question_index]
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        
        # Debug output
        print(f"Handling answer for question type: {current_question.type}")
        print(f"Selected answer: {answer}")
        
        # Add to transcript if not skipped or "Not Sure"
        if answer.lower() not in ['skip', 'not sure']:
            # Include question type and quoted text for speaker identification questions
            if current_question.type == QuestionType.SPEAKER_IDENTIFICATION and hasattr(current_question, 'quoted_text'):
                context_entry = f"\n[{timestamp}] Speaker Identification Q: {current_question.text}\nQuoted text: \"{current_question.quoted_text}\"\nA: {answer}\n"
            else:
                context_entry = f"\n[{timestamp}] Q: {current_question.text}\nA: {answer}\n"
                
            # Fix: Get the RecordingTab parent to access live_text
            recording_tab = self.parent()  # Get the parent widget
            if hasattr(recording_tab, 'live_text'):
                recording_tab.live_text.append(context_entry)
        
        # Store answer
        self.answers.append({
            'question': current_question.text,
            'answer': answer,
            'timestamp': timestamp
        })
        
        # Clear selection
        button.setChecked(False)
        
        # Move to next question
        self.current_question_index += 1
        if self.current_question_index < len(self.questions):
            self.show_current_question()
        else:
            # All questions answered
            self.question_label.setText("All questions completed!")
            self.answer_area.hide()
        
    def next_question(self):
        """Move to next question"""
        if self.current_question_index < len(self.questions) - 1:
            # Store current answer
            answer = self.get_current_answer()
            if answer:
                self.handle_answer(answer)
            
            self.current_question_index += 1
            self.show_current_question()
            
    def previous_question(self):
        """Move to previous question"""
        if self.current_question_index > 0:
            # Store current answer
            self.answers[self.current_question_index] = self.get_current_answer()
            
            self.current_question_index -= 1
            self.show_current_question()
            
    def update_navigation(self):
        """Update navigation buttons and progress"""
        if not self.questions:
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
            self.progress_label.setText("")
            return
            
        self.prev_btn.setEnabled(self.current_question_index > 0)
        self.next_btn.setEnabled(self.current_question_index < len(self.questions) - 1)
        
        progress = f"Question {self.current_question_index + 1} of {len(self.questions)}"
        self.progress_label.setText(progress)
