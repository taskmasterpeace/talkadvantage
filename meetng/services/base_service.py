import os
from typing import Optional
from dotenv import load_dotenv
from enum import Enum

class ServiceState(Enum):
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready" 
    ERROR = "error"

class TranscriptionService:
    """Base class for transcription services with state management"""
    
    def __init__(self):
        load_dotenv()
        self._state = ServiceState.UNINITIALIZED
        self._api_key = None
        self._debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        self._error_message = None
        
    def setup(self, api_key: Optional[str] = None) -> bool:
        """Initialize service with API key and state management"""
        try:
            self._state = ServiceState.INITIALIZING
            self._api_key = api_key or os.getenv(self.get_env_key())
            
            if not self._api_key:
                self._state = ServiceState.ERROR
                self._error_message = "No API key provided"
                if self._debug_mode:
                    print(f"Failed to initialize {self.__class__.__name__}: No API key")
                return False
                
            # Validate API key format
            if not self._validate_api_key(self._api_key):
                self._state = ServiceState.ERROR
                self._error_message = "Invalid API key format"
                return False
                
            self._state = ServiceState.READY
            if self._debug_mode:
                print(f"Initialized {self.__class__.__name__} with API key")
            return True
            
        except Exception as e:
            self._state = ServiceState.ERROR
            self._error_message = str(e)
            if self._debug_mode:
                print(f"Error initializing {self.__class__.__name__}: {e}")
            return False
        
    def get_env_key(self) -> str:
        """Get environment variable name for API key"""
        raise NotImplementedError
        
    def _validate_api_key(self, api_key: str) -> bool:
        """Validate API key format - to be implemented by subclasses"""
        raise NotImplementedError
        
    def get_state(self) -> ServiceState:
        """Get current service state"""
        return self._state
        
    def get_error_message(self) -> Optional[str]:
        """Get last error message"""
        return self._error_message
        
    def is_ready(self) -> bool:
        """Check if service is ready for use"""
        return self._state == ServiceState.READY

    def transcribe(self, file_path: str, config: Optional[dict] = None) -> str:
        """Transcribe audio file with state checking"""
        if self._state == ServiceState.UNINITIALIZED:
            self.setup()  # Try to initialize with environment variable
            
        if self._state != ServiceState.READY:
            raise ValueError(
                f"{self.__class__.__name__} not ready. "
                f"Current state: {self._state.value}. "
                f"Error: {self._error_message or 'Unknown error'}"
            )
            
        if self._debug_mode:
            print(f"Transcribing with {self.__class__.__name__}")
            print(f"Config: {config}")
            
        return self._transcribe_impl(file_path, config)
        
    def _transcribe_impl(self, file_path: str, config: Optional[dict] = None) -> str:
        """Implementation of transcription - to be overridden by subclasses"""
        raise NotImplementedError
        
    def reset(self) -> None:
        """Reset service state"""
        self._state = ServiceState.UNINITIALIZED
        self._api_key = None
        self._error_message = None
