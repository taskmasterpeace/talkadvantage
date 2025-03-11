from PyQt6.QtCore import QSettings
from typing import Any, Dict, Optional, Union, List, Type, TypeVar, cast
import os
import json
from pathlib import Path
import logging

# Type variable for generic type hints
T = TypeVar('T')

class ConfigurationService:
    """
    Centralized service for managing application configuration and settings.
    
    This class provides a singleton pattern for accessing settings, with
    validation, type-safe getters and setters, and consistent default values.
    """
    
    _instance = None
    
    def __new__(cls):
        """Implement singleton pattern"""
        if cls._instance is None:
            cls._instance = super(ConfigurationService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the configuration service"""
        # Only initialize once
        if self._initialized:
            return
            
        # Initialize QSettings with organization and application name
        self.settings = QSettings("PowerPlay", "MeetingAssistant")
        
        # Initialize logger
        self.logger = logging.getLogger("ConfigurationService")
        
        # Define settings schema with types and default values
        self.schema = {
            # API Keys
            "openai_api_key": {"type": str, "default": "", "sensitive": True},
            "assemblyai_api_key": {"type": str, "default": "", "sensitive": True},
            
            # LLM Settings
            "llm_model": {"type": str, "default": "gpt-4o-mini", "options": [
                "gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"
            ]},
            "temperature": {"type": float, "default": 0.7, "min": 0.0, "max": 1.0},
            "max_tokens": {"type": int, "default": 2000, "min": 100, "max": 4000},
            
            # Recording Settings
            "audio_sample_rate": {"type": int, "default": 16000, "options": [8000, 16000, 44100, 48000]},
            "audio_channels": {"type": int, "default": 1, "options": [1, 2]},
            
            # UI Settings
            "live_text_font": {"type": dict, "default": {"family": "Arial", "size": 12}},
            "analysis_text_font": {"type": dict, "default": {"family": "Arial", "size": 12}},
            
            # System Settings
            "debug_mode": {"type": bool, "default": False},
            "system_triggers": {"type": list, "default": [
                {
                    "action": "Create Quick Bookmark",
                    "trigger_phrase": "bookmark this",
                    "bookmark_name": "Quick Mark"
                },
                {
                    "action": "Create Named Bookmark",
                    "trigger_phrase": "mark important",
                    "bookmark_name": "Important Point"
                }
            ]},
            
            # Paths
            "workspace_dir": {"type": str, "default": str(Path.home() / "PowerPlay" / "Workspace")},
            "recordings_dir": {"type": str, "default": str(Path.home() / "PowerPlay" / "Recordings")},
            "transcripts_dir": {"type": str, "default": str(Path.home() / "PowerPlay" / "Transcripts")},
            "templates_dir": {"type": str, "default": str(Path.home() / "PowerPlay" / "Templates")},
        }
        
        # Load environment variables for sensitive settings
        self._load_env_variables()
        
        # Initialize directories
        self._initialize_directories()
        
        self._initialized = True
        
    def _load_env_variables(self):
        """Load sensitive settings from environment variables"""
        for key, schema in self.schema.items():
            if schema.get("sensitive", False):
                env_value = os.getenv(key.upper())
                if env_value:
                    self.set(key, env_value)
    
    def _initialize_directories(self):
        """Initialize required directories"""
        for key, schema in self.schema.items():
            if key.endswith('_dir') and schema["type"] == str:
                directory = self.get(key)
                if directory:
                    os.makedirs(directory, exist_ok=True)
    
    def get(self, key: str, default_value: Any = None) -> Any:
        """
        Get a setting value with proper type conversion.
        
        Args:
            key: The setting key
            default_value: Optional default value if not found
            
        Returns:
            The setting value with proper type
        """
        if key not in self.schema:
            self.logger.warning(f"Accessing undefined setting: {key}")
            return default_value
            
        # Get schema info
        schema_info = self.schema[key]
        schema_default = schema_info.get("default", None)
        
        # Use provided default or schema default
        if default_value is None:
            default_value = schema_default
            
        # Get raw value from QSettings
        value = self.settings.value(key, default_value)
        
        # Handle type conversion
        return self._convert_value(value, schema_info["type"])
    
    def get_typed(self, key: str, type_hint: Type[T], default_value: Optional[T] = None) -> T:
        """
        Get a setting with explicit type hint for better IDE support.
        
        Args:
            key: The setting key
            type_hint: The expected type
            default_value: Optional default value
            
        Returns:
            The setting value with the specified type
        """
        value = self.get(key, default_value)
        return cast(type_hint, value)
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set a setting value with validation.
        
        Args:
            key: The setting key
            value: The value to set
            
        Returns:
            True if successful, False if validation failed
        """
        if key not in self.schema:
            self.logger.warning(f"Setting undefined setting: {key}")
            self.settings.setValue(key, value)
            return True
            
        # Get schema info
        schema_info = self.schema[key]
        
        # Validate value
        if not self._validate_value(value, schema_info):
            self.logger.error(f"Validation failed for {key}: {value}")
            return False
            
        # Convert complex types to JSON strings
        if isinstance(value, (dict, list)):
            self.settings.setValue(key, json.dumps(value))
        else:
            self.settings.setValue(key, value)
            
        # Update environment variable for sensitive settings
        if schema_info.get("sensitive", False):
            os.environ[key.upper()] = str(value)
            
        return True
    
    def _convert_value(self, value: Any, target_type: Type) -> Any:
        """Convert value to the target type"""
        if value is None:
            return None
            
        try:
            if target_type == bool:
                # Handle boolean conversion
                if isinstance(value, str):
                    return value.lower() in ('true', 'yes', '1', 'y')
                return bool(value)
                
            elif target_type == dict or target_type == list:
                # Handle complex types stored as JSON
                if isinstance(value, str):
                    try:
                        return json.loads(value)
                    except json.JSONDecodeError:
                        self.logger.error(f"Failed to parse JSON: {value}")
                        return target_type()
                elif isinstance(value, target_type):
                    return value
                else:
                    return target_type()
                    
            else:
                # Handle basic types
                return target_type(value)
                
        except (ValueError, TypeError) as e:
            self.logger.error(f"Type conversion error: {e}")
            if target_type == str:
                return ""
            elif target_type == int:
                return 0
            elif target_type == float:
                return 0.0
            elif target_type == bool:
                return False
            elif target_type == list:
                return []
            elif target_type == dict:
                return {}
            return None
    
    def _validate_value(self, value: Any, schema_info: Dict[str, Any]) -> bool:
        """Validate value against schema"""
        target_type = schema_info["type"]
        
        # Check type
        if not isinstance(value, target_type) and not (value is None and schema_info.get("nullable", False)):
            try:
                # Try to convert
                value = self._convert_value(value, target_type)
            except (ValueError, TypeError):
                return False
                
        # Check options
        if "options" in schema_info and value not in schema_info["options"]:
            return False
            
        # Check min/max for numeric types
        if isinstance(value, (int, float)):
            if "min" in schema_info and value < schema_info["min"]:
                return False
            if "max" in schema_info and value > schema_info["max"]:
                return False
                
        return True
    
    def reset(self, key: str) -> None:
        """Reset a setting to its default value"""
        if key in self.schema:
            default_value = self.schema[key].get("default")
            self.set(key, default_value)
        else:
            self.settings.remove(key)
    
    def reset_all(self) -> None:
        """Reset all settings to defaults"""
        self.settings.clear()
        for key, schema in self.schema.items():
            self.set(key, schema.get("default"))
    
    def export_settings(self, filepath: str) -> bool:
        """Export settings to a JSON file"""
        try:
            settings_dict = {}
            for key in self.schema.keys():
                # Skip sensitive settings
                if self.schema[key].get("sensitive", False):
                    continue
                settings_dict[key] = self.get(key)
                
            with open(filepath, 'w') as f:
                json.dump(settings_dict, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Failed to export settings: {e}")
            return False
    
    def import_settings(self, filepath: str) -> bool:
        """Import settings from a JSON file"""
        try:
            with open(filepath, 'r') as f:
                settings_dict = json.load(f)
                
            for key, value in settings_dict.items():
                if key in self.schema:
                    self.set(key, value)
            return True
        except Exception as e:
            self.logger.error(f"Failed to import settings: {e}")
            return False
