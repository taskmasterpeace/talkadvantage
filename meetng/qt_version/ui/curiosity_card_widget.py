from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QRadioButton, QButtonGroup, QLineEdit,
    QFrame, QSizePolicy, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QRect, QEasingCurve, QTimer
from PyQt6.QtGui import QColor, QPalette
from qt_version.services.curiosity_engine import QuestionType, CuriosityQuestion

class CuriosityCardWidget(QFrame):
    """A card widget for displaying and answering a curiosity question"""
    
    answer_submitted = pyqtSignal(CuriosityQuestion, object)
    
    def __init__(self, question: CuriosityQuestion, parent=None):
        super().__init__(parent)
        self.question = question
        self.is_answered = False
        self.is_expanded = True
        self.answer = None
        
        # Set up frame appearance
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setLineWidth(1)
        self.setMidLineWidth(0)
        
        # Apply card styling
        self.setStyleSheet("""
            CuriosityCardWidget {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                margin: 8px;
            }
            CuriosityCardWidget:hover {
                border: 1px solid #c0c0c0;
                background-color: #f9f9f9;
            }
        """)
        
        # Set minimum size
        self.setMinimumHeight(100)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        # Create layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(10)
        
        # Create header with question text and expand/collapse button
        self.header_layout = QHBoxLayout()
        
        # Question type indicator (color coded by type)
        self.type_indicator = QLabel()
        self.type_indicator.setFixedSize(12, 12)
        self.type_indicator.setStyleSheet(self._get_type_indicator_style())
        self.header_layout.addWidget(self.type_indicator)
        
        # Question text
        self.question_label = QLabel(question.text)
        self.question_label.setWordWrap(True)
        self.question_label.setStyleSheet("""
            QLabel {
                font-size: 14pt;
                font-weight: bold;
                color: #2c3e50;  /* Darker blue color that contrasts with backgrounds */
                background-color: transparent;  /* Ensure background is transparent */
            }
        """)
        self.header_layout.addWidget(self.question_label, 1)
        
        # Expand/collapse button
        self.expand_button = QPushButton("▼")
        self.expand_button.setFixedSize(24, 24)
        self.expand_button.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                color: #7f8c8d;
            }
            QPushButton:hover {
                color: #2c3e50;
            }
        """)
        self.expand_button.clicked.connect(self.toggle_expanded)
        self.header_layout.addWidget(self.expand_button)
        
        self.main_layout.addLayout(self.header_layout)
        
        # Separator line
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.Shape.HLine)
        self.separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.separator.setStyleSheet("background-color: #e0e0e0;")
        self.main_layout.addWidget(self.separator)
        
        # Content area (will be hidden when collapsed)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create answer widget based on question type
        self.answer_widget = self._create_answer_widget()
        self.content_layout.addWidget(self.answer_widget)
        
        # Add buttons
        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch()
        
        # Skip button
        self.skip_button = QPushButton("Skip")
        self.skip_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        self.skip_button.clicked.connect(self.skip_question)
        self.button_layout.addWidget(self.skip_button)
        
        # Submit button
        self.submit_button = QPushButton("Submit")
        self.submit_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.submit_button.clicked.connect(self.submit_answer)
        self.button_layout.addWidget(self.submit_button)
        
        self.content_layout.addLayout(self.button_layout)
        self.main_layout.addWidget(self.content_widget)
        
        # Status indicator (shows after answering)
        self.status_widget = QWidget()
        self.status_widget.setVisible(False)
        self.status_layout = QHBoxLayout(self.status_widget)
        
        self.status_icon = QLabel("✓")
        self.status_icon.setStyleSheet("color: #28a745; font-size: 14pt;")
        self.status_layout.addWidget(self.status_icon)
        
        self.status_text = QLabel("Answered")
        self.status_text.setStyleSheet("color: #28a745;")
        self.status_layout.addWidget(self.status_text)
        
        self.status_layout.addStretch()
        
        self.main_layout.addWidget(self.status_widget)
        
    def _get_type_indicator_style(self) -> str:
        """Get the style for the question type indicator"""
        if self.question.type == QuestionType.YES_NO:
            return "background-color: #3498db; border-radius: 6px;"
        elif self.question.type == QuestionType.MULTIPLE_CHOICE:
            return "background-color: #2ecc71; border-radius: 6px;"
        else:  # MULTIPLE_CHOICE_FILL
            return "background-color: #9b59b6; border-radius: 6px;"
    
    def _create_answer_widget(self) -> QWidget:
        """Create the appropriate answer widget based on question type"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        
        if self.question.type == QuestionType.YES_NO:
            self.button_group = QButtonGroup()
            
            for option in ["Yes", "No", "I don't know"]:
                radio = QRadioButton(option)
                radio.setStyleSheet("""
                    QRadioButton {
                        padding: 8px;
                        border-radius: 4px;
                        font-size: 12pt;
                    }
                    QRadioButton:hover {
                        background-color: #f0f0f0;
                    }
                    QRadioButton:checked {
                        background-color: #d1e7dd;
                    }
                """)
                self.button_group.addButton(radio)
                # Connect toggled signal to auto-submit
                radio.toggled.connect(lambda checked, btn=radio: self.auto_submit(checked, btn))
                layout.addWidget(radio)
                
        elif self.question.type in [QuestionType.MULTIPLE_CHOICE, QuestionType.MULTIPLE_CHOICE_FILL]:
            self.button_group = QButtonGroup()
            
            # Add a scroll area if there are many choices
            if self.question.choices and len(self.question.choices) > 4:
                scroll_area = QScrollArea()
                scroll_area.setWidgetResizable(True)
                scroll_content = QWidget()
                scroll_layout = QVBoxLayout(scroll_content)
                
                for choice in self.question.choices:
                    radio = QRadioButton(choice)
                    radio.setStyleSheet("""
                        QRadioButton {
                            padding: 8px;
                            border-radius: 4px;
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
                            padding: 8px;
                            border-radius: 4px;
                            font-size: 12pt;
                        }
                        QRadioButton:hover {
                            background-color: #f0f0f0;
                        }
                    """)
                    self.button_group.addButton(radio)
                    # Connect toggled signal to auto-submit
                    radio.toggled.connect(lambda checked, btn=radio: self.auto_submit(checked, btn))
                    layout.addWidget(radio)
                
            if self.question.type == QuestionType.MULTIPLE_CHOICE_FILL:
                # Add custom answer option
                custom_radio = QRadioButton("Other:")
                custom_radio.setStyleSheet("""
                    QRadioButton {
                        padding: 8px;
                        border-radius: 4px;
                        font-size: 12pt;
                    }
                    QRadioButton:hover {
                        background-color: #f0f0f0;
                    }
                """)
                self.button_group.addButton(custom_radio)
                # Connect toggled signal to auto-submit (but not for custom option)
                custom_layout = QHBoxLayout()
                custom_layout.addWidget(custom_radio)
                
                self.custom_input = QLineEdit()
                self.custom_input.setEnabled(False)
                self.custom_input.setStyleSheet("""
                    QLineEdit {
                        padding: 8px;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        font-size: 12pt;
                        background-color: #ffffff;  /* Explicitly set background */
                        color: #333333;  /* Explicitly set text color */
                    }
                    QLineEdit:focus {
                        border: 1px solid #80bdff;
                    }
                """)
                custom_layout.addWidget(self.custom_input)
                
                # Enable/disable custom input based on radio selection
                custom_radio.toggled.connect(self._handle_custom_toggle)
                
                layout.addLayout(custom_layout)
        
        return widget
    
    def _handle_custom_toggle(self, checked):
        """Handle toggling of the 'Other' option"""
        self.custom_input.setEnabled(checked)
        if checked:
            self.custom_input.setFocus()
            # Animate the custom input to make it more prominent
            self.custom_input.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    border: 2px solid #80bdff;
                    border-radius: 4px;
                    font-size: 12pt;
                    background-color: #f8f9fa;
                }
            """)
        else:
            self.custom_input.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    font-size: 12pt;
                }
            """)
    
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
            self.answer = answer
            self.is_answered = True
            self.answer_submitted.emit(self.question, answer)
            self._update_appearance()
            self.toggle_expanded()  # Collapse after answering
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
        self.answer = "skipped"
        self.is_answered = True
        self.answer_submitted.emit(self.question, "skipped")
        self._update_appearance()
        self.toggle_expanded()  # Collapse after skipping
    
    def toggle_expanded(self):
        """Toggle between expanded and collapsed states"""
        self.is_expanded = not self.is_expanded
        
        # Update button text
        self.expand_button.setText("▼" if self.is_expanded else "►")
        
        # Show/hide content
        self.content_widget.setVisible(self.is_expanded)
        
        # Show status if answered and collapsed
        self.status_widget.setVisible(self.is_answered and not self.is_expanded)
        
        # Animate height change
        self.adjustSize()
    
    def auto_submit(self, checked, button):
        """Auto-submit when a radio button is selected"""
        if checked:  # Only submit when button is checked (not when unchecked)
            # Short delay to allow UI to update
            QTimer.singleShot(100, lambda: self.submit_answer())
    
    def _update_appearance(self):
        """Update appearance after answering"""
        if self.is_answered:
            # Update status text
            if self.answer == "skipped":
                self.status_icon.setText("⟳")
                self.status_icon.setStyleSheet("color: #6c757d; font-size: 14pt;")
                self.status_text.setText("Skipped")
                self.status_text.setStyleSheet("color: #6c757d;")
            else:
                self.status_icon.setText("✓")
                self.status_icon.setStyleSheet("color: #28a745; font-size: 14pt;")
                self.status_text.setText("Answered: " + self.answer[:20] + ("..." if len(self.answer) > 20 else ""))
                self.status_text.setStyleSheet("color: #28a745;")
            
            # Disable input controls
            for button in self.button_group.buttons():
                button.setEnabled(False)
            
            if hasattr(self, 'custom_input'):
                self.custom_input.setEnabled(False)
            
            # Disable buttons
            self.submit_button.setEnabled(False)
            self.skip_button.setEnabled(False)
            
            # Add subtle background color to indicate answered state
            self.setStyleSheet("""
                CuriosityCardWidget {
                    background-color: #f8f9fa;
                    border-radius: 8px;
                    border: 1px solid #e0e0e0;
                    margin: 8px;
                }
                CuriosityCardWidget:hover {
                    border: 1px solid #c0c0c0;
                }
            """)
