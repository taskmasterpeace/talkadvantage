from PyQt6.QtCore import QObject, pyqtSignal, QThread
import time
import os
import markdown
from typing import Optional, Dict, Any, List, Union

class ProcessingWorker(QThread):
    """
    Worker thread for processing text analysis in the background.
    
    This class handles the processing of text through language models without
    blocking the UI. It supports both regular and full analysis modes, with
    different chunking strategies for each.
    
    Signals:
        finished: Emitted when processing completes with the result text
        error: Emitted when an error occurs during processing
        progress: Emitted to update progress (value, max, status message)
    """
    
    finished = pyqtSignal(str)  # Signal to emit result
    error = pyqtSignal(str)     # Signal to emit error
    progress = pyqtSignal(int, int, str)  # value, max, status

    def __init__(self, langchain_service: Any, text: str, 
                template: Dict[str, Any], is_full_analysis: bool = False):
        """
        Initialize the processing worker.
        
        Args:
            langchain_service: The LangChain service for text processing
            text: The text to analyze
            template: The template to use for analysis
            is_full_analysis: Whether to perform a more comprehensive analysis
                             with larger chunks (default: False)
        """
        super().__init__()
        self.langchain_service = langchain_service
        self.text = text
        self.template = template
        self.is_full_analysis = is_full_analysis
        self._cancelled = False
        self.chunk_size = 2500 if is_full_analysis else 1500  # Smaller chunks for regular analysis

    def run(self) -> None:
        """
        Execute the text processing task.
        
        This method is called when the thread starts. It processes the text
        according to the selected mode (regular or full analysis), handles
        chunking for longer texts, and emits progress updates.
        
        For full analysis, the text is split into chunks and each chunk is
        processed separately, with results combined at the end. For regular
        analysis, the entire text is processed as a single unit.
        
        Emits:
            progress: During processing to update progress
            finished: When processing completes successfully
            error: If an error occurs during processing
        """
        try:
            # Process text
            if self.is_full_analysis:
                # For full analysis, process in larger chunks
                chunks = self.split_into_chunks(self.text, chunk_size=self.chunk_size)
                results = []
                total_chunks = len(chunks)
                
                for i, chunk in enumerate(chunks):
                    if self._cancelled:
                        return
                    
                    result = self.langchain_service.process_chunk(
                        chunk, 
                        self.template,
                        is_full_analysis=True
                    )
                    results.append(result)
                    
                    # Update status through parent's status label
                    progress = int((i + 1) / total_chunks * 100)
                    self.progress.emit(progress, 100, 
                        f"⚡ Full analysis: {i+1}/{total_chunks} sections")
                
                final_result = "\n\n".join(results)
                
            else:
                # Regular analysis
                self.progress.emit(50, 100, "Processing text...")
                final_result = self.langchain_service.process_chunk(
                    self.text, 
                    self.template,
                    is_full_analysis=False
                )
            
            self.progress.emit(100, 100, "Completing analysis...")
            self.finished.emit(final_result)
            
        except Exception as e:
            self.error.emit(str(e))

    def split_into_chunks(self, text: str, chunk_size: int = 1000) -> List[str]:
        """
        Split text into manageable chunks for processing.
        
        This method divides the input text into smaller chunks based on word
        boundaries, attempting to keep each chunk close to the specified size
        while preserving word integrity.
        
        Args:
            text: The text to split into chunks
            chunk_size: The approximate target size for each chunk in characters
        
        Returns:
            A list of text chunks, each approximately chunk_size characters
        """
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            current_size += len(word) + 1
            if current_size > chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_size = len(word) + 1
            else:
                current_chunk.append(word)
                
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        return chunks

    def cancel(self) -> None:
        """
        Cancel the ongoing processing.
        
        This sets a flag that will be checked during processing to abort
        the operation cleanly without terminating the thread abruptly.
        """
        self._cancelled = True

class CuriosityWorker(QThread):
    """
    Worker thread for generating curiosity questions in the background.
    
    This class handles the generation of curiosity questions based on
    transcript content without blocking the UI.
    
    Signals:
        questions_ready: Emitted when questions are generated successfully
        error: Emitted when an error occurs during question generation
    """
    
    questions_ready = pyqtSignal(list)  # Signal to emit generated questions
    error = pyqtSignal(str)             # Signal to emit error message
    
    def __init__(self, text: str, template: Dict[str, Any]):
        """
        Initialize the curiosity worker.
        
        Args:
            text: The text to generate questions from
            template: The template to use for question generation
        """
        super().__init__()
        self.text = text
        self.template = template
        
    def run(self) -> None:
        """
        Execute the question generation task.
        
        This method is called when the thread starts. It uses the CuriosityEngine
        to generate questions based on the provided text and template.
        
        Emits:
            questions_ready: When questions are generated successfully
            error: If an error occurs during question generation
        """
        try:
            from qt_version.services.curiosity_engine import CuriosityEngine
            curiosity_engine = CuriosityEngine()
            questions = curiosity_engine.generate_questions(self.text, self.template)
            self.questions_ready.emit(questions)
        except Exception as e:
            self.error.emit(str(e))

