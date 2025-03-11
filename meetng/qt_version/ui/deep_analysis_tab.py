from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QSplitter, QTextEdit, QListWidget,
    QTabWidget, QInputDialog, QLineEdit, QFrame,
    QMessageBox, QGroupBox, QListWidgetItem, QDialog,
    QMenu, QCheckBox, QComboBox, QStackedWidget
)
from .components.word_cloud_widget import WordCloudWidget, TopWordsWidget
from langchain.memory import ConversationBufferMemory
from langchain_community.callbacks import get_openai_callback
from .media_player_qt import MediaPlayerWidget
from .media_player.bookmark_manager import BookmarkManager
from datetime import datetime
from PyQt6.QtGui import QTextCharFormat, QColor, QTextDocument
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QObject
import os
import json
from typing import Dict, List

class TranscriptCache:
    """Cache for transcript contents with improved error handling and metadata"""
    def __init__(self):
        self.cache: Dict[str, Dict[str, any]] = {}
        self.max_cache_size = 50  # Maximum number of transcripts to keep in cache
        
    def get_transcript(self, file_path: str) -> str:
        """Get transcript content, loading from file if needed"""
        # Check if in cache and return content if available
        if file_path in self.cache:
            self.cache[file_path]['last_accessed'] = datetime.now()
            return self.cache[file_path]['content']
            
        # Not in cache, try to load it
        content = ""
        error = None
        file_size = 0
        transcript_path = None
        
        try:
            # Try direct path first
            if os.path.exists(file_path):
                transcript_path = file_path
                file_size = os.path.getsize(file_path)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                # Try with _transcript.txt suffix
                transcript_path = os.path.splitext(file_path)[0] + "_transcript.txt"
                if os.path.exists(transcript_path):
                    file_size = os.path.getsize(transcript_path)
                    with open(transcript_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                else:
                    error = f"No transcript found for: {file_path}"
                    print(error)
        except Exception as e:
            error = f"Error loading transcript: {e}"
            print(error)
            
        # Manage cache size before adding new item
        if len(self.cache) >= self.max_cache_size:
            self._prune_cache()
            
        # Add to cache with metadata
        self.cache[file_path] = {
            'content': content,
            'error': error,
            'size': file_size,
            'path': transcript_path,
            'last_accessed': datetime.now(),
            'word_count': len(content.split()) if content else 0
        }
        
        return content
        
    def _prune_cache(self):
        """Remove least recently used items from cache"""
        if not self.cache:
            return
            
        # Sort by last accessed time and remove oldest
        sorted_items = sorted(
            self.cache.items(), 
            key=lambda x: x[1]['last_accessed']
        )
        
        # Remove oldest 20% of items
        items_to_remove = max(1, int(len(self.cache) * 0.2))
        for i in range(items_to_remove):
            if i < len(sorted_items):
                del self.cache[sorted_items[i][0]]
                
    def get_stats(self) -> Dict[str, any]:
        """Get cache statistics"""
        total_size = sum(item['size'] for item in self.cache.values() if item['size'])
        total_words = sum(item['word_count'] for item in self.cache.values())
        
        return {
            'cache_entries': len(self.cache),
            'total_size_kb': total_size / 1024 if total_size else 0,
            'total_words': total_words,
            'errors': sum(1 for item in self.cache.values() if item['error'])
        }
        
    def clear(self):
        """Clear the cache"""
        self.cache.clear()

class AnalysisChatWidget(QWidget):
    """Widget for individual analysis conversations with persistent context"""
    
    def __init__(self, parent=None, langchain_service=None, transcripts=None):
        super().__init__(parent)
        self.langchain_service = langchain_service
        self.transcripts = transcripts or {}  # {path: metadata}
        self.debug_mode = False  # Flag to control debug info display
        self.conversation_name = ""
        self.chat_history = []
        
        # Initialize main layout
        self.layout = QVBoxLayout(self)
        
        # Add conversation controls
        self.control_layout = QHBoxLayout()
        
        # Initialize conversation with transcript
        self.initialize_conversation()
        
        # Export button
        export_btn = QPushButton("Export Chat")
        export_btn.setToolTip("Export conversation to markdown file")
        export_btn.clicked.connect(self.export_conversation)
        self.control_layout.addWidget(export_btn)

        # Debug toggle
        debug_btn = QPushButton("🐛 Debug")
        debug_btn.setToolTip("Toggle token usage display")
        debug_btn.setCheckable(True)
        debug_btn.clicked.connect(lambda checked: setattr(self, 'debug_mode', checked))
        self.control_layout.addWidget(debug_btn)
        
        # Clear button
        clear_btn = QPushButton("Clear Chat")
        clear_btn.setToolTip("Clear current conversation history")
        clear_btn.clicked.connect(self.clear_conversation)
        self.control_layout.addWidget(clear_btn)
        
        self.layout.addLayout(self.control_layout)
        
        # Chat history
        self.chat_view = QTextEdit()
        self.chat_view.setReadOnly(True)
        self.layout.addWidget(self.chat_view)
        
        # Input area
        self.input_layout = QHBoxLayout()
        self.input_field = QTextEdit()
        self.input_field.setMaximumHeight(100)
        self.input_field.setPlaceholderText(
            "Ask questions about the loaded transcripts...\n"
            "For example: 'What were the key decisions made?'"
        )
        self.input_layout.addWidget(self.input_field)
        
        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.send_message)
        self.input_layout.addWidget(send_btn)
        
        self.layout.addLayout(self.input_layout)
        
        # Set minimum height for chat view
        self.chat_view.setMinimumHeight(300)
        
        # Transcript list
        transcript_group = QGroupBox("Transcripts in Analysis")
        transcript_layout = QVBoxLayout(transcript_group)
        self.transcript_list = QListWidget()
        self.transcript_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.transcript_list.itemClicked.connect(self.show_transcript_content)
        self.update_transcript_list()
        transcript_layout.addWidget(self.transcript_list)
        self.layout.addWidget(transcript_group)

    def export_conversation(self):
        """Export the conversation history to a markdown file"""
        if not self.chat_history:
            QMessageBox.warning(self, "Warning", "No conversation to export")
            return
            
        try:
            # Create exports directory if it doesn't exist
            os.makedirs("exports", exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = self.conversation_name or "conversation"
            filename = f"exports/{name}_{timestamp}.md"
            
            with open(filename, 'w', encoding='utf-8') as f:
                # Write header with metadata
                f.write(f"# {name}\n\n")
                f.write(f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Write transcript sources with more details
                f.write("## Analyzed Transcripts\n\n")
                for path, meta in self.transcripts.items():
                    # Get file stats if available
                    file_info = ""
                    if os.path.exists(path):
                        size_kb = os.path.getsize(path) / 1024
                        mod_time = datetime.fromtimestamp(os.path.getmtime(path))
                        file_info = f" ({size_kb:.1f} KB, modified {mod_time.strftime('%Y-%m-%d')})"
                    
                    f.write(f"- {meta['name']}{file_info}\n")
                f.write("\n")
                
                # Write conversation with better formatting
                f.write("## Conversation\n\n")
                for msg in self.chat_history:
                    if msg['role'] == 'system':
                        # Format system messages differently
                        f.write(f"> *{msg['content']}*\n\n")
                    else:
                        role = "**Assistant**" if msg['role'] == 'assistant' else "**You**"
                        f.write(f"### {role}:\n{msg['content']}\n\n")
                
                # Add footer with application info
                f.write("---\n")
                f.write("Generated with Meeting Assistant\n")
                    
            # Show success message with option to open the file
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Export Successful")
            msg_box.setText(f"Conversation exported to:\n{filename}")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Open | QMessageBox.StandardButton.Ok)
            msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
            
            if msg_box.exec() == QMessageBox.StandardButton.Open:
                # Open the file with the default application
                import platform
                if platform.system() == "Windows":
                    os.startfile(filename)
                elif platform.system() == "Darwin":  # macOS
                    import subprocess
                    subprocess.call(["open", filename])
                else:  # Linux
                    import subprocess
                    subprocess.call(["xdg-open", filename])
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export conversation: {str(e)}")
        
    def handle_search(self, text: str):
        """Search across all loaded transcripts"""
        self.search_results.clear()
        if not text.strip():
            return
            
        # Parse search terms, handling quoted phrases
        terms = []
        current_term = []
        in_quotes = False
        
        for char in text:
            if char == '"':
                in_quotes = not in_quotes
                if not in_quotes and current_term:
                    terms.append(''.join(current_term).strip().lower())
                    current_term = []
            elif char == '+' and not in_quotes:
                if current_term:
                    terms.append(''.join(current_term).strip().lower())
                    current_term = []
            else:
                current_term.append(char)
                
        if current_term:
            terms.append(''.join(current_term).strip().lower())
            
        # Remove empty terms
        terms = [t for t in terms if t]
        
        # Get parent DeepAnalysisTab
        parent = self.parent()
        while parent and not isinstance(parent, DeepAnalysisTab):
            parent = parent.parent()
            
        if not parent:
            return
            
        # Search through transcripts
        for file_path in parent.selected_transcripts:
            transcript = self.transcript_cache.get_transcript(file_path)
            
            # Search line by line
            for line_num, line in enumerate(transcript.split('\n'), 1):
                if all(term in line.lower() for term in terms):
                    item_text = f"{os.path.basename(file_path)} - Line {line_num}: {line.strip()}"
                    self.search_results.addItem(item_text)
                    
    def on_result_clicked(self, item):
        """Handle search result click"""
        # Extract file and line info
        text = item.text()
        file_name = text.split(' - ')[0]
        
        # Highlight in transcript list
        parent = self.parent()
        while parent and not isinstance(parent, DeepAnalysisTab):
            parent = parent.parent()
            
        if parent:
            for i in range(parent.transcript_list.count()):
                if parent.transcript_list.item(i).text() == file_name:
                    parent.transcript_list.setCurrentRow(i)
                    break
        
    def update_transcript_list(self):
        """Update the list of transcripts being used in this analysis"""
        self.transcript_list.clear()
        for path, meta in self.transcripts.items():
            item = QListWidgetItem(f"📄 {meta['name']}")
            item.setToolTip(f"Full path: {path}")
            self.transcript_list.addItem(item)
            
    def show_transcript_content(self, item):
        """Show the content of the selected transcript"""
        file_name = item.text().replace("📄 ", "")
        matching_paths = [
            path for path, meta in self.transcripts.items()
            if meta['name'] == file_name
        ]
        if matching_paths:
            try:
                with open(matching_paths[0], 'r', encoding='utf-8') as f:
                    content = f.read()
                # Show in a new dialog or panel
                self.show_transcript_dialog(file_name, content)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load transcript: {str(e)}")
                
    def save_conversation_state(self):
        """Save current conversation state"""
        state = {
            'transcripts': self.transcripts,
            'chat_history': self.chat_history,
            'conversation_name': self.conversation_name
        }
        return state

    def show_transcript_dialog(self, title: str, content: str):
        """Show transcript content in a dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Transcript: {title}")
        dialog.setModal(True)
        dialog.resize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Add text viewer
        text_view = QTextEdit()
        text_view.setReadOnly(True)
        text_view.setText(content)
        layout.addWidget(text_view)
        
        # Add close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.exec()
        
    def initialize_conversation(self):
        """Load transcript and start conversation"""
        if not self.langchain_service:
            return
            
        # Combine all transcripts
        all_content = []
        transcript_names = []
        
        for path, meta in self.transcripts.items():
            try:
                transcript_path = path
                if not path.endswith('_transcript.txt'):
                    transcript_path = path.replace('.mp3', '_transcript.txt')
                
                if os.path.exists(transcript_path):
                    with open(transcript_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        all_content.append(content)
                        transcript_names.append(meta['name'])
            except Exception as e:
                print(f"Error loading transcript {path}: {e}")
        
        if not all_content:
            self.chat_view.append("System: No transcript content found. Please add transcripts to analyze.")
            return
            
        # Create a more informative initial prompt
        transcript_list = "\n".join([f"- {name}" for name in transcript_names])
        word_count = sum(len(content.split()) for content in all_content)
        
        # Send initial context to LangChain
        initial_prompt = {
            "name": "Analysis Setup",
            "user": f"""I'm providing {len(all_content)} transcript(s) to analyze:
{transcript_list}

Total word count: approximately {word_count} words.

Here is the full content to keep in context for our conversation:

{' '.join(all_content)}

Please confirm you have received the transcript(s) and provide a brief summary of what they contain.
"""
        }
        
        try:
            response = self.langchain_service.process_chunk("", initial_prompt)
            self.chat_history.append({"role": "system", "content": "Analysis session started with the following transcripts:"})
            self.chat_history.append({"role": "system", "content": transcript_list})
            self.chat_history.append({"role": "assistant", "content": response})
            
            # Update the chat view
            self.chat_view.append("System: Analysis session started with the following transcripts:")
            for name in transcript_names:
                self.chat_view.append(f"System: - {name}")
            self.chat_view.append(f"\nAssistant: {response}\n")
        except Exception as e:
            error_msg = f"Error initializing conversation: {str(e)}"
            self.chat_view.append(f"System Error: {error_msg}")
            print(error_msg)

    def restore_conversation_state(self, state):
        """Restore conversation from saved state"""
        self.transcripts = state.get('transcripts', {})
        self.chat_history = state.get('chat_history', [])
        self.conversation_name = state.get('conversation_name', '')
        self.build_initial_context()  # Changed to match new method name
        self.update_transcript_list()
        
        # Restore chat view
        self.chat_view.clear()
        for msg in self.chat_history:
            prefix = "Assistant: " if msg['role'] == 'assistant' else "You: "
            self.chat_view.append(f"{prefix}{msg['content']}\n")
            
    def clear_conversation(self):
        """Clear the current conversation while maintaining context"""
        # Clear UI
        self.chat_view.clear()
        self.chat_history.clear()
        
        # Reset LangChain memory
        if self.langchain_service:
            self.langchain_service.reset_memory()
        
        # Rebuild initial context
        self.build_initial_context()
        
        # Add system message indicating reset
        self.chat_view.append("Conversation reset. Context and transcripts maintained.")
        
    def send_message(self):
        """Send user question without resending transcript"""
        text = self.input_field.toPlainText().strip()
        if not text:
            return
            
        # Add user message to chat history and view
        self.chat_history.append({"role": "user", "content": text})
        self.chat_view.append(f"You: {text}")
        self.input_field.clear()
        
        if not self.langchain_service:
            error_msg = "Error: LangChain service not initialized"
            self.chat_view.append(error_msg)
            self.chat_history.append({"role": "system", "content": error_msg})
            return
            
        # Show typing indicator
        typing_indicator = "Assistant is thinking..."
        self.chat_view.append(typing_indicator)
        cursor = self.chat_view.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.chat_view.setTextCursor(cursor)
        QApplication.processEvents()  # Update UI
            
        try:
            # Just send the question - transcript is already in context
            template = {
                "name": "Deep Analysis",
                "user": text
            }
            
            # Process with token tracking
            with get_openai_callback() as cb:
                response = self.langchain_service.process_chunk("", template)
                
                # Remove typing indicator (move cursor to start of indicator and delete it)
                cursor = self.chat_view.textCursor()
                cursor.movePosition(cursor.MoveOperation.End)
                for _ in range(len(typing_indicator) + 1):  # +1 for newline
                    cursor.deletePreviousChar()
                
                # Add response to chat history
                self.chat_history.append({"role": "assistant", "content": response})
                
                # Only show token info if debug mode is enabled in settings
                debug_mode = self.langchain_service.settings_manager.get_setting('debug_mode', 'false').lower() == 'true'
                if debug_mode:
                    token_info = (
                        "\n---\n"
                        f"📊 Token Usage\n"
                        f"• Total: {cb.total_tokens:,}\n"
                        f"• Prompt: {cb.prompt_tokens:,}\n"
                        f"• Response: {cb.completion_tokens:,}\n"
                        "---"
                    )
                    self.chat_view.append(f"\nAssistant: {response}{token_info}\n")
                else:
                    self.chat_view.append(f"\nAssistant: {response}\n")
                
                # Scroll to the bottom
                cursor.movePosition(cursor.MoveOperation.End)
                self.chat_view.setTextCursor(cursor)
            
        except Exception as e:
            # Remove typing indicator
            cursor = self.chat_view.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            for _ in range(len(typing_indicator) + 1):  # +1 for newline
                cursor.deletePreviousChar()
                
            error_msg = f"Error: {str(e)}"
            self.chat_view.append(error_msg)
            self.chat_history.append({"role": "system", "content": error_msg})

class VisualizationsTab(QWidget):
    """Tab for visualizing transcript data with various charts and graphs"""
    
    def __init__(self, parent=None, transcript_insights_tab=None):
        super().__init__(parent)
        self.parent_tab = parent
        self.transcript_insights_tab = transcript_insights_tab
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Info label at the top
        info_label = QLabel("Select transcripts in the 'Transcript Insights' tab to visualize them here.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("font-style: italic; color: gray;")
        layout.addWidget(info_label)
        
        # Options panel
        options_group = QGroupBox("Visualization Options")
        options_layout = QVBoxLayout(options_group)
        
        # Visualization type selector
        viz_selector_layout = QHBoxLayout()
        viz_selector_layout.addWidget(QLabel("Visualization Type:"))
        
        self.viz_type_combo = QComboBox()
        self.viz_type_combo.addItem("Word Cloud", "word_cloud")
        self.viz_type_combo.addItem("Top Words", "top_words")
        self.viz_type_combo.addItem("Topic Distribution", "topic_distribution")
        self.viz_type_combo.addItem("Speaker Analysis", "speaker_analysis")
        self.viz_type_combo.addItem("Sentiment Timeline", "sentiment_timeline")
        self.viz_type_combo.currentIndexChanged.connect(self.update_visualization)
        viz_selector_layout.addWidget(self.viz_type_combo)
        
        options_layout.addLayout(viz_selector_layout)
        
        # Additional options based on visualization type
        self.options_stack = QStackedWidget()
        
        # Word cloud options
        word_cloud_options = QWidget()
        wc_layout = QHBoxLayout(word_cloud_options)
        
        wc_layout.addWidget(QLabel("Max Words:"))
        self.max_words_input = QComboBox()
        self.max_words_input.addItems(["50", "100", "200", "500"])
        self.max_words_input.setCurrentText("100")
        wc_layout.addWidget(self.max_words_input)
        
        wc_layout.addWidget(QLabel("Min Word Length:"))
        self.min_length_input = QComboBox()
        self.min_length_input.addItems(["2", "3", "4", "5"])
        self.min_length_input.setCurrentText("3")
        wc_layout.addWidget(self.min_length_input)
        
        self.exclude_common_words = QCheckBox("Exclude Common Words")
        self.exclude_common_words.setChecked(True)
        wc_layout.addWidget(self.exclude_common_words)
        
        wc_layout.addStretch()
        self.options_stack.addWidget(word_cloud_options)
        
        # Top words options
        top_words_options = QWidget()
        tw_layout = QHBoxLayout(top_words_options)
        
        tw_layout.addWidget(QLabel("Number of Words:"))
        self.top_n_input = QComboBox()
        self.top_n_input.addItems(["10", "20", "30", "50"])
        self.top_n_input.setCurrentText("20")
        tw_layout.addWidget(self.top_n_input)
        
        self.group_by_speaker = QCheckBox("Group by Speaker")
        tw_layout.addWidget(self.group_by_speaker)
        
        tw_layout.addStretch()
        self.options_stack.addWidget(top_words_options)
        
        # Topic distribution options
        topic_options = QWidget()
        topic_layout = QHBoxLayout(topic_options)
        
        topic_layout.addWidget(QLabel("Number of Topics:"))
        self.num_topics_input = QComboBox()
        self.num_topics_input.addItems(["3", "5", "7", "10"])
        self.num_topics_input.setCurrentText("5")
        topic_layout.addWidget(self.num_topics_input)
        
        topic_layout.addStretch()
        self.options_stack.addWidget(topic_options)
        
        # Speaker analysis options
        speaker_options = QWidget()
        speaker_layout = QHBoxLayout(speaker_options)
        
        speaker_layout.addWidget(QLabel("Analysis Type:"))
        self.speaker_analysis_type = QComboBox()
        self.speaker_analysis_type.addItems(["Speaking Time", "Word Count", "Interaction Pattern"])
        speaker_layout.addWidget(self.speaker_analysis_type)
        
        speaker_layout.addStretch()
        self.options_stack.addWidget(speaker_options)
        
        # Sentiment timeline options
        sentiment_options = QWidget()
        sentiment_layout = QHBoxLayout(sentiment_options)
        
        sentiment_layout.addWidget(QLabel("Segment Size:"))
        self.segment_size = QComboBox()
        self.segment_size.addItems(["By Speaker", "By Paragraph", "Equal Chunks"])
        sentiment_layout.addWidget(self.segment_size)
        
        sentiment_layout.addStretch()
        self.options_stack.addWidget(sentiment_options)
        
        # Add options stack to layout
        options_layout.addWidget(self.options_stack)
        
        # Add generate button
        generate_btn = QPushButton("Generate Visualization")
        generate_btn.clicked.connect(self.generate_visualization)
        options_layout.addWidget(generate_btn)
        
        layout.addWidget(options_group)
        
        # Visualization container
        self.visualization_container = QStackedWidget()
        layout.addWidget(self.visualization_container, stretch=1)
        
        # Add word cloud widget
        self.word_cloud_widget = WordCloudWidget()
        self.visualization_container.addWidget(self.word_cloud_widget)
        
        # Add top words widget
        self.top_words_widget = TopWordsWidget()
        self.visualization_container.addWidget(self.top_words_widget)
        
        # Add placeholder widgets for other visualization types
        for viz_type in ["topic_distribution", "speaker_analysis", "sentiment_timeline"]:
            placeholder = QLabel(f"{viz_type.replace('_', ' ').title()} visualization will appear here")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setStyleSheet("font-style: italic; color: gray; background-color: #f0f0f0; padding: 20px;")
            self.visualization_container.addWidget(placeholder)
        
    def update_visualization(self):
        """Update the visualization based on the selected type"""
        viz_type = self.viz_type_combo.currentData()
        
        # Update options stack
        if viz_type == "word_cloud":
            self.options_stack.setCurrentIndex(0)
            self.visualization_container.setCurrentWidget(self.word_cloud_widget)
        elif viz_type == "top_words":
            self.options_stack.setCurrentIndex(1)
            self.visualization_container.setCurrentWidget(self.top_words_widget)
        elif viz_type == "topic_distribution":
            self.options_stack.setCurrentIndex(2)
            self.visualization_container.setCurrentIndex(2)
        elif viz_type == "speaker_analysis":
            self.options_stack.setCurrentIndex(3)
            self.visualization_container.setCurrentIndex(3)
        elif viz_type == "sentiment_timeline":
            self.options_stack.setCurrentIndex(4)
            self.visualization_container.setCurrentIndex(4)
    
    def generate_visualization(self):
        """Generate the selected visualization for the selected transcripts"""
        # Check if we have a reference to the transcript insights tab
        if not self.transcript_insights_tab:
            QMessageBox.warning(self, "Error", "Cannot access transcript selection")
            return
            
        # Get selected transcripts
        selected_transcripts = self.transcript_insights_tab.selected_transcripts
        if not selected_transcripts:
            QMessageBox.warning(self, "No Transcripts", "Please select transcripts in the 'Transcript Insights' tab first")
            return
            
        # Show processing indicator
        self.setCursor(Qt.CursorShape.WaitCursor)
        processing_label = QLabel("Processing transcripts...", self)
        processing_label.setStyleSheet("""
            background-color: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 20px;
            border-radius: 10px;
            font-size: 16px;
        """)
        processing_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        processing_label.resize(300, 100)
        processing_label.move(
            (self.width() - processing_label.width()) // 2,
            (self.height() - processing_label.height()) // 2
        )
        processing_label.show()
        QApplication.processEvents()
        
        try:
            # Get selected visualization type
            viz_type = self.viz_type_combo.currentData()
            
            # Generate the appropriate visualization
            if viz_type == "word_cloud":
                # Get options
                max_words = int(self.max_words_input.currentText())
                min_length = int(self.min_length_input.currentText())
                exclude_common = self.exclude_common_words.isChecked()
                
                # Configure word cloud widget
                self.word_cloud_widget.set_options(
                    max_words=max_words,
                    min_word_length=min_length,
                    exclude_common_words=exclude_common
                )
                
                # Process and generate
                if self.word_cloud_widget.process_transcripts(selected_transcripts):
                    self.word_cloud_widget.generate_wordcloud()
                else:
                    QMessageBox.warning(self, "Processing Error", "Failed to process transcripts for word cloud")
                    
            elif viz_type == "top_words":
                # Get options
                top_n = int(self.top_n_input.currentText())
                group_by_speaker = self.group_by_speaker.isChecked()
                
                # Process transcripts with word cloud widget to get word counts
                if self.word_cloud_widget.process_transcripts(selected_transcripts):
                    # Configure top words widget
                    self.top_words_widget.set_options(
                        top_n=top_n,
                        group_by_speaker=group_by_speaker
                    )
                    
                    # Pass word counts to top words widget
                    self.top_words_widget.set_word_counts(self.word_cloud_widget.word_counts)
                    self.top_words_widget.generate_chart()
                else:
                    QMessageBox.warning(self, "Processing Error", "Failed to process transcripts for top words chart")
                    
            elif viz_type == "topic_distribution":
                # Get options
                num_topics = int(self.num_topics_input.currentText())
                
                # Show placeholder message for now
                QMessageBox.information(
                    self, 
                    "Topic Distribution", 
                    f"Topic distribution visualization with {num_topics} topics is not yet implemented."
                )
                
            elif viz_type == "speaker_analysis":
                # Get options
                analysis_type = self.speaker_analysis_type.currentText()
                
                # Show placeholder message for now
                QMessageBox.information(
                    self, 
                    "Speaker Analysis", 
                    f"Speaker analysis visualization for {analysis_type} is not yet implemented."
                )
                
            elif viz_type == "sentiment_timeline":
                # Get options
                segment_type = self.segment_size.currentText()
                
                # Show placeholder message for now
                QMessageBox.information(
                    self, 
                    "Sentiment Timeline", 
                    f"Sentiment timeline visualization with {segment_type} segments is not yet implemented."
                )
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate visualization: {str(e)}")
            
        finally:
            # Remove processing indicator
            processing_label.hide()
            processing_label.deleteLater()
            self.setCursor(Qt.CursorShape.ArrowCursor)


class TranscriptInsightsTab(QWidget):
    """Tab for analyzing transcript insights with visualizations"""
    
    def __init__(self, parent=None, transcripts=None):
        super().__init__(parent)
        self.parent_tab = parent
        self.transcripts = transcripts or {}  # {file_path: metadata}
        self.selected_transcripts = {}  # {file_path: metadata}
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Transcript selection section
        selection_group = QGroupBox("Transcript Selection")
        selection_layout = QVBoxLayout(selection_group)
        
        # Selection controls
        controls_layout = QHBoxLayout()
        
        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.clicked.connect(self.select_all_transcripts)
        controls_layout.addWidget(self.select_all_btn)
        
        self.clear_selection_btn = QPushButton("Clear Selection")
        self.clear_selection_btn.clicked.connect(self.clear_selection)
        controls_layout.addWidget(self.clear_selection_btn)
        
        self.selection_counter = QLabel("0/0 transcripts selected")
        controls_layout.addWidget(self.selection_counter, 1)  # Stretch to fill space
        
        selection_layout.addLayout(controls_layout)
        
        # Transcript list with checkboxes
        self.transcript_list = QListWidget()
        self.transcript_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.transcript_list.itemChanged.connect(self.on_item_checked)
        selection_layout.addWidget(self.transcript_list)
        
        layout.addWidget(selection_group)
        
        # Instructions for visualizations
        instructions = QLabel(
            "Select transcripts above to analyze them. "
            "Then switch to the 'Visualizations' tab to see visual representations of the data."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("font-style: italic; color: gray;")
        layout.addWidget(instructions)
        
    def update_transcript_list(self):
        """Update the list of available transcripts"""
        self.transcript_list.clear()
        self.selected_transcripts.clear()
        
        # Get transcripts from parent DeepAnalysisTab
        if self.parent_tab and hasattr(self.parent_tab, 'selected_transcripts'):
            self.transcripts = self.parent_tab.selected_transcripts
        
        for path, meta in self.transcripts.items():
            item = QListWidgetItem(meta['name'])
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            item.setData(Qt.ItemDataRole.UserRole, path)  # Store file path
            self.transcript_list.addItem(item)
        
        self.update_selection_counter()
    
    def on_item_checked(self, item):
        """Handle checkbox state changes"""
        path = item.data(Qt.ItemDataRole.UserRole)
        if item.checkState() == Qt.CheckState.Checked:
            self.selected_transcripts[path] = self.transcripts[path]
        else:
            if path in self.selected_transcripts:
                del self.selected_transcripts[path]
        
        self.update_selection_counter()
    
    def select_all_transcripts(self):
        """Select all transcripts in the list"""
        for i in range(self.transcript_list.count()):
            item = self.transcript_list.item(i)
            item.setCheckState(Qt.CheckState.Checked)
            path = item.data(Qt.ItemDataRole.UserRole)
            self.selected_transcripts[path] = self.transcripts[path]
        
        self.update_selection_counter()
    
    def clear_selection(self):
        """Clear all transcript selections"""
        for i in range(self.transcript_list.count()):
            item = self.transcript_list.item(i)
            item.setCheckState(Qt.CheckState.Unchecked)
        
        self.selected_transcripts.clear()
        self.update_selection_counter()
    
    def update_selection_counter(self):
        """Update the selection counter label"""
        total = self.transcript_list.count()
        selected = len(self.selected_transcripts)
        self.selection_counter.setText(f"{selected}/{total} transcripts selected")


class DeepAnalysisTab(QWidget):
    """Tab for analyzing multiple transcripts together"""
    
    transcripts_selected = pyqtSignal(list)  # Signal when transcripts are selected
    
    def __init__(self, parent=None, langchain_service=None):
        super().__init__(parent)
        self.langchain_service = langchain_service
        self.selected_transcripts = {}  # {file_path: metadata}
        
        # Connect signal to update transcript insights tab
        self.transcripts_selected.connect(self.on_transcripts_selected)
        
        # Add minimal stylesheet for borders and spacing
        self.setStyleSheet("""
            QListWidget, QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
            }
            
            QPushButton {
                padding: 6px 12px;
                border-radius: 4px;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 4px;
                margin-top: 1ex;
                padding: 10px;
            }
            
            QSplitter::handle {
                background: #cccccc;
            }
        """)
        
        # Add timer for updating highlight
        self.highlight_timer = QTimer()
        self.highlight_timer.setInterval(100)  # Check every 100ms
        self.highlight_timer.timeout.connect(self.update_highlight)
        
        self.init_ui()
        
        if not langchain_service:
            print("Warning: No LangChain service provided to DeepAnalysisTab")
        
    def on_transcripts_selected(self, transcript_paths):
        """Handle transcript selection changes"""
        # Update the transcript insights tab
        if hasattr(self, 'transcript_insights_tab'):
            self.transcript_insights_tab.update_transcript_list()
            
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)  # Add margins
        layout.setSpacing(10)  # Add spacing between widgets
        
        # Create main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background: #ccc;
                width: 2px;
            }
        """)
        
        # Left panel with vertical splitter
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create vertical splitter for transcript list, player, and viewer
        vertical_splitter = QSplitter(Qt.Orientation.Vertical)
        vertical_splitter.setHandleWidth(2)
        
        # Top section - Transcript list
        transcript_widget = QWidget()
        transcript_layout = QVBoxLayout(transcript_widget)
        transcript_layout.setContentsMargins(5, 5, 5, 5)
        
        list_header = QHBoxLayout()
        list_header.addWidget(QLabel("Selected Transcripts:"))
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_selected_transcripts)
        list_header.addWidget(remove_btn)
        transcript_layout.addLayout(list_header)
        
        self.transcript_list = QListWidget()
        self.transcript_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.transcript_list.itemSelectionChanged.connect(self.on_transcript_selected)
        self.transcript_list.setMinimumHeight(100)
        self.transcript_list.setMaximumHeight(200)
        transcript_layout.addWidget(self.transcript_list)
        
        vertical_splitter.addWidget(transcript_widget)
        
        # Middle section - Media player and bookmarks
        player_widget = QWidget()
        player_layout = QVBoxLayout(player_widget)
        player_layout.setContentsMargins(5, 5, 5, 5)
        
        # Media player and bookmark manager in same row
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)  # Increase spacing
        controls_layout.setContentsMargins(5, 5, 5, 5)  # Give more breathing room
        
        # Media player with height for waveform visualization
        self.media_player = MediaPlayerWidget(self)
        self.media_player.setMinimumHeight(150)  # Increased height for waveform
        controls_layout.addWidget(self.media_player, stretch=3)  # Give more space to media player
        
        # Bookmark manager
        self.bookmark_manager = BookmarkManager(self)
        self.bookmark_manager.setMinimumHeight(70)  # Match media player height
        self.bookmark_manager.seek_to_timestamp.connect(
            lambda ts: self.media_player.seek_to_timestamp(ts))
        controls_layout.addWidget(self.bookmark_manager, stretch=1)
        
        player_layout.addLayout(controls_layout)
        
        
        vertical_splitter.addWidget(player_widget)
        
        # Bottom section - Transcript viewer with search
        viewer_widget = QWidget()
        viewer_layout = QVBoxLayout(viewer_widget)
        viewer_layout.setContentsMargins(5, 5, 5, 5)
        
        # Search controls with shorter search box
        search_layout = QHBoxLayout()
        search_layout.setSpacing(4)
        
        self.transcript_search = QLineEdit()
        self.transcript_search.setPlaceholderText("Search...")  # Shorter placeholder
        self.transcript_search.setMaximumWidth(200)  # Limit width of search box
        self.transcript_search.textChanged.connect(self.highlight_transcript_search)
        search_layout.addWidget(self.transcript_search)
        
        # Navigation buttons with proper emoji sizing
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(2)
        self.prev_match_btn = QPushButton("↑")  # Changed from ⬆ to ↑ (simpler arrow)
        self.prev_match_btn.setFixedSize(24, 24)  # Slightly smaller, square size
        self.prev_match_btn.setToolTip("Previous Match")
        self.prev_match_btn.clicked.connect(lambda: self.navigate_search(-1))
        self.next_match_btn = QPushButton("↓")  # Changed from ⬇ to ↓ (simpler arrow)
        self.next_match_btn.setFixedSize(24, 24)  # Slightly smaller, square size
        self.next_match_btn.setToolTip("Next Match")
        self.next_match_btn.clicked.connect(lambda: self.navigate_search(1))

        # Set font size for arrows to ensure they're centered
        arrow_style = """
            QPushButton {
                font-size: 14px;
                padding: 0px;
                margin: 0px;
            }
        """
        self.prev_match_btn.setStyleSheet(arrow_style)
        self.next_match_btn.setStyleSheet(arrow_style)

        nav_layout.addWidget(self.prev_match_btn)
        nav_layout.addWidget(self.next_match_btn)
        search_layout.addLayout(nav_layout)
        
        # Replace Auto-Scroll text with lock icon
        self.auto_scroll_btn = QPushButton("🔒")  # Lock emoji
        self.auto_scroll_btn.setCheckable(True)
        self.auto_scroll_btn.setFixedSize(24, 24)  # Match size with arrow buttons
        self.auto_scroll_btn.setToolTip("Auto-scroll to follow playback")
        # Center the lock icon
        self.auto_scroll_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 0px;
                margin: 0px;
            }
        """)
        search_layout.addWidget(self.auto_scroll_btn)
        
        viewer_layout.addLayout(search_layout)
        
        # Transcript viewer
        self.transcript_viewer = QTextEdit()
        self.transcript_viewer.setReadOnly(True)
        self.transcript_viewer.mouseDoubleClickEvent = self.on_transcript_click
        viewer_layout.addWidget(self.transcript_viewer)
        
        vertical_splitter.addWidget(viewer_widget)
        
        # Add vertical splitter to left panel
        left_layout.addWidget(vertical_splitter)
        
        # Set initial sizes for vertical splitter (20% list, 25% player, 55% viewer)
        vertical_splitter.setSizes([200, 250, 550])
        
        left_panel.setLayout(left_layout)
        
        # Right panel - Analysis tabs
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Analysis tabs
        self.analysis_tabs = QTabWidget()
        self.analysis_tabs.setTabsClosable(True)
        self.analysis_tabs.tabCloseRequested.connect(self.close_analysis_tab)
        
        # Add "New Analysis" button
        new_analysis_btn = QPushButton("New Analysis")
        new_analysis_btn.clicked.connect(self.create_new_analysis)
        right_layout.addWidget(new_analysis_btn)
        right_layout.addWidget(self.analysis_tabs)
        
        # Add Transcript Insights tab
        self.transcript_insights_tab = TranscriptInsightsTab(self)
        self.analysis_tabs.addTab(self.transcript_insights_tab, "Transcript Insights")
        
        # Add Visualizations tab
        self.visualizations_tab = VisualizationsTab(self, self.transcript_insights_tab)
        self.analysis_tabs.addTab(self.visualizations_tab, "Visualizations")
        
        right_panel.setLayout(right_layout)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        # Configure splitter
        splitter.setHandleWidth(4)  # Make handle easier to grab
        splitter.setChildrenCollapsible(False)  # Prevent panels from being collapsed to 0
        splitter.setStyleSheet("""
            QSplitter::handle {
                background: #666666;
                border: 1px solid #777777;
                border-radius: 1px;
                margin: 1px;
            }
            QSplitter::handle:hover {
                background: #888888;
            }
        """)
        
        # Add splitter to main layout
        layout.addWidget(splitter)
        
        # Set initial splitter sizes (40% left, 60% right)
        splitter.setSizes([400, 600])
        
    def add_transcripts(self, file_paths):
        """Add transcripts to analysis"""
        added_count = 0
        for path in file_paths:
            if path not in self.selected_transcripts:
                self.selected_transcripts[path] = {
                    'name': os.path.basename(path),
                    'date': None  # TODO: Get from file handler
                }
                item = QListWidgetItem(os.path.basename(path))
                item.setToolTip(f"Added to analysis\nFull path: {path}")
                self.transcript_list.addItem(item)
                added_count += 1
        
        # Show feedback message
        if added_count > 0:
            QMessageBox.information(
                self,
                "Transcripts Added",
                f"Added {added_count} new transcript{'s' if added_count != 1 else ''} to analysis.\n"
                "You can now create a new analysis tab to start working with these transcripts."
            )
        
        # Emit signal with updated transcript list
        self.transcripts_selected.emit(list(self.selected_transcripts.keys()))
        
        # Update the transcript insights tab
        if hasattr(self, 'transcript_insights_tab'):
            self.transcript_insights_tab.update_transcript_list()
        
    def create_new_analysis(self):
        """Create new analysis tab"""
        if not self.selected_transcripts:
            QMessageBox.warning(
                self, 
                "No Transcripts Selected",
                "Please select transcripts for analysis first.\n\n"
                "1. Use the calendar or file browser to select transcripts\n"
                "2. Selected transcripts will appear in the left panel\n"
                "3. Create a new analysis to start analyzing them together"
            )
            return
            
        name, ok = QInputDialog.getText(
            self, 
            "New Analysis", 
            "Give your analysis a descriptive name (e.g., 'April Meeting Summary' or 'Q1 Action Items'):"
        )
        if ok and name:
            # Create new chat widget with selected transcripts
            chat_widget = AnalysisChatWidget(
                self, 
                self.langchain_service,
                self.selected_transcripts
            )
            chat_widget.conversation_name = name
            self.analysis_tabs.addTab(chat_widget, name)
            self.analysis_tabs.setCurrentWidget(chat_widget)
            
            
    def close_analysis_tab(self, index):
        """Close an analysis tab"""
        # Don't close the Transcript Insights or Visualizations tabs
        tab_widget = self.analysis_tabs.widget(index)
        if isinstance(tab_widget, (TranscriptInsightsTab, VisualizationsTab)):
            return
            
        if self.analysis_tabs.count() > 0:
            self.highlight_timer.stop()
            self.analysis_tabs.removeTab(index)
            
    def remove_selected_transcripts(self):
        """Remove selected transcripts from analysis"""
        selected_items = self.transcript_list.selectedItems()
        if not selected_items:
            return
            
        for item in selected_items:
            file_name = item.text()
            # Find and remove from selected_transcripts
            matching_paths = [
                path for path, meta in self.selected_transcripts.items()
                if meta['name'] == file_name
            ]
            for path in matching_paths:
                del self.selected_transcripts[path]
            
            # Remove from list widget
            self.transcript_list.takeItem(self.transcript_list.row(item))
            
        # Clear viewer if no transcripts left
        if self.transcript_list.count() == 0:
            self.transcript_viewer.clear()
            
        # Emit signal with updated transcript list
        self.transcripts_selected.emit(list(self.selected_transcripts.keys()))
        
        # Update the transcript insights tab
        if hasattr(self, 'transcript_insights_tab'):
            self.transcript_insights_tab.update_transcript_list()

    def highlight_transcript_search(self, text: str):
        """Highlight search terms in transcript viewer"""
        cursor = self.transcript_viewer.textCursor()
        # Store current position
        current_pos = cursor.position()
        
        # Clear existing highlighting
        cursor.select(cursor.SelectionType.Document)
        cursor.setCharFormat(QTextCharFormat())
        cursor.clearSelection()
        
        if not text.strip():
            # Restore cursor position
            cursor.setPosition(current_pos)
            self.transcript_viewer.setTextCursor(cursor)
            return
            
        # Parse search terms
        terms = []
        current_term = []
        in_quotes = False
        
        for char in text:
            if char == '"':
                in_quotes = not in_quotes
                if not in_quotes and current_term:
                    terms.append(('quoted', ''.join(current_term)))
                    current_term = []
            elif char == '+' and not in_quotes:
                if current_term:
                    terms.append(('plain', ''.join(current_term).strip()))
                    current_term = []
            else:
                current_term.append(char)
                
        if current_term:
            terms.append(('plain', ''.join(current_term).strip()))
            
        # Create highlight formats
        quoted_format = QTextCharFormat()
        quoted_format.setBackground(QColor("#1565C0"))  # Darker blue for dark mode
        quoted_format.setForeground(QColor("#FFFFFF"))  # White text
        
        plain_format = QTextCharFormat()
        plain_format.setBackground(QColor("#FFA000"))  # Darker yellow for dark mode
        plain_format.setForeground(QColor("#000000"))  # Black text
        
        # Find and highlight all matches
        cursor.setPosition(0)
        for term_type, term in terms:
            if not term.strip():
                continue
                
            format_to_use = quoted_format if term_type == 'quoted' else plain_format
            temp_cursor = self.transcript_viewer.textCursor()
            temp_cursor.setPosition(0)
            
            while True:
                temp_cursor = self.transcript_viewer.document().find(term, temp_cursor)
                if temp_cursor.isNull():
                    break
                temp_cursor.mergeCharFormat(format_to_use)
            
        # Restore cursor position
        cursor.setPosition(current_pos)
        self.transcript_viewer.setTextCursor(cursor)
        
    def navigate_search(self, direction: int):
        """Navigate between search results"""
        text = self.transcript_search.text()
        if not text.strip():
            return
            
        cursor = self.transcript_viewer.textCursor()
        current_pos = cursor.position()
        
        if direction > 0:
            # Search forward
            cursor = self.transcript_viewer.document().find(text, cursor)
            if cursor.isNull():
                # Wrap to start
                cursor = self.transcript_viewer.textCursor()
                cursor.setPosition(0)
                cursor = self.transcript_viewer.document().find(text, cursor)
        else:
            # Search backward
            cursor = self.transcript_viewer.document().find(text, cursor, 
                QTextDocument.FindFlag.FindBackward)
            if cursor.isNull():
                # Wrap to end
                cursor = self.transcript_viewer.textCursor()
                cursor.movePosition(cursor.MoveOperation.End)
                cursor = self.transcript_viewer.document().find(text, cursor,
                    QTextDocument.FindFlag.FindBackward)
                    
        if not cursor.isNull():
            self.transcript_viewer.setTextCursor(cursor)
            
    def on_transcript_selected(self):
        """Handle transcript selection change"""
        selected_items = self.transcript_list.selectedItems()
        if not selected_items:
            return
            
        # Show content of selected transcript
        file_name = selected_items[0].text()
        matching_paths = [
            path for path, meta in self.selected_transcripts.items()
            if meta['name'] == file_name
        ]
        
        if matching_paths:
            file_path = matching_paths[0]
            try:
                # First try direct path if it's already a transcript
                transcript_path = file_path
                if not file_path.endswith('_transcript.txt'):
                    # If not, look for associated transcript
                    transcript_path = file_path.replace('.mp3', '_transcript.txt')
                
                if os.path.exists(transcript_path):
                    # Load transcript
                    with open(transcript_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.transcript_viewer.setText(content)
                    
                    # Load associated audio without autoplay
                    audio_path = transcript_path.replace('_transcript.txt', '.mp3')
                    if os.path.exists(audio_path):
                        self.media_player.load_file(audio_path, autoplay=False)
                        self.highlight_timer.start()
                    else:
                        self.highlight_timer.stop()
                        print(f"No audio file found for: {audio_path}")
                else:
                    self.transcript_viewer.setText("No transcript found for this file")
                    print(f"No transcript found at: {transcript_path}")
                    
            except Exception as e:
                self.transcript_viewer.setText(f"Error loading transcript: {str(e)}")
                print(f"Error loading transcript: {e}")
                
    def update_highlight(self):
        """Update transcript highlighting based on current media position"""
        current_time = self.media_player.player.position() / 1000.0  # Current time in seconds
        
        # Get the full text
        full_text = self.transcript_viewer.toPlainText()
        
        # Find all timestamps in the text
        import re
        timestamps = list(re.finditer(r'\[(\d{2}):(\d{2})\]', full_text))
        
        if not timestamps:
            return
            
        # Clear existing highlights
        cursor = self.transcript_viewer.textCursor()
        cursor.select(cursor.SelectionType.Document)
        cursor.setCharFormat(QTextCharFormat())
        cursor.clearSelection()
        
        # Find next segment
        next_segment_idx = 0
        for i, stamp in enumerate(timestamps):
            minutes = int(stamp.group(1))
            seconds = int(stamp.group(2))
            stamp_time = minutes * 60 + seconds
            
            if stamp_time > current_time:  # Find first timestamp AFTER current time
                next_segment_idx = i
                break
        
        # Create highlight format for next segment
        format_current = QTextCharFormat()
        format_current.setBackground(QColor("#0000FF"))  # Blue highlight
        format_current.setForeground(QColor("#FFFFFF"))  # White text
        
        # Highlight next segment
        next_start = timestamps[next_segment_idx].end()
        next_end = timestamps[next_segment_idx + 1].start() if next_segment_idx + 1 < len(timestamps) else len(full_text)
        cursor.setPosition(next_start)
        cursor.setPosition(next_end, cursor.MoveMode.KeepAnchor)
        cursor.setCharFormat(format_current)
        
        # Auto-scroll if enabled
        if self.auto_scroll_btn.isChecked():
            # Ensure highlighted text is visible
            self.transcript_viewer.setTextCursor(cursor)
            self.transcript_viewer.ensureCursorVisible()

    def on_transcript_click(self, event):
        """Handle clicks in transcript viewer to seek audio"""
        cursor = self.transcript_viewer.cursorForPosition(event.pos())
        # Get approximate position in text as percentage
        total_chars = len(self.transcript_viewer.toPlainText())
        current_pos = cursor.position()
        if total_chars > 0:
            percentage = current_pos / total_chars
            # Seek media player to that percentage of duration
            duration = self.media_player.player.duration()
            seek_pos = int(duration * percentage)
            self.media_player.player.setPosition(seek_pos)
        event.accept()
            
    def send_direct_question(self):
        """Send a direct question to LangChain about the selected transcripts"""
        question = self.direct_chat_input.text().strip()
        if not question:
            return
            
        if not self.selected_transcripts:
            QMessageBox.warning(self, "Warning", "No transcripts selected")
            return
            
        try:
            # Create new analysis tab for the question
            tab_name = f"Q: {question[:30]}..." if len(question) > 30 else f"Q: {question}"
            chat_widget = AnalysisChatWidget(self, self.langchain_service)
            self.analysis_tabs.addTab(chat_widget, tab_name)
            self.analysis_tabs.setCurrentWidget(chat_widget)
            
            # Send the question
            chat_widget.input_field.setPlainText(question)
            chat_widget.send_message()
            self.direct_chat_input.clear()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process question: {str(e)}")
