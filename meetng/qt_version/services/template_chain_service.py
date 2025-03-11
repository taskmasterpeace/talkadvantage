from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.callbacks.base import BaseCallbackHandler
import json

class StreamingCallback(BaseCallbackHandler):
    """Callback handler for streaming LLM responses"""
    
    def __init__(self):
        self.text = ""
        self.progress_callback = None
        
    def on_llm_new_token(self, token: str, **kwargs):
        """Process each new token as it's generated"""
        self.text += token
        if self.progress_callback:
            self.progress_callback(token)

class TemplateChainService:
    """Handles the multi-step template generation process using LangChain"""
    
    def __init__(self, model="gpt-4", temperature=0.7):
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            streaming=True,
            callbacks=[StreamingCallback()]
        )
        
    def _generate_curiosity_prompt(self, focus_areas):
        """Generate a curiosity prompt based on focus areas
        
        Args:
            focus_areas: List of focus areas for the Curiosity Engine
            
        Returns:
            str: Customized curiosity prompt
        """
        # Base prompt structure
        prompt = """[SYSTEM INSTRUCTIONS - DO NOT MODIFY THIS SECTION]
You are an expert active listener analyzing conversation transcripts. 
Generate 2-3 insightful questions that would help understand the context better.

[QUESTION TYPES - DO NOT MODIFY THESE TYPES]
Question types:
- YES_NO: Simple yes/no questions
- MULTIPLE_CHOICE: Questions with predefined options (provide 3-4 choices)
- MULTIPLE_CHOICE_FILL: Multiple choice with an "other" option (provide 3-4 choices)
- SPEAKER_IDENTIFICATION: Questions about who said specific statements
- MEETING_TYPE: Questions about the type of meeting/conversation

[CUSTOMIZABLE GUIDELINES - YOU CAN MODIFY THIS SECTION]
Generate questions that:
"""

        # Add focus-specific guidelines
        if "context clarification" in focus_areas:
            prompt += "- Help clarify ambiguous or unclear points in the conversation\n"
        if "decision making" in focus_areas:
            prompt += "- Explore how and why decisions were made\n"
        if "action items" in focus_areas:
            prompt += "- Clarify responsibilities, deadlines, and expectations for tasks\n"
        if "participant roles" in focus_areas:
            prompt += "- Identify who said what and their role in the conversation\n"
        if "meeting type" in focus_areas:
            prompt += "- Determine the nature and purpose of the conversation\n"
            
        # Add general guidelines if no specific areas selected
        if not focus_areas:
            prompt += """- Are relevant to the transcript content
- Help clarify important points
- Uncover underlying context
"""
            
        # Add common guidelines
        prompt += """- Are concise and clear
- Have meaningful multiple choice options when applicable

[OUTPUT FORMAT - DO NOT MODIFY THIS SECTION]
Return a list of questions in the specified format."""

        return prompt
        
    def generate_templates(self, context: str, progress_callback=None) -> list:
        """
        Generate templates using a multi-step chain with streaming
        
        Args:
            context: User's responses to wizard questions
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of generated templates
        """
        def update_progress(message: str):
            """Helper function to handle progress updates"""
            if progress_callback:
                progress_callback(message)
                
        # Set up streaming callback
        self.llm.callbacks[0].progress_callback = progress_callback
        
        # Step 1: Requirements Analysis
        update_progress("🔍 Analyzing requirements...")
        analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert requirements analyst. Analyze the user's needs and create a structured analysis."),
            ("human", f"""Analyze these responses and create a detailed requirements breakdown:

{context}

Focus on:
1. Core user needs
2. Interaction patterns
3. Key functionality
4. Special considerations""")
        ])
        
        analysis_chain = analysis_prompt | self.llm | StrOutputParser()
        analysis_result = analysis_chain.invoke({})
        update_progress(f"\nAnalysis Complete:\n{analysis_result}")
        
        # Step 2: Interaction Design
        update_progress("\n\n🎨 Designing interaction patterns...")
        design_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an AI interaction designer. Create detailed interaction patterns based on requirements."),
            ("human", f"""Based on this analysis, design two different interaction approaches:

{analysis_result}

Include:
1. Interaction style
2. Response patterns
3. Proactive behaviors
4. Error handling""")
        ])
        
        design_chain = design_prompt | self.llm | StrOutputParser()
        design_result = design_chain.invoke({})
        update_progress(f"\nDesigns Complete:\n{design_result}")
        
        # Step 3: Template Generation
        update_progress("\n\n⚙️ Generating template JSON...")
        template_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a template engineer. Convert interaction designs into structured templates."),
            ("human", f"""Convert these interaction designs into two template objects:

{design_result}

Format as a JSON array with:
- name: Template identifier
- description: Three-part synthesis (User Context, AI's Role, Interaction Style)
- system_prompt: Complete personality and behavior instructions
- template: Interaction guidelines and engagement patterns
- user: User context and collaboration preferences
- bookmarks: Array of recommended interaction markers""")
        ])
        
        template_chain = template_prompt | self.llm | StrOutputParser()
        result = template_chain.invoke({})
        update_progress(f"\nTemplate Generation Complete:\n{result}")
        
        # Parse and validate JSON
        try:
            templates = json.loads(result)
            if not isinstance(templates, list):
                templates = [templates]
                
            # Extract conversation mode preference from context
            conversation_mode = "tracking"  # Default
            if "Guided Mode" in context:
                conversation_mode = "guided"
                
            # Extract bookmark preferences from context
            include_user_speaking = "User Speaking" in context
            include_decision_points = "Decision Points" in context
            include_action_items = "Action Items" in context
            
            # Extract curiosity focus areas from context
            curiosity_focus = []
            if "Context clarification" in context:
                curiosity_focus.append("context clarification")
            if "Decision making" in context:
                curiosity_focus.append("decision making")
            if "Action items" in context:
                curiosity_focus.append("action items")
            if "Participant roles" in context:
                curiosity_focus.append("participant roles")
            if "Meeting type" in context:
                curiosity_focus.append("meeting type")
                
            # Generate curiosity prompt based on focus areas
            curiosity_prompt = self._generate_curiosity_prompt(curiosity_focus)
            
            # Enhance templates with new fields
            for template in templates:
                # Rename fields if needed for compatibility
                if "template" in template and "template_prompt" not in template:
                    template["template_prompt"] = template["template"]
                if "user" in template and "user_prompt" not in template:
                    template["user_prompt"] = template["user"]
                
                # Add new fields
                template["curiosity_prompt"] = curiosity_prompt
                template["conversation_mode"] = conversation_mode
                template["version"] = 2
                
                # Add visualization settings
                template["visualization"] = {
                    "default_layout": "radial" if conversation_mode == "tracking" else "hierarchical",
                    "node_color_scheme": "default",
                    "highlight_decisions": True,
                    "highlight_questions": True,
                    "expand_level": 1 if conversation_mode == "tracking" else 2
                }
                
                # Add special bookmarks if requested
                if "bookmarks" not in template:
                    template["bookmarks"] = []
                    
                if include_user_speaking:
                    template["bookmarks"].append({
                        "name": "User Speaking",
                        "bookmark_type": "marker",
                        "key_shortcut": "Ctrl+U",
                        "voice_trigger": "me speaking",
                        "content": "[USER]",
                        "description": "Mark when the user is speaking",
                        "is_user_speaking": True,
                        "is_decision_point": False,
                        "is_action_item": False
                    })
                    
                if include_decision_points:
                    template["bookmarks"].append({
                        "name": "Decision Point",
                        "bookmark_type": "marker",
                        "key_shortcut": "Ctrl+D",
                        "voice_trigger": "decision point",
                        "content": "[DECISION]",
                        "description": "Mark an important decision point",
                        "is_user_speaking": False,
                        "is_decision_point": True,
                        "is_action_item": False
                    })
                    
                if include_action_items:
                    template["bookmarks"].append({
                        "name": "Action Item",
                        "bookmark_type": "marker",
                        "key_shortcut": "Ctrl+A",
                        "voice_trigger": "action item",
                        "content": "[ACTION]",
                        "description": "Mark an assigned task or action item",
                        "is_user_speaking": False,
                        "is_decision_point": False,
                        "is_action_item": True
                    })
            
            return templates
            
        except json.JSONDecodeError:
            # Try to clean up the response if it's not valid JSON
            cleaned = result.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            templates = json.loads(cleaned)
            if not isinstance(templates, list):
                templates = [templates]
                
            # Apply the same enhancements as above
            # Extract conversation mode preference from context
            conversation_mode = "tracking"  # Default
            if "Guided Mode" in context:
                conversation_mode = "guided"
                
            # Extract bookmark preferences from context
            include_user_speaking = "User Speaking" in context
            include_decision_points = "Decision Points" in context
            include_action_items = "Action Items" in context
            
            # Extract curiosity focus areas from context
            curiosity_focus = []
            if "Context clarification" in context:
                curiosity_focus.append("context clarification")
            if "Decision making" in context:
                curiosity_focus.append("decision making")
            if "Action items" in context:
                curiosity_focus.append("action items")
            if "Participant roles" in context:
                curiosity_focus.append("participant roles")
            if "Meeting type" in context:
                curiosity_focus.append("meeting type")
                
            # Generate curiosity prompt based on focus areas
            curiosity_prompt = self._generate_curiosity_prompt(curiosity_focus)
            
            # Enhance templates with new fields
            for template in templates:
                # Rename fields if needed for compatibility
                if "template" in template and "template_prompt" not in template:
                    template["template_prompt"] = template["template"]
                if "user" in template and "user_prompt" not in template:
                    template["user_prompt"] = template["user"]
                
                # Add new fields
                template["curiosity_prompt"] = curiosity_prompt
                template["conversation_mode"] = conversation_mode
                template["version"] = 2
                
                # Add visualization settings
                template["visualization"] = {
                    "default_layout": "radial" if conversation_mode == "tracking" else "hierarchical",
                    "node_color_scheme": "default",
                    "highlight_decisions": True,
                    "highlight_questions": True,
                    "expand_level": 1 if conversation_mode == "tracking" else 2
                }
                
                # Add special bookmarks if requested
                if "bookmarks" not in template:
                    template["bookmarks"] = []
                    
                if include_user_speaking:
                    template["bookmarks"].append({
                        "name": "User Speaking",
                        "bookmark_type": "marker",
                        "key_shortcut": "Ctrl+U",
                        "voice_trigger": "me speaking",
                        "content": "[USER]",
                        "description": "Mark when the user is speaking",
                        "is_user_speaking": True,
                        "is_decision_point": False,
                        "is_action_item": False
                    })
                    
                if include_decision_points:
                    template["bookmarks"].append({
                        "name": "Decision Point",
                        "bookmark_type": "marker",
                        "key_shortcut": "Ctrl+D",
                        "voice_trigger": "decision point",
                        "content": "[DECISION]",
                        "description": "Mark an important decision point",
                        "is_user_speaking": False,
                        "is_decision_point": True,
                        "is_action_item": False
                    })
                    
                if include_action_items:
                    template["bookmarks"].append({
                        "name": "Action Item",
                        "bookmark_type": "marker",
                        "key_shortcut": "Ctrl+A",
                        "voice_trigger": "action item",
                        "content": "[ACTION]",
                        "description": "Mark an assigned task or action item",
                        "is_user_speaking": False,
                        "is_decision_point": False,
                        "is_action_item": True
                    })
            
            return templates
            
    def analyze_with_template(self, transcript: str, template: dict, context: dict = None) -> str:
        """
        Analyze a transcript using a specific template
        
        Args:
            transcript: The transcript text to analyze
            template: The template dictionary to use
            context: Additional context for the analysis (optional)
            
        Returns:
            str: The analysis result
        """
        try:
            # Extract template components
            system_prompt = template.get("system_prompt", "")
            user_prompt = template.get("user", "")
            template_prompt = template.get("template", "")
            
            # Include special bookmark information in the analysis context
            bookmark_info = ""
            if "bookmarks" in template:
                special_bookmarks = [b for b in template["bookmarks"] if 
                                    b.get("is_user_speaking") or 
                                    b.get("is_decision_point") or 
                                    b.get("is_action_item")]
                
                if special_bookmarks:
                    bookmark_info = "\nSpecial markers in the transcript:\n"
                    for b in special_bookmarks:
                        if b.get("is_user_speaking"):
                            bookmark_info += f"- '{b.get('content', '[USER]')}' indicates the user is speaking\n"
                        if b.get("is_decision_point"):
                            bookmark_info += f"- '{b.get('content', '[DECISION]')}' indicates a decision point\n"
                        if b.get("is_action_item"):
                            bookmark_info += f"- '{b.get('content', '[ACTION]')}' indicates an action item\n"
            
            # Create the messages
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{user_prompt}\n\n{bookmark_info}\n\nTranscript:\n{transcript}\n\n{template_prompt}"}
            ]
            
            # Add conversation mode context if available
            if "conversation_mode" in template:
                mode_context = f"\nThis conversation was conducted in '{template['conversation_mode']}' mode."
                messages[1]["content"] += mode_context
                
            # Add any additional context
            if context:
                context_str = "\nAdditional context:\n"
                for key, value in context.items():
                    context_str += f"- {key}: {value}\n"
                messages[1]["content"] += context_str
                
            # Set up streaming callback
            callback = StreamingCallback()
            callback.progress_callback = lambda x: print(f"Analysis progress: {len(x)} chars")
            
            # Call the model
            from langchain_openai import ChatOpenAI
            from langchain.schema import StrOutputParser
            
            llm = ChatOpenAI(
                model="gpt-4",
                temperature=0.7,
                streaming=True,
                callbacks=[callback]
            )
            
            chain = llm | StrOutputParser()
            result = chain.invoke(messages)
            
            return result
            
        except Exception as e:
            print(f"Error analyzing with template: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"Error analyzing transcript: {str(e)}"
