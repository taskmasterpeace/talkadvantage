from PyQt6.QtCore import QObject, pyqtSignal, QThread
from typing import Optional, Dict, Any
import os
from services.openai_service import OpenAITranscriptionService
from services.assemblyai_service import AssemblyAITranscriptionService
from qt_version.services.langchain_service import LangChainService

class TranscriptionWorker(QThread):
    """Worker thread for transcription tasks"""
    
    progress = pyqtSignal(str, int, int)  # file, current, total
    finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, service, files):
        super().__init__()
        self.service = service
        self.files = files
        self.stop_flag = False
    
    def run(self):
        total = len(self.files)
        processed = 0
        
        for file in self.files:
            if self.stop_flag:
                break
                
            try:
                self.progress.emit(file, processed, total)
                result = self.service.transcribe(file)
                
                # Save transcript
                output_file = f"{os.path.splitext(file)[0]}_transcript.txt"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result)
                    
                processed += 1
                
            except Exception as e:
                self.finished.emit(False, str(e))
                return
        
        self.finished.emit(True, f"Processed {processed} files")
    
    def stop(self):
        self.stop_flag = True

class QtServiceAdapter(QObject):
    """Adapts transcription services for Qt"""
    
    progress_update = pyqtSignal(str, int, int)  # file, current, total
    status_update = pyqtSignal(str)  # status message
    transcription_complete = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, app=None):
        super().__init__()
        self.app = app
        self._debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        
        # Get settings manager
        from qt_version.utils.settings_manager import SettingsManager
        self.settings_manager = SettingsManager()
        
        # Initialize services with debug mode
        self.openai_service = OpenAITranscriptionService()
        self.openai_service._debug_mode = self._debug_mode
        
        self.assemblyai_service = AssemblyAITranscriptionService()
        self.assemblyai_service._debug_mode = self._debug_mode
        
        self.langchain_service = LangChainService()
        self.langchain_service._debug_mode = self._debug_mode
        self.langchain_service.app = app  # Pass app reference to LangChain service
        self.current_worker: Optional[TranscriptionWorker] = None
        
        # Initialize all services with keys from settings
        self.init_services()
    
    def init_services(self):
        """Initialize all services with keys from settings manager"""
        # Get keys from settings (this also updates env vars)
        openai_key = self.settings_manager.get_setting('OPENAI_API_KEY')
        assemblyai_key = self.settings_manager.get_setting('ASSEMBLYAI_API_KEY')
        
        if self._debug_mode:
            print("Initializing services with keys from settings manager")
            
        self.setup_services(openai_key, assemblyai_key)
        
    def setup_services(self, openai_key: str, assemblyai_key: str):
        """Initialize services with provided API keys"""
        try:
            success = True
            message = []
            
            if openai_key:
                try:
                    self.openai_service.setup(openai_key)
                    if self._debug_mode:
                        print(f"OpenAI service initialized with key: {'*' * len(openai_key)}")
                    message.append("OpenAI service initialized")
                except Exception as e:
                    success = False
                    message.append(f"OpenAI setup failed: {str(e)}")
                    
            if assemblyai_key:
                try:
                    self.assemblyai_service.setup(assemblyai_key)
                    if self._debug_mode:
                        print(f"AssemblyAI service initialized with key: {'*' * len(assemblyai_key)}")
                    message.append("AssemblyAI service initialized")
                except Exception as e:
                    success = False
                    message.append(f"AssemblyAI setup failed: {str(e)}")
                    
            return success, "; ".join(message)
        except Exception as e:
            return False, f"Failed to initialize services: {str(e)}"
    
    def process_files(self, files: list, service: str = "openai"):
        """Start processing files with selected service"""
        if self.current_worker and self.current_worker.isRunning():
            return False, "A transcription task is already running"
        
        service_obj = (self.openai_service if service == "openai" 
                      else self.assemblyai_service)
        
        self.current_worker = TranscriptionWorker(service_obj, files)
        self.current_worker.progress.connect(self.progress_update)
        self.current_worker.finished.connect(self.transcription_complete)
        self.current_worker.start()
        
        return True, "Started processing files"
    
    def stop_processing(self):
        """Stop current processing task"""
        if self.current_worker:
            self.current_worker.stop()
            self.current_worker.wait()
            self.current_worker = None
            
    def cleanup(self):
        """Clean up resources before shutdown"""
        try:
            # Stop any running workers
            if self.current_worker and self.current_worker.isRunning():
                self.current_worker.stop()
                self.current_worker.wait()

            # Clean up services
            if hasattr(self, 'langchain_service'):
                self.langchain_service.save_template_stats()
                
        except Exception as e:
            print(f"Error cleaning up service adapter: {e}")
