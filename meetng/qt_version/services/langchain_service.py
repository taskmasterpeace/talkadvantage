from typing import Dict, List, Optional, Any
import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
import time
from services.template_manager import TemplateManager
from PyQt6.QtCore import QTimer

class LangChainService:
    """Handles LangChain processing of transcription chunks"""
    
    def __init__(self):
        print("Initializing new LangChainService")
        self._debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        
        # Load from root .env first, then override with qt_version/.env if it exists
        root_env = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
        qt_env = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        
        # Load root .env first
        if os.path.exists(root_env):
            load_dotenv(root_env)
            if self._debug_mode:
                print(f"Loaded root .env from: {root_env}")
                
        # Then override with qt_version/.env if it exists
        if os.path.exists(qt_env):
            load_dotenv(qt_env, override=True)
            if self._debug_mode:
                print(f"Loaded Qt .env from: {qt_env}")
        
        self._debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        self.template_manager = TemplateManager()
        self.llm = None
        self.init_llm()
        self.model_stats = {}  # {model: {template: {times: [], avg: float}}}
        self._load_stats()
        
    def _load_stats(self):
        """Load model stats from file"""
        stats_file = os.path.join(os.getcwd(), "model_stats.json")
        if os.path.exists(stats_file):
            try:
                with open(stats_file, 'r') as f:
                    self.model_stats = json.load(f)
            except Exception as e:
                if self._debug_mode:
                    print(f"Error loading stats: {e}")
                    
    def _save_stats(self):
        """Save model stats to file"""
        stats_file = os.path.join(os.getcwd(), "model_stats.json")
        try:
            with open(stats_file, 'w') as f:
                json.dump(self.model_stats, f, indent=2)
        except Exception as e:
            if self._debug_mode:
                print(f"Error saving stats: {e}")
                
    def update_model_stats(self, model: str, template_name: str, response_time: float, response_length: int):
        """Update usage statistics for model/template combination"""
        if model not in self.model_stats:
            self.model_stats[model] = {}
            
        if template_name not in self.model_stats[model]:
            self.model_stats[model][template_name] = {
                "times": [],
                "avg": 0.0,
                "calls": 0,
                "avg_length": 0
            }
            
        stats = self.model_stats[model][template_name]
        stats["times"].append(response_time)
        stats["calls"] += 1
        stats["avg"] = sum(stats["times"]) / len(stats["times"])
        stats["avg_length"] = ((stats["avg_length"] * (stats["calls"] - 1)) + response_length) / stats["calls"]
        
        # Keep only last 100 times
        if len(stats["times"]) > 100:
            stats["times"].pop(0)
            
        # Save in background
        QTimer.singleShot(0, self._save_stats)
        
    def init_llm(self):
        """Initialize the language model"""
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                print("Warning: No OpenAI API key found in environment")
                return
                
            # Get model from settings with correct default
            from qt_version.utils.settings_manager import SettingsManager
            settings_manager = SettingsManager()
            model = settings_manager.get_setting('OPENAI_MODEL', 'gpt-4o-mini')  # Use actual default from settings
            temperature = float(settings_manager.get_setting('OPENAI_TEMPERATURE', '0.7'))
            
            if self._debug_mode:
                print(f"Initializing LLM with model: {model}, temperature: {temperature}")
                
            self.llm = ChatOpenAI(
                model=model,
                temperature=temperature,
                api_key=api_key
            )
            print(f"LLM initialized successfully with model: {model}")
        except Exception as e:
            print(f"Error initializing LLM: {e}")
            
    def process_chunk(self, chunk: str, template: Dict[str, str], chat_history: List[Dict[str, str]] = None, is_full_analysis: bool = False) -> str:
        """Process a chunk of text using the given template with chat history"""
        try:
            if self._debug_mode:
                print("\n=== LangChain Debug ===")
                print(f"Chunk type: {type(chunk)}")
                print(f"Template type: {type(template)}")
                print(f"Template content: {template}")
                print(f"Chat history: {len(chat_history) if chat_history else 0} messages")
                print(f"Is full analysis: {is_full_analysis}")
                start_time = time.time()
            
            # Build messages list from chat history (skip for full analysis)
            messages = []
            if chat_history and not is_full_analysis:
                for msg in chat_history:
                    messages.append((msg["role"], msg["content"]))
            
            # Use template's system prompt to define AI's role
            system_prompt = template["system_prompt"]  # Now required, no fallback
            messages = [("system", system_prompt)] + messages
            
            # Combine user context, template instructions, and transcript
            user_message = f"""{template['user']}

{template['template']}

Transcript:
{chunk}"""
            messages.append(("human", user_message))
            
            # Create prompt template with history
            prompt = ChatPromptTemplate.from_messages(messages)
            
            # Create and invoke chain
            chain = prompt | self.llm | StrOutputParser()
            response = chain.invoke({"text": chunk})
            
            if self._debug_mode:
                print(f"Processing took: {time.time() - start_time:.2f}s")
                
            return response
            
        except Exception as e:
            error_msg = f"Error processing chunk: {str(e)}"
            print(error_msg)
            return error_msg
            
    def generate_conversation_suggestions(self, prompt: str, num_suggestions: int = 3, context: Optional[Dict[str, Any]] = None, history=None) -> str:
        """Generate suggestions for conversation continuations
        
        Args:
            prompt: The prompt to send to the LLM
            num_suggestions: Number of suggestions to generate
            context: Optional conversation context
            history: Optional conversation history
            
        Returns:
            str: The generated suggestions
        """
        if not self.llm:
            self.init_llm()
            
        try:
            # Create messages
            messages = [
                ("system", "You are an expert conversation assistant helping to guide effective conversations."),
                ("human", prompt)
            ]
            
            # Create prompt template
            prompt_template = ChatPromptTemplate.from_messages(messages)
            
            # Generate response
            start_time = time.time()
            chain = prompt_template | self.llm | StrOutputParser()
            content = chain.invoke({})
            end_time = time.time()
            
            # Update stats
            try:
                self.update_model_stats(
                    model=self.llm.model_name,
                    template_name="conversation_suggestions",
                    response_time=end_time - start_time,
                    response_length=len(content)
                )
            except Exception as stats_error:
                print(f"Error updating stats: {str(stats_error)}")
            
            return content
            
        except Exception as e:
            print(f"Error generating conversation suggestions: {str(e)}")
            # Return a simple fallback response as valid JSON
            return json.dumps([
                {"speaker": "Sales Rep", "content": "How can I help you today?"},
                {"speaker": "Sales Rep", "content": "What specific features are you looking for?"},
                {"speaker": "Sales Rep", "content": "Let me tell you about our current offers."}
            ])
            
    def get_available_templates(self) -> List[Dict[str, str]]:
        """Get list of available templates"""
        return [
            {
                "name": template.name,
                "user": template.user_prompt,
                "template": template.template_prompt,
                "system_prompt": template.system_prompt,
                "description": template.description
            }
            for template in self.template_manager.templates.values()
        ]
        
    def save_template(self, template: Dict[str, str]) -> bool:
        """Save a template and refresh template manager"""
        try:
            from services.template_manager import PromptTemplate
            prompt_template = PromptTemplate(
                name=template["name"],
                user_prompt=template["user"],
                template_prompt=template["template"],
                system_prompt=template.get("system_prompt", ""),
                description=template.get("description", "")
            )
            success = self.template_manager.save_template(prompt_template)
            
            if success:
                # Reload templates to ensure immediate availability
                self.template_manager = TemplateManager()
                if self._debug_mode:
                    print(f"Template saved and manager refreshed: {template['name']}")
                    
            return success
        except Exception as e:
            print(f"Error saving template: {e}")
            return False

    def delete_template(self, template_name: str) -> bool:
        """Delete a template from the template manager"""
        try:
            if self._debug_mode:
                print(f"Attempting to delete template: {template_name}")
                
            success = self.template_manager.delete_template(template_name)
            
            if success:
                # Reload templates to ensure immediate availability
                self.template_manager = TemplateManager()
                if self._debug_mode:
                    print(f"Template deleted and manager refreshed: {template_name}")
                    
            return success
            
        except Exception as e:
            print(f"Error deleting template: {e}")
            return False
            
    def get_template_stats(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get usage statistics for a template"""
        # For now, return placeholder stats
        return {
            "uses": 0,
            "last_used": "Never",
            "avg_response_time": 0.0,
            "avg_length": 0
        }
