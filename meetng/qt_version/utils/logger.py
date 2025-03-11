import logging
import os
from datetime import datetime
from pathlib import Path

class Logger:
    """Centralized logging system for the application"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the logger"""
        self.logger = logging.getLogger('PowerPlay')
        self.logger.setLevel(logging.DEBUG)
        
        # Create logs directory if it doesn't exist
        logs_dir = Path('logs')
        logs_dir.mkdir(exist_ok=True)
        
        # Create file handler with rotation
        log_file = logs_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add the handlers to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Set debug mode based on environment variable
        self.debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        
    def get_logger(self, name=None):
        """Get a logger instance with the given name"""
        if name:
            return logging.getLogger(f'PowerPlay.{name}')
        return self.logger
    
    def is_debug_mode(self):
        """Check if debug mode is enabled"""
        return self.debug_mode

# Create a convenience function to get a logger
def get_logger(name=None):
    """Get a logger instance with the given name"""
    return Logger().get_logger(name)
