from .base import BaseCuriosityWidget
from qt_version.services.curiosity_engine import CuriosityQuestion, QuestionType
from PyQt6.QtCore import QDateTime

class SentimentAnalysisWidget(BaseCuriosityWidget):
    """Widget for analyzing emotional context and tone"""
    widget_type = "Sentiment Analysis"
    icon = "😊"
    purpose = "Analyze emotional context and tone"
    
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
                print("Updating curiosity tab with sentiment analysis questions")
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
        """Generate sentiment analysis questions"""
        system_prompt = """You are an emotional intelligence assistant.
        Generate 5 questions to understand:
        1. Speaker's emotional state
        2. Tone of discussion
        3. Group dynamics
        Format as MULTIPLE_CHOICE with emotional scale options."""
        
        # TODO: Implement question generation using LangChain
        # For now, return sample questions
        questions = [
            CuriosityQuestion(
                type=QuestionType.MULTIPLE_CHOICE,
                text="How would you describe the overall tone of the discussion?",
                context="Tone analysis",
                purpose="Understand discussion atmosphere",
                choices=[
                    "Very positive",
                    "Somewhat positive",
                    "Neutral",
                    "Somewhat negative",
                    "Very negative"
                ]
            ),
            CuriosityQuestion(
                type=QuestionType.MULTIPLE_CHOICE,
                text="How engaged did participants seem?",
                context="Engagement analysis",
                purpose="Assess participation level",
                choices=[
                    "Highly engaged",
                    "Moderately engaged",
                    "Neutral",
                    "Somewhat disengaged",
                    "Very disengaged"
                ]
            )
        ]
        
        # Add a speaker identification question if transcript is long enough
        if len(transcript.split()) > 100:
            # Find a potential quote to ask about
            import re
            sentences = re.split(r'[.!?]+', transcript)
            potential_quotes = [s.strip() for s in sentences if len(s.strip()) > 20]
            
            if potential_quotes:
                import random
                quote = random.choice(potential_quotes)
                
                speaker_question = CuriosityQuestion(
                    type=QuestionType.SPEAKER_IDENTIFICATION,
                    text="Who do you think said this?",
                    context=f"From the transcript: \"{quote}\"",
                    purpose="Identify speakers in the conversation",
                    choices=["You (the user)", "Another participant", "Multiple people", "Not sure"],
                    quoted_text=quote
                )
                questions.append(speaker_question)
        
        return questions
