from .base import BaseCuriosityWidget
from qt_version.services.curiosity_engine import CuriosityQuestion, QuestionType
from PyQt6.QtCore import QDateTime

class ContextVerificationWidget(BaseCuriosityWidget):
    """Widget for verifying understanding of key points"""
    widget_type = "Context Verification"
    icon = "✓"
    purpose = "Verify understanding of key points"
    
    def process_text(self, text: str):
        """Process transcript text and generate questions"""
        try:
            # Generate questions based on transcript
            questions = self.generate_questions(text)
            
            # Set questions in widget
            self.set_questions(questions)
            
            # Show first question
            self.show_current_question()
            
            # Also update the curiosity tab if it exists
            recording_tab = self.parent()
            if hasattr(recording_tab, 'curiosity_tab'):
                print("Updating curiosity tab with context verification questions")
                recording_tab.curiosity_tab.set_questions(questions)
            
        except Exception as e:
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
            self.question_label.setText(error_html)
    
    def generate_questions(self, transcript):
        """Generate verification questions from transcript"""
        system_prompt = """You are a verification assistant.
        Generate 5 yes/no questions to verify:
        1. Key facts mentioned
        2. Decisions made
        3. Agreements reached
        Format as YES_NO questions only."""
        
        # TODO: Implement question generation using LangChain
        # For now, return sample questions
        questions = [
            CuriosityQuestion(
                type=QuestionType.YES_NO,
                text="Was there a clear decision made about the project timeline?",
                context="Decision verification",
                purpose="Verify key decisions"
            ),
            CuriosityQuestion(
                type=QuestionType.YES_NO,
                text="Did all participants agree to the proposed solution?",
                context="Agreement verification",
                purpose="Verify consensus"
            )
        ]
        
        # Add a meeting type question if transcript is long enough
        if len(transcript.split()) > 100:
            meeting_question = CuriosityQuestion(
                type=QuestionType.MEETING_TYPE,
                text="What type of meeting would you categorize this as?",
                context="Meeting classification",
                purpose="Understand meeting context",
                choices=[
                    "Discussion",
                    "Presentation",
                    "Interview",
                    "Brainstorming",
                    "Status update",
                    "Decision making"
                ]
            )
            questions.append(meeting_question)
            
        return questions
