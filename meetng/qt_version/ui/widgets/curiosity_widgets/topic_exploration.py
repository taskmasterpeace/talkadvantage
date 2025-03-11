from .base import BaseCuriosityWidget
from qt_version.services.curiosity_engine import CuriosityQuestion, QuestionType
from PyQt6.QtCore import QDateTime

class TopicExplorationWidget(BaseCuriosityWidget):
    """Widget for exploring key topics and themes in conversations"""
    widget_type = "Topic Exploration"
    icon = "🔍"
    purpose = "Explore key topics and themes in the conversation"
    
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
        """Generate topic exploration questions from transcript"""
        try:
            from qt_version.services.curiosity_engine import CuriosityEngine
            
            # Initialize engine
            engine = CuriosityEngine()
            
            # Create template for question generation
            template = {
                "name": "topic_exploration",
                "context": transcript,
                "purpose": "Generate questions to explore key topics and themes"
            }
            
            # Generate questions using engine
            questions = engine.generate_questions(transcript, template)
            
            # If no questions were generated or we want to ensure specific types
            if not questions:
                # Create fallback questions
                questions = self._create_fallback_questions(transcript)
                
            return questions
            
        except Exception as e:
            print(f"Error generating topic questions: {str(e)}")
            return self._create_fallback_questions(transcript)
            
    def _create_fallback_questions(self, transcript):
        """Create fallback questions when engine fails"""
        questions = [
            CuriosityQuestion(
                type=QuestionType.MULTIPLE_CHOICE,
                text="Which topic was most thoroughly discussed?",
                context="Topic analysis",
                purpose="Identify main discussion topics",
                choices=[
                    "Project planning",
                    "Resource allocation",
                    "Timeline/scheduling",
                    "Technical issues",
                    "Other"
                ]
            ),
            CuriosityQuestion(
                type=QuestionType.YES_NO,
                text="Were there any topics that needed more discussion time?",
                context="Topic coverage",
                purpose="Identify under-discussed topics"
            ),
            CuriosityQuestion(
                type=QuestionType.MULTIPLE_CHOICE,
                text="How would you rate the depth of topic coverage?",
                context="Discussion quality",
                purpose="Assess topic exploration depth",
                choices=[
                    "Very thorough",
                    "Adequately covered",
                    "Somewhat superficial",
                    "Too shallow",
                    "Varied by topic"
                ]
            )
        ]
        
        # Add a meeting type question if transcript is long enough
        if len(transcript.split()) > 100:
            meeting_question = CuriosityQuestion(
                type=QuestionType.MULTIPLE_CHOICE,
                text="Which topic would benefit from follow-up discussion?",
                context="Follow-up planning",
                purpose="Identify topics for future meetings",
                choices=[
                    "Technical implementation",
                    "Budget/resources",
                    "Timeline/deadlines",
                    "Team responsibilities",
                    "Stakeholder concerns"
                ]
            )
            questions.append(meeting_question)
                
        return questions
