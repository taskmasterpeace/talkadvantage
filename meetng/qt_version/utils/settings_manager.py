import sqlite3
import os
from pathlib import Path

class SettingsManager:
    """Manages persistent settings storage using SQLite"""
    
    def __init__(self, db_path='settings.db'):
        """Initialize settings manager with secure storage"""
        # Use the user's app data directory for settings
        app_data = os.getenv('APPDATA') if os.name == 'nt' else os.path.expanduser('~/.config')
        self.db_path = os.path.join(app_data, 'PowerPlay', db_path)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        self.init_db()

    def get_connection(self):
        """Get a database connection"""
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """Initialize SQLite database and create settings table"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    )
                ''')
                
                # Add default curiosity engine prompt if it doesn't exist
                default_prompt = '''[SYSTEM INSTRUCTIONS - DO NOT MODIFY THIS SECTION]
You are an expert active listener analyzing meeting transcripts. 
Generate 2-3 insightful questions that would help understand the context better.

[QUESTION TYPES - DO NOT MODIFY THESE TYPES]
Question types:
- YES_NO: Simple yes/no questions
- MULTIPLE_CHOICE: Questions with predefined options (provide 3-4 choices)
- MULTIPLE_CHOICE_FILL: Multiple choice with an "other" option (provide 3-4 choices)

[CUSTOMIZABLE GUIDELINES - YOU CAN MODIFY THIS SECTION]
Generate questions that:
- Are relevant to the transcript content
- Help clarify important points
- Uncover underlying context
- Are concise and clear
- Have meaningful multiple choice options when applicable

[OUTPUT FORMAT - DO NOT MODIFY THIS SECTION]
Return a list of questions in the specified format.'''

                cursor = conn.cursor()
                cursor.execute(
                    'INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)',
                    ('curiosity_engine_prompt', default_prompt)
                )
                conn.commit()
        except Exception as e:
            print(f"Error initializing database: {e}")

    def save_setting(self, key: str, value: str):
        """Save or update a setting with proper connection handling"""
        try:
            if not value:
                print(f"Warning: Attempting to save empty value for {key}")
                return
                
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO settings 
                    (key, value) 
                    VALUES (?, ?)
                ''', (key, value))
                conn.commit()
                
                # Verify the save
                cursor = conn.execute('SELECT value FROM settings WHERE key = ?', (key,))
                saved_value = cursor.fetchone()
                if not saved_value or saved_value[0] != value:
                    raise ValueError(f"Value verification failed for {key}")
                    
                if os.getenv('DEBUG_MODE', 'false').lower() == 'true':
                    print(f"Saved and verified setting {key}: {'*' * len(value)}")
                    
                # Update environment variable
                os.environ[key] = value
                
        except Exception as e:
            print(f"Error saving setting {key}: {e}")
            raise

    def get_setting(self, key: str, default: str = None) -> str:
        """Retrieve a setting value with proper connection handling"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('SELECT value FROM settings WHERE key = ?', (key,))
                result = cursor.fetchone()
                value = result[0] if result else default
                if os.getenv('DEBUG_MODE', 'false').lower() == 'true':
                    print(f"Loading setting {key}: {'*' * len(value) if value else 'None'}")
                    
                # Update environment variable for API keys
                if key.endswith('_API_KEY') and value:
                    os.environ[key] = value
                    
                return value
        except Exception as e:
            print(f"Error getting setting {key}: {e}")
            return default

    def delete_setting(self, key: str):
        """Delete a setting with proper connection handling"""
        try:
            with self.get_connection() as conn:
                conn.execute('DELETE FROM settings WHERE key = ?', (key,))
                conn.commit()
                if os.getenv('DEBUG_MODE', 'false').lower() == 'true':
                    print(f"Deleted setting {key}")
        except Exception as e:
            print(f"Error deleting setting {key}: {e}")
            raise

    def get_all_settings(self) -> dict:
        """Get all settings as a dictionary with proper connection handling"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('SELECT key, value FROM settings')
                settings = dict(cursor.fetchall())
                if os.getenv('DEBUG_MODE', 'false').lower() == 'true':
                    print(f"Loaded {len(settings)} settings")
                return settings
        except Exception as e:
            print(f"Error getting all settings: {e}")
            return {}
            
    def close(self):
        """Close database connection"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.commit()
        except Exception as e:
            print(f"Error closing settings database: {e}")
            
    def test_persistence(self) -> bool:
        """Test settings persistence"""
        test_key = "_TEST_SETTING"
        test_value = "test_value"
        
        try:
            # Save test setting
            self.save_setting(test_key, test_value)
            
            # Verify it was saved
            saved_value = self.get_setting(test_key)
            if saved_value != test_value:
                print(f"Test failed: Saved value '{saved_value}' doesn't match test value '{test_value}'")
                return False
                
            # Clean up test setting
            self.delete_setting(test_key)
            
            # Verify deletion
            deleted_value = self.get_setting(test_key)
            if deleted_value is not None:
                print(f"Test failed: Setting still exists after deletion")
                return False
                
            print("Settings persistence test passed!")
            return True
            
        except Exception as e:
            print(f"Test failed with error: {e}")
            return False