class AnalysisManager(QObject):
    """
    Manages AI analysis functionality.
    
    This class handles the processing of text through language models for analysis,
    manages templates, and coordinates the generation of insights and curiosity
    questions. It serves as a bridge between the UI and the language model services.
    
    The AnalysisManager uses worker threads for background processing to keep
    the UI responsive during potentially lengthy analysis operations.
    
    Signals:
        analysis_complete: Emitted when analysis completes with result, processing time, and template name
        analysis_error: Emitted when an error occurs during analysis
        status_changed: Emitted when the status of the analysis process changes
        progress_updated: Emitted to update progress of long-running analyses
        questions_ready: Emitted when curiosity questions are generated
    """
    
    # Signals
    analysis_complete = pyqtSignal(str, float, str)  # result, process_time, template_name
    analysis_error = pyqtSignal(str)  # error message
    status_changed = pyqtSignal(str)  # status message
    progress_updated = pyqtSignal(int, int, str)  # value, max, status
    questions_ready = pyqtSignal(list)  # curiosity questions
    
    def __init__(self, parent: Optional[QObject] = None):
        """
        Initialize the AnalysisManager.
        
        Sets up the analysis manager with default values and connects to the
        parent application if available.
        
        Args:
            parent: The parent QObject, typically a UI component that will
                   receive signals from this manager
        """
        super().__init__(parent)
        self._debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        self.worker: Optional[ProcessingWorker] = None
        self.curiosity_worker: Optional[CuriosityWorker] = None
        self.process_start_time: float = 0
        self.templates_cache: List[Dict[str, Any]] = []
        self.current_template: Optional[Dict[str, Any]] = None
        self.app = parent.app if parent and hasattr(parent, 'app') else None
        
    def load_templates(self, preserve_selection: bool = True) -> List[Dict[str, Any]]:
        """
        Load available templates from the language model service.
        
        This method retrieves the available templates from the LangChain service
        and updates the internal cache. It can optionally preserve the current
        template selection if the template still exists in the new list.
        
        Args:
            preserve_selection: Whether to preserve the current template selection
                               if possible (default: True)
        
        Returns:
            A list of template dictionaries, each containing at minimum a "name" key
        
        Emits:
            analysis_error: If templates cannot be loaded
        """
        if not self.app or not hasattr(self.app, 'service_adapter'):
            self.analysis_error.emit("Service adapter not available")
            return []
            
        try:
            # Store current selection
            current_template_name = None
            if preserve_selection and self.current_template:
                current_template_name = self.current_template.get("name")
                
            # Get templates
            templates = self.app.service_adapter.langchain_service.get_available_templates()
            
            # Store templates in cache
            self.templates_cache = templates
            
            # Restore previous selection if it still exists
            if preserve_selection and current_template_name:
                for template in templates:
                    if template.get("name") == current_template_name:
                        self.current_template = template
                        break
            elif templates:
                # Default to first template
                self.current_template = templates[0]
                
            return templates
            
        except Exception as e:
            error_msg = f"Failed to load templates: {str(e)}"
            self.analysis_error.emit(error_msg)
            return []
            
    def set_current_template(self, template_name: str) -> bool:
        """
        Set the current template by name.
        
        This method searches the template cache for a template with the specified
        name and sets it as the current template if found.
        
        Args:
            template_name: The name of the template to set as current
        
        Returns:
            True if the template was found and set, False otherwise
        """
        for template in self.templates_cache:
            if template.get("name") == template_name:
                self.current_template = template
                return True
        return False
        
    def get_template_description(self, template_name: str) -> str:
        """
        Get the description for a specific template.
        
        This method searches the template cache for a template with the specified
        name and returns its description if found.
        
        Args:
            template_name: The name of the template to get the description for
        
        Returns:
            The template description, or an empty string if the template is not found
            or has no description
        """
        for template in self.templates_cache:
            if template.get("name") == template_name:
                return template.get("description", "")
        return ""
        
    def process_text(self, text: str, template_name: Optional[str] = None, 
                    is_full_analysis: bool = False) -> bool:
        """
        Process text for AI analysis.
        
        This method handles the processing of text through language models for analysis.
        It validates inputs, sets up the environment, creates a worker thread for
        background processing, and initiates curiosity question generation.
        
        Args:
            text: The text to analyze
            template_name: Optional name of the template to use. If not provided,
                          the current template will be used.
            is_full_analysis: Whether to perform a more comprehensive analysis
                             with larger chunks (default: False)
        
        Returns:
            True if processing was started successfully, False otherwise
        
        Emits:
            analysis_error: If processing cannot be started
            status_changed: When processing begins
        """
        if not text.strip():
            self.analysis_error.emit("No text to analyze")
            return False
            
        try:
            # Get API key from environment
            openai_key = os.getenv('OPENAI_API_KEY')
            
            if not openai_key:
                self.analysis_error.emit("OpenAI API key not found in settings. Please configure it in Settings.")
                return False
                
            # Set environment variable for LangChain
            os.environ['OPENAI_API_KEY'] = openai_key
            
            # Get template
            template = None
            if template_name:
                for t in self.templates_cache:
                    if t.get("name") == template_name:
                        template = t
                        break
            else:
                template = self.current_template
                
            if not template:
                self.analysis_error.emit("No template selected")
                return False
                
            # Record start time
            self.process_start_time = time.time()
            
            # Update status
            status_msg = "⚡ Starting full analysis..." if is_full_analysis else "🔄 Processing text..."
            self.status_changed.emit(status_msg)
            
            # Stop existing worker if running
            if self.worker and self.worker.isRunning():
                self.worker.terminate()
                self.worker.wait()
                
            # Create worker
            self.worker = ProcessingWorker(
                self.app.service_adapter.langchain_service,
                text,
                template,
                is_full_analysis
            )
            
            # Connect signals
            self.worker.finished.connect(self._on_analysis_complete)
            self.worker.error.connect(self._on_analysis_error)
            self.worker.progress.connect(self.progress_updated)
            
            # Start worker
            self.worker.start()
            
            # Generate curiosity questions in background
            self._generate_curiosity_questions(text, template)
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to process text: {str(e)}"
            self.analysis_error.emit(error_msg)
            return False
            
    def _on_analysis_complete(self, result: str) -> None:
        """
        Handle completed analysis.
        
        This method is called when the worker thread completes processing.
        It calculates the processing time, updates model statistics, and
        emits the result signal.
        
        Args:
            result: The analysis result text
        
        Emits:
            analysis_complete: With the result, processing time, and template name
        """
        process_time = time.time() - self.process_start_time
        template_name = self.current_template.get("name") if self.current_template else "Unknown"
        
        # Update model stats
        if self.app and hasattr(self.app, 'service_adapter'):
            current_model = self.app.service_adapter.langchain_service.llm.model_name
            self.app.service_adapter.langchain_service.update_model_stats(
                model=current_model,
                template_name=template_name,
                response_time=process_time,
                response_length=len(result)
            )
            
        # Emit result signal
        self.analysis_complete.emit(result, process_time, template_name)
        
    def _on_analysis_error(self, error: str) -> None:
        """
        Handle analysis error.
        
        This method is called when the worker thread encounters an error.
        It forwards the error message through the appropriate signal.
        
        Args:
            error: The error message
        
        Emits:
            analysis_error: With the error message
        """
        self.analysis_error.emit(error)
        
    def generate_curiosity_questions(self, text: str, template: Dict[str, Any]) -> None:
        """
        Public method to generate curiosity questions.
        
        This method provides a public interface to generate curiosity questions
        based on the provided text and template.
        
        Args:
            text: The transcript text to analyze
            template: The template to use for generating questions
            
        Returns:
            None - questions are emitted via the questions_ready signal
        """
        if not text.strip():
            print("Warning: Empty text provided to generate_curiosity_questions")
            self.questions_ready.emit([])
            return
            
        print(f"AnalysisManager.generate_curiosity_questions called with {len(text)} chars of text")
        self.status_changed.emit("Generating curiosity questions...")
        return self._generate_curiosity_questions(text, template)
        
    def _generate_curiosity_questions(self, text: str, template: Dict[str, Any]) -> None:
        """
        Generate curiosity questions based on text.
        
        This method creates a background worker to generate curiosity questions
        based on the provided text and template. The questions are emitted through
        the questions_ready signal when available.
        
        Args:
            text: The text to generate questions from
            template: The template to use for question generation
        
        Emits:
            questions_ready: When questions are generated (via worker)
            analysis_error: If an error occurs during generation (via worker)
        """
        # Stop existing worker if running
        if self.curiosity_worker and self.curiosity_worker.isRunning():
            self.curiosity_worker.terminate()
            self.curiosity_worker.wait()
            
        # Create worker
        self.curiosity_worker = CuriosityWorker(text, template)
        
        # Connect signals
        self.curiosity_worker.questions_ready.connect(self._on_curiosity_questions_ready)
        self.curiosity_worker.error.connect(lambda e: self.analysis_error.emit(f"Curiosity error: {e}"))
        
        # Start worker
        self.curiosity_worker.start()
        
    def _on_curiosity_questions_ready(self, questions):
        """Handle when curiosity questions are ready"""
        print(f"AnalysisManager: Received {len(questions)} curiosity questions")
        # Forward the questions to any listeners
        self.questions_ready.emit(questions)
        
    def cancel_processing(self) -> None:
        """
        Cancel ongoing processing.
        
        This method stops any active worker threads, both for analysis and
        curiosity question generation. It attempts to cancel processing gracefully
        first, then terminates the threads if necessary.
        
        Emits:
            status_changed: When processing is cancelled
        """
        if self.worker and self.worker.isRunning():
            self.worker.cancel()  # Try graceful cancellation first
            self.worker.terminate()  # Force termination if needed
            self.worker.wait()  # Wait for thread to finish
            
        if self.curiosity_worker and self.curiosity_worker.isRunning():
            self.curiosity_worker.terminate()
            self.curiosity_worker.wait()
            
        self.status_changed.emit("Processing cancelled")
