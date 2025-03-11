from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QScrollArea, QFrame, QSizePolicy,
    QMessageBox, QButtonGroup, QRadioButton, QLineEdit,
    QTextEdit, QGridLayout, QLayout, QWidgetItem, QTabWidget,
    QGraphicsOpacityEffect, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QRect, QSize, QPropertyAnimation, QEasingCurve, pyqtProperty, QTimer
from qt_version.services.curiosity_engine import CuriosityQuestion, QuestionType, QUESTION_TYPE_EMOJIS
from math import cos, radians

class FlowLayout(QLayout):
    """Custom flow layout that arranges items left-to-right, top-to-bottom"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.item_list = []
        self.spacing_x = 12
        self.spacing_y = 12
        self.max_items_per_row = 2  # Limit to 2 cards per row for better readability
        
    def addItem(self, item):
        self.item_list.append(item)
        
    def count(self):
        return len(self.item_list)
        
    def itemAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list[index]
        return None
        
    def takeAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list.pop(index)
        return None
        
    def indexOf(self, widget):
        """Find the index of a widget in the layout"""
        for i, item in enumerate(self.item_list):
            if item.widget() == widget:
                return i
        return -1
        
    def expandingDirections(self):
        return Qt.Orientation(0)
        
    def hasHeightForWidth(self):
        return True
        
    def heightForWidth(self, width):
        return self._do_layout(QRect(0, 0, width, 0), True)
        
    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, False)
        
    def sizeHint(self):
        return self.minimumSize()
        
    def minimumSize(self):
        size = QSize()
        for item in self.item_list:
            size = size.expandedTo(item.minimumSize())
        return size
        
    def setSpacing(self, spacing):
        self.spacing_x = spacing
        self.spacing_y = spacing
        
    def _do_layout(self, rect, test_only=False):
        """Layout items within the given rectangle
        
        This method positions items in a flow layout, ensuring they don't
        overlap and properly respect the container boundaries.
        
        Args:
            rect: The rectangle to layout items within
            test_only: If True, only calculate height without setting geometry
            
        Returns:
            int: The total height required for the layout
        """
        x = rect.x()
        y = rect.y()
        line_height = 0
        item_count_in_row = 0
        
        # Leave space for scroll bar (20px)
        scroll_bar_width = 20
        available_width = max(rect.width() - scroll_bar_width, 1)
        
        # Calculate item width based on available width and max items per row
        # Ensure we have at least 1px per item to avoid division by zero
        item_width = max(1, (available_width - (self.max_items_per_row - 1) * self.spacing_x) / self.max_items_per_row)
        
        for i, item in enumerate(self.item_list):
            # Skip invalid items
            if not item:
                continue
                
            # Get widget if available
            widget = item.widget()
            
            # Get item size hint
            hint = item.sizeHint()
            item_height = hint.height()
            
            # Force new row if we've reached max items per row
            if item_count_in_row >= self.max_items_per_row:
                x = rect.x()
                y = y + line_height + self.spacing_y
                line_height = 0
                item_count_in_row = 0
                
            # Set item geometry if not just testing
            if not test_only:
                # Set widget width if available
                if widget:
                    # Ensure widget is visible
                    widget.setVisible(True)
                    # Set fixed width to ensure consistent layout
                    widget.setFixedWidth(int(item_width))
                
                # Set item geometry
                item.setGeometry(QRect(int(x), int(y), int(item_width), int(item_height)))
                
            # Update position and counters
            x = x + item_width + self.spacing_x
            line_height = max(line_height, item_height)
            item_count_in_row += 1
            
        # Return total height needed for all items
        total_height = y + line_height - rect.y()
        return total_height
        
    def addWidget(self, widget):
        """Add a widget to the layout"""
        item = QWidgetItem(widget)
        self.addItem(item)
        return item

class CuriosityCardWidget(QFrame):
    """Widget for displaying and answering a curiosity question"""
    
    answer_submitted = pyqtSignal(CuriosityQuestion, str)
    
    def __init__(self, question, parent=None):
        super().__init__(parent)
        self.question = question
        self.setFrameShape(QFrame.Shape.Box)
        self.setLineWidth(1)
        
        # Set size constraints - more consistent sizing
        self.setMinimumWidth(350)  # Increased from 300
        self.setMaximumWidth(600)  # Increased from 450
        self.setMinimumHeight(180)  # Increased from 150
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        # Ensure visibility
        self.setVisible(True)
        
        # We'll store the original geometry during hover events
        self.original_geometry = None
        
        # Style based on question type
        self._set_style_for_question_type()
            
        self._init_ui()
        
        # Add fade-in animation
        self._setup_fade_in_animation()
        
    def _set_style_for_question_type(self):
        """Set style based on question type"""
        base_style = """
            QFrame {
                border-radius: 8px;
                margin: 5px;
                color: white;
                border: 1px solid #1B2631;
            }
            QFrame:hover {
                border: 2px solid #3498DB;
            }
            QLabel {
                color: white;
            }
            QRadioButton {
                color: white;
                background-color: rgba(255, 255, 255, 0.1);
                padding: 10px;  /* Increased from 8px */
                margin: 5px 0px;  /* Increased from 4px */
                border-radius: 4px;
            }
            QRadioButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
            QRadioButton:checked {
                background-color: rgba(255, 255, 255, 0.3);
                font-weight: bold;
            }
        """
        
        self.setStyleSheet(base_style)
        
    def _setup_fade_in_animation(self):
        """Set up and start the fade-in animation"""
        opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(opacity_effect)
        
        self.fade_animation = QPropertyAnimation(opacity_effect, b"opacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade_animation.start()

    # Add hover event handlers for scale animation
    def enterEvent(self, event):
        """Handle mouse enter event with scale animation"""
        # Don't animate if we're still in the initial layout phase
        if not self.isVisible() or not self.width() or not self.height():
            super().enterEvent(event)
            return
            
        # Store current geometry before animation
        current_rect = self.geometry()
        
        # Calculate expansion (grow from center)
        expand_x = 5
        expand_y = 5
        target_rect = QRect(
            current_rect.x() - expand_x, 
            current_rect.y() - expand_y,
            current_rect.width() + (expand_x * 2), 
            current_rect.height() + (expand_y * 2)
        )
        
        # Create scale animation
        self.scale_animation = QPropertyAnimation(self, b"geometry")
        self.scale_animation.setDuration(150)
        self.scale_animation.setStartValue(current_rect)
        self.scale_animation.setEndValue(target_rect)
        self.scale_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.scale_animation.start()
        
        # Store original geometry for leave event
        self.original_geometry = current_rect
        
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Handle mouse leave event with scale animation"""
        # Don't animate if we're still in the initial layout phase
        if not self.isVisible() or not self.width() or not self.height():
            super().leaveEvent(event)
            return
            
        if hasattr(self, 'original_geometry') and self.original_geometry:
            current_rect = self.geometry()
            
            # Create scale animation
            self.scale_animation = QPropertyAnimation(self, b"geometry")
            self.scale_animation.setDuration(150)
            self.scale_animation.setStartValue(current_rect)
            self.scale_animation.setEndValue(self.original_geometry)
            self.scale_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.scale_animation.start()
        
        super().leaveEvent(event)
        
        
    def _init_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins to allow header to touch edges
        layout.setSpacing(0)  # Remove spacing between header and content
        
        # Get emoji for question type
        emoji = QUESTION_TYPE_EMOJIS.get(self.question.type, "❓")
        
        # Create header with emoji and question
        header_widget = QWidget()
        
        # Set header color based on question type
        if self.question.type == QuestionType.YES_NO:
            header_color = "#1976D2"  # Blue
        elif self.question.type == QuestionType.MULTIPLE_CHOICE:
            header_color = "#388E3C"  # Green
        elif self.question.type == QuestionType.SPEAKER_IDENTIFICATION:
            header_color = "#7B1FA2"  # Purple
        elif self.question.type == QuestionType.MEETING_TYPE:
            header_color = "#E64A19"  # Orange
        else:
            header_color = "#455A64"  # Blue-grey
        
        header_widget.setStyleSheet(f"""
            background-color: {header_color};
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
        """)
        
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(8, 4, 8, 4)  # Reduced vertical padding
        
        # Add emoji to header
        emoji_label = QLabel(emoji)
        emoji_label.setStyleSheet("font-size: 16px; color: white;")  # Smaller emoji
        header_layout.addWidget(emoji_label, 0)  # No stretch
        
        # Add question text to header
        question_label = QLabel(self.question.text)
        question_label.setWordWrap(True)
        question_label.setStyleSheet("font-weight: bold; font-size: 16px; color: white;")
        header_layout.addWidget(question_label, 1)  # Give stretch factor
        
        layout.addWidget(header_widget)
        
        # Content area
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            background-color: #2C3E50;
            border-bottom-left-radius: 8px;
            border-bottom-right-radius: 8px;
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(12, 6, 12, 6)  # Reduced vertical padding
        content_layout.setSpacing(4)  # Reduced spacing between elements
        
        # Context (if available)
        if self.question.context:
            context_layout = QHBoxLayout()
            
            # Add context emoji
            context_emoji = QLabel("📝")
            context_emoji.setStyleSheet("font-size: 14px;")
            context_layout.addWidget(context_emoji)
            
            # Add context label with improved readability
            context_label = QLabel("Context: " + self.question.context)
            context_label.setWordWrap(True)
            context_label.setStyleSheet("font-style: italic; color: #BBDEFB; font-size: 14px;")  # Increased from 11px
            context_layout.addWidget(context_label, 1)  # Give it stretch factor
            
            content_layout.addLayout(context_layout)
            
        # Answer area
        self.answer_widget = QWidget()
        self.answer_layout = QVBoxLayout(self.answer_widget)
        self.answer_layout.setContentsMargins(0, 4, 0, 0)  # Reduced top padding
        self.answer_layout.setSpacing(2)  # Tighter spacing between options
        
        # Create appropriate input based on question type
        if self.question.type == QuestionType.YES_NO:
            self._create_yes_no_buttons()
        elif self.question.type in [QuestionType.MULTIPLE_CHOICE, QuestionType.MULTIPLE_CHOICE_FILL, 
                                   QuestionType.SPEAKER_IDENTIFICATION, QuestionType.MEETING_TYPE]:
            self._create_multiple_choice()
        else:
            self._create_text_input()
            
        content_layout.addWidget(self.answer_widget)
        
        # Status label for showing when answered
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 11px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.status_label.setVisible(False)
        content_layout.addWidget(self.status_label)
        
        layout.addWidget(content_widget)
        
    def _create_multiple_choice(self):
        """Create multiple choice options"""
        self.option_group = QButtonGroup(self)
        
        # Ensure we have choices to display
        if not self.question.choices:
            print(f"Warning: No choices for question: {self.question.text}")
            # Add default choices based on question type
            if self.question.type == QuestionType.SPEAKER_IDENTIFICATION:
                self.question.choices = ["Me (User)", "Another Person", "Multiple People", "Unknown"]
            elif self.question.type == QuestionType.MEETING_TYPE:
                self.question.choices = ["Discussion", "Presentation", "Negotiation", "Interview", "Other"]
            else:
                self.question.choices = ["Option 1", "Option 2", "Option 3"]
        
        # Create radio buttons for each choice
        for i, option in enumerate(self.question.choices):
            radio = QRadioButton(option)
            radio.setStyleSheet("""
                QRadioButton {
                    padding: 8px;
                    margin: 4px 0px;
                    border-radius: 4px;
                }
                QRadioButton:hover {
                    background-color: rgba(0, 0, 0, 0.05);
                }
            """)
            # Connect directly to submit when clicked
            radio.clicked.connect(lambda checked=False, opt=option: self._on_option_selected(opt))
            self.option_group.addButton(radio, i)
            self.answer_layout.addWidget(radio)
            
        # Add "Other" option for MULTIPLE_CHOICE_FILL
        if self.question.type == QuestionType.MULTIPLE_CHOICE_FILL:
            other_radio = QRadioButton("Other:")
            self.option_group.addButton(other_radio, len(self.question.choices))
            
            other_layout = QHBoxLayout()
            other_layout.addWidget(other_radio)
            
            self.other_input = QLineEdit()
            self.other_input.setEnabled(False)
            other_radio.toggled.connect(lambda checked: self.other_input.setEnabled(checked))
            other_layout.addWidget(self.other_input)
            
            self.answer_layout.addLayout(other_layout)
            
    def _create_yes_no_buttons(self):
        """Create Yes/No buttons"""
        button_layout = QHBoxLayout()
        
        self.yes_btn = QPushButton("✓ Yes")
        self.yes_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
            QPushButton:disabled {
                background-color: #A5D6A7;
            }
        """)
        self.yes_btn.clicked.connect(lambda: self._on_yes_no("Yes"))
        button_layout.addWidget(self.yes_btn)
        
        self.no_btn = QPushButton("✗ No")
        self.no_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
            QPushButton:disabled {
                background-color: #FFCDD2;
            }
        """)
        self.no_btn.clicked.connect(lambda: self._on_yes_no("No"))
        button_layout.addWidget(self.no_btn)
        
        # Not sure button
        self.not_sure_btn = QPushButton("? Not Sure")
        self.not_sure_btn.setStyleSheet("""
            QPushButton {
                background-color: #607D8B;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                color: white;
            }
            QPushButton:hover {
                background-color: #455A64;
            }
            QPushButton:disabled {
                background-color: #B0BEC5;
            }
        """)
        self.not_sure_btn.clicked.connect(lambda: self._on_yes_no("Not Sure"))
        button_layout.addWidget(self.not_sure_btn)
        
        self.answer_layout.addLayout(button_layout)
        
    def _create_text_input(self):
        """Create text input for free-form answers"""
        self.answer_text = QTextEdit()
        self.answer_text.setMaximumHeight(80)
        self.answer_text.setPlaceholderText("Enter your answer...")
        self.answer_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                background-color: white;
                padding: 4px;
            }
            QTextEdit:focus {
                border: 1px solid #2196F3;
            }
        """)
        self.answer_layout.addWidget(self.answer_text)
        
        # Add a submit button for text input
        self.submit_text_btn = QPushButton("📤 Submit")
        self.submit_text_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #BBDEFB;
            }
        """)
        self.submit_text_btn.clicked.connect(self._on_text_submit)
        self.answer_layout.addWidget(self.submit_text_btn)
        
    def _show_answer_animation(self):
        """Show checkmark animation when answer is submitted"""
        # Create checkmark overlay with transparent background
        self.checkmark = QLabel("✓", self)
        self.checkmark.setStyleSheet("""
            font-size: 0px;
            color: #4CAF50;
            background-color: transparent;
            border-radius: 25px;
            font-weight: bold;
        """)
        self.checkmark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.checkmark.resize(50, 50)
        
        # Convert float coordinates to integers for move method
        x_pos = int(self.width()/2 - 25)
        y_pos = int(self.height()/2 - 25)
        self.checkmark.move(x_pos, y_pos)
        
        self.checkmark.show()
        
        # Animate checkmark
        self.check_animation = QPropertyAnimation(self.checkmark, b"styleSheet")
        self.check_animation.setDuration(500)
        self.check_animation.setStartValue("font-size: 0px; color: #4CAF50; background-color: transparent; border-radius: 25px; font-weight: bold;")
        self.check_animation.setEndValue("font-size: 40px; color: #4CAF50; background-color: transparent; border-radius: 25px; font-weight: bold;")
        self.check_animation.start()
        
        # Start fade out animation after a delay
        QTimer.singleShot(1000, lambda: self._start_fade_out())

    def _start_fade_out(self):
        """Start fade out animation for the card with a pulse effect"""
        # Create a sequence of animations
        
        # 1. First, create a subtle pulse effect
        pulse_anim = QPropertyAnimation(self, b"geometry")
        pulse_anim.setDuration(300)
        
        current_rect = self.geometry()
        expanded_rect = QRect(
            current_rect.x() - 5,
            current_rect.y() - 5,
            current_rect.width() + 10,
            current_rect.height() + 10
        )
        
        pulse_anim.setStartValue(current_rect)
        pulse_anim.setEndValue(expanded_rect)
        pulse_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        # 2. Then, create a fade out animation
        fade_out = QPropertyAnimation(self, b"windowOpacity")
        fade_out.setDuration(500)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.3)
        fade_out.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Start the sequence
        pulse_anim.start()
        QTimer.singleShot(300, lambda: fade_out.start())
        
    def _on_option_selected(self, option):
        """Handle option selection for multiple choice"""
        self.question.answer = option
        
        # Show answered status
        self.status_label.setText("✓ Answered")
        self.status_label.setVisible(True)
        
        # Update styling for all buttons
        for button in self.option_group.buttons():
            if button.text() == option:
                button.setEnabled(True)
                button.setStyleSheet("""
                    QRadioButton {
                        background-color: rgba(33, 150, 243, 0.2);
                        color: #FFFFFF;
                        font-weight: bold;
                        padding: 8px;
                        margin: 4px 0px;
                        border-radius: 4px;
                        border-left: 3px solid #2196F3;
                    }
                """)
            else:
                button.setEnabled(False)
                button.setStyleSheet("""
                    QRadioButton {
                        color: #BBBBBB;
                        padding: 8px;
                        margin: 4px 0px;
                        border-radius: 4px;
                        background-color: rgba(0, 0, 0, 0.1);
                    }
                """)
        
        # Emit signal immediately before animation
        self.answer_submitted.emit(self.question, self.question.answer)
        
        # Show answer animation
        self._show_answer_animation()
        
    def _on_yes_no(self, answer):
        """Handle Yes/No button click"""
        self.question.answer = answer
        
        # Show answered status
        self.status_label.setText("✓ Answered")
        self.status_label.setVisible(True)
        
        # Disable all buttons
        self.yes_btn.setEnabled(False)
        self.no_btn.setEnabled(False)
        self.not_sure_btn.setEnabled(False)
        
        # Keep the selected button enabled but with a different style
        if answer == "Yes":
            self.yes_btn.setEnabled(True)
            self.yes_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    color: white;
                    font-weight: bold;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                }
            """)
        elif answer == "No":
            self.no_btn.setEnabled(True)
            self.no_btn.setStyleSheet("""
                QPushButton {
                    background-color: #F44336;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    color: white;
                    font-weight: bold;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                }
            """)
        else:
            self.not_sure_btn.setEnabled(True)
            self.not_sure_btn.setStyleSheet("""
                QPushButton {
                    background-color: #607D8B;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    color: white;
                    font-weight: bold;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                }
            """)
        
        # Emit signal immediately before animation
        self.answer_submitted.emit(self.question, self.question.answer)
        
        # Show answer animation
        self._show_answer_animation()
        
    def _on_text_submit(self):
        """Handle text submission"""
        answer = self.answer_text.toPlainText().strip()
        if answer:
            self.question.answer = answer
            
            # Show answered status
            self.status_label.setText("✓ Answered")
            self.status_label.setVisible(True)
            
            # Disable further editing
            self.answer_text.setReadOnly(True)
            self.answer_text.setStyleSheet("""
                QTextEdit {
                    border: 1px solid #4CAF50;
                    border-radius: 4px;
                    background-color: #F1F8E9;
                    padding: 4px;
                }
            """)
            
            self.submit_text_btn.setEnabled(False)
            self.submit_text_btn.setText("✓ Submitted")
            self.submit_text_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-weight: bold;
                }
            """)
            
            # Emit signal immediately before animation
            self.answer_submitted.emit(self.question, self.question.answer)
            
            # Show answer animation
            self._show_answer_animation()

