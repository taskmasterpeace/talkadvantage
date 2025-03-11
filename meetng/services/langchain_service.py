from typing import List, Dict, Any
import os
import sys
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.chat_message_histories import ChatMessageHistory
from services.template_manager import TemplateManager, PromptTemplate

BASE_SYSTEM_PROMPT = """You are an AI assistant analyzing conversation transcripts. Your key behaviors:

1. Process each text segment according to the template instructions provided
2. If this is part of a sequence, use any provided conversation_summary for context
3. If no summary is provided, treat the segment as a standalone analysis
4. Always prioritize the specific template instructions for your response format
5. Maintain professional, clear, and concise analysis

Your responses should exactly match what the template asks for - no more, no less."""

class LangChainService:
    """Handles LangChain processing of transcription chunks"""
    
    def __init__(self, settings_manager=None):
        # Get application path (works for both script and exe)
        if getattr(sys, 'frozen', False):
            # Running in PyInstaller bundle
            application_path = os.path.dirname(sys._MEIPASS)
        else:
            # Running in normal Python environment
            application_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Store settings manager
        self.settings_manager = settings_manager

        # Look for .env in multiple locations
        possible_env_paths = [
            os.path.join(application_path, '.env'),
            os.path.join(os.path.dirname(application_path), '.env'),
            '.env'  # Current directory
        ]

        env_loaded = False
        for env_path in possible_env_paths:
            if os.path.exists(env_path):
                load_dotenv(env_path)
                print(f"Loaded .env from: {env_path}")
                env_loaded = True
                break

        if not env_loaded:
            print("Warning: No .env file found")

        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            print("Warning: OPENAI_API_KEY not found in environment")

        # Initialize components
        self.context_window = []
        self.max_context_chunks = 5
        self.memory = ChatMessageHistory()
        self.llm = None

        # Initialize LLM if API key is available
        if self.api_key:
            try:
                self.init_llm()
            except Exception as e:
                print(f"Failed to initialize LLM: {e}")
        
        # Initialize template statistics
        self.stats_file = "template_stats.json"
        self.template_stats = self.load_template_stats()
        
    def init_llm(self):
        """Initialize the language model with API key"""
        try:
            # Define available models
            self.available_models = {
                "gpt-4o-mini": {
                    "name": "GPT-4o Mini",
                    "description": "Default model - Optimized for general use",
                    "max_tokens": 128000,
                },
                "gpt-4o": {
                    "name": "GPT-4o",
                    "description": "Full GPT-4o capabilities",
                    "max_tokens": 128000,
                },
                "gpt-o1": {
                    "name": "GPT-o1",
                    "description": "Specialized model for complex reasoning",
                    "max_tokens": 128000,
                }
            }
            
            # Get model from environment or use default
            model_name = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')  # Changed default model
            
            if not self.api_key:
                print("No OpenAI API key found")
                self.llm = None
                return

            self.llm = ChatOpenAI(
                api_key=self.api_key,
                temperature=0.3,
                model_name=model_name,
                streaming=True,
                max_tokens=4000,
                request_timeout=120,
                tags=["powerplay"],
                metadata={
                    "app": "powerplay",
                    "feature": "transcription_analysis",
                    "model": model_name
                }
            )
            
            # Test the LLM with a simple prompt
            try:
                test_response = self.llm.invoke("Test connection")
                print("LLM initialized successfully")
            except Exception as e:
                print(f"LLM test failed: {e}")
                self.llm = None
        except Exception as e:
            print(f"Error initializing LLM: {e}")
            self.llm = None
        
        # Initialize memory
        self.memory = ChatMessageHistory()
        
        # Initialize template manager
        from services.template_manager import TemplateManager
        self.template_manager = TemplateManager()
        
    def process_chunk(self, chunk: str, template: Dict[str, str], is_full_analysis: bool = False) -> str:
        """
        Process a chunk of text using LangChain with memory and sequential analysis
        
        Args:
            chunk: Text chunk to process
            template: Dictionary containing system and user prompts
            is_full_analysis: Whether this is a full analysis of the entire transcript
            
        Returns:
            Processed response
        """
        try:
            if self._debug_mode:
                print("\n=== LangChain Debug ===")
                print(f"Chunk type: {type(chunk)}")
                print(f"Template type: {type(template)}")
                print(f"Template content: {template}")
                print(f"Processing chunk with memory id: {id(self.memory)}")
                print(f"Current message count: {len(self.memory.messages)}")
                print(f"Is full analysis: {is_full_analysis}")
            
            # Verify API key and LLM
            if not self.api_key:
                return "[Error: OpenAI API key not configured. Please check your settings.]"
                
            if not self.llm:
                self.init_llm()  # Try to initialize again
                if not self.llm:
                    return "[Error: Could not initialize language model. Please check your API key and internet connection.]"
                
            start_time = time.time()
            
            # Adjust prompt based on whether this is a full analysis
            if is_full_analysis:
                # For full analysis, use a more comprehensive prompt
                prompt_text = f"Perform a comprehensive analysis of the entire transcript:\n\n{chunk}"
                system_instruction = "You are analyzing a complete transcript. Provide a thorough analysis covering key topics, decisions, action items, and important insights."
            else:
                # For regular analysis, use the template's prompt
                prompt_text = f"Text to analyze:\n{chunk}"
                system_instruction = BASE_SYSTEM_PROMPT
            
            # Create prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_instruction),
                ("human", template.get("user", "")),
                MessagesPlaceholder(variable_name="history"),
                ("human", prompt_text)
            ])

            # Create chain
            chain = prompt | self.llm | StrOutputParser()
            
            # Get history
            history = self.memory.messages
            
            # Process chunk
            try:
                response = chain.invoke({
                    "history": history,
                    "text": chunk
                })
            except Exception as e:
                error_msg = str(e).lower()
                if "api_key" in error_msg:
                    raise ValueError("Invalid API key - Please check your OpenAI API key")
                elif "connect" in error_msg:
                    raise ValueError("Connection error - Please check your internet connection")
                else:
                    raise ValueError(f"Processing error: {str(e)}")
            
            # Add to memory
            self.memory.add_user_message(chunk)
            self.memory.add_ai_message(response)
            
            # Update statistics
            processing_time = time.time() - start_time
            self.update_template_stats(
                template["name"],
                processing_time,
                len(response)
            )
            
            return response
            
        except Exception as e:
            print(f"Error processing chunk: {e}")
            return f"Error processing chunk: {str(e)}"
            
    def load_template_stats(self) -> dict:
        """Load template statistics from file"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading template stats: {e}")
        return {}

    def save_template_stats(self):
        """Save template statistics to file"""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.template_stats, f, indent=2)
        except Exception as e:
            print(f"Error saving template stats: {e}")

    def update_template_stats(self, template_name: str, response_time: float, response_length: int):
        """Update statistics for a template"""
        if template_name not in self.template_stats:
            self.template_stats[template_name] = {
                "uses": 0,
                "total_response_time": 0,
                "total_length": 0,
                "first_used": datetime.now().isoformat(),
            }
        
        stats = self.template_stats[template_name]
        stats["uses"] += 1
        stats["total_response_time"] += response_time
        stats["total_length"] += response_length
        stats["last_used"] = datetime.now().isoformat()
        stats["avg_response_time"] = stats["total_response_time"] / stats["uses"]
        stats["avg_length"] = stats["total_length"] / stats["uses"]
        
        self.save_template_stats()

    def get_template_stats(self, template_name: str) -> dict:
        """Get statistics for a template"""
        if template_name in self.template_stats:
            stats = self.template_stats[template_name].copy()
            # Format timestamps for display
            if "first_used" in stats:
                stats["first_used"] = datetime.fromisoformat(stats["first_used"]).strftime("%Y-%m-%d %H:%M")
            if "last_used" in stats:
                stats["last_used"] = datetime.fromisoformat(stats["last_used"]).strftime("%Y-%m-%d %H:%M")
            return stats
        return None

    def reset_template_stats(self):
        """Reset all template statistics"""
        self.template_stats = {}
        self.save_template_stats()
        
    def _ensure_curiosity_engine(self):
        """Ensure the curiosity engine is initialized"""
        if not hasattr(self, 'curiosity_engine'):
            from qt_version.services.curiosity_engine import CuriosityEngine
            self.curiosity_engine = CuriosityEngine()
        return self.curiosity_engine
            
    def generate_curiosity_questions(self, transcript: str, template: Dict[str, str]):
        """Generate curiosity questions based on the current transcript"""
        engine = self._ensure_curiosity_engine()
        questions = engine.generate_questions(transcript, template)
        print(f"Generated {len(questions)} curiosity questions")
        return questions
        
    def process_curiosity_answers(self, answers):
        """Process answers from the curiosity dialog"""
        try:
            engine = self._ensure_curiosity_engine()
            
            # Process each answer
            for question, answer in answers:
                engine.process_answer(question, answer)
            
            # Return insights that could be displayed in the AI Insights tab
            return engine.get_insights()
        except Exception as e:
            print(f"Error processing curiosity answers: {str(e)}")
            return {}
    
    def get_available_templates(self) -> List[Dict[str, str]]:
        """Get list of available templates from template manager"""
        try:
            templates = []
            # Always ensure Full Analysis template is first
            full_analysis_template = {
                "name": "*Full Analysis",
                "user": "Provide a comprehensive analysis of the entire discussion covering:\n\n1. Key Topics\n2. Decisions Made\n3. Action Items\n4. Follow-ups Needed\n5. Important Insights",
                "template": "Full Analysis Template",
                "description": "Complete analysis of the entire transcript",
                "system_prompt": {
                    "id": None,
                    "name": "Default",
                    "content": BASE_SYSTEM_PROMPT
                }
            }
            templates.append(full_analysis_template)
            
            # Get other templates
            for name in self.template_manager.get_template_names():
                template = self.template_manager.get_template(name)
                if template and template.name != "*Full Analysis":
                    # Default system prompt data
                    system_prompt_data = {
                        "id": None,
                        "name": "Default",
                        "content": BASE_SYSTEM_PROMPT
                    }
                
                    # Get system prompt info
                    if hasattr(template, 'system_prompt_id') and template.system_prompt_id:
                        try:
                            from qt_version.utils.system_prompt_manager import SystemPromptManager
                            prompt_manager = SystemPromptManager()
                            system_prompt = prompt_manager.get_prompt_by_id(template.system_prompt_id)
                            if system_prompt:
                                system_prompt_data = {
                                    'id': system_prompt.id,
                                    'name': system_prompt.name,
                                    'content': system_prompt.content
                                }
                        except Exception as e:
                            print(f"Error loading system prompt: {e}")
                    elif hasattr(template, 'system_prompt'):
                        system_prompt_data = template.system_prompt

                    # Create consistent template structure
                    template_dict = {
                        "name": template.name,
                        "user": template.user_prompt,
                        "template": template.template_prompt,
                        "description": template.description,
                        "system_prompt": system_prompt_data
                    }
                    templates.append(template_dict)
            return templates
        except Exception as e:
            print(f"Error getting templates: {e}")
            return []
        
    def delete_template(self, name: str) -> bool:
        """Delete a template using the template manager"""
        return self.template_manager.delete_template(name)
        
    def save_template(self, template: Dict[str, str]) -> bool:
        """Save a new or updated template
        
        Args:
            template: Dictionary containing template data
                     Must have 'name', 'user', and 'template' keys
                     May have 'system_prompt' dict with 'id' and 'content'
                     
        Returns:
            bool: True if save was successful
        """
        try:
            # Convert dictionary to PromptTemplate
            prompt_template = PromptTemplate(
                name=template['name'],
                user_prompt=template.get('user', ''),
                template_prompt=template.get('template', ''),
                system_prompt_id=template.get('system_prompt', {}).get('id'),
                description=template.get('description', '')
            )
            
            # Use template manager to save
            return self.template_manager.save_template(prompt_template)
            
        except Exception as e:
            print(f"Error saving template: {e}")
            return False
    def update_model_stats(self, model: str, template_name: str, response_time: float, response_length: int):
        """Update statistics for model usage"""
        if not hasattr(self, 'model_stats'):
            self.model_stats = {}
            
        if model not in self.model_stats:
            self.model_stats[model] = {
                "uses": 0,
                "total_response_time": 0,
                "total_length": 0,
                "first_used": datetime.now().isoformat(),
            }
            
        stats = self.model_stats[model]
        stats["uses"] += 1
        stats["total_response_time"] += response_time
        stats["total_length"] += response_length
        stats["last_used"] = datetime.now().isoformat()
        stats["avg_response_time"] = stats["total_response_time"] / stats["uses"]
        stats["avg_length"] = stats["total_length"] / stats["uses"]
        
        # Also update template stats
        self.update_template_stats(template_name, response_time, response_length)
