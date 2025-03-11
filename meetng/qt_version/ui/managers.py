from PyQt6.QtCore import QObject, pyqtSignal, QTimer
import time
import os
from services.assemblyai_realtime import AssemblyAIRealTimeTranscription

class RecordingManager(QObject):
    """Manager for recording audio and handling recording state"""
    
    # Signals
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal(str, bytes)  # path, mp3_data
    recording_paused = pyqtSignal()
    recording_resumed = pyqtSignal()
    mute_toggled = pyqtSignal(bool)  # is_muted
    audio_level_changed = pyqtSignal(float)  # level 0.0-1.0
    status_changed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        self._recording = False
        self._paused = False
        self._muted = False
        self._start_time = None
        self._pause_time = None
        self._total_pause_time = 0
        self._recorder = None
        self._session_name = ""
        
        # Initialize timer for elapsed time tracking
        self._timer = QTimer()
        self._timer.timeout.connect(self._update_audio_level)
        self._timer.setInterval(100)  # 100ms updates
        
    def set_session_name(self, name):
        """Set the session name for recording"""
        self._session_name = name
        
    def start_recording(self):
        """Start recording audio"""
        if self._recording:
            return False
            
        try:
            # Import recorder here to avoid circular imports
            from qt_version.audio.recorder import AudioRecorder
            
            # Create recorder instance
            self._recorder = AudioRecorder()
            
            # Connect recorder signals
            self._recorder.audio_level_changed.connect(self._on_audio_level_changed)
            self._recorder.error_occurred.connect(self._on_recorder_error)
            
            # Start recording
            if not self._recorder.start():
                self.error_occurred.emit("Failed to start audio recorder")
                return False
                
            # Set recording state
            self._recording = True
            self._paused = False
            self._muted = False
            self._start_time = time.time()
            self._total_pause_time = 0
            
            # Start timer for updates
            self._timer.start()
            
            # Emit signal
            self.recording_started.emit()
            self.status_changed.emit("Recording started")
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to start recording: {str(e)}"
            self.error_occurred.emit(error_msg)
            return False
            
    def stop_recording(self):
        """Stop recording and save audio"""
        if not self._recording:
            return False
            
        try:
            # Stop timer
            self._timer.stop()
            
            # Stop recorder
            mp3_path, mp3_data = self._recorder.stop()
            
            # Reset state
            self._recording = False
            self._paused = False
            
            # Emit signal with recording data
            self.recording_stopped.emit(mp3_path, mp3_data)
            self.status_changed.emit("Recording stopped")
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to stop recording: {str(e)}"
            self.error_occurred.emit(error_msg)
            return False
            
    def toggle_pause(self):
        """Toggle pause/resume state"""
        if not self._recording:
            return False
            
        if self._paused:
            return self.resume_recording()
        else:
            return self.pause_recording()
            
    def pause_recording(self):
        """Pause recording"""
        if not self._recording or self._paused:
            return False
            
        try:
            # Pause recorder
            if self._recorder:
                self._recorder.pause()
                
            # Set pause state
            self._paused = True
            self._pause_time = time.time()
            
            # Emit signal
            self.recording_paused.emit()
            self.status_changed.emit("Recording paused")
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to pause recording: {str(e)}"
            self.error_occurred.emit(error_msg)
            return False
            
    def resume_recording(self):
        """Resume recording"""
        if not self._recording or not self._paused:
            return False
            
        try:
            # Resume recorder
            if self._recorder:
                self._recorder.resume()
                
            # Update pause time tracking
            if self._pause_time:
                self._total_pause_time += time.time() - self._pause_time
                self._pause_time = None
                
            # Set state
            self._paused = False
            
            # Emit signal
            self.recording_resumed.emit()
            self.status_changed.emit("Recording resumed")
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to resume recording: {str(e)}"
            self.error_occurred.emit(error_msg)
            return False
            
    def toggle_mute(self):
        """Toggle mute state"""
        if not self._recording:
            return False
            
        try:
            # Toggle mute state
            self._muted = not self._muted
            
            # Apply to recorder
            if self._recorder:
                self._recorder.set_mute(self._muted)
                
            # Emit signal
            self.mute_toggled.emit(self._muted)
            self.status_changed.emit(f"Microphone {'muted' if self._muted else 'unmuted'}")
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to toggle mute: {str(e)}"
            self.error_occurred.emit(error_msg)
            return False
            
    def get_elapsed_time(self):
        """Get total elapsed recording time in seconds"""
        if not self._recording or not self._start_time:
            return 0
            
        # Calculate elapsed time accounting for pauses
        total_time = time.time() - self._start_time
        
        # Subtract total pause time
        pause_time = self._total_pause_time
        
        # Add current pause duration if paused
        if self._paused and self._pause_time:
            pause_time += time.time() - self._pause_time
            
        return total_time - pause_time
        
    def is_recording(self):
        """Check if recording is active"""
        return self._recording
        
    def is_paused(self):
        """Check if recording is paused"""
        return self._paused
        
    def is_muted(self):
        """Check if microphone is muted"""
        return self._muted
        
    def _update_audio_level(self):
        """Update audio level from recorder"""
        if self._recording and self._recorder:
            # Audio level is already emitted by recorder
            pass
            
    def _on_audio_level_changed(self, level):
        """Handle audio level change from recorder"""
        self.audio_level_changed.emit(level)
        
    def _on_recorder_error(self, error_msg):
        """Handle error from recorder"""
        self.error_occurred.emit(error_msg)


