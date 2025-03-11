import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

class ConversationCompassService:
    """Service for managing the Conversation Compass functionality"""
    
    def __init__(self, langchain_service=None):
        self.langchain_service = langchain_service
        self.conversation_tree = {}
        self.current_node_id = None
        self.conversation_context = {}
        self.mode = "tracking"  # Default mode: "tracking" or "guided"
        
    def create_new_conversation(self, context: Dict[str, Any]) -> bool:
        """Create a new conversation with the given context
        
        Args:
            context: Dictionary containing conversation metadata
                - title: Conversation title
                - description: Conversation description
                - participants: List of participant names
                - goals: List of conversation goals
                - settings: Dictionary of additional settings
                
        Returns:
            bool: Success status
        """
        try:
            # Store conversation context
            self.conversation_context = context
            
            # Set mode based on template if available
            template_name = context.get("template")
            if template_name and self.langchain_service:
                template = self.langchain_service.get_template(template_name)
                if template and "conversation_mode" in template:
                    self.mode = template["conversation_mode"]
            
            # Create root node
            root_id = "root"
            root_node = {
                "id": root_id,
                "content": "Conversation Start",
                "speaker": "",
                "parent_id": None,
                "children": [],
                "node_type": "actual",
                "metadata": {"is_root": True},
                "timestamp": datetime.now().isoformat()
            }
            
            # Initialize tree
            self.conversation_tree = {root_id: root_node}
            self.current_node_id = root_id
            
            # Generate initial suggestions if in guided mode
            if self.mode == "guided":
                self._generate_initial_suggestions()
                
            return True
            
        except Exception as e:
            print(f"Failed to create conversation: {str(e)}")
            return False
    
    def add_utterance(self, content: str, speaker: str) -> str:
        """Add a new utterance to the conversation tree
        
        Args:
            content: The text content of the utterance
            speaker: The name of the speaker
            
        Returns:
            str: The ID of the new node
        """
        try:
            # Create a unique ID for the new node
            node_id = f"node_{len(self.conversation_tree)}"
            
            # Extract sentiment and key topics if possible
            sentiment = "neutral"
            topics = []
            
            if self.langchain_service:
                try:
                    # Try to analyze the utterance with LangChain
                    analysis = self.langchain_service.analyze_utterance(content)
                    if isinstance(analysis, dict):
                        sentiment = analysis.get("sentiment", sentiment)
                        topics = analysis.get("topics", topics)
                except Exception as analysis_error:
                    print(f"Error analyzing utterance: {str(analysis_error)}")
            
            # Create the new node with enhanced metadata
            new_node = {
                "id": node_id,
                "content": content,
                "speaker": speaker,
                "parent_id": self.current_node_id,
                "children": [],
                "node_type": "actual",
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "word_count": len(content.split()),
                    "sentiment": sentiment,
                    "topics": topics,
                    "is_question": content.strip().endswith("?")
                },
                "timestamp": datetime.now().isoformat()
            }
            
            # Add the new node to the tree
            self.conversation_tree[node_id] = new_node
            
            # Update the parent node's children
            if self.current_node_id in self.conversation_tree:
                self.conversation_tree[self.current_node_id]["children"].append(node_id)
            
            # Update the current node
            self.current_node_id = node_id
            
            # Generate new suggestions if in guided mode
            if self.mode == "guided":
                self._generate_suggestions_for_current_node()
                
            return node_id
            
        except Exception as e:
            print(f"Failed to add utterance: {str(e)}")
            return ""
    
    def _generate_initial_suggestions(self) -> None:
        """Generate initial suggestions for the conversation"""
        if not self.langchain_service:
            # Create fallback suggestions
            self._create_fallback_suggestions()
            return
            
        try:
            # Prepare the prompt for initial suggestions
            prompt = self._create_initial_suggestions_prompt()
            
            # Call LangChain service
            response = self.langchain_service.generate_conversation_suggestions(
                prompt=prompt,
                num_suggestions=3,
                context=self.conversation_context
            )
            
            # Process the response
            suggestions = self._parse_suggestions(response)
            
            # Add suggestions as nodes
            self._add_suggestion_nodes(suggestions)
            
        except Exception as e:
            print(f"Failed to generate initial suggestions: {str(e)}")
            # Create fallback suggestions
            self._create_fallback_suggestions()
    
    def _create_fallback_suggestions(self) -> None:
        """Create fallback suggestions when LangChain fails"""
        fallback_suggestions = [
            {"speaker": "You", "content": "Hello, how can I help you today?"},
            {"speaker": "You", "content": "Let's start by discussing your needs."},
            {"speaker": "You", "content": "I'd like to understand more about what you're looking for."}
        ]
        
        self._add_suggestion_nodes(fallback_suggestions)
    
    def _add_suggestion_nodes(self, suggestions: List[Dict[str, str]]) -> None:
        """Add suggestion nodes to the tree"""
        for i, suggestion in enumerate(suggestions):
            node_id = f"suggestion_{len(self.conversation_tree)}_{i}"
            node = {
                "id": node_id,
                "content": suggestion["content"],
                "speaker": suggestion["speaker"],
                "parent_id": self.current_node_id,
                "children": [],
                "node_type": "suggested",
                "metadata": {"suggestion_index": i},
                "timestamp": datetime.now().isoformat()
            }
            
            self.conversation_tree[node_id] = node
            if self.current_node_id in self.conversation_tree:
                self.conversation_tree[self.current_node_id]["children"].append(node_id)
    
    def _generate_suggestions_for_current_node(self) -> None:
        """Generate suggestions for the current node"""
        if not self.langchain_service:
            self._create_fallback_suggestions()
            return
            
        try:
            # Get conversation history
            history = self.get_conversation_history()
            
            # Get current node to analyze context
            current_node = self.get_current_node()
            if not current_node:
                self._create_fallback_suggestions()
                return
                
            # Analyze the current conversation state
            current_speaker = current_node.get("speaker", "")
            current_content = current_node.get("content", "")
            is_question = current_content.strip().endswith("?")
            
            # Determine suggestion strategy based on conversation state
            if is_question:
                # If current utterance is a question, generate answers
                strategy = "answer_question"
            elif len(history) < 3:
                # For early conversation, focus on establishing rapport
                strategy = "establish_rapport"
            else:
                # For ongoing conversation, advance the discussion
                strategy = "advance_discussion"
                
            # Prepare the prompt for suggestions with strategy
            prompt = self._create_suggestions_prompt(history, strategy)
            
            # Call LangChain service with enhanced context
            response = self.langchain_service.generate_conversation_suggestions(
                prompt=prompt,
                num_suggestions=3,
                context={
                    **self.conversation_context,
                    "current_speaker": current_speaker,
                    "is_question": is_question,
                    "strategy": strategy,
                    "conversation_length": len(history)
                },
                history=history
            )
            
            # Process the response
            suggestions = self._parse_suggestions(response)
            
            # Add suggestions as nodes
            self._add_suggestion_nodes(suggestions)
            
        except Exception as e:
            print(f"Failed to generate suggestions: {str(e)}")
            self._create_fallback_suggestions()
    
    def _create_initial_suggestions_prompt(self) -> str:
        """Create a prompt for generating initial suggestions"""
        participants = ", ".join(self.conversation_context.get("participants", []))
        goals = "\n".join([f"- {goal}" for goal in self.conversation_context.get("goals", [])])
        
        prompt = f"""
You are an expert conversation assistant helping with a conversation between {participants}.

Conversation Title: {self.conversation_context.get("title", "Untitled Conversation")}
Description: {self.conversation_context.get("description", "")}

Goals of the conversation:
{goals}

The conversation is just beginning. Please suggest 3 different ways one of the participants could start this conversation effectively.

For each suggestion, specify:
1. Which participant should speak
2. What they should say to effectively open the conversation

Format your response as a JSON array with "speaker" and "content" fields.
"""
        return prompt
    
    def _create_suggestions_prompt(self, history: List[Dict[str, Any]], strategy: str = "advance_discussion") -> str:
        """Create a prompt for generating suggestions based on conversation history and strategy
        
        Args:
            history: List of conversation utterances
            strategy: Suggestion strategy - one of "answer_question", "establish_rapport", or "advance_discussion"
            
        Returns:
            str: Formatted prompt for generating suggestions
        """
        participants = ", ".join(self.conversation_context.get("participants", []))
        goals = "\n".join([f"- {goal}" for goal in self.conversation_context.get("goals", [])])
        
        # Format conversation history
        history_text = ""
        for utterance in history:
            history_text += f"{utterance['speaker']}: {utterance['content']}\n"
            
        # Get the last speaker
        last_speaker = history[-1]['speaker'] if history else ""
        
        # Create strategy-specific instructions
        strategy_instructions = ""
        if strategy == "answer_question":
            strategy_instructions = """
The last message contains a question. Please suggest 3 different ways to answer this question effectively.
Focus on providing clear, helpful responses that address the question directly.
Vary the tone and depth of the answers to provide different options.
"""
        elif strategy == "establish_rapport":
            strategy_instructions = """
This conversation is just beginning. Please suggest 3 different ways to establish rapport and set a positive tone.
Focus on building trust, showing understanding, and creating a comfortable atmosphere.
Vary the approaches to give different options for establishing connection.
"""
        else:  # advance_discussion
            strategy_instructions = """
Please suggest 3 different ways the conversation could continue effectively.
Consider different directions the conversation could take to achieve the stated goals.
Vary the suggestions to provide different strategic options for moving forward.
"""
            
        prompt = f"""
You are an expert conversation assistant helping with a conversation between {participants}.

Conversation Title: {self.conversation_context.get("title", "Untitled Conversation")}
Description: {self.conversation_context.get("description", "")}

Goals of the conversation:
{goals}

Here is the conversation so far:

{history_text}

{strategy_instructions}

For each suggestion, specify:
1. Which participant should speak next (someone other than {last_speaker} if possible)
2. What they should say to move the conversation forward effectively

Format your response as a JSON array with "speaker" and "content" fields.
"""
        return prompt
    
    def _parse_suggestions(self, response: str) -> List[Dict[str, str]]:
        """Parse suggestions from LangChain response"""
        try:
            # Try to parse as JSON
            suggestions = json.loads(response)
            
            # Validate format
            if not isinstance(suggestions, list):
                raise ValueError("Response is not a list")
                
            # Ensure each suggestion has required fields
            validated_suggestions = []
            for suggestion in suggestions:
                if not isinstance(suggestion, dict):
                    continue
                    
                if "speaker" not in suggestion or "content" not in suggestion:
                    continue
                    
                validated_suggestions.append({
                    "speaker": suggestion["speaker"],
                    "content": suggestion["content"]
                })
                
            return validated_suggestions
            
        except json.JSONDecodeError:
            # If not valid JSON, try to extract suggestions from text
            lines = response.strip().split("\n")
            suggestions = []
            current_suggestion = {}
            
            for line in lines:
                if line.startswith("Speaker:") or line.startswith("Participant:"):
                    if current_suggestion and "speaker" in current_suggestion and "content" in current_suggestion:
                        suggestions.append(current_suggestion)
                    current_suggestion = {"speaker": line.split(":", 1)[1].strip()}
                elif line.startswith("Content:") or line.startswith("Say:"):
                    if "speaker" in current_suggestion:
                        current_suggestion["content"] = line.split(":", 1)[1].strip()
                        
            if current_suggestion and "speaker" in current_suggestion and "content" in current_suggestion:
                suggestions.append(current_suggestion)
                
            return suggestions
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history as a list of utterances"""
        if not self.current_node_id:
            return []
            
        # Get the path from root to current node
        path = self.get_path_to_node(self.current_node_id)
        
        # Convert path to list of utterances
        history = []
        for node_id in path:
            node = self.conversation_tree.get(node_id)
            if node and node["id"] != "root":  # Skip the root node
                history.append({
                    "speaker": node["speaker"],
                    "content": node["content"]
                })
                
        return history
    
    def get_path_to_node(self, node_id: str) -> List[str]:
        """Get the path from the root to the specified node"""
        path = []
        current = node_id
        
        while current:
            path.insert(0, current)
            node = self.conversation_tree.get(current)
            if not node or not node["parent_id"]:
                break
            current = node["parent_id"]
            
        return path
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get a node by its ID"""
        return self.conversation_tree.get(node_id)
    
    def get_current_node(self) -> Optional[Dict[str, Any]]:
        """Get the current node"""
        if self.current_node_id:
            return self.conversation_tree.get(self.current_node_id)
        return None
    
    def get_suggested_responses(self) -> List[Dict[str, Any]]:
        """Get suggested responses for the current node"""
        if not self.current_node_id:
            return []
            
        current_node = self.conversation_tree.get(self.current_node_id)
        if not current_node:
            return []
            
        suggestions = []
        for child_id in current_node["children"]:
            child = self.conversation_tree.get(child_id)
            if child and child["node_type"] == "suggested":
                suggestions.append(child)
                
        return suggestions
    
    def save_tree(self, file_path: str) -> bool:
        """Save the conversation tree to a file"""
        try:
            data = {
                "context": self.conversation_context,
                "current_node_id": self.current_node_id,
                "mode": self.mode,
                "tree": self.conversation_tree
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
            return True
            
        except Exception as e:
            print(f"Failed to save tree: {str(e)}")
            return False
    
    def load_tree(self, file_path: str) -> bool:
        """Load a conversation tree from a file"""
        try:
            if not os.path.exists(file_path):
                return False
                
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.conversation_context = data.get("context", {})
            self.current_node_id = data.get("current_node_id")
            self.mode = data.get("mode", "tracking")
            self.conversation_tree = data.get("tree", {})
            
            return True
            
        except Exception as e:
            print(f"Failed to load tree: {str(e)}")
            return False
    
    def set_mode(self, mode: str) -> None:
        """Set the conversation mode
        
        Args:
            mode: Either "tracking" or "guided"
        """
        if mode in ["tracking", "guided"]:
            self.mode = mode
            
            # If switching to guided mode, generate suggestions
            if mode == "guided" and self.current_node_id:
                self._generate_suggestions_for_current_node()
