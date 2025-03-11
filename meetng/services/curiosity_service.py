import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

class CuriosityService:
    """Service for managing the Curiosity Engine functionality"""
    
    def __init__(self, langchain_service=None):
        self.langchain_service = langchain_service
        self.questions_history = []
        self.answers_history = {}
        self.insights = {}
        
    def generate_questions(self, transcript: str, template_name: str = None) -> List[Dict[str, Any]]:
        """Generate contextual questions based on transcript content
        
        Args:
            transcript: The conversation transcript text
            template_name: Optional template name to use specific curiosity prompt
            
        Returns:
            List of question objects with type, text, and options
        """
        try:
            # Get template-specific curiosity prompt if available
            curiosity_prompt = None
            if template_name and self.langchain_service:
                template = self.langchain_service.get_template(template_name)
                if template and "curiosity_prompt" in template:
                    curiosity_prompt = template["curiosity_prompt"]
            
            # Use the Curiosity Engine to generate questions
            if self.langchain_service:
                questions = self.langchain_service.generate_curiosity_questions(
                    transcript, 
                    max_questions=3,
                    custom_prompt=curiosity_prompt
                )
                
                # Store questions in history
                timestamp = datetime.now().isoformat()
                for question in questions:
                    question["timestamp"] = timestamp
                    question["answered"] = False
                    self.questions_history.append(question)
                    
                return questions
            else:
                # Fallback questions if LangChain service is not available
                return self._generate_fallback_questions()
                
        except Exception as e:
            print(f"Error generating questions: {str(e)}")
            return self._generate_fallback_questions()
    
    def _generate_fallback_questions(self) -> List[Dict[str, Any]]:
        """Generate fallback questions when LangChain fails"""
        return [
            {
                "type": "yes_no",
                "text": "Is this conversation meeting your expectations?",
                "timestamp": datetime.now().isoformat(),
                "answered": False
            },
            {
                "type": "multiple_choice",
                "text": "What type of meeting is this?",
                "options": ["Discussion", "Presentation", "Interview", "Brainstorming", "Other"],
                "timestamp": datetime.now().isoformat(),
                "answered": False
            }
        ]
    
    def process_answer(self, question_id: str, answer: Any) -> None:
        """Process and store a user's answer to a question
        
        Args:
            question_id: Unique identifier for the question
            answer: The user's answer (string, boolean, or option index)
        """
        # Find the question in history
        for question in self.questions_history:
            if question.get("id") == question_id:
                # Mark as answered
                question["answered"] = True
                
                # Store the answer
                self.answers_history[question_id] = {
                    "question": question["text"],
                    "answer": answer,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Update insights based on answer
                self._update_insights(question, answer)
                break
    
    def _update_insights(self, question: Dict[str, Any], answer: Any) -> None:
        """Update insights based on answered question"""
        # Determine category based on question type
        if "type" not in question:
            return
            
        category = question["type"]
        if category not in self.insights:
            self.insights[category] = []
            
        # Add the insight
        self.insights[category].append({
            "question": question["text"],
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_insights(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get accumulated insights from answered questions"""
        return self.insights
    
    def get_unanswered_questions(self) -> List[Dict[str, Any]]:
        """Get list of unanswered questions"""
        return [q for q in self.questions_history if not q.get("answered", False)]
    
    def save_state(self, filepath: str) -> bool:
        """Save engine state to file"""
        try:
            state = {
                "questions_history": self.questions_history,
                "answers_history": self.answers_history,
                "insights": self.insights
            }
            
            with open(filepath, 'w') as f:
                json.dump(state, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving curiosity state: {str(e)}")
            return False
    
    def load_state(self, filepath: str) -> bool:
        """Load engine state from file"""
        try:
            if not os.path.exists(filepath):
                return False
                
            with open(filepath, 'r') as f:
                state = json.load(f)
                
            self.questions_history = state.get("questions_history", [])
            self.answers_history = state.get("answers_history", {})
            self.insights = state.get("insights", {})
            return True
        except Exception as e:
            print(f"Error loading curiosity state: {str(e)}")
            return False
