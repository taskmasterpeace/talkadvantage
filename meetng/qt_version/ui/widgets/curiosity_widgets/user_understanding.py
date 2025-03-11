from .base import BaseCuriosityWidget
from qt_version.services.curiosity_engine import CuriosityQuestion, QuestionType
from PyQt6.QtCore import QDateTime

class UserUnderstandingWidget(BaseCuriosityWidget):
    """Widget for understanding user's role and goals"""
    widget_type = "User Understanding"
    icon = "👤"
    purpose = "Understand user's role, goals, and perspective"
    
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
                print(f"Updating curiosity tab with {len(questions)} user understanding questions")
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
        """Generate questions based on transcript content"""
        try:
            from qt_version.services.curiosity_engine import CuriosityEngine
            
            # Initialize engine
            engine = CuriosityEngine()
            
            # Create template for question generation
            template = {
                "name": "user_understanding",
                "context": transcript,
                "purpose": "Generate questions to understand the discussion context"
            }
            
            # Generate questions using engine
            questions = engine.generate_questions(transcript, template)
            
            # If no questions were generated or we want to ensure specific types
            if not questions:
                # Create fallback questions
                questions = self._create_fallback_questions(transcript)
                
            # Ensure we have at least one speaker identification and meeting type question
            has_speaker_question = any(q.type == QuestionType.SPEAKER_IDENTIFICATION for q in questions)
            has_meeting_question = any(q.type == QuestionType.MEETING_TYPE for q in questions)
            
            # Add missing question types if transcript is long enough
            if len(transcript.split()) > 100:
                if not has_speaker_question:
                    speaker_question = self._create_speaker_question(transcript)
                    if speaker_question:
                        questions.append(speaker_question)
                        
                if not has_meeting_question:
                    meeting_question = self._create_meeting_question()
                    if meeting_question:
                        questions.append(meeting_question)
                
            return questions
            
        except Exception as e:
            print(f"Error generating questions: {str(e)}")
            return self._create_fallback_questions(transcript)
            
    def _create_fallback_questions(self, transcript):
        """Create fallback questions when engine fails"""
        questions = [
            CuriosityQuestion(
                type=QuestionType.YES_NO,
                text="Is this discussion meeting your expectations?",
                context="General feedback",
                purpose="Understand user satisfaction"
            ),
            CuriosityQuestion(
                type=QuestionType.MULTIPLE_CHOICE,
                text="How would you rate the clarity of this discussion?",
                context="Communication quality",
                purpose="Assess communication effectiveness",
                choices=[
                    "Very clear",
                    "Somewhat clear",
                    "Neutral",
                    "Somewhat unclear",
                    "Very unclear"
                ]
            )
        ]
        
        # Add speaker and meeting questions if transcript is long enough
        if len(transcript.split()) > 100:
            speaker_question = self._create_speaker_question(transcript)
            if speaker_question:
                questions.append(speaker_question)
                
            meeting_question = self._create_meeting_question()
            if meeting_question:
                questions.append(meeting_question)
                
        return questions
        
    def _create_speaker_question(self, transcript):
        """Create a speaker identification question"""
        try:
            # Extract a potential quote to ask about
            import re
            import random
            sentences = re.split(r'[.!?]+', transcript)
            potential_quotes = [s.strip() for s in sentences if len(s.strip()) > 20]
            
            if potential_quotes:
                quote = random.choice(potential_quotes)
                
                return CuriosityQuestion(
                    type=QuestionType.SPEAKER_IDENTIFICATION,
                    text="Who do you think said this statement?",
                    context=f"From the transcript: \"{quote}\"",
                    purpose="Identify speakers in the conversation",
                    choices=["You (the user)", "Another participant", "Multiple people", "Not sure"],
                    quoted_text=quote
                )
            return None
        except Exception as e:
            print(f"Error creating speaker question: {str(e)}")
            return None
            
    def _create_meeting_question(self):
        """Create a meeting type question"""
        return CuriosityQuestion(
            type=QuestionType.MEETING_TYPE,
            text="What type of conversation would you categorize this as?",
            context="Meeting classification",
            purpose="Understand conversation context",
            choices=[
                "Discussion",
                "Presentation",
                "Interview",
                "Brainstorming",
                "Status update",
                "Decision making"
            ]
        )
