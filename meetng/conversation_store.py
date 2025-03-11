from typing import Dict, List, Optional
import json
import os
from datetime import datetime
from langchain.memory import ConversationBufferMemory

class ConversationStore:
    """Handles persistence of conversation history and state"""
    
    def __init__(self, base_path: str = "conversations"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
        
    def save_conversation(self, conversation_id: str, data: Dict) -> bool:
        """Save conversation state to disk"""
        try:
            # Ensure valid filename
            safe_id = "".join(c for c in conversation_id if c.isalnum() or c in (' ', '-', '_')).strip()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{safe_id}_{timestamp}.json"
            
            # Convert memory to serializable format
            if 'memory' in data and isinstance(data['memory'], ConversationBufferMemory):
                data['memory'] = {
                    'messages': data['memory'].chat_memory.messages,
                    'return_messages': data['memory'].return_messages,
                    'memory_key': data['memory'].memory_key,
                    'output_key': data['memory'].output_key
                }
                
            filepath = os.path.join(self.base_path, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            return True
            
        except Exception as e:
            print(f"Error saving conversation: {e}")
            return False
            
    def load_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Load most recent conversation state for given ID"""
        try:
            # Find most recent matching file
            files = [f for f in os.listdir(self.base_path) 
                    if f.startswith(conversation_id) and f.endswith('.json')]
            if not files:
                return None
                
            latest = max(files, key=lambda f: f.split('_')[-1].split('.')[0])
            
            with open(os.path.join(self.base_path, latest), 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Reconstruct memory if present
            if 'memory' in data:
                mem_data = data['memory']
                memory = ConversationBufferMemory(
                    memory_key=mem_data['memory_key'],
                    return_messages=mem_data['return_messages'],
                    output_key=mem_data['output_key']
                )
                memory.chat_memory.messages = mem_data['messages']
                data['memory'] = memory
                
            return data
            
        except Exception as e:
            print(f"Error loading conversation: {e}")
            return None
            
    def list_conversations(self) -> List[Dict]:
        """List all saved conversations"""
        conversations = []
        try:
            for filename in os.listdir(self.base_path):
                if filename.endswith('.json'):
                    conv_id = filename.split('_')[0]
                    timestamp = filename.split('_')[1].split('.')[0]
                    conversations.append({
                        'id': conv_id,
                        'timestamp': timestamp,
                        'filename': filename
                    })
        except Exception as e:
            print(f"Error listing conversations: {e}")
        return conversations