class TranscriptionManager(QObject):
    """Manager for real-time transcription of audio"""
    
    # Signals
    transcription_ready = pyqtSignal(str)  # transcript text
    transcription_error = pyqtSignal(str)  # error message
    status_changed = pyqtSignal(str)  # status message
    trigger_detected = pyqtSignal(dict)  # trigger info
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        self._transcription = None
        self._initialized = False
        self._paused = False
        self._accumulated_text = ""
        self._last_process_time = time.time()
        self._triggers = []
        
        # Load triggers from parent if available
        if parent and hasattr(parent, 'triggers'):
            self._triggers = parent.triggers
            
    def initialize(self):
        """Initialize transcription service"""
        if self._initialized:
            return True
            
        try:
            # Check for API key
            api_key = os.getenv('ASSEMBLYAI_API_KEY')
            if not api_key:
                self.transcription_error.emit("AssemblyAI API key not found")
                return False
                
            # Initialize transcription service
            self._transcription = AssemblyAIRealTimeTranscription(api_key)
            
            # Connect callbacks
            self._transcription.on_data = self._on_transcription_data
            self._transcription.on_error = self._on_transcription_error
            
            # Start transcription
            self._transcription.start()
            self._initialized = True
            self._paused = False
            self._accumulated_text = ""
            self._last_process_time = time.time()
            
            self.status_changed.emit("Transcription initialized")
            return True
            
        except Exception as e:
            error_msg = f"Failed to initialize transcription: {str(e)}"
            self.transcription_error.emit(error_msg)
            return False
            
    def stop(self):
        """Stop transcription service"""
        if not self._initialized:
            return
            
        try:
            if self._transcription:
                self._transcription.stop()
                
            self._initialized = False
            self._paused = False
            self.status_changed.emit("Transcription stopped")
            
        except Exception as e:
            error_msg = f"Failed to stop transcription: {str(e)}"
            self.transcription_error.emit(error_msg)
            
    def pause(self):
        """Pause transcription"""
        if not self._initialized or self._paused:
            return
            
        try:
            if self._transcription:
                self._transcription.pause()
                
            self._paused = True
            self.status_changed.emit("Transcription paused")
            
        except Exception as e:
            error_msg = f"Failed to pause transcription: {str(e)}"
            self.transcription_error.emit(error_msg)
            
    def resume(self):
        """Resume transcription"""
        if not self._initialized or not self._paused:
            return
            
        try:
            if self._transcription:
                self._transcription.resume()
                
            self._paused = False
            self.status_changed.emit("Transcription resumed")
            
        except Exception as e:
            error_msg = f"Failed to resume transcription: {str(e)}"
            self.transcription_error.emit(error_msg)
            
    def process_audio_chunk(self, chunk):
        """Process audio chunk for transcription"""
        if not self._initialized or self._paused:
            return
            
        try:
            if self._transcription:
                self._transcription.process_audio_chunk(chunk)
                
        except Exception as e:
            error_msg = f"Failed to process audio chunk: {str(e)}"
            self.transcription_error.emit(error_msg)
            
    def get_accumulated_text(self):
        """Get accumulated text since last reset"""
        return self._accumulated_text
        
    def reset_accumulated_text(self):
        """Reset accumulated text"""
        self._accumulated_text = ""
        self._last_process_time = time.time()
        
    def should_process_chunk(self, type_, value):
        """Determine if current chunk should be processed based on settings"""
        if type_ == "manual":
            return False
            
        elif type_ == "time":
            current_time = time.time()
            return (current_time - self._last_process_time) >= value
            
        elif type_ == "words":
            word_count = len(self._accumulated_text.split())
            return word_count >= value
            
        return False
        
    def _on_transcription_data(self, text):
        """Handle incoming transcription data"""
        if not text or not text.strip():
            return
            
        # Add to accumulated text
        self._accumulated_text += " " + text
        self._accumulated_text = self._accumulated_text.strip()
        
        # Check for trigger phrases
        self._check_triggers(text)
        
        # Emit signal with new text
        self.transcription_ready.emit(text)
        
    def _on_transcription_error(self, error):
        """Handle transcription error"""
        self.transcription_error.emit(str(error))
        
    def _check_triggers(self, text):
        """Check for trigger phrases in text"""
        if not hasattr(self, '_triggers') or not self._triggers:
            return
            
        text = text.lower()
        for trigger in self._triggers:
            # Skip if no trigger phrase defined
            if not trigger.get('trigger_phrase'):
                continue
                
            # Split trigger phrases by semicolon and strip whitespace
            trigger_phrases = [phrase.strip().lower() 
                             for phrase in trigger['trigger_phrase'].split(';')]
            
            # Check each phrase
            for phrase in trigger_phrases:
                if phrase and phrase in text:
                    if self._debug_mode:
                        print(f"Matched trigger phrase: '{phrase}' for action: {trigger['action']}")
                    
                    # Emit signal with trigger info
                    self.trigger_detected.emit(trigger)
                    break


