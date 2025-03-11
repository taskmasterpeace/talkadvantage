from PyQt6.QtCore import QObject, pyqtSignal
import time
from typing import List, Dict, Any, Optional, Tuple
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ConversationTreeService")

class ConversationNode:
    """Represents a node in the conversation tree"""
    
    def __init__(self, 
                 id: str,
                 content: str, 
                 speaker: str = "", 
                 parent_id: Optional[str] = None,
                 node_type: str = "actual",  # "actual", "possible", "suggested"
                 metadata: Optional[Dict[str, Any]] = None):
        self.id = id
        self.content = content
        self.speaker = speaker
        self.parent_id = parent_id
        self.children = []  # List of child node IDs
        self.node_type = node_type
        self.metadata = metadata or {}
        self.timestamp = time.time()
        
    def add_child(self, child_id: str):
        """Add a child node ID to this node"""
        if child_id not in self.children:
            self.children.append(child_id)
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary for serialization"""
        return {
            "id": self.id,
            "content": self.content,
            "speaker": self.speaker,
            "parent_id": self.parent_id,
            "children": self.children,
            "node_type": self.node_type,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationNode':
        """Create node from dictionary"""
        node = cls(
            id=data["id"],
            content=data["content"],
            speaker=data["speaker"],
            parent_id=data["parent_id"],
            node_type=data["node_type"],
            metadata=data["metadata"]
        )
        node.children = data["children"]
        node.timestamp = data.get("timestamp", time.time())
        return node


class ConversationTreeService(QObject):
    """Service for managing conversation trees with LangChain integration"""
    
    # Signals
    tree_updated = pyqtSignal()
    node_added = pyqtSignal(str)  # Node ID
    suggestions_ready = pyqtSignal(list)  # List of suggestion nodes
    error_occurred = pyqtSignal(str)  # Error message
    current_position_changed = pyqtSignal(str)  # Current node ID
    
    def __init__(self, langchain_service=None):
        super().__init__()
        self.langchain_service = langchain_service
        self.nodes = {}  # Dictionary of node_id -> ConversationNode
        self.root_id = None
        self.current_node_id = None
        self.conversation_context = {
            "title": "",
            "description": "",
            "participants": [],
            "goals": [],
            "settings": {}
        }
        
    def create_new_conversation(self, context: Dict[str, Any]) -> bool:
        """Create a new conversation tree with the given context
        
        Args:
            context: Dictionary containing conversation metadata
                - title: Conversation title
                - description: Conversation description
                - participants: List of participant names
                - goals: List of conversation goals
                - settings: Dictionary of additional settings
                - template: Template information (optional)
                
        Returns:
            bool: Success status
        """
        try:
            logger.info(f"Creating new conversation with context: {context}")
            self.conversation_context = context
            
            # Check for template-specific conversation mode
            template_info = context.get("template", {})
            conversation_mode = "tracking"  # Default mode
            
            if template_info and "conversation_mode" in template_info:
                conversation_mode = template_info["conversation_mode"]
                logger.info(f"Using template-specific conversation mode: {conversation_mode}")
            
            # Store the conversation mode
            self.conversation_mode = conversation_mode
            
            # Create root node
            root_id = "root"
            root_node = ConversationNode(
                id=root_id,
                content="Conversation Start",
                node_type="actual",
                metadata={"is_root": True, "conversation_mode": conversation_mode}
            )
            
            # Reset and initialize tree
            self.nodes = {root_id: root_node}
            self.root_id = root_id
            self.current_node_id = root_id
            
            logger.info(f"Root node created with ID: {root_id}")
            
            # Generate initial suggestions - behavior differs based on mode
            if conversation_mode == "guided":
                # In guided mode, generate more extensive suggestions
                self._generate_guided_suggestions()
            else:
                # In tracking mode, generate minimal initial suggestions
                self._generate_initial_suggestions()
            
            self.tree_updated.emit()
            logger.info(f"New conversation created successfully with mode: {conversation_mode}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to create conversation: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)
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
            logger.info(f"Adding utterance from {speaker}: {content[:50]}...")
            
            # Create a unique ID for the new node
            node_id = f"node_{len(self.nodes)}"
            
            # Create the new node
            new_node = ConversationNode(
                id=node_id,
                content=content,
                speaker=speaker,
                parent_id=self.current_node_id,
                node_type="actual"
            )
            
            # Add the new node to the tree
            self.nodes[node_id] = new_node
            
            # Update the parent node's children
            if self.current_node_id in self.nodes:
                self.nodes[self.current_node_id].add_child(node_id)
                logger.info(f"Added node {node_id} as child of {self.current_node_id}")
            
            # Update the current node
            self.current_node_id = node_id
            
            # Generate new suggestions based on the updated conversation
            self._generate_suggestions_for_current_node()
            
            # Emit signals
            self.node_added.emit(node_id)
            self.tree_updated.emit()
            self.current_position_changed.emit(node_id)
            
            logger.info(f"Utterance added successfully with node ID: {node_id}")
            return node_id
            
        except Exception as e:
            error_msg = f"Failed to add utterance: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)
            return ""
            
    def get_node(self, node_id: str) -> Optional[ConversationNode]:
        """Get a node by its ID
        
        Args:
            node_id: The ID of the node to retrieve
            
        Returns:
            Optional[ConversationNode]: The node, or None if not found
        """
        return self.nodes.get(node_id)
        
    def get_current_node(self) -> Optional[ConversationNode]:
        """Get the current node
        
        Returns:
            Optional[ConversationNode]: The current node, or None if not set
        """
        if self.current_node_id:
            return self.nodes.get(self.current_node_id)
        return None
        
    def get_path_to_node(self, node_id: str) -> List[str]:
        """Get the path from the root to the specified node
        
        Args:
            node_id: The ID of the target node
            
        Returns:
            List[str]: List of node IDs from root to target
        """
        path = []
        current = node_id
        
        while current:
            path.insert(0, current)
            node = self.nodes.get(current)
            if not node or not node.parent_id:
                break
            current = node.parent_id
            
        return path
        
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history as a list of utterances
        
        Returns:
            List[Dict[str, Any]]: List of utterances with speaker and content
        """
        if not self.root_id:
            return []
            
        # Get the path from root to current node
        path = self.get_path_to_node(self.current_node_id)
        
        # Convert path to list of utterances
        history = []
        for node_id in path:
            node = self.nodes.get(node_id)
            if node and node.id != self.root_id:  # Skip the root node
                history.append({
                    "speaker": node.speaker,
                    "content": node.content
                })
                
        return history
        
    def _generate_initial_suggestions(self):
        """Generate initial suggestions for the conversation"""
        if not self.langchain_service:
            error_msg = "LangChain service not available"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            # Create fallback suggestions
            self._create_fallback_suggestions()
            return
            
        try:
            logger.info("Generating initial conversation suggestions")
            
            # Check if method exists
            if not hasattr(self.langchain_service, 'generate_conversation_suggestions'):
                logger.error("Method 'generate_conversation_suggestions' not found in LangChain service")
                # Create fallback suggestions
                self._create_fallback_suggestions()
                return
                
            # Prepare the prompt for initial suggestions
            prompt = self._create_initial_suggestions_prompt()
            logger.debug(f"Initial suggestions prompt: {prompt}")
            
            # Call LangChain service
            response = self.langchain_service.generate_conversation_suggestions(
                prompt=prompt,
                num_suggestions=3,
                context=self.conversation_context
            )
            
            # Process the response
            suggestions = self._parse_suggestions(response)
            logger.info(f"Received {len(suggestions)} initial suggestions")
            
            # Add suggestions as nodes
            self._add_suggestion_nodes(suggestions)
            
        except Exception as e:
            error_msg = f"Failed to generate initial suggestions: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)
            
            # Create fallback suggestions
            self._create_fallback_suggestions()
            
    def _create_fallback_suggestions(self):
        """Create fallback suggestions when LangChain fails"""
        suggestion_nodes = []
        fallback_suggestions = [
            {"speaker": "You", "content": "Hello, how can I help you today?"},
            {"speaker": "You", "content": "Let's start by discussing your needs."},
            {"speaker": "You", "content": "I'd like to understand more about what you're looking for."}
        ]
        
        for i, suggestion in enumerate(fallback_suggestions):
            node_id = f"suggestion_{len(self.nodes)}_{i}"
            node = ConversationNode(
                id=node_id,
                content=suggestion["content"],
                speaker=suggestion["speaker"],
                parent_id=self.current_node_id,
                node_type="suggested",
                metadata={"suggestion_index": i, "is_fallback": True}
            )
            self.nodes[node_id] = node
            if self.current_node_id in self.nodes:
                self.nodes[self.current_node_id].add_child(node_id)
            suggestion_nodes.append(node)
            
        # Emit signal with fallback suggestions
        self.suggestions_ready.emit(suggestion_nodes)
        logger.info("Fallback suggestions generated")
        
    def _add_suggestion_nodes(self, suggestions):
        """Add suggestion nodes to the tree
        
        Args:
            suggestions: List of suggestion dictionaries with speaker and content
        """
        suggestion_nodes = []
        for i, suggestion in enumerate(suggestions):
            node_id = f"suggestion_{len(self.nodes)}_{i}"
            node = ConversationNode(
                id=node_id,
                content=suggestion["content"],
                speaker=suggestion["speaker"],
                parent_id=self.current_node_id,
                node_type="suggested",
                metadata={"suggestion_index": i}
            )
            self.nodes[node_id] = node
            if self.current_node_id in self.nodes:
                self.nodes[self.current_node_id].add_child(node_id)
            suggestion_nodes.append(node)
            logger.debug(f"Added suggestion node: {node_id} - {suggestion['speaker']}: {suggestion['content'][:30]}...")
            
        # Emit signal with suggestions
        self.suggestions_ready.emit(suggestion_nodes)
        logger.info("Suggestions added successfully")
            
    def _generate_suggestions_for_current_node(self):
        """Generate suggestions for the current node"""
        if not self.langchain_service:
            self.error_occurred.emit("LangChain service not available")
            return
            
        try:
            # Check if method exists
            if not hasattr(self.langchain_service, 'generate_conversation_suggestions'):
                logger.error("Method 'generate_conversation_suggestions' not found in LangChain service")
                # Create fallback suggestions
                self._create_fallback_suggestions()
                return
                
            # Get conversation history
            history = self.get_conversation_history()
            
            # Prepare the prompt for suggestions
            prompt = self._create_suggestions_prompt(history)
            
            # Call LangChain service - adjust number of suggestions based on mode
            num_suggestions = 5 if hasattr(self, 'conversation_mode') and self.conversation_mode == "guided" else 3
            
            response = self.langchain_service.generate_conversation_suggestions(
                prompt=prompt,
                num_suggestions=num_suggestions,
                context=self.conversation_context,
                history=history
            )
            
            # Process the response
            suggestions = self._parse_suggestions(response)
            
            # Add suggestions as nodes
            self._add_suggestion_nodes(suggestions)
            
        except Exception as e:
            error_msg = f"Failed to generate suggestions: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)
            
            # Create fallback suggestions
            self._create_fallback_suggestions()
            
    def _create_initial_suggestions_prompt(self) -> str:
        """Create a prompt for generating initial suggestions
        
        Returns:
            str: The prompt text
        """
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
        
    def _create_suggestions_prompt(self, history: List[Dict[str, Any]]) -> str:
        """Create a prompt for generating suggestions based on conversation history
        
        Args:
            history: List of conversation utterances
            
        Returns:
            str: The prompt text
        """
        participants = ", ".join(self.conversation_context.get("participants", []))
        goals = "\n".join([f"- {goal}" for goal in self.conversation_context.get("goals", [])])
        
        # Format conversation history
        history_text = ""
        for utterance in history:
            history_text += f"{utterance['speaker']}: {utterance['content']}\n"
            
        prompt = f"""
You are an expert conversation assistant helping with a conversation between {participants}.

Conversation Title: {self.conversation_context.get("title", "Untitled Conversation")}
Description: {self.conversation_context.get("description", "")}

Goals of the conversation:
{goals}

Here is the conversation so far:

{history_text}

Please suggest 3 different ways the conversation could continue effectively. Consider different participants who might speak next and different directions the conversation could take.

For each suggestion, specify:
1. Which participant should speak next
2. What they should say to move the conversation forward effectively

Format your response as a JSON array with "speaker" and "content" fields.
"""
        return prompt
        
    def _parse_suggestions(self, response: str) -> List[Dict[str, str]]:
        """Parse suggestions from LangChain response
        
        Args:
            response: The response from LangChain
            
        Returns:
            List[Dict[str, str]]: List of suggestions with speaker and content
        """
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
    def _generate_guided_suggestions(self):
        """Generate more extensive suggestions for guided conversation mode"""
        if not self.langchain_service:
            error_msg = "LangChain service not available"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            # Create fallback suggestions
            self._create_fallback_suggestions()
            return
            
        try:
            logger.info("Generating guided conversation suggestions")
            
            # Check if method exists
            if not hasattr(self.langchain_service, 'generate_conversation_suggestions'):
                logger.error("Method 'generate_conversation_suggestions' not found in LangChain service")
                # Create fallback suggestions
                self._create_fallback_suggestions()
                return
                
            # Prepare the prompt for guided suggestions
            prompt = self._create_guided_suggestions_prompt()
            logger.debug(f"Guided suggestions prompt: {prompt}")
            
            # Call LangChain service with more suggestions for guided mode
            response = self.langchain_service.generate_conversation_suggestions(
                prompt=prompt,
                num_suggestions=5,  # More suggestions for guided mode
                context=self.conversation_context
            )
            
            # Process the response
            suggestions = self._parse_suggestions(response)
            logger.info(f"Received {len(suggestions)} guided suggestions")
            
            # Add suggestions as nodes
            self._add_suggestion_nodes(suggestions)
            
        except Exception as e:
            error_msg = f"Failed to generate guided suggestions: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)
            
            # Create fallback suggestions
            self._create_fallback_suggestions()

    def _create_guided_suggestions_prompt(self) -> str:
        """Create a prompt for generating guided conversation suggestions
        
        Returns:
            str: The prompt text
        """
        participants = ", ".join(self.conversation_context.get("participants", []))
        goals = "\n".join([f"- {goal}" for goal in self.conversation_context.get("goals", [])])
        
        prompt = f"""
You are an expert conversation guide helping with a structured conversation between {participants}.

Conversation Title: {self.conversation_context.get("title", "Untitled Conversation")}
Description: {self.conversation_context.get("description", "")}

Goals of the conversation:
{goals}

The conversation is just beginning. Please suggest 5 different structured approaches to this conversation.
For each suggestion, provide:
1. Which participant should speak
2. What they should say to effectively guide the conversation
3. How this approach helps achieve the conversation goals

Your suggestions should provide clear direction and structure for the conversation.
Each suggestion should represent a different possible path the conversation could take.

Format your response as a JSON array with "speaker" and "content" fields.
"""
        return prompt
            
    def save_tree(self, file_path: str) -> bool:
        """Save the conversation tree to a file
        
        Args:
            file_path: Path to save the file
            
        Returns:
            bool: Success status
        """
        try:
            logger.info(f"Saving conversation tree to {file_path}")
            
            data = {
                "context": self.conversation_context,
                "root_id": self.root_id,
                "current_node_id": self.current_node_id,
                "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()}
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
            logger.info(f"Tree saved successfully with {len(self.nodes)} nodes")
            return True
            
        except Exception as e:
            error_msg = f"Failed to save tree: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)
            return False
            
    def load_tree(self, file_path: str) -> bool:
        """Load a conversation tree from a file
        
        Args:
            file_path: Path to the file
            
        Returns:
            bool: Success status
        """
        try:
            logger.info(f"Loading conversation tree from {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.conversation_context = data.get("context", {})
            self.root_id = data.get("root_id")
            self.current_node_id = data.get("current_node_id")
            
            # Load nodes
            self.nodes = {}
            for node_id, node_data in data.get("nodes", {}).items():
                self.nodes[node_id] = ConversationNode.from_dict(node_data)
                
            logger.info(f"Tree loaded successfully with {len(self.nodes)} nodes")
            self.tree_updated.emit()
            return True
            
        except Exception as e:
            error_msg = f"Failed to load tree: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)
            return False
