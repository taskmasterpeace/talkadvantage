import sqlite3
import os
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path

@dataclass
class SystemPrompt:
    id: Optional[int] = None
    name: str = ''
    description: str = ''
    content: str = ''
    is_default: bool = False

class SystemPromptManager:
    def __init__(self, db_path='system_prompts.db'):
        self.db_path = db_path
        self._create_table()
        self._ensure_default_prompt()  # Keep original default
        self._ensure_default_prompts() # Add our persona prompts
        
    def _ensure_default_prompts(self):
        """Ensure default system prompt exists"""
        # Call _ensure_default_prompt to set up our single prompt
        self._ensure_default_prompt()

    def _create_table(self):
        """Create system prompts table if not exists"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS system_prompts (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE,
                    description TEXT,
                    content TEXT,
                    is_default BOOLEAN DEFAULT 0
                )
            ''')
            conn.commit()

    def _ensure_default_prompt(self):
        """Ensure a default system prompt exists"""
        default_prompt = SystemPrompt(
            name='Default Analysis Prompt',
            description='Standard system prompt for general analysis',
            content="""You are an AI assistant analyzing conversation transcripts. Your key behaviors:

1. Process each text segment according to the template instructions provided
2. If this is part of a sequence, use any provided conversation_summary for context
3. If no summary is provided, treat the segment as a standalone analysis
4. Always prioritize the specific template instructions for your response format
5. Maintain professional, clear, and concise analysis

Your responses should exactly match what the template asks for - no more, no less.""",
            is_default=True
        )
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM system_prompts WHERE is_default = 1')
            if not cursor.fetchone():
                self.save_prompt(default_prompt)

    def save_prompt(self, prompt: SystemPrompt) -> int:
        """Save a system prompt, returns the ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if prompt.is_default:
                cursor.execute('UPDATE system_prompts SET is_default = 0')
            
            if prompt.id:
                cursor.execute('''
                    UPDATE system_prompts 
                    SET name = ?, description = ?, content = ?, is_default = ?
                    WHERE id = ?
                ''', (prompt.name, prompt.description, prompt.content, prompt.is_default, prompt.id))
            else:
                cursor.execute('''
                    INSERT INTO system_prompts 
                    (name, description, content, is_default) 
                    VALUES (?, ?, ?, ?)
                ''', (prompt.name, prompt.description, prompt.content, prompt.is_default))
                prompt.id = cursor.lastrowid
            
            conn.commit()
            return prompt.id

    def get_prompt(self, id_or_name) -> Optional[SystemPrompt]:
        """Get a system prompt by ID or name"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if isinstance(id_or_name, int):
                cursor.execute('SELECT * FROM system_prompts WHERE id = ?', (id_or_name,))
            else:
                cursor.execute('SELECT * FROM system_prompts WHERE name = ?', (id_or_name,))
            
            row = cursor.fetchone()
            if row:
                return SystemPrompt(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    content=row['content'],
                    is_default=bool(row['is_default'])
                )
            return None

    def get_all_prompts(self) -> List[SystemPrompt]:
        """Get all system prompts"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM system_prompts ORDER BY name')
            
            return [
                SystemPrompt(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    content=row['content'],
                    is_default=bool(row['is_default'])
                ) for row in cursor.fetchall()
            ]

    def delete_prompt(self, id_or_name) -> bool:
        """Delete a system prompt"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if isinstance(id_or_name, int):
                cursor.execute('DELETE FROM system_prompts WHERE id = ? AND is_default = 0', (id_or_name,))
            else:
                cursor.execute('DELETE FROM system_prompts WHERE name = ? AND is_default = 0', (id_or_name,))
            
            success = cursor.rowcount > 0
            conn.commit()
            return success