class AnalysisManager(QObject):
    """Manager for text analysis using LLM services"""
    
    # Signals
    analysis_complete = pyqtSignal(str, float, str)  # result, process_time, template_name
    analysis_error = pyqtSignal(str)  # error message
    status_changed = pyqtSignal(str)  # status message
    progress_updated = pyqtSignal(int, int, str)  # value, max, status
    questions_ready = pyqtSignal(list)  # list of questions
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        self._app = parent.app if parent and hasattr(parent, 'app') else None
        self._current_template = None
        self._templates_cache = []
        
        # Load templates
        self.load_templates()
        
    def load_templates(self, preserve_selection=True):
        """Load available templates"""
        try:
            # Store current selection if needed
            current_template_name = None
            if preserve_selection and self._current_template:
                current_template_name = self._current_template.get("name")
                
            # Get templates from service
            if self._app and hasattr(self._app, 'service_adapter'):
                service = self._app.service_adapter.langchain_service
                templates = service.get_available_templates()
                self._templates_cache = templates
            else:
                # Fallback templates if service not available
                self._templates_cache = [
                    {
                        "name": "Meeting Summary",
                        "description": "Summarize key points from the meeting",
                        "system": "You are an AI assistant helping summarize meetings.",
                        "user": "Provide a concise summary of the key points discussed:"
                    },
                    {
                        "name": "Action Items",
                        "description": "Extract action items and assignments",
                        "system": "You are an AI assistant tracking action items.",
                        "user": "List all action items and assignments mentioned:"
                    },
                    {
                        "name": "Decision Tracking",
                        "description": "Track decisions made during the meeting",
                        "system": "You are an AI assistant tracking decisions.",
                        "user": "List all decisions made during this discussion:"
                    }
                ]
                
            # Restore previous selection if needed
            if preserve_selection and current_template_name:
                for template in self._templates_cache:
                    if template.get("name") == current_template_name:
                        self._current_template = template
                        break
                        
            # Default to first template if needed
            if not self._current_template and self._templates_cache:
                self._current_template = self._templates_cache[0]
                
            return self._templates_cache
                
        except Exception as e:
            error_msg = f"Failed to load templates: {str(e)}"
            self.analysis_error.emit(error_msg)
            return []
            
    def get_template_description(self, template_name):
        """Get description for the specified template"""
        for template in self._templates_cache:
            if template.get("name") == template_name:
                return template.get("description", "")
        return ""
        
    def set_current_template(self, template_name):
        """Set current template by name"""
        for template in self._templates_cache:
            if template.get("name") == template_name:
                self._current_template = template
                return True
        return False
        
    def process_text(self, text, template_name=None, is_full_analysis=False):
        """Process text for analysis"""
        if not text or not text.strip():
            self.analysis_error.emit("No text to analyze")
            return
            
        # Set template if specified
        if template_name:
            self.set_current_template(template_name)
            
        # Ensure we have a template
        if not self._current_template:
            self.analysis_error.emit("No template selected")
            return
            
        try:
            # Get service
            if not self._app or not hasattr(self._app, 'service_adapter'):
                self.analysis_error.emit("Service adapter not available")
                return
                
            service = self._app.service_adapter.langchain_service
            
            # Update status
            self.status_changed.emit("Processing text...")
            self.progress_updated.emit(10, 100, "Starting analysis...")
            
            # Start processing time
            start_time = time.time()
            
            if is_full_analysis:
                # For full analysis, process in larger chunks
                chunks = self._split_into_chunks(text, chunk_size=2500)
                results = []
                total_chunks = len(chunks)
                
                for i, chunk in enumerate(chunks):
                    # Update progress
                    progress = int((i + 1) / total_chunks * 100)
                    self.progress_updated.emit(progress, 100, 
                        f"⚡ Full analysis: {i+1}/{total_chunks} sections")
                    
                    # Process chunk
                    result = service.process_chunk(chunk, self._current_template)
                    results.append(result)
                    
                final_result = "\n\n".join(results)
                
            else:
                # Regular analysis
                self.progress_updated.emit(50, 100, "Processing text...")
                final_result = service.process_chunk(text, self._current_template)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Update progress
            self.progress_updated.emit(100, 100, "Analysis complete")
            
            # Emit result
            self.analysis_complete.emit(
                final_result, 
                process_time,
                self._current_template.get("name", "Unknown")
            )
            
            # Generate curiosity questions
            self._generate_curiosity_questions(text)
            
        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            self.analysis_error.emit(error_msg)
            
    def _split_into_chunks(self, text, chunk_size=1000):
        """Split text into manageable chunks"""
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
        
    def _generate_curiosity_questions(self, text):
        """Generate curiosity questions based on the transcript"""
        try:
            # Get service
            if not self._app or not hasattr(self._app, 'service_adapter'):
                return
                
            service = self._app.service_adapter.langchain_service
            
            # Generate questions
            questions = service.generate_curiosity_questions(text, self._current_template)
            
            # Emit questions
            self.questions_ready.emit(questions)
            
        except Exception as e:
            if self._debug_mode:
                print(f"Failed to generate curiosity questions: {str(e)}")