class CuriosityTabWidget(QWidget):
    """Widget for displaying and managing curiosity questions as cards"""
    
    questions_answered = pyqtSignal(list)  # Signal emitted when questions are answered
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.questions = []
        self.answered_questions = []
        self.card_widgets = []
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Empty state message
        self.empty_label = QLabel("No questions generated yet. Use the 'Refresh Questions' button in Analysis Tools.")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 14pt;
                padding: 20px;
            }
        """)
        main_layout.addWidget(self.empty_label)
        
        # Scroll area for question cards
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.StyledPanel)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #ddd;
                background-color: #f9f9f9;
                border-radius: 4px;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 14px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #bbb;
                min-height: 20px;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical:hover {
                background: #999;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Container widget for cards
        self.cards_container = QWidget()
        self.cards_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Use a grid layout for 3 columns
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setSpacing(10)
        self.cards_layout.setContentsMargins(10, 10, 10, 10)
        
        # Set the container as the scroll area widget
        self.scroll_area.setWidget(self.cards_container)
        
        # Add scroll area to main layout with stretch factor
        main_layout.addWidget(self.scroll_area, 1)
        
    def set_questions(self, questions):
        """Set the questions to display"""
        self.clear_all_questions()
        self.questions = questions
        
        if not questions:
            self.empty_label.setText("No questions generated. Use the 'Refresh Questions' button in Analysis Tools.")
            self.empty_label.setVisible(True)
            self.scroll_area.setVisible(False)
            return
            
        # Hide the empty label when showing questions
        self.empty_label.setVisible(False)
        self.scroll_area.setVisible(True)
        
        # Create card widgets for each question
        for question in questions:
            self.add_question_card(question)
            
        # Force layout update
        self.cards_container.updateGeometry()
        self.scroll_area.updateGeometry()
        
        # Ensure the scroll area is visible and sized correctly
        self.scroll_area.setMinimumHeight(300)
        self.update()
        
    def add_question_card(self, question):
        """Add a question card to the layout"""
        card = CuriosityCardWidget(question, self)
        card.answer_submitted.connect(self.on_answer_submitted)
        
        # Make sure card is visible and has proper size
        card.setVisible(True)
        card.setMinimumHeight(180)  # Increased from 150
        
        # Calculate position in grid (3 columns)
        row = len(self.card_widgets) // 3
        col = len(self.card_widgets) % 3
        
        # Add to grid layout
        self.cards_layout.addWidget(card, row, col)
        self.card_widgets.append(card)
        
    def on_answer_submitted(self, question, answer):
        """Handle when a question is answered"""
        # Add to answered questions if not already there
        if question not in [q for q, _ in self.answered_questions]:
            self.answered_questions.append((question, answer))
        
        # Update UI state
        self.update_ui_state()
        
        # Find the card widget that was answered
        answered_card = None
        for card in self.card_widgets:
            if card.question == question:
                answered_card = card
                break
        
        if answered_card:
            # Start fade out animation for the card
            self._animate_card_removal(answered_card)
        
        # Automatically add to transcript
        self.questions_answered.emit([(question, answer)])
        
    def _animate_card_removal(self, card):
        """Animate the removal of a card and rearrange remaining cards"""
        # Create fade out animation
        opacity_effect = QGraphicsOpacityEffect(card)
        card.setGraphicsEffect(opacity_effect)
        
        fade_out = QPropertyAnimation(opacity_effect, b"opacity")
        fade_out.setDuration(800)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # When animation finishes, remove the card and rearrange
        fade_out.finished.connect(lambda: self._remove_card_and_rearrange(card))
        
        # Start animation
        fade_out.start()

    def _remove_card_and_rearrange(self, card):
        """Remove a card and rearrange the remaining cards"""
        # Store current positions of all cards
        positions = {}
        for c in self.card_widgets:
            if c != card:  # Skip the card being removed
                positions[c] = c.geometry()
        
        # Remove the card from layout and list
        index = self.cards_layout.indexOf(card)
        if index != -1:
            self.cards_layout.takeAt(index)
        
        if card in self.card_widgets:
            self.card_widgets.remove(card)
        
        # Delete the card widget
        card.deleteLater()
        
        # Rearrange remaining cards
        self._rearrange_cards(positions)

    def _rearrange_cards(self, old_positions):
        """Rearrange cards with animation after one is removed"""
        # Recalculate layout
        self.cards_container.updateGeometry()
        QApplication.processEvents()
        
        # Animate cards to their new positions
        for card in self.card_widgets:
            if card in old_positions:
                # Get new position
                new_pos = card.geometry()
                
                # Reset to old position for animation
                card.setGeometry(old_positions[card])
                
                # Create animation to new position
                anim = QPropertyAnimation(card, b"geometry")
                anim.setDuration(300)
                anim.setStartValue(old_positions[card])
                anim.setEndValue(new_pos)
                anim.setEasingCurve(QEasingCurve.Type.OutCubic)
                anim.start()
        
    def update_ui_state(self):
        """Update UI state based on questions and answers"""
        # Update empty state message
        if not self.questions:
            self.empty_label.setText("Questions will be generated automatically when you process text (F12).")
            self.empty_label.setVisible(True)
        else:
            # Make sure empty label is hidden when there are questions
            self.empty_label.setVisible(False)
            
    def generate_questions_clicked(self):
        """Signal that the Generate Questions button was clicked"""
        # This will be connected to a method in the main window
        pass
        
    def refresh_questions(self):
        """Refresh the questions"""
        # Show loading indicator IN THE TAB
        self.empty_label.setText("Generating new questions...")
        self.empty_label.setVisible(True)
        
        # Find the RecordingTab parent
        recording_tab = None
        parent = self.parent()
        
        # Try to find RecordingTab in the parent hierarchy
        while parent:
            if hasattr(parent, 'refresh_curiosity_questions'):
                recording_tab = parent
                break
            parent = parent.parent()
        
        if recording_tab:
            print(f"Found RecordingTab parent, calling refresh_curiosity_questions")
            recording_tab.refresh_curiosity_questions()
        else:
            print("Could not find RecordingTab parent")
            self.empty_label.setText("Cannot generate questions - please use the main refresh button")
        
    def clear_all_questions(self):
        """Clear all questions and reset the UI"""
        # Remove all card widgets
        for card in self.card_widgets:
            # Find the item in the layout
            index = self.cards_layout.indexOf(card)
            if index != -1:
                # Remove from layout
                self.cards_layout.takeAt(index)
            card.deleteLater()
            
        self.card_widgets = []
        self.questions = []
        self.answered_questions = []
        
        # Show empty state
        self.empty_label.setText("Questions will be generated automatically when you process text (F12).")
        self.empty_label.setVisible(True)
        self.scroll_area.setVisible(False)
        
        # Update UI state
        self.update_ui_state()
        
        # Emit signal with empty list to notify parent
        self.questions_answered.emit([])
        
