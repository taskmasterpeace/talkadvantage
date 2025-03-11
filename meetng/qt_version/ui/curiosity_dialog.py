from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QRadioButton, QButtonGroup, QLineEdit,
    QWidget, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from qt_version.services.curiosity_engine import QuestionType, CuriosityQuestion

class CuriosityDialog(QDialog):
    """Dialog for asking Curiosity Engine questions"""
    
    answer_submitted = pyqtSignal(CuriosityQuestion, object)
    
    def __init__(self, question: CuriosityQuestion, parent=None, is_last_question=False, question_index=0, total_questions=1):
        super().__init__(parent)
        self.question = question
        self.is_last_question = is_last_question
        self.question_index = question_index
        self.total_questions = total_questions
        self.setWindowTitle("🤔 I'm Curious...")
        self.setModal(True)
        
        # Set proper window flags to fix maximize/minimize buttons and ensure dialog stays on top of ALL windows
        self.setWindowFlags(
            Qt.WindowType.Dialog | 
            Qt.WindowType.WindowSystemMenuHint |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool  # Add Tool flag to make it stay on top of everything
        )
        
        # Increase size significantly to ensure content is visible
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.resize(850, 650)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)  # Add more spacing between elements
        
        # Add progress indicator
        progress_text = f"Question {question_index + 1} of {total_questions}"
        progress_label = QLabel(progress_text)
        progress_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        progress_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        layout.addWidget(progress_label)
        
        # Question text
        question_label = QLabel(question.text)
        question_label.setWordWrap(True)
        question_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        question_label.setStyleSheet("""
            QLabel {
                font-size: 14pt;
                color: #2c3e50;
                margin-bottom: 15px;
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 8px;
                min-height: 60px;
            }
        """)
        layout.addWidget(question_label)
        
        # Answer section
        self.answer_widget = self._create_answer_widget()
        layout.addWidget(self.answer_widget)
        
        # Add spacer to push buttons to bottom
        layout.addStretch(1)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Change button text based on whether this is the last question
        skip_btn = QPushButton("Skip")
        skip_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        skip_btn.clicked.connect(self.skip_question)
        
        # Add close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        close_btn.clicked.connect(self.close)
        
        # Change submit button text if it's the last question
        submit_text = "Finish" if self.is_last_question else "Submit"
        submit_btn = QPushButton(submit_text)
        submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        submit_btn.clicked.connect(self.submit_answer)
        
        button_layout.addWidget(skip_btn)
        button_layout.addWidget(close_btn)
        button_layout.addWidget(submit_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def on_questions_answered(self, answered_questions):
        """Handle when questions are answered in the curiosity tab"""
        self.answered_questions = answered_questions
        self.all_answers_submitted.emit(answered_questions)
        
    def get_answer(self):
        """Get the selected/entered answer"""
        if self.question.type == QuestionType.YES_NO:
            selected = self.button_group.checkedButton()
            return selected.text() if selected else None
            
        elif self.question.type == QuestionType.MULTIPLE_CHOICE:
            selected = self.button_group.checkedButton()
            return selected.text() if selected else None
            
        elif self.question.type == QuestionType.MULTIPLE_CHOICE_FILL:
            selected = self.button_group.checkedButton()
            if not selected:
                return None
            if selected.text() == "Other:":
                return self.custom_input.text()
            return selected.text()
            
    def submit_answer(self):
        """Submit the answer"""
        answer = self.get_answer()
        if answer:
            self.answer_submitted.emit(self.question, answer)
            self.accept()
        else:
            # Visual feedback that an answer is required
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self, 
                "Answer Required", 
                "Please select an answer before submitting.",
                QMessageBox.StandardButton.Ok
            )
        
    def skip_question(self):
        """Skip the question"""
        self.answer_submitted.emit(self.question, "skipped")
        self.reject()
        
    def keyPressEvent(self, event):
        """Handle key press events"""
        from PyQt6.QtCore import Qt
        # Close dialog on Escape key
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
        
    def showEvent(self, event):
        """Override showEvent to ensure dialog gets focus"""
        super().showEvent(event)
        # Center on parent
        if self.parent():
            self.move(
                self.parent().x() + (self.parent().width() - self.width()) // 2,
                self.parent().y() + (self.parent().height() - self.height()) // 2
            )
        
        # Process events to ensure UI updates before we try to focus
        from PyQt6.QtWidgets import QApplication
        QApplication.processEvents()
        
        # Ensure dialog gets focus - multiple calls for stubborn window managers
        self.raise_()
        self.activateWindow()
        self.setFocus()
        
        # Force to front again after a short delay
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, lambda: (self.raise_(), self.activateWindow()))
        
    def closeEvent(self, event):
        """Override closeEvent to ensure proper cleanup"""
        # Emit signal with "closed" as answer if dialog is closed without submitting
        if not self.result():
            self.answer_submitted.emit(self.question, "closed")
        super().closeEvent(event)
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTabWidget, QWidget, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from qt_version.services.curiosity_engine import QuestionType, CuriosityQuestion
from qt_version.ui.curiosity_card_widget import CuriosityCardWidget
from qt_version.ui.curiosity_tab_widget import CuriosityTabWidget

