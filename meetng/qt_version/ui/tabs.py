from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QFileDialog, QProgressBar, QTextEdit,
    QLineEdit, QMessageBox, QSplitter, QComboBox,
    QGroupBox, QApplication, QGridLayout, QCheckBox,
    QListWidget, QListWidgetItem, QRadioButton,
    QButtonGroup, QStackedWidget, QDialog, QToolButton,
    QTabWidget, QFrame, QMenu, QFormLayout, QDialogButtonBox,
    QGraphicsView, QGraphicsScene
)
from qt_version.ui.managers import RecordingManager, TranscriptionManager, AnalysisManager
from qt_version.ui.curiosity_tab_widget import CuriosityTabWidget
from qt_version.utils.settings_manager import SettingsManager
from qt_version.utils.configuration_service import ConfigurationService
from qt_version.ui.components.font_control import FontControlPanel
from .trigger_manager import TriggerManagerDialog
from PyQt6.QtGui import QKeySequence, QShortcut, QTextCursor, QTextCharFormat
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QDateTime, QObject, QThread, QSettings
from datetime import datetime
import os
from pathlib import Path
import markdown
import time
import json
from .components import TimerIndicator

class ImportTab(QWidget):
    """Tab for importing and processing audio files (single or batch)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = parent.app if parent else None
        self._debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        self.settings_manager = SettingsManager()
        
        # Verify services are available
        if not self.app or not hasattr(self.app, 'service_adapter'):
            raise RuntimeError("Import tab requires application service adapter")
            
        layout = QVBoxLayout()
        
        # Import Options Group
        import_group = QGroupBox("Import Options")
        import_layout = QVBoxLayout()
        
        # Source Selection
        source_layout = QHBoxLayout()
        self.source_combo = QComboBox()
        self.source_combo.addItems(["Single File", "Folder"])
        source_layout.addWidget(QLabel("Import Source:"))
        source_layout.addWidget(self.source_combo)
        import_layout.addLayout(source_layout)
        
        # File/Folder Selection
        select_layout = QHBoxLayout()
        self.path_label = QLabel("No file/folder selected")
        select_layout.addWidget(self.path_label)
        self.select_btn = QPushButton("Select...")
        self.select_btn.clicked.connect(self.select_source)
        select_layout.addWidget(self.select_btn)
        import_layout.addLayout(select_layout)
        
        # Service Selection
        service_group = QGroupBox("Transcription Service")
        service_layout = QVBoxLayout()
        
        # Service Selection
        service_group = QGroupBox("Transcription Service")
        service_layout = QVBoxLayout()
        
        # Service Selection Radio Buttons
        self.service_var = QButtonGroup()
        self.openai_radio = QRadioButton("OpenAI Whisper")
        self.assemblyai_radio = QRadioButton("AssemblyAI")
        self.service_var.addButton(self.openai_radio)
        self.service_var.addButton(self.assemblyai_radio)
        self.openai_radio.setChecked(True)  # Default to OpenAI
        service_layout.addWidget(self.openai_radio)
        service_layout.addWidget(self.assemblyai_radio)
        
        # Model Selection
        model_group = QGroupBox("Model Options")
        model_layout = QVBoxLayout()
        
        # AssemblyAI Models
        self.assemblyai_model_combo = QComboBox()
        self.assemblyai_model_combo.addItems(["best", "nano"])
        self.assemblyai_model_combo.setVisible(False)
        model_layout.addWidget(QLabel("AssemblyAI Model:"))
        model_layout.addWidget(self.assemblyai_model_combo)
        
        # OpenAI Model (single option)
        self.openai_model_label = QLabel("Model: whisper-1")
        model_layout.addWidget(self.openai_model_label)
        
        # Common Features
        features_group = QGroupBox("Features")
        features_layout = QVBoxLayout()
        
        # Timestamps (available for both)
        self.timestamps = QCheckBox("Enable Word-level Timestamps")
        self.timestamps.setChecked(True)
        features_layout.addWidget(self.timestamps)
        
        # AssemblyAI-specific features
        self.speaker_detection = QCheckBox("Speaker Detection")
        self.chapters = QCheckBox("Auto Chapters")
        self.entity = QCheckBox("Entity Detection")
        self.keyphrases = QCheckBox("Key Phrases")
        self.summary = QCheckBox("Auto Summary")
        
        # Add AssemblyAI features
        for widget in [self.speaker_detection, self.chapters, self.entity, 
                      self.keyphrases, self.summary]:
            features_layout.addWidget(widget)
            widget.setVisible(False)  # Hide by default (OpenAI selected)
            
        features_group.setLayout(features_layout)
        model_layout.addWidget(features_group)
        
        # Connect service selection to UI updates
        self.openai_radio.toggled.connect(self.update_service_options)
        self.assemblyai_radio.toggled.connect(self.update_service_options)
        
        model_group.setLayout(model_layout)
        service_layout.addWidget(model_group)
        
        # Connect radio buttons to update options
        self.openai_radio.toggled.connect(self.update_service_options)
        self.assemblyai_radio.toggled.connect(self.update_service_options)
        
        service_group.setLayout(service_layout)
        import_layout.addWidget(service_group)
        
        # Processing Options
        options_layout = QGridLayout()
        
        # Timestamps
        self.timestamps = QCheckBox("Include Timestamps")
        self.timestamps.setChecked(True)
        options_layout.addWidget(self.timestamps, 0, 1)
        
        # Naming Convention
        options_layout.addWidget(QLabel("File Naming:"), 1, 0)
        self.naming_combo = QComboBox()
        self.naming_combo.addItems([
            "YYMMDD_HHMM_description",
            "YYMMDD_description",
            "Original Name"
        ])
        options_layout.addWidget(self.naming_combo, 1, 1)
        
        # Description field
        options_layout.addWidget(QLabel("Description:"), 2, 0)
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("Enter description for file naming...")
        options_layout.addWidget(self.description_edit, 2, 1)
        
        import_layout.addLayout(options_layout)
        import_group.setLayout(import_layout)
        layout.addWidget(import_group)
        
        # Progress Section
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel()
        progress_layout.addWidget(self.status_label)
        
        # File List
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        progress_layout.addWidget(self.file_list)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # Control Buttons
        button_layout = QHBoxLayout()
        self.process_btn = QPushButton("Process Selected")
        self.process_btn.clicked.connect(self.process_files)
        button_layout.addWidget(self.process_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.cancel_processing)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def select_source(self):
        """Handle file/folder selection"""
        if self.source_combo.currentText() == "Single File":
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Audio File",
                "",
                "Audio Files (*.mp3 *.wav *.m4a);;All Files (*.*)"
            )
            if file_path:
                abs_path = os.path.abspath(file_path)
                if self._debug_mode:
                    print(f"\nSelected file:")
                    print(f"- Original path: {file_path!r}")
                    print(f"- Absolute path: {abs_path!r}")
                    print(f"- Exists: {os.path.exists(abs_path)}")
                    
                self.path_label.setText(abs_path)
                self.add_file_to_list(abs_path)
        else:
            folder_path = QFileDialog.getExistingDirectory(
                self,
                "Select Folder",
                "",
                QFileDialog.Option.ShowDirsOnly
            )
            if folder_path:
                self.path_label.setText(folder_path)
                self.scan_folder(folder_path)
                
    def add_file_to_list(self, file_path: str):
        """Add file to processing list"""
        abs_path = os.path.abspath(file_path)
        if self._debug_mode:
            print(f"\nAdding file to list:")
            print(f"- Input path: {file_path!r}")
            print(f"- Absolute path: {abs_path!r}")
            print(f"- Exists: {os.path.exists(abs_path)}")
            
        if not os.path.exists(abs_path):
            if self._debug_mode:
                print(f"Warning: File not found: {abs_path}")
            return
            
        item = QListWidget.QListWidgetItem(os.path.basename(abs_path))
        item.setData(Qt.ItemDataRole.UserRole, abs_path)
        self.file_list.addItem(item)
        
    def scan_folder(self, folder_path: str):
        """Scan folder for audio files"""
        self.file_list.clear()
        file_count = 0
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(('.mp3', '.wav', '.m4a')):
                    full_path = os.path.join(root, file)
                    self.add_file_to_list(full_path)
                    file_count += 1
        self.status_label.setText(f"Found {file_count} audio files")
        
    def load_workspace_files(self):
        """Load audio files from the workspace directory"""
        if not hasattr(self.app, 'path_manager'):
            self.status_label.setText("Path manager not available")
            return
            
        workspace_dir = self.app.path_manager.workspace_dir
        if not workspace_dir or not os.path.exists(workspace_dir):
            self.status_label.setText("Workspace directory not configured or doesn't exist")
            return
            
        # Update folder label
        self.folder_label.setText(f"Workspace: {workspace_dir}")
        
        # Load files from workspace directory
        self.load_files_from_folder(workspace_dir)
        
        # Set as current folder
        self.current_folder = workspace_dir
                    
    def update_service_options(self):
        """Update visible options based on selected service"""
        is_assemblyai = self.assemblyai_radio.isChecked()
        
        # Update model visibility
        self.assemblyai_model_combo.setVisible(is_assemblyai)
        self.openai_model_label.setVisible(not is_assemblyai)
        
        # Update feature visibility
        for widget in [self.speaker_detection, self.chapters, self.entity,
                      self.keyphrases, self.summary]:
            widget.setVisible(is_assemblyai)
            
        # Timestamps always visible
        self.timestamps.setVisible(True)
        
    def process_files(self):
        """Process selected files"""
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select files to process")
            return
            
        # Check API keys from configuration service
        config = ConfigurationService()
        openai_key = config.get_typed("openai_api_key", str, "")
        assemblyai_key = config.get_typed("assemblyai_api_key", str, "")
            
        if not openai_key and not assemblyai_key:
            QMessageBox.critical(self, "Error", "No API keys configured. Please configure at least one service in Settings.")
            return
                
        if self.openai_radio.isChecked() and not openai_key:
            QMessageBox.warning(self, "Warning", "OpenAI API key not found. Please configure it in Settings.")
            return
        elif self.assemblyai_radio.isChecked() and not assemblyai_key:
            QMessageBox.warning(self, "Warning", "AssemblyAI API key not found. Please configure it in Settings.")
            return
        
        try:
            self.status_label.setText("Preparing to process files...")
            # Get processing options
            config = {
                'speaker_detection': self.speaker_detection.isChecked(),
                'timestamps': self.timestamps.isChecked(),
                'naming_convention': self.naming_combo.currentText(),
                'description': self.description_edit.text().strip()
            }
            
            # Process each selected file
            self.progress_bar.setMaximum(len(selected_items))
            for i, item in enumerate(selected_items):
                file_path = item.data(Qt.ItemDataRole.UserRole)
                if self._debug_mode:
                    print(f"\nProcessing file:")
                    print(f"- Full path: {file_path!r}")
                    print(f"- Exists: {os.path.exists(file_path) if file_path else False}")
                    print(f"- Type: {type(file_path)}")
                
                if not file_path or not os.path.exists(file_path):
                    raise ValueError(f"Invalid file path: {file_path!r}")
                    
                self.status_label.setText(f"Processing: {os.path.basename(file_path)}")
                
                # Get selected service (API keys already verified)
                service = self._get_selected_transcription_service(config)
                
                if self._debug_mode:
                    print(f"Using service: {'OpenAI' if self.openai_radio.isChecked() else 'AssemblyAI'}")
                    print(f"Config: {config}")
                
                transcript = service.transcribe(file_path, config)
                
                # Generate output filename directly
                output_file = os.path.join(
                    os.path.dirname(file_path),
                    f"{os.path.splitext(os.path.basename(file_path))[0]}_transcript.txt"
                )
                
                try:
                    # Initialize selected service
                    if not service.is_initialized():
                        self.status_label.setText(f"Initializing {service.__class__.__name__}...")
                        if not service.setup():
                            raise ValueError(f"Failed to initialize {service.__class__.__name__}")

                    if self._debug_mode:
                        print(f"Using service: {service.__class__.__name__}")
                        print(f"Config: {config}")
                    
                    # Perform transcription
                    transcript = service.transcribe(file_path, config)
                    
                    if not transcript:
                        raise ValueError("No transcript generated")
                        
                    # Save transcript
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(transcript)
                        
                except Exception as e:
                    raise ValueError(f"Transcription failed: {str(e)}")
                
                self.progress_bar.setValue(i + 1)
                self.status_label.setText(f"Processed {i+1}/{len(selected_items)} files")
                QApplication.processEvents()  # Update UI
                
            QMessageBox.information(self, "Success", "Processing completed successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Processing failed: {str(e)}")
            
        finally:
            self.status_label.clear()
            self.progress_bar.setValue(0)
            
    def _get_selected_transcription_service(self, config):
        """Get the selected transcription service and update config
        
        Args:
            config: Configuration dictionary to update
            
        Returns:
            The selected transcription service
        """
        if self.openai_radio.isChecked():
            service = self.app.service_adapter.openai_service
            config.update({
                'model': 'whisper-1',
                'timestamps': self.timestamps.isChecked()
            })
        else:  # AssemblyAI
            service = self.app.service_adapter.assemblyai_service
            config.update({
                'model': self.assemblyai_model_combo.currentText(),
                'timestamps': self.timestamps.isChecked(),
                'speaker_detection': self.speaker_detection.isChecked(),
                'chapters': self.chapters.isChecked(),
                'entity': self.entity.isChecked(),
                'keyphrases': self.keyphrases.isChecked(),
                'summary': self.summary.isChecked()
            })
        return service
        
    def cancel_processing(self):
        """Cancel ongoing processing"""
        if hasattr(self, 'current_process'):
            self.current_process.terminate()
        self.status_label.setText("Processing cancelled")
        self.progress_bar.setValue(0)

class ProcessingWorker(QThread):
    finished = pyqtSignal(str)  # Signal to emit result
    error = pyqtSignal(str)     # Signal to emit error
    progress = pyqtSignal(int, int, str)  # value, max, status

    def __init__(self, langchain_service, text, template, is_full_analysis=False):
        super().__init__()
        self.langchain_service = langchain_service
        self.text = text
        self.template = template
        self.is_full_analysis = is_full_analysis
        self._cancelled = False
        self.chunk_size = 2500 if is_full_analysis else 1500  # Smaller chunks for regular analysis

    def run(self):
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

    def split_into_chunks(self, text, chunk_size=1000):
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

    def cancel(self):
        """Cancel processing"""
        self._cancelled = True

class RecordingTab(QWidget):
    """Tab for real-time recording and transcription"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = parent.app if parent else None
        self._debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        self.settings_manager = SettingsManager()
        self._templates_cache = {}
        self._current_template_cache = None
        self.bookmarks = []
        
        # Initialize managers
        self.recording_manager = RecordingManager(self)
        self.transcription_manager = TranscriptionManager(self)
        self.analysis_manager = AnalysisManager(self)
        
        # Connect manager signals
        self._connect_manager_signals()
        
        # Initialize UI components
        self._init_ui()
        
        # Initialize state
        self.recording = False
        self.recorder = None
        self.start_time = None
        self.timer = None
        self.transcription = None
        self.accumulated_text = ""
        self.worker = None
        self.bookmarks = []
        
        # Load initial triggers
        self.load_triggers_from_settings()
        
        # Load templates once at startup
        self.load_templates()
        
    def _init_ui(self):
        """Initialize the user interface components"""
        # Create main layout
        layout = QVBoxLayout()
        
        # Initialize session name section
        self._init_session_section(layout)
        
        # Create top panels layout (horizontal)
        top_panels_layout = QHBoxLayout()
        
        # Initialize recording controls panel
        self._init_recording_controls(top_panels_layout)
        
        # Initialize analysis panel
        self._init_analysis_panel(top_panels_layout)
        
        # Add the top panels to the main layout
        layout.addLayout(top_panels_layout)
        
        # Bind F12 key for instant processing
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        QShortcut(QKeySequence("F12"), self, self.trigger_instant_processing)
        
        # Initialize main content area (transcript and analysis)
        self._init_content_area(layout)
        
        # Initialize control buttons
        self._init_control_buttons(layout)
        
        # Add status bar
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #666;")
        layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignBottom)
        
        # Initialize bookmark panel
        self._init_bookmark_panel(layout)
        
        # Set the main layout
        self.setLayout(layout)
        
    def _connect_manager_signals(self):
        """Connect signals from manager classes"""
        # Recording Manager signals
        self.recording_manager.recording_started.connect(self._on_recording_started, Qt.ConnectionType.QueuedConnection)
        self.recording_manager.recording_stopped.connect(self._on_recording_stopped, Qt.ConnectionType.QueuedConnection)
        self.recording_manager.recording_paused.connect(self._on_recording_paused, Qt.ConnectionType.QueuedConnection)
        self.recording_manager.recording_resumed.connect(self._on_recording_resumed, Qt.ConnectionType.QueuedConnection)
        self.recording_manager.mute_toggled.connect(self._on_mute_toggled, Qt.ConnectionType.QueuedConnection)
        self.recording_manager.audio_level_changed.connect(self.update_audio_level, Qt.ConnectionType.QueuedConnection)
        self.recording_manager.status_changed.connect(self.update_status, Qt.ConnectionType.QueuedConnection)
        self.recording_manager.error_occurred.connect(self._on_recording_error, Qt.ConnectionType.QueuedConnection)
        self.recording_manager.audio_chunk_ready.connect(self.process_audio_chunk, Qt.ConnectionType.QueuedConnection)
        
        # Transcription Manager signals
        self.transcription_manager.transcription_ready.connect(self._on_transcription_ready, Qt.ConnectionType.QueuedConnection)
        self.transcription_manager.transcription_error.connect(self._on_transcription_error, Qt.ConnectionType.QueuedConnection)
        self.transcription_manager.status_changed.connect(self.update_status, Qt.ConnectionType.QueuedConnection)
        self.transcription_manager.trigger_detected.connect(self._on_trigger_detected, Qt.ConnectionType.QueuedConnection)
        
        # Analysis Manager signals
        self.analysis_manager.analysis_complete.connect(self._on_analysis_complete, Qt.ConnectionType.QueuedConnection)
        self.analysis_manager.analysis_error.connect(self._on_analysis_error, Qt.ConnectionType.QueuedConnection)
        self.analysis_manager.status_changed.connect(self.update_status, Qt.ConnectionType.QueuedConnection)
        self.analysis_manager.progress_updated.connect(self._on_progress_updated, Qt.ConnectionType.QueuedConnection)
        self.analysis_manager.questions_ready.connect(self._on_questions_ready, Qt.ConnectionType.QueuedConnection)
    
    def toggle_pause(self):
        """Toggle pause/resume state"""
        if not self.recording_manager.is_recording():
            return
            
        self.recording_manager.toggle_pause()

    # These methods are now handled by the RecordingManager class
    # The code is kept here for reference but is no longer used
    
    def toggle_mute(self):
        """Toggle mute state"""
        if not self.recording_manager.is_recording():
            return
            
        self.recording_manager.toggle_mute()
            
    def start_recording(self):
        """Start recording and transcription"""
        if not self.session_name.text():
            QMessageBox.warning(self, "Error", "Please enter a session name")
            return
            
        # Set session name in recording manager
        self.recording_manager.set_session_name(self.session_name.text())
        
        # Start recording
        if self.recording_manager.start_recording():
            # Recording started successfully
            self.accumulated_text = ""
            self.last_process_time = time.time()
            self.last_sound_time = time.time()
            
    def stop_recording(self):
        """Stop recording and save"""
        if not self.recording_manager.is_recording():
            return
            
        # Stop recording through manager
        self.recording_manager.stop_recording()
            
    def update_audio_level(self, level: float):
        """Update audio level indicator"""
        # Audio level is now handled by the timer indicator
        if hasattr(self, 'timer_indicator'):
            audio_level = int(level * 100)
            self.timer_indicator.set_audio_level(audio_level)
            
            # Handle silence detection
            type_, interval = self.get_interval_settings()
            if type_ == "silence" and self.recording_manager.is_recording():
                if audio_level > 10:  # Sound detected (using threshold)
                    self.last_sound_time = time.time()
                    # Reset silence notification if it was showing
                    if hasattr(self, '_silence_notification_showing') and self._silence_notification_showing:
                        self._silence_notification_showing = False
                elif hasattr(self, 'last_sound_time'):
                    silence_duration = time.time() - self.last_sound_time
                    
                    # Show visual feedback for approaching silence threshold
                    if silence_duration >= interval * 0.7 and silence_duration < interval:
                        # Only show notification once per approach
                        if not hasattr(self, '_silence_notification_showing') or not self._silence_notification_showing:
                            self.show_quick_feedback(f"Approaching silence threshold ({silence_duration:.1f}s / {interval}s)")
                            self._silence_notification_showing = True
                    
                    if silence_duration >= interval:
                        # Process chunk after silence threshold
                        accumulated_text = self.transcription_manager.get_accumulated_text()
                        if accumulated_text.strip():
                            # Show visual feedback
                            self.show_quick_feedback(f"Silence threshold reached - processing chunk")
                            
                            self.process_for_analysis(accumulated_text)
                            self.transcription_manager.reset_accumulated_text()
                        self.last_sound_time = time.time()
                        self._silence_notification_showing = False
        
    def update_timer(self):
        """Update timer display and progress"""
        if not self.recording_manager.is_recording():
            return
            
        # Update total recording time
        elapsed_total = self.recording_manager.get_elapsed_time()
        hours = int(elapsed_total // 3600)
        minutes = int((elapsed_total % 3600) // 60)
        seconds = int(elapsed_total % 60)
        self.timer_display.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        
        # Update progress indicator based on interval settings
        type_, interval = self.get_interval_settings()
        if interval == float('inf'):
            self.timer_indicator.set_progress(0, "M")
            return
            
        if type_ == "silence" and hasattr(self, 'last_sound_time'):
            # For silence mode, show time since last sound
            elapsed = time.time() - self.last_sound_time
            remaining = max(0, interval - elapsed)
            progress = 100 * (elapsed / interval)
            
            # Update status label with silence info if significant silence detected
            if elapsed > 2.0:  # Only show after 2 seconds of silence
                self.status_label.setText(f"🔇 Silence detected: {elapsed:.1f}s / {interval}s")
        else:
            # Normal timer behavior for other modes
            elapsed = self.recording_manager.get_elapsed_time()
            remaining = max(0, interval - (elapsed % interval))
            progress = 100 * (1 - (remaining / interval))
        
        # Update indicator
        self.timer_indicator.set_progress(progress, str(int(remaining)))
            
    def process_audio_chunk(self, chunk: bytes):
        """Process incoming audio chunk"""
        # Get latest audio chunk from recorder and send to transcription manager
        if self.recording_manager.is_recording() and not self.recording_manager.is_paused():
            # Get audio chunk from recorder
            if chunk:
                # Process through transcription manager
                self.transcription_manager.process_audio_chunk(chunk)
                
                # Update status with current mode and progress
                self._update_status_for_current_mode()
    def _update_status_for_current_mode(self):
        """Update status label based on current processing mode"""
        type_, value = self.get_interval_settings()
        if type_ == "manual":
            self.status_label.setText("🎙️ Recording (Manual mode - Press F12 to process)")
        elif type_ == "time":
            time_left = value - ((time.time() - self.last_process_time) if hasattr(self, 'last_process_time') else 0)
            self.status_label.setText(f"⏱️ Recording ({time_left:.1f}s until next chunk)")
        elif type_ == "words":
            current_words = len(self.transcription_manager.get_accumulated_text().split())
            self.status_label.setText(f"📝 Recording ({current_words}/{value} words)")
    
    # Define CuriosityWorker class for background question generation
    class CuriosityWorker(QThread):
        questions_ready = pyqtSignal(list)
        error = pyqtSignal(str)
        
        def __init__(self, text, template):
            super().__init__()
            self.text = text
            self.template = template
            
        def run(self):
            try:
                from qt_version.services.curiosity_engine import CuriosityEngine
                curiosity_engine = CuriosityEngine()
                questions = curiosity_engine.generate_questions(self.text, self.template)
                self.questions_ready.emit(questions)
            except Exception as e:
                self.error.emit(str(e))
    
    def process_for_analysis(self, text: str, is_full_analysis=False):
        """Process accumulated text for AI analysis"""
        # For regular analysis, use complete transcript
        if not is_full_analysis:
            text = self.live_text.toPlainText()
        
        # Add bookmarks to the text if the option is enabled
        include_bookmarks = self.settings_manager.get_setting('include_bookmarks_in_analysis', 'true').lower() == 'true'
        if include_bookmarks:
            bookmark_text = self.format_bookmarks_for_analysis()
            if bookmark_text:
                text += bookmark_text
        
        # Show loading state
        self._show_analysis_loading_state()
        
        # Process text through analysis manager
        template_name = self.template_combo.currentText()
        self.analysis_manager.process_text(text, template_name, is_full_analysis)
        
        # Update last process time
        self.last_process_time = time.time()
        
    def _show_analysis_loading_state(self):
        """Show loading state in the curiosity tab"""
        self.curiosity_tab.empty_label.setText("Generating questions...")
        self.curiosity_tab.empty_label.setVisible(True)
        QApplication.processEvents()  # Keep UI responsive

    def toggle_edit_mode(self):
        """Toggle edit mode for transcript and analysis"""
        edit_mode = self.edit_mode_btn.isChecked()
        
        if edit_mode and self.recording:
            QMessageBox.warning(self, "Warning", "Cannot enable edit mode while recording!")
            self.edit_mode_btn.setChecked(False)
            return
            
        # Update button text
        self.edit_mode_btn.setText("🔓 Edit Mode: On" if edit_mode else "🔒 Edit Mode: Off")
        
        # Enable/disable editing
        self.live_text.setReadOnly(not edit_mode)
        self.analysis_text.setReadOnly(not edit_mode)
        
        # Enable/disable save buttons
        self.save_transcript_btn.setEnabled(edit_mode)
        self.save_analysis_btn.setEnabled(edit_mode)
        
        # Update status
        if edit_mode:
            self.status_label.setText("Edit mode enabled - you can modify transcript and analysis")
            self.status_label.setStyleSheet("color: #ff9800;")  # Orange for edit mode
        else:
            self.status_label.setText("Edit mode disabled")
            self.status_label.setStyleSheet("")
            
    def _handle_file_exists(self, file_path):
        """Handle case when file already exists
        
        Args:
            file_path: Path object of the file
            
        Returns:
            Path: New path to use, or None if operation should be cancelled
        """
        reply = QMessageBox.question(
            self,
            "File Exists",
            "This file already exists. Would you like to:\n"
            "Yes = Save as new version\n"
            "No = Overwrite existing\n"
            "Cancel = Cancel save",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No |
            QMessageBox.StandardButton.Cancel
        )
        
        if reply == QMessageBox.StandardButton.Cancel:
            return None
        elif reply == QMessageBox.StandardButton.Yes:
            # Create new version
            stem = file_path.stem
            if '_v' in stem:
                base = stem[:stem.rfind('_v')]
                current_version = int(stem[stem.rfind('_v')+2:])
                new_version = current_version + 1
            else:
                base = stem
                new_version = 1
                
            return file_path.with_name(f"{base}_v{new_version:02d}{file_path.suffix}")
        else:
            # Overwrite existing
            return file_path
    
    def save_transcript(self):
        """Save current transcript text"""
        try:
            if hasattr(self, 'current_transcript_path') and self.current_transcript_path:
                if self._debug_mode:
                    print(f"\nSaving transcript:")
                    print(f"Path type: {type(self.current_transcript_path)}")
                    print(f"Path: {self.current_transcript_path}")
                    
                # Ensure path is a Path object
                if isinstance(self.current_transcript_path, str):
                    self.current_transcript_path = Path(self.current_transcript_path)
                
                # Check if file exists
                if self.current_transcript_path.exists():
                    new_path = self._handle_file_exists(self.current_transcript_path)
                    if new_path is None:
                        return  # User cancelled
                    self.current_transcript_path = new_path
                
                # Save transcript
                with open(self.current_transcript_path, 'w', encoding='utf-8') as f:
                    f.write(self.live_text.toPlainText())
                    
                self.status_label.setText(f"Transcript saved: {self.current_transcript_path.name}")
                self.status_label.setStyleSheet("color: #4caf50;")  # Green for success
                
                if self._debug_mode:
                    print("Transcript saved successfully")
            else:
                # No path set - this is a new recording
                if not self.session_name.text():
                    QMessageBox.warning(self, "Warning", "Please enter a session name first")
                    return
                    
                # Create new paths using PathManager
                session_dir = self.app.path_manager.get_session_dir(self.session_name.text())
                timestamp = datetime.now().strftime("%y%m%d_%H%M")  # Format: YYMMDD_HHMM
                filename = f"{timestamp}_{self.session_name.text()}"
                self.current_transcript_path = Path(self.app.path_manager.get_transcript_path(session_dir, filename))
                
                # Save transcript
                with open(self.current_transcript_path, 'w', encoding='utf-8') as f:
                    f.write(self.live_text.toPlainText())
                    
                self.status_label.setText(f"New transcript saved: {self.current_transcript_path.name}")
                self.status_label.setStyleSheet("color: #4caf50;")  # Green for success
                
        except Exception as e:
            error_msg = f"Failed to save transcript: {str(e)}"
            print(f"Error: {error_msg}")  # Debug output
            QMessageBox.critical(self, "Error", error_msg)
            self.status_label.setText(error_msg)
            self.status_label.setStyleSheet("color: #f44336;")  # Red for error

    def save_analysis(self):
        """Save current analysis text"""
        try:
            if hasattr(self, 'current_transcript_path') and self.current_transcript_path:
                # Create analysis path from transcript path
                analysis_path = self.current_transcript_path.parent / \
                              f"{self.current_transcript_path.stem.replace('_transcript', '')}_analysis.txt"
                
                # Check if file exists
                if analysis_path.exists():
                    new_path = self._handle_file_exists(analysis_path)
                    if new_path is None:
                        return  # User cancelled
                    analysis_path = new_path
                
                # Add metadata header
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                template_name = self.template_combo.currentText()
                model_name = self.app.service_adapter.langchain_service.llm.model_name
                
                header = f"""=== Analysis Generated ===
Date: {current_time}
Template: {template_name}
Model: {model_name}
Source: {self.current_transcript_path.name}
========================

"""
                with open(analysis_path, 'w', encoding='utf-8') as f:
                    f.write(header + self.analysis_text.toPlainText())
                    
                self.status_label.setText(f"Analysis saved: {analysis_path.name}")
                self.status_label.setStyleSheet("color: #4caf50;")  # Green for success
            else:
                QMessageBox.warning(self, "Warning", "No transcript file selected")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save analysis: {str(e)}")
            self.status_label.setText(f"Error saving analysis: {str(e)}")
            self.status_label.setStyleSheet("color: #f44336;")  # Red for error

    def handle_analysis_result(self, result: str):
        """Handle successful analysis result"""
        # This method is no longer needed as we're using the AnalysisManager
        # All functionality has been moved to _on_analysis_complete
        pass

    def handle_analysis_error(self, error: str):
        """Handle analysis error"""
        # This method is no longer needed as we're using the AnalysisManager
        # All functionality has been moved to _on_analysis_error
        pass
    def get_interval_settings(self):
        """Get current interval type and value"""
        setting = self.interval_combo.currentText()
        
        if setting == "Manual (F12)":
            return ("manual", float('inf'))
            
        type_, value = setting.split(": ")
        
        if type_ == "Time":
            # Convert time formats to seconds
            unit = value[-1]
            number = int(value[:-1])
            seconds = number * 60 if unit == 'm' else number
            return ("time", seconds)
            
        elif type_ == "Words":
            return ("words", int(value))
            
        elif type_ == "Silence":
            return ("silence", int(value[:-1]))
            
        return ("manual", float('inf'))
            
    def should_process_chunk(self):
        """Determine if current chunk should be processed"""
        type_, value = self.get_interval_settings()
        
        if type_ == "manual":
            return False
            
        elif type_ == "time":
            current_time = time.time()
            if hasattr(self, 'last_process_time'):
                return (current_time - self.last_process_time) >= value
            return False
            
        elif type_ == "words":
            word_count = len(self.accumulated_text.split())
            return word_count >= value
            
        return False
        
    def trigger_instant_processing(self):
        """Process current text immediately when F12 is pressed"""
        if not self.recording_manager.is_recording():
            return
            
        # Get accumulated text from transcription manager
        accumulated_text = self.transcription_manager.get_accumulated_text()
        if accumulated_text.strip():
            self.status_label.setText("🔄 Processing manual chunk...")
            self.status_label.setStyleSheet("color: #ff9800;")  # Orange for processing
            
            # Show loading indicator in curiosity tab
            self.curiosity_tab.empty_label.setText("Processing text...")
            self.curiosity_tab.empty_label.setVisible(True)
            
            # Process the accumulated text
            self.process_for_analysis(accumulated_text)
            
            # Reset accumulated text
            self.transcription_manager.reset_accumulated_text()
    def add_quick_bookmark(self):
        """Add instant bookmark at current position"""
        if not self.recording_manager.is_recording():
            return
            
        timestamp = self.recording_manager.get_elapsed_time()
        timestamp_str = f"{int(timestamp // 60):02d}:{int(timestamp % 60):02d}"
        
        # Create bookmark
        bookmark = {
            'timestamp': timestamp,
            'display_time': timestamp_str,
            'name': f"Quick Mark {len(self.bookmarks) + 1}",
            'context': self.get_context_window(),
            'type': 'quick'
        }
        self.bookmarks.append(bookmark)
        
        # Add visual marker
        cursor = self.live_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        marker_html = f"""
            <div style="margin: 10px 0; padding: 8px 10px; background-color: #E8F5E9; border-left: 4px solid #4CAF50; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <span style="color: #2E7D32; font-weight: bold; font-size: 14px;">📌 BOOKMARK [{timestamp_str}]</span><br>
                <span style="color: #1B5E20; background-color: transparent;">{bookmark['name']}</span>
            </div>
        """
        cursor.insertHtml(marker_html)
        
        # Update bookmark list
        self.update_bookmark_list()
        
        # Show quick feedback
        self.show_quick_feedback(f"Bookmark added at {timestamp_str}")

    def add_named_bookmark(self, preset_name=None):
        """Add bookmark with custom name or preset name"""
        try:
            # Check if recording is active
            if not self.recording_manager.is_recording():
                self.show_quick_feedback("Cannot add bookmark - not recording")
                return
                
            # Get current timestamp
            timestamp = self.recording_manager.get_elapsed_time()
            timestamp_str = f"{int(timestamp // 60):02d}:{int(timestamp % 60):02d}"
            
            # If preset_name is provided, create bookmark immediately without dialog
            if preset_name:
                bookmark = {
                    'timestamp': timestamp,
                    'display_time': timestamp_str,
                    'name': preset_name,
                    'context': self.get_context_window(),
                    'type': 'named'
                }
                
                # Add to bookmarks list
                if not hasattr(self, 'bookmarks'):
                    self.bookmarks = []
                self.bookmarks.append(bookmark)
                
                # Add visual marker
                cursor = self.live_text.textCursor()
                cursor.movePosition(cursor.MoveOperation.End)
                marker_html = f"""
                    <div style="margin: 10px 0; padding: 8px 10px; background-color: #FFF3E0; border-left: 4px solid #FF9800; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                        <span style="color: #E65100; font-weight: bold; font-size: 14px;">🏷️ CUSTOM BOOKMARK [{timestamp_str}]</span><br>
                        <span style="color: #BF360C; background-color: transparent;">{bookmark['name']}</span>
                    </div>
                """
                cursor.insertHtml(marker_html)
                
                # Update bookmark list
                self.update_bookmark_list()
                
                # Show quick feedback
                self.show_quick_feedback(f"Bookmark '{preset_name}' added at {timestamp_str}")
                return
            
            # For manual naming, show a dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Add Named Bookmark")
            dialog.setMinimumWidth(300)
            
            layout = QVBoxLayout(dialog)
            
            # Name input
            layout.addWidget(QLabel(f"Bookmark at {timestamp_str}:"))
            name_edit = QLineEdit(f"Bookmark {len(self.bookmarks) + 1 if hasattr(self, 'bookmarks') else 1}")
            name_edit.selectAll()
            layout.addWidget(name_edit)
            
            # Buttons
            btn_layout = QHBoxLayout()
            save_btn = QPushButton("Save")
            save_btn.clicked.connect(dialog.accept)
            skip_btn = QPushButton("Cancel")
            skip_btn.clicked.connect(dialog.reject)
            
            btn_layout.addWidget(save_btn)
            btn_layout.addWidget(skip_btn)
            layout.addLayout(btn_layout)
            
            dialog.setLayout(layout)
            
            # Show dialog and process result
            if dialog.exec() == QDialog.DialogCode.Accepted:
                bookmark_name = name_edit.text().strip()
                if not bookmark_name:
                    bookmark_name = f"Bookmark {len(self.bookmarks) + 1 if hasattr(self, 'bookmarks') else 1}"
                    
                bookmark = {
                    'timestamp': timestamp,
                    'display_time': timestamp_str,
                    'name': bookmark_name,
                    'context': self.get_context_window(),
                    'type': 'named'
                }
                
                # Add to bookmarks list
                if not hasattr(self, 'bookmarks'):
                    self.bookmarks = []
                self.bookmarks.append(bookmark)
                
                # Add visual marker
                cursor = self.live_text.textCursor()
                cursor.movePosition(cursor.MoveOperation.End)
                marker_html = f"""
                    <div style="margin: 10px 0; padding: 8px 10px; background-color: #FFF3E0; border-left: 4px solid #FF9800; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                        <span style="color: #E65100; font-weight: bold; font-size: 14px;">🏷️ NAMED MARK [{timestamp_str}]</span><br>
                        <span style="color: #BF360C;">{bookmark['name']}</span>
                    </div>
                """
                cursor.insertHtml(marker_html)
                
                # Update bookmark list
                self.update_bookmark_list()
                
                # Show quick feedback
                self.show_quick_feedback(f"Named bookmark added at {timestamp_str}")
        
        except Exception as e:
            print(f"Error adding named bookmark: {str(e)}")
            self.status_label.setText(f"Error adding bookmark: {str(e)}")
            self.status_label.setStyleSheet("color: #f44336;")  # Red for error
            self.show_quick_feedback(f"Error adding bookmark: {str(e)}")

    def update_bookmark_list(self):
        """Update the bookmark list widget with current bookmarks"""
        self.bookmark_list.clear()
        
        if not hasattr(self, 'bookmarks') or not self.bookmarks:
            # Add a placeholder item if no bookmarks
            placeholder = QListWidgetItem("No bookmarks yet")
            placeholder.setFlags(placeholder.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            placeholder.setForeground(Qt.GlobalColor.gray)
            self.bookmark_list.addItem(placeholder)
            return
        
        for idx, bookmark in enumerate(self.bookmarks):
            # Create a more informative item
            display_text = f"[{bookmark['display_time']}] {bookmark['name']}"
            item = QListWidgetItem(display_text)
            
            # Store the bookmark index for reference
            item.setData(Qt.ItemDataRole.UserRole, idx)
            
            # Set tooltip with context if available
            if 'context' in bookmark and bookmark['context']:
                context = bookmark['context']
                if len(context) > 100:
                    context = context[:97] + "..."
                item.setToolTip(f"Context: {context}")
            
            # Add to list
            self.bookmark_list.addItem(item)
        
        # Ensure the list has a reasonable minimum height
        min_height = min(120, max(60, len(self.bookmarks) * 22))
        self.bookmark_list.setMinimumHeight(min_height)

    def jump_to_bookmark(self, item):
        """Jump to bookmark position in transcript"""
        idx = item.data(Qt.ItemDataRole.UserRole)
        bookmark = self.bookmarks[idx]
        
        # Find bookmark in transcript
        doc = self.live_text.document()
        cursor = QTextCursor(doc)
        
        # Search for the bookmark marker
        while not cursor.atEnd():
            cursor.movePosition(cursor.MoveOperation.NextBlock)
            block_text = cursor.block().text()
            if f"[{bookmark['display_time']}]" in block_text:
                self.live_text.setTextCursor(cursor)
                self.live_text.ensureCursorVisible()
                break

    def get_context_window(self, window_size=200):
        """Get recent context around current position"""
        cursor = self.live_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        pos = cursor.position()
        
        # Get text window around current position
        doc = self.live_text.document()
        start = max(0, pos - window_size)
        end = pos
        
        cursor.setPosition(start)
        cursor.movePosition(QTextCursor.MoveOperation.Right, 
                          QTextCursor.MoveMode.KeepAnchor, 
                          end - start)
        return cursor.selectedText()

    def open_trigger_manager(self):
        """Open the trigger manager dialog"""
        dialog = TriggerManagerDialog(self)
        if dialog.exec():
            # Reload triggers after dialog is closed with OK
            self.load_triggers_from_settings()
            
    def load_triggers_from_settings(self):
        """Load saved triggers from settings"""
        # Create settings with organization and application name
        settings = QSettings("PowerPlay", "MeetingAssistant")
        
        saved_triggers = settings.value('system_triggers', None)
        print("DEBUG: Raw loaded triggers:", saved_triggers)
        
        if saved_triggers:
            self.triggers = saved_triggers
            print("DEBUG: Loaded existing triggers:", self.triggers)
        else:
            print("DEBUG: No triggers found, initializing defaults")
            self.triggers = [
                {
                    'action': "Create Quick Bookmark",
                    'trigger_phrase': "bookmark this",
                    'bookmark_name': "Quick Mark"
                },
                {
                    'action': "Create Named Bookmark",
                    'trigger_phrase': "mark important",
                    'bookmark_name': "Important Point"
                }
            ]
            # Save defaults
            settings.setValue('system_triggers', self.triggers)
            
    # This method is now handled by the TranscriptionManager class
    # The code is kept here for reference but is no longer used
                    
    def _execute_trigger_action(self, trigger):
        """Execute the action associated with a trigger
        
        Args:
            trigger: Dictionary containing trigger information
        """
        action = trigger['action']
        
        if action == "Create Quick Bookmark":
            self.add_quick_bookmark()
        elif action == "Create Named Bookmark":
            self.add_named_bookmark(preset_name=trigger['bookmark_name'])
        elif action == "Process Current Section":
            self.trigger_instant_processing()
        elif action == "Pause/Resume Recording":
            self.toggle_pause()
        elif action == "Stop Recording Session":
            self.stop_recording()

    def show_quick_feedback(self, message):
        """Show non-intrusive feedback message"""
        feedback = QLabel(message)
        feedback.setStyleSheet("""
            QLabel {
                background-color: #333;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
        """)
        feedback.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        
        # Position near the bookmark button
        pos = self.quick_bookmark_btn.mapToGlobal(self.quick_bookmark_btn.rect().bottomRight())
        feedback.move(pos.x() - feedback.sizeHint().width(), pos.y() + 5)
        
        feedback.show()
        QTimer.singleShot(1500, feedback.deleteLater)  # Remove after 1.5 seconds

    def copy_to_clipboard(self, text_widget):
        """Copy text widget contents to clipboard"""
        text = text_widget.toPlainText()
        QApplication.clipboard().setText(text)
        
        # Create a temporary overlay label for feedback
        feedback = QLabel("Copied to clipboard!", text_widget)
        feedback.setStyleSheet("""
            background-color: rgba(70, 70, 70, 0.8);
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            font-weight: bold;
        """)
        feedback.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Position in the center of the text widget
        feedback.adjustSize()
        x = (text_widget.width() - feedback.width()) // 2
        y = (text_widget.height() - feedback.height()) // 2
        feedback.move(x, y)
        
        # Show and auto-hide after 1 second
        feedback.show()
        QTimer.singleShot(1000, feedback.deleteLater)
        
    def _format_analysis_html(self, result, current_time, template_name, model_name, process_time):
        """Format analysis result as HTML content"""
        # Create a helper method to format the HTML content for analysis results
        return self._create_html_message_container(
            content=markdown.markdown(result, extensions=['tables']),
            timestamp=current_time,
            template=template_name,
            model=model_name,
            duration=f"{process_time:.1f}s"
        )
        
    def _create_html_message_container(self, content, timestamp, template, model, duration):
        """Create a styled HTML container for messages
        
        Args:
            content: The HTML content to display
            timestamp: The timestamp string
            template: The template name
            model: The model name
            duration: The processing duration
            
        Returns:
            str: Formatted HTML string
        """
        # Check if we're in dark mode
        settings = QSettings("PowerPlay", "MeetingAssistant")
        is_dark_mode = settings.value('dark_mode', 'false').lower() == 'true'
        
        # Set colors based on mode
        if is_dark_mode:
            bg_color = "#2C3E50"
            text_color = "#FFFFFF"
            header_color = "#666"
            template_color = "#2196F3"
        else:
            bg_color = "#f5f5f5"
            text_color = "#333333"
            header_color = "#666"
            template_color = "#0D47A1"
        
        html_content = f"""
    <div class="message-container" style="margin: 15px 10px;">
        <!-- Global style overrides -->
        <style>
            /* Universal reset for all elements inside container */
            .message-container * {{
                background: transparent !important;
                margin: 0 !important;
                padding: 0 !important;
            }}
            
            /* Specific element adjustments */
            .message-container p {{ margin-bottom: 8px !important; }}
            .message-container ul, 
            .message-container ol {{ 
                margin: 4px 0 !important;
                padding-left: 20px !important;
            }}
            .message-container blockquote {{
                border-left: 3px solid #ccc !important;
                margin-left: 0 !important;
                padding-left: 10px !important;
            }}
            .message-container table {{
                border-collapse: collapse !important;
                margin: 8px 0 !important;
            }}
            .message-container th,
            .message-container td {{
                border: 1px solid #ddd !important;
                padding: 6px !important;
            }}
        </style>
        
        <!-- Header -->
        <div style="margin-bottom: 5px;">
            <span style="color: {header_color}; font-size: 0.9em;">{timestamp}</span>
            <span style="color: {template_color}; margin-left: 10px; font-weight: bold;">{template}</span>
            <span style="color: {header_color}; margin-left: 10px;">🤖 {model}</span>
            <span style="color: {header_color}; margin-left: 10px;">⏱️ {duration}</span>
        </div>
        
        <!-- Message Bubble -->
        <div class="message-bubble" style="
            background-color: {bg_color};
            border-radius: 15px;
            padding: 15px;
            margin: 5px 0;
            color: {text_color};
            line-height: 1.6;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        ">
            <div style="color: {text_color};">
                {content}
            </div>
        </div>
    </div>
        """
        return html_content
            
    def refresh_curiosity_questions(self):
        """Refresh curiosity questions with current transcript"""
        # Get current transcript
        transcript = self.live_text.toPlainText()
        
        if not transcript.strip():
            self.curiosity_tab.empty_label.setText("No transcript text to analyze.")
            self.curiosity_tab.empty_label.setVisible(True)
            return
        
        # Show loading state IN THE TAB, not in a popup
        self.curiosity_tab.empty_label.setText("Generating questions...")
        self.curiosity_tab.empty_label.setVisible(True)
        QApplication.processEvents()  # Force UI update
        
        # Process through analysis manager
        template = {"type": "curiosity", "include_speaker_identification": True}
        print(f"Generating curiosity questions with transcript length: {len(transcript)}")
        self.analysis_manager.generate_curiosity_questions(transcript, template)
        
    def on_curiosity_questions_answered(self, answered_questions):
        """Handle when curiosity questions are answered"""
        if not answered_questions:
            return
            
        try:
            # Add answers to transcript
            cursor = self.live_text.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            
            # Add each question and answer
            for question, answer in answered_questions:
                if answer == "skipped" or answer == "closed":
                    continue
                    
                # Format similar to bookmarks
                timestamp = self.recording_manager.get_elapsed_time() if self.recording_manager.is_recording() else 0
                timestamp_str = f"{int(timestamp // 60):02d}:{int(timestamp % 60):02d}"
                
                # Create HTML marker similar to bookmarks but with different styling
                marker_html = f"""
                    <div style="margin: 10px 0; padding: 8px 10px; background-color: #E3F2FD; border-left: 4px solid #2196F3; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                        <span style="color: #0D47A1; font-weight: bold; font-size: 14px;">🧠 CURIOSITY ENGINE [{timestamp_str}]</span><br>
                        <span style="color: #1565C0; font-weight: bold; background-color: transparent;">Q: {question.text}</span><br>
                        <span style="color: #1976D2; background-color: transparent;">A: {answer}</span>
                    </div>
                """
                
                cursor.insertHtml(marker_html)
                
                # Show a brief notification
                self.status_label.setText(f"Answer added to transcript: {answer[:20]}...")
                self.status_label.setStyleSheet("color: #4caf50;")  # Green for success
            
        except Exception as e:
            print(f"Error adding curiosity answers to transcript: {str(e)}")
            self.status_label.setText(f"Error adding answers: {str(e)}")
            self.status_label.setStyleSheet("color: #f44336;")  # Red for error
        

    def _on_recording_started(self):
        """Handle recording started event"""
        # Update UI state
        self.record_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.mute_btn.setEnabled(True)
        
        # Add pulsing animation to status indicator
        self.status_indicator.setStyleSheet("""
            background-color: #f44336;
            border-radius: 10px;
            animation: pulse 1.5s infinite;
        """)
        
        # Add pulsing animation to status
        self.status_label.setText("🎙️ Recording in progress")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #ef5350;
                font-weight: bold;
                padding: 4px 8px;
                border-radius: 4px;
                background: #FFEBEE;
            }
        """)
        
        # Start timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(100)  # Update more frequently for smoother display
        
        # Clear displays
        self.live_text.clear()
        self.analysis_text.clear()
        
        # Create animation for recording indicator using color animation instead of opacity
        try:
            # Create color animation for the status indicator
            self.pulse_timer = QTimer(self)
            self.pulse_timer.timeout.connect(self._pulse_status_indicator)
            self.pulse_timer.start(500)  # Pulse every 500ms
            self._pulse_state = True
        except Exception as e:
            print(f"Error setting up pulse animation: {str(e)}")
        
        # Initialize transcription service
        self.transcription_manager.initialize()
        
    def _pulse_status_indicator(self):
        """Pulse the status indicator by changing its color"""
        try:
            if hasattr(self, '_pulse_state'):
                if self._pulse_state:
                    self.status_indicator.setStyleSheet("""
                        background-color: #f44336;
                        border-radius: 10px;
                    """)
                else:
                    self.status_indicator.setStyleSheet("""
                        background-color: #e53935;
                        border-radius: 10px;
                    """)
                self._pulse_state = not self._pulse_state
        except Exception as e:
            print(f"Error in pulse animation: {str(e)}")
        
    def _on_recording_stopped(self, mp3_path, mp3_data):
        """Handle recording stopped event"""
        # Reset UI state
        self.record_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText("⏸️ Pause")
        self.stop_btn.setEnabled(False)
        self.mute_btn.setEnabled(False)
        self.mute_btn.setText("🔊 Mute")
        self.mute_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 20px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
            QPushButton:disabled {
                background-color: #C8E6C9;
            }
        """)
        
        # Reset status indicator
        self.status_indicator.setStyleSheet("""
            background-color: #ccc;
            border-radius: 10px;
        """)
        
        # Stop pulse animation if it exists
        if hasattr(self, 'pulse_animation'):
            self.pulse_animation.stop()
        
        # Stop timer
        if hasattr(self, 'timer') and self.timer:
            self.timer.stop()
            self.timer = None
            
        # Reset timer display
        self.timer_display.setText("00:00:00")
        
        # Stop transcription service
        self.transcription_manager.stop()
        
        if mp3_data and self.session_name.text():
            try:
                # Get session name and timestamp
                session_name = self.session_name.text()
                timestamp = datetime.now().strftime("%y%m%d_%H%M")  # Format: YYMMDD_HHMM
                
                # Get workspace directory
                session_dir = self.app.path_manager.get_session_dir(session_name)
                
                # Create filename using timestamp and session name
                filename = f"{timestamp}_{session_name}"
        
                # Get file paths with consistent naming
                audio_path = self.app.path_manager.get_recording_path(session_dir, filename)
                transcript_path = self.app.path_manager.get_transcript_path(session_dir, filename)
                analysis_path = self.app.path_manager.get_analysis_path(session_dir, filename)
        
                # Save MP3
                with open(audio_path, 'wb') as f:
                    f.write(mp3_data)
        
                # Save transcript
                transcript_text = self.live_text.toPlainText()
                with open(transcript_path, 'w', encoding='utf-8') as f:
                    f.write(transcript_text)
                    
                # Save bookmarks if any exist
                if hasattr(self, 'bookmarks') and self.bookmarks:
                    bookmark_path = os.path.join(session_dir, f"{filename}_bookmarks.json")
                    try:
                        with open(bookmark_path, 'w', encoding='utf-8') as f:
                            json.dump(self.bookmarks, f, indent=2)
                        print(f"Bookmarks saved to {bookmark_path}")
                    except Exception as e:
                        print(f"Error saving bookmarks: {str(e)}")
        
                # Save analysis if any
                analysis_text = self.analysis_text.toPlainText()
                if analysis_text:
                    with open(analysis_path, 'w', encoding='utf-8') as f:
                        f.write(analysis_text)
        
                # Set current paths for later saving
                self.current_transcript_path = Path(transcript_path)
                self.current_analysis_path = Path(analysis_path)
        
                # Update status bar
                self.status_label.setText(f"Session saved: {os.path.abspath(session_dir)}")
                
            except Exception as e:
                error_msg = f"Failed to save session files: {str(e)}"
                self.status_label.setText(error_msg)
                QMessageBox.critical(self, "Error", error_msg)
    
    def _on_recording_paused(self):
        """Handle recording paused event"""
        self.pause_btn.setText("▶️ Resume")
        self.pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #455a64;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 20px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #37474f;
            }
            QPushButton:disabled {
                background-color: #cfd8dc;
            }
        """)
        self.status_indicator.setStyleSheet("""
            background-color: #FFC107;
            border-radius: 10px;
        """)
        self.timer_indicator.paused = True
        self.timer_indicator.update()
        
        # Pause transcription
        self.transcription_manager.pause()
    
    def _on_recording_resumed(self):
        """Handle recording resumed event"""
        self.pause_btn.setText("⏸️ Pause")
        self.pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #546e7a;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 20px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #455a64;
            }
            QPushButton:disabled {
                background-color: #cfd8dc;
            }
        """)
        self.status_indicator.setStyleSheet("""
            background-color: #f44336;
            border-radius: 10px;
            animation: pulse 1.5s infinite;
        """)
        self.timer_indicator.paused = False
        self.timer_indicator.update()
        
        # Resume transcription
        self.transcription_manager.resume()
    
    def _on_mute_toggled(self, is_muted):
        """Handle mute toggled event"""
        if is_muted:
            self.mute_btn.setText("🔇 Unmute")
            self.mute_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e53935;
                    color: white;
                    font-weight: bold;
                    padding: 8px 16px;
                    border-radius: 20px;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: #c62828;
                }
            """)
        else:
            self.mute_btn.setText("🔊 Mute")
            self.mute_btn.setStyleSheet("""
                QPushButton {
                    background-color: #78909c;
                    color: white;
                    font-weight: bold;
                    padding: 8px 16px;
                    border-radius: 20px;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: #607d8b;
                }
                QPushButton:checked {
                    background-color: #e53935;
                }
                QPushButton:disabled {
                    background-color: #cfd8dc;
                }
            """)
    
    def _on_recording_error(self, error_msg):
        """Handle recording error"""
        QMessageBox.critical(self, "Recording Error", error_msg)
        self.status_label.setText(f"Error: {error_msg}")
        self.status_label.setStyleSheet("color: #f44336;")  # Red for error
    
    def _on_transcription_ready(self, transcript_text):
        """Handle new transcription text"""
        # Format timestamp
        timestamp = self.recording_manager.get_elapsed_time()
        minutes = int(timestamp // 60)
        seconds = int(timestamp % 60)
        timestamp_str = f"[{minutes:02d}:{seconds:02d}]"
        
        # Add to transcript
        text = f"{timestamp_str} {transcript_text}\n"
        self.live_text.append(text)
        QApplication.processEvents()  # Keep UI responsive
        
        # Check if we should process based on current settings
        type_, value = self.get_interval_settings()
        if self.transcription_manager.should_process_chunk(type_, value):
            # Get complete transcript up to this point
            full_transcript = self.live_text.toPlainText()
            self.process_for_analysis(full_transcript)
            self.transcription_manager.reset_accumulated_text()
            
        # Process transcript for keyword detection in compass
        if hasattr(self, 'compass_tab'):
            self.compass_tab.process_live_text(transcript_text)
    
    def _on_transcription_error(self, error_msg):
        """Handle transcription error"""
        self.status_label.setText(f"Transcription error: {error_msg}")
        self.status_label.setStyleSheet("color: #f44336;")  # Red for error
        
        if self._debug_mode:
            print(f"Transcription error: {error_msg}")
    
    def _on_trigger_detected(self, trigger):
        """Handle detected voice command trigger"""
        # Show feedback
        self.show_quick_feedback(f"Voice command detected: {trigger['trigger_phrase']}")
        
        if trigger['action'] == "Create Quick Bookmark":
            self.add_quick_bookmark()
        elif trigger['action'] == "Create Named Bookmark":
            self.add_named_bookmark(preset_name=trigger['bookmark_name'])
        elif trigger['action'] == "Process Current Section":
            self.trigger_instant_processing()
        elif trigger['action'] == "Pause/Resume Recording":
            self.toggle_pause()
        elif trigger['action'] == "Stop Recording Session":
            self.stop_recording()
    
    def _on_analysis_complete(self, result, process_time, template_name):
        """Handle completed analysis"""
        current_time = QDateTime.currentDateTime().toString("hh:mm:ss")
        current_model = self.app.service_adapter.langchain_service.llm.model_name
        
        # Update status bar
        self.status_label.setText(f"Last: {current_model} ({process_time:.1f}s)")
        self.status_label.setStyleSheet("color: #4caf50;")
        
        # Enable save analysis button after new analysis
        self.save_analysis_btn.setEnabled(True)
        
        # Create formatted HTML content for the analysis result
        html_content = self._format_analysis_html(
            result=result,
            current_time=current_time,
            template_name=template_name,
            model_name=current_model,
            process_time=process_time
        )
        
        # Update stats
        self.app.service_adapter.langchain_service.update_model_stats(
            model=current_model,
            template_name=template_name,
            response_time=process_time,
            response_length=len(result)
        )
        
        # Clear any existing formatting
        cursor = self.analysis_text.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.setCharFormat(QTextCharFormat())
        
        self.analysis_text.setTextCursor(cursor)
        
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertHtml(html_content)
        
        self.analysis_text.setTextCursor(cursor)
        self.analysis_text.ensureCursorVisible()
    
    def _on_analysis_error(self, error_msg):
        """Handle analysis error"""
        error_time = QDateTime.currentDateTime().toString("hh:mm:ss")
        error_html = f"""
        <div style="margin: 10px 0; color: red;">
            <strong>Error at {error_time}:</strong><br/>
            {error_msg}
        </div>
        """
        cursor = self.analysis_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertHtml(error_html)
        cursor.insertBlock()
        
        self.status_label.setText(f"Analysis error: {error_msg}")
        self.status_label.setStyleSheet("color: #f44336;")  # Red for error
        
        if self._debug_mode:
            print(f"Analysis error: {error_msg}")
    
    def _on_progress_updated(self, value, maximum, status):
        """Handle progress updates from analysis"""
        self.status_label.setText(status)
        
    def _on_questions_ready(self, questions):
        """Handle curiosity questions ready"""
        print(f"Questions ready: {len(questions)} questions received")
        for q in questions:
            print(f"  - {q.text}")
        
        # Directly set questions on the curiosity tab
        if hasattr(self, 'curiosity_tab'):
            print("Setting questions on curiosity tab")
            self.curiosity_tab.set_questions(questions)
            
            # Ensure we're on the curiosity tab to see the results
            if hasattr(self, 'analysis_tabs'):
                # Find the index of the curiosity tab
                for i in range(self.analysis_tabs.count()):
                    if self.analysis_tabs.widget(i) == self.curiosity_tab:
                        # Don't automatically switch tabs - let user control this
                        # self.analysis_tabs.setCurrentIndex(i)
                        break
        else:
            print("ERROR: No curiosity_tab attribute found!")
        
    def load_templates(self, preserve_selection=True):
        """Load available templates and set descriptions"""
        if self._debug_mode:
            print("Loading templates...")
            
        try:
            # Store current selection
            current_template = None
            if preserve_selection and self.template_combo.count() > 0:
                current_template = self.template_combo.currentText()
                
            # Load templates through analysis manager
            templates = self.analysis_manager.load_templates(preserve_selection)
            
            # Update combo box
            self.template_combo.clear()
            for template in templates:
                self.template_combo.addItem(template["name"])
                
            # Restore previous selection if it exists
            if preserve_selection and current_template:
                index = self.template_combo.findText(current_template)
                if index >= 0:
                    self.template_combo.setCurrentIndex(index)
                    
            # Default to first template if needed
            if self.template_combo.count() > 0 and self.template_combo.currentIndex() < 0:
                self.template_combo.setCurrentIndex(0)
                
            # Update template description
            self.on_template_changed()
            
        except Exception as e:
            if self._debug_mode:
                print(f"Error loading templates: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load templates: {str(e)}")

    def on_template_changed(self):
        """Update template description when selection changes"""
        current_template = self.template_combo.currentText()
        description = self.analysis_manager.get_template_description(current_template)
        
        # We no longer need to update the template_description widget
        # as it was removed in the UI improvements
            
        # Update analysis manager's current template
        self.analysis_manager.set_current_template(current_template)

    def open_template_editor(self):
        """Open the template editor dialog"""
        # Guard against multiple calls
        if hasattr(self, '_template_editor_open') and self._template_editor_open:
            print("Template editor already open, ignoring second call")
            return
        
        self._template_editor_open = True
        try:
            from .template_editor_dialog import TemplateEditorDialog
            
            # Ensure we have the app reference
            if not hasattr(self, 'app') or not self.app:
                QMessageBox.critical(self, "Error", "Application reference not available")
                return
                
            # Ensure we have access to langchain_service
            if not hasattr(self.app, 'langchain_service'):
                QMessageBox.critical(self, "Error", "LangChain service not available")
                return
                
            # Ensure we have access to template_manager
            if not hasattr(self.app.langchain_service, 'template_manager'):
                QMessageBox.critical(self, "Error", "Template manager not available")
                return
                
            # Pass both self (which has app attribute) and the template manager
            editor = TemplateEditorDialog(self, self.app.langchain_service.template_manager)
            
            # Debug output
            print(f"App reference: {self.app}")
            print(f"LangChain service: {self.app.langchain_service}")
            print(f"Template manager: {self.app.langchain_service.template_manager}")
            
            if editor.exec():
                # Only reload if changes were made (dialog accepted)
                self.load_templates(preserve_selection=True)
        finally:
            self._template_editor_open = False

    def update_status(self, message):
        """Update status bar message"""
        self.status_label.setText(message)
        
        # Reset style if it was set for errors/warnings
        if not message.startswith("Error") and not message.startswith("Warning"):
            self.status_label.setStyleSheet("")
        
    def send_to_deep_analysis(self):
        """Send current analysis to deep analysis tab"""
        # Get main window
        main_window = self.parent()
        while main_window and not hasattr(main_window, 'deep_analysis_tab'):
            main_window = main_window.parent()
            
        if not main_window:
            QMessageBox.critical(self, "Error", "Could not find main window")
            return
            
        if not hasattr(self, 'current_transcript_path') or not self.current_transcript_path:
            # If no transcript path but we have text, create a temporary transcript
            if hasattr(self, 'live_text') and self.live_text.toPlainText().strip():
                try:
                    # Create temporary transcript in session directory
                    session_dir = self.app.path_manager.get_session_dir("temp_analysis")
                    temp_path = Path(self.app.path_manager.get_transcript_path(session_dir))
                    temp_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(temp_path, 'w', encoding='utf-8') as f:
                        f.write(self.live_text.toPlainText())
                    
                    self.current_transcript_path = temp_path
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to create temporary transcript: {str(e)}")
                    return
            else:
                QMessageBox.warning(self, "Warning", "No transcript available to analyze")
                return
            
        # Send to deep analysis tab
        main_window.deep_analysis_tab.add_transcripts([str(self.current_transcript_path)])
        main_window.tab_widget.setCurrentWidget(main_window.deep_analysis_tab)
        
    def run_full_analysis(self):
        """Run full analysis on all accumulated text"""
        if not hasattr(self, 'live_text'):
            return
            
        # Get all text
        full_text = self.live_text.toPlainText()
        if not full_text.strip():
            return
            
        # Process with full analysis flag
        self.process_for_analysis(full_text, is_full_analysis=True)
    def _init_session_section(self, layout):
        """Initialize the session name section"""
        session_group = QGroupBox("Session Name")
        session_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ccc;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 7px;
                padding: 0 5px;
            }
        """)
        session_layout = QHBoxLayout(session_group)
        session_layout.setContentsMargins(10, 2, 10, 2)
        
        self.session_name = QLineEdit()
        self.session_name.setPlaceholderText("Enter session name...")
        self.session_name.setToolTip("Enter a name for this recording session")
        self.session_name.setMinimumWidth(300)
        self.session_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.session_name.setStyleSheet("""
            QLineEdit {
                font-size: 12pt;
                font-weight: bold;
                padding: 4px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
                color: #333333;
            }
            QLineEdit:focus {
                border: 2px solid #546e7a;
                background-color: #f5f5f5;
            }
            QLineEdit::placeholder {
                color: #9e9e9e;
            }
        """)
        session_layout.addWidget(self.session_name)
        
        # Add session header to main layout
        layout.addWidget(session_group)
        
    def _init_recording_controls(self, parent_layout):
        """Initialize the recording controls panel"""
        recording_panel = QGroupBox("Recording Controls")
        recording_panel.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ccc;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 7px;
                padding: 0 5px;
            }
        """)
        recording_layout = QHBoxLayout()
        recording_layout.setContentsMargins(10, 2, 10, 2)
        
        # Recording status indicator
        self.status_indicator = QLabel()
        self.status_indicator.setFixedSize(20, 20)
        self.status_indicator.setStyleSheet("""
            background-color: #ccc;
            border-radius: 10px;
        """)
        recording_layout.addWidget(self.status_indicator)
        
        # Recording buttons on the left
        recording_buttons = QHBoxLayout()
        
        # Record button - keep red for recording but reduce padding
        self.record_btn = QPushButton("⏺️ Record")
        self.record_btn.setToolTip("Start Recording (Alt+R)")
        self.record_btn.setShortcut("Alt+R")
        self.record_btn.setStyleSheet("""
            QPushButton {
                background-color: #e53935;
                color: white;
                font-weight: bold;
                padding: 4px 12px;
                border-radius: 16px;
                min-width: 90px;
            }
            QPushButton:hover {
                background-color: #c62828;
            }
            QPushButton:disabled {
                background-color: #ffcdd2;
            }
        """)
        self.record_btn.clicked.connect(self.start_recording)
        recording_buttons.addWidget(self.record_btn)
        
        # Pause button - with reduced padding
        self.pause_btn = QPushButton("⏸️ Pause")
        self.pause_btn.setToolTip("Pause/Resume Recording (Alt+P)")
        self.pause_btn.setShortcut("Alt+P")
        self.pause_btn.setEnabled(False)  # Disabled until recording starts
        self.pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #546e7a;
                color: white;
                font-weight: bold;
                padding: 4px 12px;
                border-radius: 16px;
                min-width: 90px;
            }
            QPushButton:hover {
                background-color: #455a64;
            }
            QPushButton:disabled {
                background-color: #cfd8dc;
            }
        """)
        self.pause_btn.clicked.connect(self.toggle_pause)
        recording_buttons.addWidget(self.pause_btn)
        
        # Stop button - with reduced padding
        self.stop_btn = QPushButton("⏹️ Stop")
        self.stop_btn.setToolTip("Stop Recording and Save (Alt+S)")
        self.stop_btn.setShortcut("Alt+S")
        self.stop_btn.setEnabled(False)  # Disabled until recording starts
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #37474f;
                color: white;
                font-weight: bold;
                padding: 4px 12px;
                border-radius: 16px;
                min-width: 90px;
            }
            QPushButton:hover {
                background-color: #263238;
            }
            QPushButton:disabled {
                background-color: #cfd8dc;
            }
        """)
        self.stop_btn.clicked.connect(self.stop_recording)
        recording_buttons.addWidget(self.stop_btn)
        
        # Add Mute button - with reduced padding
        self.mute_btn = QPushButton("🔊 Mute")
        self.mute_btn.setToolTip("Mute/Unmute Microphone (Alt+M)")
        self.mute_btn.setShortcut("Alt+M")
        self.mute_btn.setEnabled(False)  # Disabled until recording starts
        self.mute_btn.setCheckable(True)
        self.mute_btn.setStyleSheet("""
            QPushButton {
                background-color: #78909c;
                color: white;
                font-weight: bold;
                padding: 4px 12px;
                border-radius: 16px;
                min-width: 90px;
            }
            QPushButton:hover {
                background-color: #607d8b;
            }
            QPushButton:checked {
                background-color: #e53935;
            }
            QPushButton:disabled {
                background-color: #cfd8dc;
            }
        """)
        self.mute_btn.clicked.connect(self.toggle_mute)
        recording_buttons.addWidget(self.mute_btn)
        
        # Add recording buttons to layout
        recording_layout.addLayout(recording_buttons)
        
        # Add timer display with more compact size and font
        self.timer_display = QLabel("00:00:00")
        self.timer_display.setStyleSheet("""
            font-size: 18pt;
            font-weight: bold;
            color: #333;
            padding: 0 5px;
            min-width: 120px;
        """)
        self.timer_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        recording_layout.addWidget(self.timer_display)
        
        # Add audio level visualization with further reduced size
        self.timer_indicator = TimerIndicator()
        self.timer_indicator.setFixedSize(60, 60)  # Further reduce size
        recording_layout.addWidget(self.timer_indicator)
        
        recording_panel.setLayout(recording_layout)
        parent_layout.addWidget(recording_panel)
        
    def _init_analysis_panel(self, parent_layout):
        """Initialize the analysis panel"""
        analysis_panel = QGroupBox("Analysis Tools")
        analysis_panel.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ccc;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 7px;
                padding: 0 5px;
            }
        """)
        
        # Use a more organized grid layout
        analysis_layout = QGridLayout()
        analysis_layout.setContentsMargins(10, 10, 10, 10)
        analysis_layout.setSpacing(8)  # Consistent spacing
        
        # Row 0: Template selection with label
        analysis_layout.addWidget(QLabel("Template:"), 0, 0, Qt.AlignmentFlag.AlignRight)
        
        template_layout = QHBoxLayout()
        self.template_combo = QComboBox()
        self.template_combo.currentTextChanged.connect(self.on_template_changed)
        self.template_combo.setMinimumWidth(200)
        template_layout.addWidget(self.template_combo, 1)  # Give stretch
        
        self.edit_template_btn = QPushButton("✏️")
        self.edit_template_btn.setToolTip("Edit Templates")
        self.edit_template_btn.setMaximumWidth(30)
        self.edit_template_btn.clicked.connect(self.open_template_editor)
        template_layout.addWidget(self.edit_template_btn, 0)  # No stretch
        
        analysis_layout.addLayout(template_layout, 0, 1)
        
        # Row 1: Processing interval with label
        analysis_layout.addWidget(QLabel("Processing:"), 1, 0, Qt.AlignmentFlag.AlignRight)
        self.interval_combo = QComboBox()
        self.interval_combo.addItems([
            "Manual (F12)", 
            "Time: 10s", 
            "Time: 45s", 
            "Time: 5m", 
            "Time: 10m",
            "Words: 50",
            "Words: 100",
            "Words: 200",
            "Words: 500",
            "Silence: 5s",
            "Silence: 15s",
            "Silence: 30s"
        ])
        self.interval_combo.setToolTip(
            "Choose how to chunk the transcript:\n"
            "- Time: Process every N seconds\n"
            "- Words: Process every N words\n"
            "- Manual: Only process when F12 is pressed"
        )
        analysis_layout.addWidget(self.interval_combo, 1, 1)
        
        # Row 2: Action buttons in a horizontal layout
        action_layout = QHBoxLayout()
        
        # Process button
        self.process_btn = QPushButton("⚡ Process (F12)")
        self.process_btn.setStyleSheet("""
            QPushButton {
                background-color: #546e7a;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #455a64;
            }
        """)
        self.process_btn.clicked.connect(self.trigger_instant_processing)
        action_layout.addWidget(self.process_btn)
        
        # Full analysis button
        self.full_analysis_btn = QPushButton("🔍 Full Analysis (F10)")
        self.full_analysis_btn.setStyleSheet("""
            QPushButton {
                background-color: #78909c;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #607d8b;
            }
        """)
        self.full_analysis_btn.clicked.connect(self.run_full_analysis)
        action_layout.addWidget(self.full_analysis_btn)
        
        # Deep analysis button
        self.deep_analysis_btn = QPushButton("🧠 Deep Analysis")
        self.deep_analysis_btn.setStyleSheet("""
            QPushButton {
                background-color: #455a64;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #37474f;
            }
        """)
        self.deep_analysis_btn.clicked.connect(self.send_to_deep_analysis)
        action_layout.addWidget(self.deep_analysis_btn)
        
        analysis_layout.addLayout(action_layout, 2, 0, 1, 2)
        
        # Row 3: Curiosity controls
        curiosity_layout = QHBoxLayout()
        
        # Refresh button for curiosity questions
        self.refresh_curiosity_btn = QPushButton("🔄 Refresh Questions")
        self.refresh_curiosity_btn.setStyleSheet("""
            QPushButton {
                background-color: #546e7a;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #455a64;
            }
        """)
        self.refresh_curiosity_btn.clicked.connect(self.refresh_curiosity_questions)
        curiosity_layout.addWidget(self.refresh_curiosity_btn)
        
        # Clear button for curiosity questions
        self.clear_curiosity_btn = QPushButton("🗑️ Clear Questions")
        self.clear_curiosity_btn.setStyleSheet("""
            QPushButton {
                background-color: #78909c;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #607d8b;
            }
        """)
        self.clear_curiosity_btn.clicked.connect(lambda: self.curiosity_tab.clear_all_questions())
        curiosity_layout.addWidget(self.clear_curiosity_btn)
        
        analysis_layout.addLayout(curiosity_layout, 3, 0, 1, 2)
        
        # Add F10 shortcut
        QShortcut(QKeySequence("F10"), self, self.run_full_analysis)
        
        analysis_panel.setLayout(analysis_layout)
        parent_layout.addWidget(analysis_panel)
        
    def _init_content_area(self, layout):
        """Initialize the main content area with transcript and analysis sections"""
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Transcript Section
        transcript_widget = QGroupBox("Live Text")
        transcript_widget.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ccc;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 7px;
                padding: 0 5px;
            }
        """)
        transcript_layout = QVBoxLayout(transcript_widget)
        transcript_layout.setContentsMargins(10, 2, 10, 2)
        
        # Add font control
        font_control_layout = QHBoxLayout()
        self.live_text_font = FontControlPanel(settings_key="live_text_font")
        self.live_text_font.fontChanged.connect(lambda f: self.live_text.setFont(f))
        font_control_layout.addWidget(self.live_text_font)
        
        self.copy_transcript_btn = QPushButton("📋 Copy")
        self.copy_transcript_btn.clicked.connect(lambda: self.copy_to_clipboard(self.live_text))
        font_control_layout.addWidget(self.copy_transcript_btn)
        transcript_layout.addLayout(font_control_layout)
        
        self.live_text = QTextEdit()
        self.live_text.setReadOnly(True)
        self.live_text.setMinimumHeight(300)  # Make it taller
        self.live_text.setProperty("controlled_by", self.live_text_font)
        self.live_text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                color: black;
            }
        """)
        transcript_layout.addWidget(self.live_text)
        content_splitter.addWidget(transcript_widget)
        
        # Analysis Section with Tabs
        analysis_widget = QWidget()
        analysis_layout = QVBoxLayout(analysis_widget)

        # Create tab widget for analysis
        self.analysis_tabs = QTabWidget()
    
        # AI Insights Tab
        self.insights_tab = QWidget()
        insights_layout = QVBoxLayout(self.insights_tab)
    
        # Analysis output
        analysis_header = QHBoxLayout()
        analysis_header.addWidget(QLabel("AI Insights"))
    
        # Add font control
        self.analysis_text_font = FontControlPanel(settings_key="analysis_text_font")
        self.analysis_text_font.fontChanged.connect(lambda f: self.analysis_text.setFont(f))
        analysis_header.addWidget(self.analysis_text_font)
    
        self.copy_analysis_btn = QPushButton("📋 Copy")
        self.copy_analysis_btn.clicked.connect(lambda: self.copy_to_clipboard(self.analysis_text))
        analysis_header.addWidget(self.copy_analysis_btn)
        insights_layout.addLayout(analysis_header)
    
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        self.analysis_text.setMinimumHeight(300)  # Make it taller
        self.analysis_text.setProperty("controlled_by", self.analysis_text_font)
        self.analysis_text.setAcceptRichText(True)
        self.analysis_text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                color: black;
            }
        """)
        # Set default styles for markdown content
        self.analysis_text.document().setDefaultStyleSheet("""
            h1 { font-size: 18pt; margin-top: 6px; margin-bottom: 6px; }
            h2 { font-size: 16pt; margin-top: 6px; margin-bottom: 6px; }
            h3 { font-size: 14pt; margin-top: 6px; margin-bottom: 6px; }
            p { margin-top: 4px; margin-bottom: 4px; }
            ul, ol { margin-top: 4px; margin-bottom: 4px; }
            code { background-color: #f0f0f0; padding: 2px 4px; border-radius: 3px; }
            pre { background-color: #f0f0f0; padding: 8px; border-radius: 3px; }
        """)
        insights_layout.addWidget(self.analysis_text)
    
        # Curiosity Tab
        self.curiosity_tab = CuriosityTabWidget()
        self.curiosity_tab.questions_answered.connect(self.on_curiosity_questions_answered)
    
        # Add tabs to tab widget
        self.analysis_tabs.addTab(self.insights_tab, "AI Insights")
        self.analysis_tabs.addTab(self.curiosity_tab, "Curiosity")
        
        # Add Conversation Compass tab
        from .conversation_compass_widget import ConversationCompassWidget
        self.compass_tab = ConversationCompassWidget(
            parent=self,
            langchain_service=self.app.langchain_service if hasattr(self.app, 'langchain_service') else None
        )
        self.analysis_tabs.addTab(self.compass_tab, "Conversation Compass")
        
        # Connect transcription manager signals to compass tab
        self.transcription_manager.transcription_ready.connect(
            lambda text: self._update_compass_with_transcription(text)
        )
        
        # Connect compass to live text for keyword detection
        if hasattr(self, 'live_text'):
            self.compass_tab.connect_to_live_text(self.live_text)
            
            # Update navigation options when tree changes
            if hasattr(self.compass_tab, 'tree_view') and hasattr(self.compass_tab.tree_view, 'node_clicked'):
                self.compass_tab.tree_view.node_clicked.connect(
                    lambda _: self.compass_tab.update_navigation_options()
                )
                
            # Also update when current node changes
            if hasattr(self.compass_tab, 'tree_service') and hasattr(self.compass_tab.tree_service, 'current_position_changed'):
                self.compass_tab.tree_service.current_position_changed.connect(
                    lambda _: self.compass_tab.update_navigation_options()
                )
    
        analysis_layout.addWidget(self.analysis_tabs)
        
        content_splitter.addWidget(analysis_widget)
        
        # Set initial splitter sizes (40% transcript, 60% analysis)
        content_splitter.setSizes([400, 600])
        layout.addWidget(content_splitter, stretch=1)  # Give it all available space
        
    def _init_control_buttons(self, layout):
        """Initialize the control buttons section"""
        control_layout = QHBoxLayout()
        
        # Edit mode toggle
        self.edit_mode_btn = QPushButton("🔒 Edit Mode: Off")
        self.edit_mode_btn.setCheckable(True)
        self.edit_mode_btn.clicked.connect(self.toggle_edit_mode)
        control_layout.addWidget(self.edit_mode_btn)
        
        # Save buttons
        self.save_transcript_btn = QPushButton("💾 Save Transcript")
        self.save_transcript_btn.clicked.connect(self.save_transcript)
        self.save_transcript_btn.setEnabled(False)
        control_layout.addWidget(self.save_transcript_btn)
        
        self.save_analysis_btn = QPushButton("💾 Save Analysis")
        self.save_analysis_btn.clicked.connect(self.save_analysis)
        self.save_analysis_btn.setEnabled(False)
        control_layout.addWidget(self.save_analysis_btn)
        
        layout.addLayout(control_layout)
        
    def _init_bookmark_panel(self, layout):
        """Initialize the bookmark and voice command panel"""
        bookmark_panel = QGroupBox("Bookmarks & Voice Commands")
        bookmark_panel.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ccc;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 7px;
                padding: 0 5px;
            }
        """)
        bookmark_layout = QHBoxLayout()
        bookmark_layout.setContentsMargins(10, 2, 10, 2)
        
        # Voice Commands Manager
        self.trigger_manager_btn = QPushButton("🎤 Voice Commands")
        self.trigger_manager_btn.setToolTip("Manage voice commands and triggers")
        self.trigger_manager_btn.clicked.connect(self.open_trigger_manager)
        bookmark_layout.addWidget(self.trigger_manager_btn)
        
        # Quick Bookmark
        self.quick_bookmark_btn = QPushButton("📌 Quick Mark (F8)")
        self.quick_bookmark_btn.setStyleSheet("""
            QPushButton:pressed { 
                background-color: #4CAF50; 
                color: white;
            }
        """)
        self.quick_bookmark_btn.clicked.connect(self.add_quick_bookmark)
        bookmark_layout.addWidget(self.quick_bookmark_btn)
        
        # Named Bookmark
        self.named_bookmark_btn = QPushButton("🏷️ Named Mark (F9)")
        self.named_bookmark_btn.setStyleSheet("""
            QPushButton:pressed { 
                background-color: #FF9800; 
                color: white;
            }
        """)
        self.named_bookmark_btn.clicked.connect(self.add_named_bookmark)
        bookmark_layout.addWidget(self.named_bookmark_btn)
        
        # Full Analysis button with reduced padding
        self.full_analysis_btn = QPushButton("⚡ Full Analysis (F10)")
        self.full_analysis_btn.setStyleSheet("""
            QPushButton {
                background-color: #673AB7;
                color: white;
                font-weight: bold;
                padding: 4px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5E35B1;
            }
        """)
        self.full_analysis_btn.clicked.connect(self.run_full_analysis)
        bookmark_layout.addWidget(self.full_analysis_btn)
        
        # Bookmark list with reduced height
        self.bookmark_list = QListWidget()
        self.bookmark_list.setMaximumHeight(60)
        self.bookmark_list.itemDoubleClicked.connect(self.jump_to_bookmark)
        bookmark_layout.addWidget(self.bookmark_list)
        
        bookmark_panel.setLayout(bookmark_layout)
        layout.addWidget(bookmark_panel)
        
        # Keyboard shortcuts
        self.f8_shortcut = QShortcut(QKeySequence("F8"), self)
        self.f8_shortcut.activated.connect(self.add_quick_bookmark)
        self.f9_shortcut = QShortcut(QKeySequence("F9"), self)
        self.f9_shortcut.activated.connect(self.add_named_bookmark)
        
        # Set up bookmark context menu
        self.setup_bookmark_context_menu()
    def format_bookmarks_for_analysis(self):
        """Format bookmarks for inclusion in analysis prompts"""
        if not hasattr(self, 'bookmarks') or not self.bookmarks:
            return ""
            
        formatted = "\n\nBOOKMARKS:\n"
        for idx, bookmark in enumerate(self.bookmarks):
            formatted += f"{idx+1}. [{bookmark['display_time']}] {bookmark['name']}"
            if 'context' in bookmark and bookmark['context']:
                # Include a snippet of context (truncated if too long)
                context = bookmark['context']
                if len(context) > 100:
                    context = context[:97] + "..."
                formatted += f"\n   Context: \"{context}\"\n"
            else:
                formatted += "\n"
                
        return formatted
        
    def _update_compass_with_transcription(self, text):
        """Update the Conversation Compass with new transcription text
        
        Args:
            text: The new transcription text
        """
        # Only process if compass tab exists and is initialized
        if not hasattr(self, 'compass_tab') or not self.compass_tab:
            return
            
        # Check if tree service is initialized
        if not hasattr(self.compass_tab, 'tree_service') or not self.compass_tab.tree_service:
            return
            
        # Parse speaker and content from text
        # Format is typically "[00:00] Speaker: Content"
        try:
            # Skip timestamp
            if "]" in text:
                text = text.split("]", 1)[1].strip()
                
            # Extract speaker and content
            if ":" in text:
                speaker, content = text.split(":", 1)
                speaker = speaker.strip()
                content = content.strip()
            else:
                # No speaker identified, use default
                speaker = "Unknown"
                content = text.strip()
                
            # Add utterance to conversation tree
            if content:
                try:
                    node_id = self.compass_tab.tree_service.add_utterance(content, speaker)
                    # If we're on the compass tab, update the visualization
                    if self.analysis_tabs.currentWidget() == self.compass_tab and node_id:
                        self.compass_tab.tree_view.set_current_node(node_id)
                    print(f"Added utterance to conversation tree: {speaker}: {content[:30]}...")
                    
                    # Update navigation options after adding utterance
                    self.compass_tab.update_navigation_options()
                    
                    # For Guidance mode, generate new suggestions after each utterance
                    if hasattr(self.compass_tab, 'active_mode') and self.compass_tab.active_mode == 1:
                        self.compass_tab._generate_suggestions_for_current_node()
                except Exception as e:
                    print(f"Error adding utterance to tree: {str(e)}")
                
        except Exception as e:
            print(f"Error parsing transcription for compass: {str(e)}")
            
        # Process transcript for keyword detection in compass
        if hasattr(self, 'compass_tab'):
            self.compass_tab.process_live_text(text)
        
    def load_bookmarks_from_file(self, bookmark_path):
        """Load bookmarks from a saved file"""
        if not os.path.exists(bookmark_path):
            return False
            
        try:
            with open(bookmark_path, 'r', encoding='utf-8') as f:
                self.bookmarks = json.load(f)
                
            # Update bookmark list
            self.update_bookmark_list()
            return True
        except Exception as e:
            print(f"Error loading bookmarks: {str(e)}")
            return False
            
    def setup_bookmark_context_menu(self):
        """Set up context menu for bookmark list"""
        self.bookmark_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.bookmark_list.customContextMenuRequested.connect(self.show_bookmark_context_menu)

    def show_bookmark_context_menu(self, position):
        """Show context menu for bookmark list"""
        menu = QMenu()
        
        # Get selected item
        item = self.bookmark_list.itemAt(position)
        if not item:
            # No item selected, show limited menu
            import_action = menu.addAction("Import Bookmarks...")
            export_action = menu.addAction("Export Bookmarks...")
            
            action = menu.exec(self.bookmark_list.mapToGlobal(position))
            if action == import_action:
                self.import_bookmarks()
            elif action == export_action:
                self.export_bookmarks()
            return
        
        # Item selected, show full menu
        jump_action = menu.addAction("Jump to Bookmark")
        edit_action = menu.addAction("Edit Bookmark...")
        delete_action = menu.addAction("Delete Bookmark")
        menu.addSeparator()
        import_action = menu.addAction("Import Bookmarks...")
        export_action = menu.addAction("Export Bookmarks...")
        
        action = menu.exec(self.bookmark_list.mapToGlobal(position))
        if action == jump_action:
            self.jump_to_bookmark(item)
        elif action == edit_action:
            self.edit_bookmark(item)
        elif action == delete_action:
            self.delete_bookmark(item)
        elif action == import_action:
            self.import_bookmarks()
        elif action == export_action:
            self.export_bookmarks()

    def edit_bookmark(self, item):
        """Edit a bookmark"""
        idx = item.data(Qt.ItemDataRole.UserRole)
        bookmark = self.bookmarks[idx]
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Bookmark")
        layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        name_edit = QLineEdit(bookmark['name'])
        form_layout.addRow("Name:", name_edit)
        
        layout.addLayout(form_layout)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Update bookmark
            bookmark['name'] = name_edit.text()
            self.update_bookmark_list()

    def delete_bookmark(self, item):
        """Delete a bookmark"""
        idx = item.data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self,
            "Delete Bookmark",
            f"Are you sure you want to delete the bookmark '{self.bookmarks[idx]['name']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            del self.bookmarks[idx]
            self.update_bookmark_list()
            
    def export_bookmarks(self):
        """Export bookmarks to a file"""
        if not hasattr(self, 'bookmarks') or not self.bookmarks:
            QMessageBox.information(self, "Export Bookmarks", "No bookmarks to export.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Bookmarks", "", "JSON Files (*.json)"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.bookmarks, f, indent=2)
                
            self.status_label.setText(f"Bookmarks exported to {file_path}")
            self.status_label.setStyleSheet("color: #4caf50;")  # Green for success
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export bookmarks: {str(e)}")

    def import_bookmarks(self):
        """Import bookmarks from a file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Bookmarks", "", "JSON Files (*.json)"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_bookmarks = json.load(f)
                
            # Initialize bookmarks list if it doesn't exist
            if not hasattr(self, 'bookmarks'):
                self.bookmarks = []
                
            # Add imported bookmarks to existing ones
            self.bookmarks.extend(imported_bookmarks)
            
            # Update bookmark list
            self.update_bookmark_list()
            
            # Add visual markers to transcript
            for bookmark in imported_bookmarks:
                self.add_bookmark_marker_to_transcript(bookmark)
                
            self.status_label.setText(f"Imported {len(imported_bookmarks)} bookmarks")
            self.status_label.setStyleSheet("color: #4caf50;")  # Green for success
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import bookmarks: {str(e)}")

    def add_bookmark_marker_to_transcript(self, bookmark):
        """Add a visual marker for a bookmark to the transcript"""
        # Only add if we have a transcript
        if not hasattr(self, 'live_text') or not self.live_text.toPlainText():
            return
            
        cursor = self.live_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        
        # Choose style based on bookmark type
        if bookmark.get('type') == 'named' or 'name' in bookmark and bookmark['name'] != f"Quick Mark {len(self.bookmarks)}":
            # Named bookmark style
            marker_html = f"""
                <div style="margin: 10px 0; padding: 8px 10px; background-color: #FFF3E0; border-left: 4px solid #FF9800; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <span style="color: #E65100; font-weight: bold; font-size: 14px;">🏷️ IMPORTED MARK [{bookmark['display_time']}]</span><br>
                    <span style="color: #BF360C; background-color: transparent;">{bookmark['name']}</span>
                </div>
            """
        else:
            # Quick bookmark style
            marker_html = f"""
                <div style="margin: 10px 0; padding: 8px 10px; background-color: #E8F5E9; border-left: 4px solid #4CAF50; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <span style="color: #2E7D32; font-weight: bold; font-size: 14px;">📌 IMPORTED BOOKMARK [{bookmark['display_time']}]</span><br>
                    <span style="color: #1B5E20; background-color: transparent;">{bookmark['name']}</span>
                </div>
            """
        
        cursor.insertHtml(marker_html)
