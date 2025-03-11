from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QSplitter, QListWidget, QFileDialog,
    QMessageBox, QCalendarWidget, QTabWidget,
    QListWidgetItem, QTableWidget, QTableWidgetItem,
    QCheckBox, QMenu, QApplication, QInputDialog,
    QLineEdit
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QRectF, QUrl

from PyQt6.QtGui import (
    QColor, QBrush, QTextCharFormat, 
    QTextFormat
)

# Calendar color constants
CALENDAR_COLORS = {
    "selected_date": QColor(74, 144, 226, 180),  # Bright blue
    "no_transcripts": QColor(135, 206, 250, 160),  # Light blue
    "partial_transcripts": QColor(152, 251, 152, 160),  # Light green
    "all_transcribed": QColor(46, 204, 113, 160)  # Dark green
}
from pathlib import Path
import platform
import subprocess
from .media_player_qt import MediaPlayerWidget
import os
import re
from pathlib import Path

class LibraryTab(QWidget):
    # Add signal definition at class level
    play_audio_signal = pyqtSignal(str)
    
    def __init__(self, parent=None, app=None):
        super().__init__(parent)
        self.app = app
        self.audio_files = {}
        self.current_folder = None
        
        # Initialize media player reference
        self.media_player = None
        
        # Create lists with explicit styling to ensure proper contrast
        self.date_files_list = QListWidget()
        self.all_files_list = QListWidget()
        
        # Apply consistent styling to both list widgets
        list_style = """
            QListWidget {
                background-color: palette(base);
                color: palette(text);
                border: 1px solid palette(mid);
                border-radius: 4px;
                font-size: 10pt;
            }
            QListWidget::item {
                padding: 4px;
                border-bottom: 1px solid rgba(0, 0, 0, 0.05);
                color: palette(text); /* Force text color */
            }
            QListWidget::item:selected {
                background-color: palette(highlight);
                color: palette(highlighted-text);
                font-weight: bold;
            }
            QListWidget::item:hover:!selected {
                background-color: rgba(0, 0, 0, 0.05);
            }
        """
        self.date_files_list.setStyleSheet(list_style)
        self.all_files_list.setStyleSheet(list_style)
        
        # Ensure list widgets use the correct palette
        self.date_files_list.setPalette(QApplication.instance().palette())
        self.all_files_list.setPalette(QApplication.instance().palette())
        
        # Apply consistent styling to both list widgets
        list_style = """
            QListWidget {
                background-color: palette(base);
                color: palette(text);
                border: 1px solid palette(mid);
                border-radius: 4px;
                font-size: 10pt;
            }
            QListWidget::item {
                padding: 4px;
                border-bottom: 1px solid rgba(0, 0, 0, 0.05);
                color: palette(text); /* Force text color */
            }
            QListWidget::item:selected {
                background-color: palette(highlight);
                color: palette(highlighted-text);
                font-weight: bold;
            }
            QListWidget::item:hover:!selected {
                background-color: rgba(0, 0, 0, 0.05);
            }
        """
        self.date_files_list.setStyleSheet(list_style)
        self.all_files_list.setStyleSheet(list_style)
        
        # Add selection count label
        self.selection_label = QLabel("")
        
        # Initialize UI (only once)
        self.init_ui()
        
        # Setup context menu
        self.date_files_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.all_files_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.date_files_list.customContextMenuRequested.connect(self.show_context_menu)
        self.all_files_list.customContextMenuRequested.connect(self.show_context_menu)
        
        # Restore splitter positions after UI is initialized
        QApplication.processEvents()
        self.restore_splitter_state()
        
        # Automatically load files from workspace directory
        self.load_workspace_files()
        
    def play_in_media_player(self):
        """Play selected audio file in the media player"""
        active_list = self.get_active_list()
        current_item = active_list.currentItem()
        
        if not current_item:
            return
            
        file_path = current_item.data(Qt.ItemDataRole.UserRole)
        if not file_path or not os.path.exists(file_path):
            return
            
        # Try to play using media player widget
        if hasattr(self, 'media_player') and self.media_player:
            self.media_player.load_file(file_path)
        else:
            # Emit signal for parent to handle
            self.play_audio_signal.emit(file_path)

    def update_selection_count(self):
        """Update the selection count label"""
        active_list = self.get_active_list()
        count = len(active_list.selectedItems())
        self.selection_label.setText(f"Selected: {count}")

    def filter_files(self, text):
        """
        Filter files using advanced search syntax:
        - Quoted text for exact matches
        - Minus sign to exclude terms
        - Multiple terms for AND logic
        """
        def parse_search_terms(query):
            terms = []
            exclude_terms = []
            
            # Regular expression to handle quoted phrases and individual terms
            pattern = r'"([^"]*)"|\S+'
            matches = re.finditer(pattern, query)
            
            for match in matches:
                term = match.group(1) if match.group(1) else match.group(0)
                if term.startswith('-'):
                    exclude_terms.append(term[1:].lower())
                else:
                    terms.append(term.lower())
                    
            return terms, exclude_terms
        
        def matches_criteria(item_text, include_terms, exclude_terms):
            text_lower = item_text.lower()
            
            # Check excluded terms first
            for term in exclude_terms:
                if term in text_lower:
                    return False
                    
            # Check included terms
            for term in include_terms:
                if term not in text_lower:
                    return False
                    
            return True
        
        # Parse search terms
        include_terms, exclude_terms = parse_search_terms(text)
        
        # Filter both lists
        for list_widget in [self.date_files_list, self.all_files_list]:
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                should_show = matches_criteria(item.text(), include_terms, exclude_terms)
                item.setHidden(not should_show)

    def get_active_list(self) -> QListWidget:
        """Get the currently active list widget"""
        return (self.date_files_list 
                if self.file_tabs.currentIndex() == 0 
                else self.all_files_list)
                
                

    def on_file_double_clicked(self, item):
        """Handle file double click"""
        if item:
            file_path = item.data(Qt.ItemDataRole.UserRole)
            if file_path:
                self.media_player.load_file(file_path)


    def init_ui(self):
        """Initialize the user interface"""
        # Create main layout
        main_layout = QVBoxLayout(self)
        
        # Top controls in single horizontal layout
        folder_controls = QHBoxLayout()
        
        # Controls
        select_btn = QPushButton("📁 Select Folder")
        select_btn.setToolTip("Select additional folder to scan")
        select_btn.clicked.connect(self.select_folder)
        folder_controls.addWidget(select_btn)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setToolTip("Refresh files from all selected folders")
        refresh_btn.clicked.connect(self.refresh_files)
        folder_controls.addWidget(refresh_btn)
        
        self.include_subfolders = QCheckBox("Include Subfolders")
        self.include_subfolders.stateChanged.connect(self.refresh_files)
        folder_controls.addWidget(self.include_subfolders)
        
        self.include_live_folder = QCheckBox("Live Workspace Folder")
        self.include_live_folder.setChecked(True)  # Default checked
        if hasattr(self.app, 'path_manager'):
            live_path = self.app.path_manager.workspace_dir
            self.include_live_folder.setToolTip(f"Live Workspace Path: {live_path}")
        self.include_live_folder.stateChanged.connect(self.on_live_folder_toggled)
        folder_controls.addWidget(self.include_live_folder)
        
        # Simple folder label
        self.folder_label = QLabel("No folder selected")
        self.folder_label.setStyleSheet("""
            QLabel {
                color: #333;
                padding: 2px 8px;
                background: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 3px;
                min-height: 20px;
                max-height: 24px;
                line-height: 20px;
                margin: 0 5px;
            }
        """)
        folder_controls.addWidget(self.folder_label)
        
        folder_controls.addStretch()
        
        main_layout.addLayout(folder_controls)
        
        # Create main splitter and store reference
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.main_splitter)

        # Left side - Calendar
        calendar_widget = QWidget()
        calendar_layout = QVBoxLayout(calendar_widget)
        calendar_layout.setContentsMargins(0, 0, 0, 0)
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.on_date_selected)
        self.calendar.selectionChanged.connect(self.on_date_selected)
        
        # Set calendar style for better visibility
        self.calendar.setStyleSheet("""
            QCalendarWidget QWidget { 
                alternate-background-color: #F0F0F0;
            }
            /* Make day names and numbers clearly visible */
            QCalendarWidget QAbstractItemView:enabled {
                color: #000000;
                background-color: #FFFFFF;
                selection-background-color: #4A90E2;
                selection-color: white;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #FFFFFF;
            }
            QCalendarWidget QToolButton {
                color: #000000;
                background-color: transparent;
            }
            QCalendarWidget QWidget#qt_calendar_dayheader {
                color: #000000;
                font-weight: bold;
                background-color: #FFFFFF;
                border-bottom: 1px solid #C0C0C0;
            }
            QCalendarWidget QWidget#qt_calendar_weekheader {
                color: #000000;
                background-color: #FFFFFF;
            }
        """)
        # Add color legend below calendar
        legend = QWidget()
        legend_layout = QHBoxLayout(legend)
        legend_layout.setContentsMargins(5, 0, 5, 0)
        
        # Add color samples
        colors = [
            ("Selected Date", CALENDAR_COLORS["selected_date"]),
            ("No Transcripts", CALENDAR_COLORS["no_transcripts"]),
            ("Partial Transcripts", CALENDAR_COLORS["partial_transcripts"]),
            ("All Transcribed", CALENDAR_COLORS["all_transcribed"])
        ]
        
        for text, color in colors:
            sample = QLabel()
            sample.setFixedSize(16, 16)
            if text == "Selected Date":
                # Special styling for selected date sample
                sample.setStyleSheet(f"""
                    background-color: {color.name()};
                    border: 1px solid #999;
                    border-radius: 2px;
                    color: white;
                """)
            else:
                sample.setStyleSheet(f"""
                    background-color: rgba({color.red()},{color.green()},{color.blue()},{color.alpha()});
                    border: 1px solid #999;
                    border-radius: 2px;
                """)
            legend_layout.addWidget(sample)
            
            # Add label with specific styling for "Selected Date"
            label = QLabel(text)
            if text == "Selected Date":
                label.setStyleSheet("font-weight: bold;")
            legend_layout.addWidget(label)
            
            if text != colors[-1][0]:  # Don't add spacer after last item
                legend_layout.addSpacing(10)
        
        calendar_layout.addWidget(self.calendar)
        calendar_layout.addWidget(legend)
        self.main_splitter.addWidget(calendar_widget)

        # Right side - Files and Media Player
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Create vertical splitter for media player and file list
        self.right_splitter = QSplitter(Qt.Orientation.Vertical)
        right_layout.addWidget(self.right_splitter)

        # Add media player with debug feedback
        self.media_player = MediaPlayerWidget(self)
        self.right_splitter.addWidget(self.media_player)
        
        # Set initial sizes more aggressively
        self.right_splitter.setSizes([400, 200])  # More space for media player

        # Add filter bar
        filter_layout = QHBoxLayout()
        search_icon = QLabel("🔍")
        filter_layout.addWidget(search_icon)
        
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText('Filter files... (Use " for exact match, - to exclude)')
        self.filter_input.setToolTip(
            "Advanced Search Tips:\n"
            '• Use quotes for exact phrase: "team meeting"\n'
            "• Use - to exclude terms: -test\n"
            '• Combine terms: "weekly sync" -draft\n'
            "• Space between terms = AND\n"
            "• Case insensitive search"
        )
        self.filter_input.textChanged.connect(self.filter_files)
        filter_layout.addWidget(self.filter_input)
        
        clear_btn = QPushButton("✖")
        clear_btn.setFixedWidth(30)
        clear_btn.clicked.connect(lambda: self.filter_input.clear())
        filter_layout.addWidget(clear_btn)
        
        right_layout.addLayout(filter_layout)

        # Add file tabs
        self.file_tabs = QTabWidget()
        self.right_splitter.addWidget(self.file_tabs)

        # Set initial sizes
        self.main_splitter.setSizes([300, 700])  # 30% calendar, 70% right side
        self.right_splitter.setSizes([400, 400])  # Equal space for media player and file list
        
        # Date view tab
        date_tab = QWidget()
        date_layout = QVBoxLayout(date_tab)
        self.date_files_list = QListWidget()
        self.date_files_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.date_files_list.itemDoubleClicked.connect(self.on_file_double_clicked)
        self.date_files_list.itemSelectionChanged.connect(self.update_selection_count)
        date_layout.addWidget(self.date_files_list)
        date_layout.addLayout(self.create_action_buttons())  # Add buttons
        
        self.file_tabs.addTab(date_tab, "By Date")
        
        # All files tab
        all_tab = QWidget()
        all_layout = QVBoxLayout(all_tab)
        self.all_files_list = QListWidget()
        self.all_files_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.all_files_list.itemDoubleClicked.connect(self.on_file_double_clicked)
        self.all_files_list.itemSelectionChanged.connect(self.update_selection_count)
        all_layout.addWidget(self.all_files_list)
        all_layout.addLayout(self.create_action_buttons())  # Add buttons
        self.file_tabs.addTab(all_tab, "All Files")
        
        right_layout.addWidget(self.file_tabs)
        self.main_splitter.addWidget(right_widget)

    def select_folder(self):
        """Select folder and load audio files"""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            # If selecting the workspace folder, just check the box
            workspace_dir = self.app.path_manager.workspace_dir if hasattr(self.app, 'path_manager') else None
            if workspace_dir and folder == workspace_dir:
                self.include_live_folder.setChecked(True)
                return
                
            # Set as current folder
            self.current_folder = folder
            
            # Clear existing files if not showing workspace
            if not self.include_live_folder.isChecked():
                self.audio_files = {}
                self.all_files_list.clear()
                self.date_files_list.clear()
                
            # Load files from the selected folder
            self.load_files_from_folder(folder)

    def refresh_files(self):
        """Refresh file list"""
        # Clear existing data
        self.audio_files = {}
        self.all_files_list.clear()
        self.date_files_list.clear()
        
        # Load files based on selections
        workspace_dir = self.app.path_manager.workspace_dir if hasattr(self.app, 'path_manager') else None
        
        # Load workspace folder if checked
        if self.include_live_folder.isChecked() and workspace_dir:
            self.load_files_from_folder(workspace_dir)
            
        # Load selected folder if it exists and is different from workspace
        if self.current_folder and (not workspace_dir or self.current_folder != workspace_dir):
            self.load_files_from_folder(self.current_folder)
            
        # Update folder label
        self.update_folder_label()

    def update_file_list(self):
        """Update file list based on selected dates"""
        self.file_list.clear()
        
        for date in self.calendar.selectedDates():
            date_str = date.toString("yyyy-MM-dd")
            if date_str in self.audio_files:
                for file_path in self.audio_files[date_str]:
                    # Create list item with status indicators
                    abs_path = str(Path(file_path).resolve())
                    status = self.get_file_status(abs_path)
                    
                    # Create rich text item
                    item = QListWidgetItem()
                    
                    # Set icon based on status
                    icon_text = "📝" if status["has_transcript"] else "🎵"
                    
                    # Set display text
                    display_text = f"{icon_text} {os.path.basename(file_path)}"
                    if status.get("duration"):
                        display_text += f" ({status['duration']})"
                        
                    item.setText(display_text)
                    item.setData(Qt.ItemDataRole.UserRole, abs_path)
                    
                    self.file_list.addItem(item)
                    
    def on_date_selected(self, date=None):
        """Handle date selection in calendar"""
        try:
            # Clear current file list
            self.date_files_list.clear()
            
            # Get selected date
            selected_date = self.calendar.selectedDate()
            if selected_date.isValid():
                date_str = selected_date.toString("yyyy-MM-dd")
                
                # Switch to date view tab
                self.file_tabs.setCurrentIndex(0)
                
                # Add files for selected date
                if date_str in self.audio_files:
                    for file_path in self.audio_files[date_str]:
                        abs_path = str(Path(file_path).resolve())
                        status = self.get_file_status(abs_path)
                        
                        item = QListWidgetItem()
                        icon_text = "📝 " if status["has_transcript"] else "🎵 "
                        basename = os.path.basename(file_path)
                        
                        item.setText(f"{icon_text}{basename}")
                        item.setData(Qt.ItemDataRole.UserRole, abs_path)
                        self.date_files_list.addItem(item)
                    
        except Exception as e:
            print(f"Error handling date selection: {e}")

    def load_files_from_folder(self, folder_path):
        """Load all audio files from folder"""
        try:
            # Get files using file handler
            mp3_files, _ = self.app.file_handler.get_mp3_files(
                folder_path,
                include_subfolders=self.include_subfolders.isChecked()
            )
            
            print(f"Found {len(mp3_files)} files in {folder_path}")  # Debug print
            
            # Process each file
            for file_path in mp3_files:
                try:
                    # Extract date from filename (YYMMDD_...)
                    basename = os.path.basename(file_path)
                    date_match = re.match(r'^(\d{2})(\d{2})(\d{2})_', basename)
                    if date_match:
                        year, month, day = date_match.groups()
                        date_str = f"20{year}-{month}-{day}"
                        
                        # Add to audio_files dict
                        if date_str not in self.audio_files:
                            self.audio_files[date_str] = []
                        
                        # Only add if not already in the list
                        if file_path not in self.audio_files[date_str]:
                            self.audio_files[date_str].append(file_path)
                            
                            # Add to all files list
                            abs_path = str(Path(file_path).resolve())
                            status = self.get_file_status(abs_path)
                            status_prefix = "📝 " if status["has_transcript"] else "🎵 "
                            
                            item = QListWidgetItem(f"{status_prefix}{basename}")
                            item.setData(Qt.ItemDataRole.UserRole, abs_path)
                            self.all_files_list.addItem(item)
                            
                            print(f"Added file: {basename} for date {date_str}")  # Debug print
                
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")
                    continue
                    
            # Update calendar display
            self.mark_dates_with_files()
            
            # Update folder label
            self.update_folder_label()
            
            print(f"Total dates with files: {len(self.audio_files)}")  # Debug print
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load folder: {str(e)}")

    def on_live_folder_toggled(self, state):
        """Handle live folder checkbox toggle"""
        if hasattr(self, 'live_folder_label'):
            self.live_folder_label.setVisible(state == Qt.CheckState.Checked.value)
        
        if state == Qt.CheckState.Checked.value:
            # Load workspace files
            self.load_workspace_files()
        else:
            # Clear all files and reload only the selected folder if any
            self.audio_files = {}
            self.all_files_list.clear()
            self.date_files_list.clear()
            
            # If a custom folder is selected, load only that folder
            if self.current_folder and self.current_folder != self.app.path_manager.workspace_dir:
                self.load_files_from_folder(self.current_folder)
            else:
                # No folder selected or workspace was the only folder
                self.folder_label.setText("No folder selected")
                self.mark_dates_with_files()  # Clear calendar
    
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
        
    def mark_dates_with_files(self):
        """Mark dates that have associated files with count indicators"""
        try:
            # Clear existing date formats
            default_format = QTextCharFormat()
            self.calendar.setDateTextFormat(QDate(), default_format)
            
            # Mark dates that have files
            for date_str, files in self.audio_files.items():
                try:
                    # Convert date string to QDate
                    date = QDate.fromString(date_str, "yyyy-MM-dd")
                    if date.isValid():
                        # Count MP3s and transcripts
                        mp3_count = len(files)
                        transcript_count = sum(
                            1 for f in files 
                            if self.app.file_handler.check_transcript_exists(f)
                        )
                        
                        # Create format for dates with files
                        fmt = QTextCharFormat()
                        
                        # Calculate transcript ratio and set color intensity
                        if mp3_count > 0:
                            ratio = transcript_count / mp3_count
                            # Set color based on transcript ratio
                            if ratio == 0:
                                color = CALENDAR_COLORS["no_transcripts"]
                            elif ratio < 1:
                                color = CALENDAR_COLORS["partial_transcripts"]
                            else:
                                color = CALENDAR_COLORS["all_transcribed"]
                            fmt.setBackground(color)
                            fmt.setForeground(QColor(0, 0, 0))  # Black text
                            fmt.setFontWeight(700)  # Bold
                        
                        # Store counts in format property
                        fmt.setProperty(
                            QTextFormat.Property.UserProperty,
                            f"{mp3_count}|{transcript_count}|{';'.join(files)}"
                        )
                        
                        # Create tooltip with file info
                        tooltip = f"🎵 Audio Files: {mp3_count}\n📝 Transcripts: {transcript_count}\n\nRecordings:\n"
                        for file in files:
                            basename = os.path.basename(file)
                            desc = basename.split('_', 1)[1] if '_' in basename else basename
                            desc = os.path.splitext(desc)[0]
                            has_transcript = "📝 " if self.app.file_handler.check_transcript_exists(file) else "🎵 "
                            tooltip += f"{has_transcript}{desc}\n"
                        
                        fmt.setToolTip(tooltip.strip())
                        
                        # Apply format to date
                        self.calendar.setDateTextFormat(date, fmt)
                        
                except Exception as e:
                    print(f"Error marking date {date_str}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error in mark_dates_with_files: {e}")

    def get_file_status(self, file_path: str) -> dict:
        """Get status info for a file with caching"""
        if not hasattr(self, '_file_status_cache'):
            self._file_status_cache = {}
            
        abs_path = str(Path(file_path).resolve())
        
        # Return cached status if available
        if abs_path in self._file_status_cache:
            return self._file_status_cache[abs_path]
            
        try:
            # Build new status
            status = {
                "has_transcript": self.app.file_handler.check_transcript_exists(abs_path),
                "file_path": abs_path,
                "duration": None,  # Will be populated later
                "error": None
            }
            
            # Get transcript path for tooltip
            transcript_path = Path(abs_path).with_name(f"{Path(abs_path).stem}_transcript.txt")
            if transcript_path.exists():
                try:
                    with open(transcript_path, 'r', encoding='utf-8') as f:
                        first_line = f.readline().strip()
                    status["transcript_preview"] = first_line[:100] + "..." if len(first_line) > 100 else first_line
                except Exception as e:
                    status["transcript_preview"] = f"Error reading transcript: {str(e)}"
            
            # Cache the status
            self._file_status_cache[abs_path] = status
            
        except Exception as e:
            status = {
                "has_transcript": False,
                "file_path": abs_path,
                "duration": None,
                "error": str(e)
            }
            self._file_status_cache[abs_path] = status
            
        return status

    def show_month(self, year, month):
        """Show specified month in calendar"""
        try:
            # Update calendar display
            self.calendar.show_month(year, month)
            
            # Re-mark dates with files
            self.mark_dates_with_files()
            
        except Exception as e:
            print(f"Error showing month {month}/{year}: {e}")

    def on_file_double_clicked(self, item):
        """Handle file double click"""
        if item:
            file_path = item.data(Qt.ItemDataRole.UserRole)
            if file_path:
                self.media_player.load_file(file_path)

    def view_transcript(self):
        """View transcript for selected file"""
        active_list = self.get_active_list()
        if not active_list.currentItem():
            QMessageBox.warning(self, "Warning", "Please select a file to view")
            return
            
        file_path = active_list.currentItem().data(Qt.ItemDataRole.UserRole)
        if file_path:
            transcript_path = Path(file_path).with_name(f"{Path(file_path).stem}_transcript.txt")
            if transcript_path.exists():
                if platform.system() == "Windows":
                    os.startfile(str(transcript_path))
                else:
                    subprocess.call(["xdg-open", str(transcript_path)])
            else:
                QMessageBox.information(self, "Info", "No transcript found for this file")

    def send_to_live_analysis(self):
        """Send selected transcript to live session for analysis"""
        list_widget = self.get_active_list()
        if not list_widget or not list_widget.currentItem():
            QMessageBox.warning(self, "Warning", "Please select a file to analyze")
            return
            
        # Get absolute path from item data
        abs_path = list_widget.currentItem().data(Qt.ItemDataRole.UserRole)
        if not abs_path:
            return
            
        # Get transcript path
        transcript_path = Path(abs_path).with_name(f"{Path(abs_path).stem}_transcript.txt")
        if not transcript_path.exists():
            QMessageBox.warning(self, "Warning", "No transcript found for this file")
            return
            
        # Get the live session tab through main window
        main_window = self.parent()
        while main_window and not hasattr(main_window, 'live_session_tab'):
            main_window = main_window.parent()
            
        if not main_window:
            QMessageBox.critical(self, "Error", "Could not find main window")
            return
            
        live_tab = main_window.live_session_tab
        
        # Check if recording is active
        if live_tab.recording:
            QMessageBox.warning(
                self,
                "Warning", 
                "Cannot load transcript while recording is in progress!"
            )
            return
            
        # Confirm action
        reply = QMessageBox.question(
            self,
            "Load Transcript",
            "Load this transcript into live analysis?\nThis will clear current content.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Load transcript
                with open(transcript_path, 'r', encoding='utf-8') as f:
                    transcript_text = f.read()
                    
                # Clear and set new content
                live_tab.live_text.clear()
                live_tab.analysis_text.clear()
                live_tab.live_text.setText(transcript_text)
                live_tab.accumulated_text = transcript_text
                
                # Set current transcript path
                live_tab.current_transcript_path = transcript_path
                
                # Update status
                live_tab.status_label.setText(f"Loaded transcript: {transcript_path.name}")
                
                # Switch to live session tab
                main_window.tab_widget.setCurrentWidget(live_tab)
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load transcript: {str(e)}")

    def transcribe_selected(self):
        """Transcribe selected file"""
        list_widget = self.get_active_list()
        if not list_widget or not list_widget.currentItem():
            QMessageBox.warning(self, "Warning", "Please select a file to transcribe")
            return
            
        file_path = list_widget.currentItem().data(Qt.ItemDataRole.UserRole)
        if file_path:
            try:
                # Get current service and config from app
                service = self.app.current_service
                config = {
                    'model': 'whisper-1',
                    'speaker_labels': True,
                    'timestamps': True
                }
                
                transcript = service.transcribe(file_path, config)
                
                # Save transcript
                output_file = self.app.file_handler.generate_output_filename(file_path, "txt")
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(transcript)
                    
                QMessageBox.information(self, "Success", "Transcription completed successfully!")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Transcription failed: {str(e)}")

    def show_context_menu(self, pos):
        """Show context menu for list widgets"""
        list_widget = self.sender()
        if not list_widget.itemAt(pos):
            return
            
        item = list_widget.itemAt(pos)
        file_path = item.data(Qt.ItemDataRole.UserRole)
        
        menu = QMenu(self)
        
        # Add Rename action
        rename_action = menu.addAction("Rename")
        rename_action.triggered.connect(lambda: self.rename_file(file_path))
        
        menu.addSeparator()
        
        # Add Go to Date action
        go_to_date = menu.addAction("Go to Date")
        go_to_date.triggered.connect(lambda: self.go_to_date_from_file(file_path))
        
        menu.addSeparator()
        
        # Add transcript actions
        view_transcript = menu.addAction("View Transcript")
        view_transcript.triggered.connect(self.view_transcript)
        
        live_analysis = menu.addAction("Send to Live Analysis")
        live_analysis.triggered.connect(self.send_to_live_analysis)
        
        deep_analysis = menu.addAction("Send to Deep Analysis")
        deep_analysis.triggered.connect(self.send_to_deep_analysis)
        
        # Show file status in tooltip
        status = self.get_file_status(file_path)
        if status.get("error"):
            menu.setToolTip(f"Error: {status['error']}")
        elif status.get("transcript_preview"):
            menu.setToolTip(f"Transcript preview:\n{status['transcript_preview']}")
        
        menu.exec(list_widget.mapToGlobal(pos))
        
    def go_to_date_from_file(self, file_path):
        """Navigate to the date of the selected file"""
        try:
            # Extract date from filename (YYMMDD_...)
            basename = os.path.basename(file_path)
            date_match = re.match(r'^(\d{2})(\d{2})(\d{2})_', basename)
            
            if date_match:
                year, month, day = date_match.groups()
                date = QDate(2000 + int(year), int(month), int(day))
                
                # Switch to date view tab
                self.file_tabs.setCurrentIndex(0)
                
                # Select the date in calendar
                self.calendar.setSelectedDate(date)
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to navigate to date: {str(e)}")

    def create_action_buttons(self) -> QHBoxLayout:
        """Create standard button layout for file actions"""
        button_layout = QHBoxLayout()
        
        # Add selection count
        selection_label = QLabel("")
        button_layout.addWidget(selection_label)
        
        # Transcribe button
        transcribe_btn = QPushButton("Transcribe Selected")
        transcribe_btn.clicked.connect(self.transcribe_selected)
        button_layout.addWidget(transcribe_btn)
        
        # View transcript button
        view_transcript_btn = QPushButton("View Transcript")
        view_transcript_btn.clicked.connect(self.view_transcript)
        button_layout.addWidget(view_transcript_btn)
        
        # Live analysis button
        live_analysis_btn = QPushButton("Send to Live Analysis")
        live_analysis_btn.clicked.connect(self.send_to_live_analysis)
        button_layout.addWidget(live_analysis_btn)
        
        # Deep analysis button
        deep_analysis_btn = QPushButton("Send to Deep Analysis")
        deep_analysis_btn.clicked.connect(self.send_to_deep_analysis)
        button_layout.addWidget(deep_analysis_btn)
        
        return button_layout

    def rename_file(self, file_path):
        """Rename file while preserving date/time prefix and .mp3 extension"""
        try:
            # If file is currently playing, stop and release it
            if (hasattr(self, 'media_player') and 
                self.media_player.player.source().toString() == QUrl.fromLocalFile(file_path).toString()):
                self.media_player.player.stop()
                self.media_player.player.setSource(QUrl())  # Clear source
            
            # Get current filename parts
            dirname = os.path.dirname(file_path)
            basename = os.path.basename(file_path)
            prefix = '_'.join(basename.split('_')[:2])  # Get YYMMDD_HHMM
            
            # Get current description without .mp3
            current_desc = basename.split('_', 2)[2] if len(basename.split('_', 2)) > 2 else ''
            if current_desc.endswith('.mp3'):
                current_desc = current_desc[:-4]
            
            # Get new description
            new_desc, ok = QInputDialog.getText(
                self, 
                "Rename File",
                "Enter new description:",
                text=current_desc
            )
            
            if ok and new_desc:
                # Create new filename
                new_name = f"{prefix}_{new_desc}.mp3"
                new_path = os.path.join(dirname, new_name)
                
                # Check if transcript exists
                transcript_path = Path(file_path).with_name(f"{Path(file_path).stem}_transcript.txt")
                new_transcript_path = Path(new_path).with_name(f"{Path(new_path).stem}_transcript.txt")
                
                # Rename files
                os.rename(file_path, new_path)
                if transcript_path.exists():
                    os.rename(transcript_path, new_transcript_path)
                
                # Refresh display
                self.refresh_files()
                
                # If this was the playing file, reload it
                if (hasattr(self, 'media_player') and 
                    self.media_player.file_label.text() == basename):
                    self.media_player.load_file(new_path, autoplay=False)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to rename file: {str(e)}")
            
    def send_to_deep_analysis(self):
        """Send selected files to deep analysis tab"""
        selected_items = self.date_files_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select files to analyze")
            return
            
        transcript_paths = []
        for item in selected_items:
            file_path = item.data(Qt.ItemDataRole.UserRole)
            transcript_path = Path(file_path).with_name(f"{Path(file_path).stem}_transcript.txt")
            if transcript_path.exists():
                transcript_paths.append(str(transcript_path))
        
        if not transcript_paths:
            QMessageBox.warning(self, "Warning", "No transcripts found for selected files")
            return
            
        # Get main window
        main_window = self.parent()
        while main_window and not hasattr(main_window, 'deep_analysis_tab'):
            main_window = main_window.parent()
            
        if main_window and main_window.deep_analysis_tab:
            main_window.deep_analysis_tab.add_transcripts(transcript_paths)
            main_window.tab_widget.setCurrentWidget(main_window.deep_analysis_tab)


    def save_splitter_state(self):
        """Save splitter positions"""
        settings = self.app.settings_manager
        settings.save_setting('library_main_splitter', str(self.main_splitter.saveState().toHex(), 'utf-8'))
        settings.save_setting('library_right_splitter', str(self.right_splitter.saveState().toHex(), 'utf-8'))

    def restore_splitter_state(self):
        """Restore splitter positions"""
        settings = self.app.settings_manager
        main_state = settings.get_setting('library_main_splitter')
        right_state = settings.get_setting('library_right_splitter')
        
        if main_state:
            self.main_splitter.restoreState(bytes.fromhex(main_state))
        if right_state:
            self.right_splitter.restoreState(bytes.fromhex(right_state))
    def update_folder_label(self):
        """Update folder label to show current selection"""
        workspace_dir = self.app.path_manager.workspace_dir if hasattr(self.app, 'path_manager') else None
        
        if self.include_live_folder.isChecked() and workspace_dir:
            if self.current_folder and self.current_folder != workspace_dir:
                # Both workspace and custom folder
                self.folder_label.setText(f"Workspace: {workspace_dir}\nLibrary: {self.current_folder}")
            else:
                # Only workspace
                self.folder_label.setText(f"Workspace: {workspace_dir}")
        elif self.current_folder:
            # Only custom folder
            self.folder_label.setText(f"Library: {self.current_folder}")
        else:
            # No folder selected
            self.folder_label.setText("No folder selected")