class CuriosityDialog(QDialog):
    """Dialog for asking Curiosity Engine questions"""
    
    answer_submitted = pyqtSignal(CuriosityQuestion, object)
    all_answers_submitted = pyqtSignal(list)  # Signal for all answers
    
    def __init__(self, questions, parent=None):
        super().__init__(parent)
        self.questions = questions
        self.answered_questions = []
        self.setWindowTitle("🤔 Curiosity Engine")
        self.setModal(True)
        
        # Set proper window flags to fix maximize/minimize buttons and ensure dialog stays on top
        self.setWindowFlags(
            Qt.WindowType.Dialog | 
            Qt.WindowType.WindowSystemMenuHint |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        
        # Increase size significantly to ensure content is visible
        self.setMinimumWidth(900)
        self.setMinimumHeight(700)
        self.resize(950, 750)
        
        # Create main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create AI Insights tab (placeholder for now)
        self.insights_tab = QWidget()
        insights_layout = QVBoxLayout(self.insights_tab)
        insights_label = QLabel("AI Insights will be displayed here.")
        insights_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        insights_layout.addWidget(insights_label)
        
        # Create Curiosity tab with the new widget
        self.curiosity_tab = CuriosityTabWidget()
        self.curiosity_tab.questions_answered.connect(self.on_questions_answered)
        
        # Add tabs
        self.tab_widget.addTab(self.insights_tab, "AI Insights")
        self.tab_widget.addTab(self.curiosity_tab, "Curiosity")
        
        # Set Curiosity tab as active
        self.tab_widget.setCurrentIndex(1)
        
        layout.addWidget(self.tab_widget)
        
        # Add close button at the bottom
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        # Set questions in the curiosity tab
        self.curiosity_tab.set_questions(questions)
        
    def _create_answer_widget(self) -> QWidget:
        """Create the appropriate answer widget based on question type"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)  # Add more spacing between options
        
        if self.question.type == QuestionType.YES_NO:
            print("Creating YES_NO options")
            self.button_group = QButtonGroup()
            
            # Create a container widget with a more visible background
            options_container = QWidget()
            options_container.setStyleSheet("background-color: #f8f9fa; border-radius: 8px; padding: 5px;")
            options_layout = QVBoxLayout(options_container)
            
            for option in ["Yes", "No", "I don't know"]:
                radio = QRadioButton(option)
                radio.setStyleSheet("""
                    QRadioButton {
                        padding: 10px;
                        border-radius: 5px;
                        font-size: 12pt;
                        margin: 5px;
                    }
                    QRadioButton:hover {
                        background-color: #e9ecef;
                    }
                    QRadioButton:checked {
                        background-color: #d1e7dd;
                    }
                """)
                self.button_group.addButton(radio)
                options_layout.addWidget(radio)
            
            layout.addWidget(options_container)
                
        elif self.question.type in [QuestionType.MULTIPLE_CHOICE, QuestionType.MULTIPLE_CHOICE_FILL]:
            self.button_group = QButtonGroup()
            
            # Add a scroll area if there are many choices
            if self.question.choices and len(self.question.choices) > 4:
                from PyQt6.QtWidgets import QScrollArea
                scroll_area = QScrollArea()
                scroll_area.setWidgetResizable(True)
                scroll_content = QWidget()
                scroll_layout = QVBoxLayout(scroll_content)
                
                for choice in self.question.choices:
                    radio = QRadioButton(choice)
                    radio.setStyleSheet("""
                        QRadioButton {
                            padding: 10px;
                            border-radius: 5px;
                            font-size: 12pt;
                        }
                        QRadioButton:hover {
                            background-color: #f0f0f0;
                        }
                    """)
                    self.button_group.addButton(radio)
                    scroll_layout.addWidget(radio)
                
                scroll_area.setWidget(scroll_content)
                layout.addWidget(scroll_area)
            else:
                # Original implementation for fewer choices
                for choice in self.question.choices:
                    radio = QRadioButton(choice)
                    radio.setStyleSheet("""
                        QRadioButton {
                            padding: 10px;
                            border-radius: 5px;
                            font-size: 12pt;
                        }
                        QRadioButton:hover {
                            background-color: #f0f0f0;
                        }
                    """)
                    self.button_group.addButton(radio)
                    layout.addWidget(radio)
                
            if self.question.type == QuestionType.MULTIPLE_CHOICE_FILL:
                # Add custom answer option
                custom_radio = QRadioButton("Other:")
                custom_radio.setStyleSheet("""
                    QRadioButton {
                        padding: 10px;
                        border-radius: 5px;
                        font-size: 12pt;
                    }
                    QRadioButton:hover {
                        background-color: #f0f0f0;
                    }
                """)
                self.button_group.addButton(custom_radio)
                custom_layout = QHBoxLayout()
                custom_layout.addWidget(custom_radio)
                
                self.custom_input = QLineEdit()
                self.custom_input.setEnabled(False)
                self.custom_input.setStyleSheet("""
                    QLineEdit {
                        padding: 8px;
                        border: 1px solid #ddd;
                        border-radius: 5px;
                        font-size: 12pt;
                    }
                """)
                custom_layout.addWidget(self.custom_input)
                
                # Enable/disable custom input based on radio selection
                custom_radio.toggled.connect(self.custom_input.setEnabled)
                
                layout.addLayout(custom_layout)
        
        widget.setLayout(layout)
        return widget
        
    def get_answer(self):
        """Get the selected/entered answer"""
        if self.question.type == QuestionType.YES_NO:
            selected = self.button_group.checkedButton()
            return selected.text() if selected else None
            
        elif self.question.type == QuestionType.MULTIPLE_CHOICE:
            selected = self.button_group.checkedButton()
            return selected.text() if selected else None
            
        elif self.question.type == QuestionType.MULTIPLE_CHOICE_FILL:
            selected = self.button_group.checkedButton()
            if not selected:
                return None
            if selected.text() == "Other:":
                return self.custom_input.text()
            return selected.text()
            
    def submit_answer(self):
        """Submit the answer"""
        answer = self.get_answer()
        if answer:
            self.answer_submitted.emit(self.question, answer)
            self.accept()
        
    def skip_question(self):
        """Skip the question"""
        self.answer_submitted.emit(self.question, "skipped")
        self.reject()
