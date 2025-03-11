from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QFileDialog, QListWidget, QSplitter,
    QGroupBox, QCheckBox, QMessageBox, QCalendarWidget,
    QTextEdit, QMenu, QTabWidget, QListWidgetItem,
    QApplication, QTableView, QHeaderView
)
from .media_player_qt import MediaPlayerWidget
from PyQt6.QtCore import Qt, QDate, QRectF, QPointF, QEvent
from PyQt6.QtGui import (
    QTextCharFormat, QPainter, QBrush, QPen, QFont,
    QColor, QLinearGradient, QTextFormat
)
import os
from datetime import datetime
import platform
import subprocess
import re
from pathlib import Path

from PyQt6.QtCore import pyqtSignal

class BadgedCalendarWidget(QCalendarWidget):
    # Custom signal for selection changes
    selectionChanged = pyqtSignal()
    
    def __init__(self, parent=None, app=None):
        super().__init__(parent)
        self.app = app
        self._selected_dates = set()  # Track selected dates
        self._file_cache = {}  # Cache for file metadata
        
        # Initialize UI elements
        self.init_ui()
        
        # Install event filter for headers
        calendar_view = self.findChild(QTableView, "qt_calendar_calendarview")
        if calendar_view:
            header = calendar_view.horizontalHeader()
            header.installEventFilter(self)
        
        # Set tooltips
        self.setToolTip("Click to select/deselect dates. Hold Ctrl for multi-select.")
        
    def init_ui(self):
        """Initialize UI elements"""
        # Initialize selection tracking
        self._selected_dates = set()
        
        # Get the internal calendar view
        calendar_view = self.findChild(QTableView, "qt_calendar_calendarview")
        if calendar_view:
            # Disable header interactions
            header = calendar_view.horizontalHeader()
            header.setSectionsClickable(False)
            header.setHighlightSections(False)
        
    def selectedDates(self):
        """Return the currently selected dates"""
        return list(self._selected_dates)
        
    def setDateRange(self, start_date, end_date):
        """Select a range of dates"""
        if not start_date.isValid() or not end_date.isValid():
            self._selected_dates.clear()
            return
            
        current = start_date
        while current <= end_date:
            self._selected_dates.add(current)
            current = current.addDays(1)
            
        self.updateCells()
        self.selectionChanged.emit()
        
    def eventFilter(self, watched, event):
        """Filter events to prevent header selection"""
        if isinstance(watched, QHeaderView):
            if event.type() in (QEvent.Type.MouseButtonPress, 
                              QEvent.Type.MouseButtonDblClick):
                return True  # Block header clicks
        return super().eventFilter(watched, event)
        
    def dateAt(self, pos):
        """Get date at position"""
        # Get the cell size
        header_height = 40  # Standard header height for QCalendarWidget
        day_header_height = 30  # Height of day names section
        
        # Skip if clicked in any header area (navigation or day names)
        if pos.y() < day_header_height:
            return QDate()
            
        cell_width = self.width() / 7
        cell_height = (self.height() - header_height) / 6
        
        # Adjust position for header
        adjusted_y = pos.y() - header_height
        
        # Skip if clicked in remaining header area
        if adjusted_y < 0:
            return QDate()
            
        # Calculate row and column
        row = int(adjusted_y / cell_height)
        col = int(pos.x() / cell_width)
        
        # Get first day of month
        first_day = QDate(self.yearShown(), self.monthShown(), 1)
        start_day_of_week = first_day.dayOfWeek()
        
        # Calculate day number
        day = row * 7 + col - start_day_of_week + 2
        
        # Create and validate date
        date = QDate(self.yearShown(), self.monthShown(), day)
        if date.isValid() and date.month() == self.monthShown():
            return date
            
        return QDate()

    def mousePressEvent(self, event):
        """Handle mouse clicks for date selection"""
        pos = event.pos()
        
        # Get header heights
        nav_header_height = 40  # Navigation header height
        day_header_height = 30  # Day names header height
        total_header_height = nav_header_height + day_header_height
        
        # Ignore clicks in any header area
        if pos.y() < total_header_height:
            event.accept()
            return
            
        clicked_date = self.dateAt(pos)
        
        if clicked_date.isValid():
            event.accept()
            
            # Toggle the date in our set
            if clicked_date in self._selected_dates:
                self._selected_dates.remove(clicked_date)
            else:
                self._selected_dates.add(clicked_date)
            
            # Block Qt's default selection
            self.blockSignals(True)
            self.updateCells()
            self.blockSignals(False)
            self.selectionChanged.emit()
    
    def paintCell(self, painter, rect, date):
        """Custom painting for calendar cells"""
        # Call base class to paint the regular cell
        super().paintCell(painter, rect, date)
        
        # Draw selection if date is in our selected set
        if date in self._selected_dates:
            painter.save()
            painter.setPen(QPen(QColor("#2196F3"), 2))
            painter.setBrush(QBrush(QColor(33, 150, 243, 50)))  # Semi-transparent blue
            painter.drawRect(rect.adjusted(2, 2, -2, -2))
            painter.restore()
        
        # Get the date format (which includes our badge counts)
        fmt = self.dateTextFormat(date)
        badge_data = fmt.property(QTextFormat.Property.UserProperty)
        
        if badge_data:
            mp3_count, transcript_count, _ = badge_data.split('|', 2)
            mp3_count = int(mp3_count)
            transcript_count = int(transcript_count)
            
            if mp3_count > 0:
                painter.save()
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                
                # Calculate badge sizes and positions
                badge_size = min(rect.width(), rect.height()) * 0.22
                spacing = badge_size * 0.3
                
                # Draw MP3 count badge (top right)
                if mp3_count > 0:
                    mp3_rect = QRectF(
                        rect.right() - badge_size - 2,
                        rect.top() + 2,
                        badge_size,
                        badge_size
                    )
                    
                    # Draw badge background
                    painter.setBrush(QBrush(QColor("#2196F3")))  # Blue for audio
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawEllipse(mp3_rect)
                    
                    # Draw count
                    painter.setPen(Qt.GlobalColor.white)
                    font = painter.font()
                    font.setPointSizeF(badge_size * 0.65)
                    painter.setFont(font)
                    painter.drawText(mp3_rect, Qt.AlignmentFlag.AlignCenter, str(mp3_count))
                
                # Draw transcript count badge (below MP3 badge)
                if transcript_count > 0:
                    transcript_rect = QRectF(
                        rect.right() - badge_size - 2,
                        rect.top() + badge_size + spacing,
                        badge_size,
                        badge_size
                    )
                    
                    # Draw badge background
                    painter.setBrush(QBrush(QColor("#4CAF50")))  # Green for transcripts
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawEllipse(transcript_rect)
                    
                    # Draw count
                    painter.setPen(Qt.GlobalColor.white)
                    painter.drawText(transcript_rect, Qt.AlignmentFlag.AlignCenter, str(transcript_count))
                
                painter.restore()
            
    def setDateWithFiles(self, date, count, files):
        """Set date format with file count and names for tooltip"""
        fmt = QTextCharFormat()
        
        # Store both count and file info as a string
        fmt.setProperty(QTextFormat.Property.UserProperty, 
                      f"{count}|{';'.join(files)}")
        
        # Create detailed tooltip
        tooltip = "Recordings:\n"
        for file in files:
            # Use the full file path that was passed in
            if os.path.exists(file):
                # Extract description part after YYMMDD_
                basename = os.path.basename(file)
                desc = basename.split('_', 1)[1] if '_' in basename else basename
                # Remove .mp3 extension if present
                desc = os.path.splitext(desc)[0]
                # Add transcript status indicator
                has_transcript = "📝 " if self.app.file_handler.check_transcript_exists(file) else "🎵 "
                tooltip += f"{has_transcript}{desc}\n"
        
        fmt.setToolTip(tooltip.strip())
        
        # Set background tint based on count
        tint = QColor("#ECF0F1")
        tint.setAlpha(min(30 + (count * 15), 120))
        fmt.setBackground(tint)
        
        self.setDateTextFormat(date, fmt)


class CalendarViewQt(QWidget):
    def __init__(self, parent=None, app=None):
        super().__init__(parent)
        self.app = app
        print(f"CalendarViewQt initialized with app: {self.app}")  # Debug print
        if not self.app:
            print("Warning: No app object provided to CalendarViewQt")
        self.audio_files = {}
        self.transcripts = {}
        self.current_folder = None
        self._debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        
        # Create main layout
        main_layout = QVBoxLayout(self)  # Set layout directly on self
        
        # Create main vertical splitter
        main_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Top section for folder selection
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        
        # Folder selection controls
        folder_controls = QHBoxLayout()
        
        select_btn = QPushButton("📁 Select Folder")
        select_btn.clicked.connect(self.select_folder)
        select_btn.setMaximumWidth(120)
        folder_controls.addWidget(select_btn)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_files)
        refresh_btn.setMaximumWidth(120)
        refresh_btn.setToolTip("Refresh files from selected folders")
        folder_controls.addWidget(refresh_btn)
        
        folder_controls.addStretch()
        top_layout.addLayout(folder_controls)
        
        checkbox_layout = QVBoxLayout()
        self.include_subfolders = QCheckBox("Include Subfolders")
        self.include_subfolders.stateChanged.connect(self.refresh_files)
        checkbox_layout.addWidget(self.include_subfolders)
        
        # Add live session folder checkbox
        self.include_live_folder = QCheckBox("Include Live Session Folder")
        self.include_live_folder.stateChanged.connect(self.on_live_folder_toggled)
        if hasattr(self.app, 'path_manager'):
            live_path = self.app.path_manager.recordings_dir
            self.include_live_folder.setToolTip(f"Include files from: {live_path}")
        checkbox_layout.addWidget(self.include_live_folder)
        
        top_layout.addLayout(checkbox_layout)
        
        # Create folder path display
        folder_path_layout = QVBoxLayout()
        self.folder_label = QLabel("No folder selected")
        self.folder_label.setWordWrap(True)
        folder_path_layout.addWidget(self.folder_label)
        
        self.live_folder_label = QLabel()
        self.live_folder_label.setWordWrap(True)
        self.live_folder_label.setStyleSheet("color: #666;")  # Slightly dimmed
        folder_path_layout.addWidget(self.live_folder_label)
        
        # Update live folder label if path exists
        if hasattr(self.app, 'path_manager'):
            live_path = self.app.path_manager.get_session_dir("recordings")
            self.live_folder_label.setText(f"Live Sessions: {live_path}")
            self.live_folder_label.setVisible(self.include_live_folder.isChecked())
        
        top_layout.addLayout(folder_path_layout, stretch=1)
        
        main_splitter.addWidget(top_widget)
        
        # Bottom section with horizontal splitter
        bottom_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - Calendar
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Create calendar with app reference
        self.calendar = BadgedCalendarWidget(parent=self, app=self.app)
        self.calendar.setMinimumDate(QDate(1900, 1, 1))
        self.calendar.setMaximumDate(QDate(3000, 1, 1))
        self.calendar.setGridVisible(True)
        self.calendar.setNavigationBarVisible(True)
        self.calendar.setFirstDayOfWeek(Qt.DayOfWeek.Monday)
        # Set calendar formats
        self.calendar.setHorizontalHeaderFormat(QCalendarWidget.HorizontalHeaderFormat.ShortDayNames)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        
        # Style the calendar headers for better visibility
        self.calendar.setStyleSheet("""
            QCalendarWidget QWidget { 
                alternate-background-color: #E0E0E0; 
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: #000000;
                background-color: #FFFFFF;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #F5F5F5;
            }
            /* Style the day names header */
            QCalendarWidget QWidget#qt_calendar_calendarview QWidget#qt_calendar_dayheader {
                color: #000000;
                background-color: #E0E0E0;
            }
            /* Make day names bold and clearly visible */
            QCalendarWidget QWidget#qt_calendar_calendarview QWidget#qt_calendar_dayheader QLabel {
                color: #000000;
                font-weight: bold;
                qproperty-alignment: AlignCenter;
            }
        """)
        
        # Connect calendar signals
        self.calendar.clicked.connect(self.on_date_selected)
        self.calendar.selectionChanged.connect(self.on_date_selected)
        self.calendar.currentPageChanged.connect(self.mark_dates_with_files)
        
        # Set size
        self.calendar.setMinimumWidth(400)
        self.calendar.setMinimumHeight(300)
        
        left_layout.addWidget(self.calendar)
        left_widget.setLayout(left_layout)
        
        bottom_splitter.addWidget(left_widget)
        
        # Right side - Files and Transcript
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_widget.setLayout(right_layout)  # Set layout explicitly
        
        # Add media player
        self.media_player = MediaPlayerWidget(self)
        right_layout.addWidget(self.media_player)
        
        # File view tabs
        self.file_tabs = QTabWidget()
        
        # Date view tab
        date_tab = QWidget()
        date_layout = QVBoxLayout(date_tab)
        
        # Status legend
        status_frame = QHBoxLayout()
        status_frame.addWidget(QLabel("🎵 Audio Only"))
        status_frame.addWidget(QLabel("📝 Has Transcript"))
        date_layout.addLayout(status_frame)
        
        self.date_files_list = QListWidget()
        self.date_files_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.date_files_list.itemDoubleClicked.connect(self.view_transcript)
        self.date_files_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.date_files_list.customContextMenuRequested.connect(self.show_context_menu)
        date_layout.addWidget(self.date_files_list)
        
        date_tab.setLayout(date_layout)
        self.file_tabs.addTab(date_tab, "By Date")
        
        # All files tab
        all_files_tab = QWidget()
        all_files_layout = QVBoxLayout(all_files_tab)
        
        self.all_files_list = QListWidget()
        self.all_files_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.all_files_list.itemDoubleClicked.connect(self.view_transcript)
        self.all_files_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.all_files_list.customContextMenuRequested.connect(self.show_context_menu)
        all_files_layout.addWidget(self.all_files_list)
        
        all_files_tab.setLayout(all_files_layout)
        self.file_tabs.addTab(all_files_tab, "All Files")
        
        # Add file tabs to right layout
        right_layout.addWidget(self.file_tabs)
        
        # Add controls
        control_frame = QHBoxLayout()
        
        self.transcribe_btn = QPushButton("Transcribe Selected")
        self.transcribe_btn.clicked.connect(self.transcribe_selected)
        control_frame.addWidget(self.transcribe_btn)
        
        self.view_transcript_btn = QPushButton("View Transcript")
        self.view_transcript_btn.clicked.connect(self.view_transcript)
        control_frame.addWidget(self.view_transcript_btn)
        
        self.analyze_btn = QPushButton("Send to Live Analysis")
        self.analyze_btn.clicked.connect(self.send_to_live_analysis)
        control_frame.addWidget(self.analyze_btn)
        
        right_layout.addLayout(control_frame)
        
        # Set layout for right widget
        right_widget.setLayout(right_layout)
        
        # Add right widget to splitter
        bottom_splitter.addWidget(right_widget)
        
        # Add bottom splitter to main splitter
        main_splitter.addWidget(bottom_splitter)
        
        # Add main splitter to layout
        main_layout.addWidget(main_splitter)
        
        # Set initial splitter sizes
        main_splitter.setSizes([50, 750])  # Give most space to bottom section
        bottom_splitter.setSizes([400, 600])
        
        
    def show_context_menu(self, pos):
        """Show context menu for file list"""
        list_widget = self.sender()
        if list_widget.itemAt(pos):
            self.file_context_menu.exec(list_widget.mapToGlobal(pos))
            
    def play_in_media_player(self):
        """Load selected file in media player"""
        list_widget = self.get_active_list()
        if not list_widget or not list_widget.currentItem():
            return
            
        # Get absolute path from item data
        item = list_widget.currentItem()
        abs_path = item.data(Qt.ItemDataRole.UserRole)
        if abs_path:
            self.media_player.load_file(abs_path)
            
    def get_active_list(self) -> QListWidget:
        """Get the currently active list widget"""
        return (self.date_files_list 
                if self.file_tabs.currentIndex() == 0 
                else self.all_files_list)
                
    def get_file_path_from_item(self, item) -> str:
        """Get absolute file path from list item"""
        if not item:
            return None
        return item.data(Qt.ItemDataRole.UserRole)
        
    def go_to_date(self):
        """Navigate to the date of the selected file"""
        list_widget = self.get_active_list()
        if not list_widget or not list_widget.currentItem():
            return
            
        try:
            # Get file path from item data
            file_path = list_widget.currentItem().data(Qt.ItemDataRole.UserRole)
            if not file_path:
                return
                
            # Extract date from filename (YYMMDD_...)
            basename = os.path.basename(file_path)
            date_match = re.match(r'^(\d{2})(\d{2})(\d{2})_', basename)
            
            if not date_match:
                QMessageBox.warning(self, "Error", "Could not extract date from filename")
                return
                
            # Convert YY MM DD to full date
            year, month, day = date_match.groups()
            date = QDate(2000 + int(year), int(month), int(day))
            
            # Switch to date view tab
            self.file_tabs.setCurrentIndex(0)
            
            # Select the date in calendar
            self.calendar.setSelectedDate(date)
            
        except Exception as e:
            if self._debug_mode:
                print(f"Error in go_to_date: {str(e)}")
            QMessageBox.warning(self, "Error", "Failed to navigate to date")
        
    def send_to_deep_analysis(self):
        """Send selected files to deep analysis tab"""
        list_widget = self.get_active_list()
        selected_items = list_widget.selectedItems() if list_widget else []
        
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select files to analyze")
            return
            
        # Get transcript paths for selected files
        transcript_paths = []
        for item in selected_items:
            file_path = item.data(Qt.ItemDataRole.UserRole)
            if not file_path:
                continue
                
            # Get transcript path
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
            
        if not main_window:
            QMessageBox.critical(self, "Error", "Could not find main window")
            return
            
        # Send to deep analysis tab
        main_window.deep_analysis_tab.add_transcripts(transcript_paths)
        main_window.tab_widget.setCurrentWidget(main_window.deep_analysis_tab)

    def send_to_live_analysis(self):
        """Send selected transcript to live session for analysis"""
        list_widget = self.get_active_list()
        if not list_widget or not list_widget.currentItem():
            QMessageBox.warning(self, "Warning", "Please select a file to analyze")
            return
            
                
    def view_transcript(self, item=None):
        """View transcript for selected file"""
        if not item:
            item = self.get_active_list().currentItem()
        
        if not item:
            QMessageBox.warning(self, "Warning", "Please select a file to view")
            return
            
        # Get absolute path from item data
        abs_path = item.data(Qt.ItemDataRole.UserRole)
        if not abs_path:
            return
            
        transcript_path = Path(abs_path).with_name(f"{Path(abs_path).stem}_transcript.txt")
        if transcript_path.exists():
            if platform.system() == "Windows":
                os.startfile(str(transcript_path))
            else:
                subprocess.call(["xdg-open", str(transcript_path)])
        else:
            QMessageBox.information(self, "Info", "No transcript found for this file")
        
        
    def on_date_selected(self, date=None):
        """Handle date selection in calendar"""
        if self._debug_mode:
            print("\nHandling date selection:")
            
        # Clear the date files list
        self.date_files_list.clear()
        
        # Switch to the "By Date" tab
        self.file_tabs.setCurrentIndex(0)
        
        # Get files for all selected dates
        selected_files = []
        for selected_date in self.calendar.selectedDates():
            if selected_date.isValid():
                date_str = selected_date.toString("yyyy-MM-dd")
                if date_str in self.audio_files:
                    selected_files.extend(self.audio_files[date_str])
                    
        # Sort files by date
        selected_files.sort(key=lambda x: os.path.basename(x)[:6])  # Sort by YYMMDD prefix
                        
        if self._debug_mode:
            print(f"Total files found: {len(selected_files)}")
            
        # Add files to list
        for file_path in selected_files:
            try:
                # Get file status and add to listbox with status indicator
                abs_path = str(Path(file_path).resolve())
                if not os.path.exists(abs_path):
                    if self._debug_mode:
                        print(f"File not found: {abs_path}")
                    continue
                    
                status = self.get_file_status(abs_path)
                status_prefix = "📝 " if status["has_transcript"] else "🎵 "
                display_name = f"{os.path.basename(file_path)}"
                
                if self._debug_mode:
                    print(f"Processing file: {abs_path}")
                    print(f"Status: {status}")
                    print(f"Display name: {display_name}")
                
                item = QListWidgetItem(f"{status_prefix}{display_name}")
                item.setData(Qt.ItemDataRole.UserRole, abs_path)
                self.date_files_list.addItem(item)
                
                if self._debug_mode:
                    print(f"Added file to list: {display_name}")
                    
            except Exception as e:
                if self._debug_mode:
                    print(f"Error processing file {file_path}: {e}")
                    print(f"Exception details: {str(e)}")
        
        
    def transcribe_selected(self):
        """Transcribe selected file"""
        list_widget = self.get_active_list()
        if not list_widget or not list_widget.currentItem():
            QMessageBox.warning(self, "Warning", "Please select a file to transcribe")
            return
            
        file_path = self.get_file_path_from_item(list_widget.currentItem().text())
        if file_path:
            try:
                # Get current service and config from app
                service = self.app.current_service
                config = {
                    'model': 'whisper-1',  # TODO: Get from settings
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
        
    def select_folder(self):
        """Select folder and load all audio files"""
        try:
            folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
            if folder_path:
                print(f"Selected folder: {folder_path}")  # Debug print
                self.current_folder = folder_path
                self.folder_label.setText(folder_path)
                self.load_files_from_folder(folder_path)
        except Exception as e:
            print(f"Error in select_folder: {str(e)}")  # Debug print
            QMessageBox.critical(self, "Error", f"Failed to select folder: {str(e)}")
            
    def on_live_folder_toggled(self, state):
        """Handle live folder checkbox toggle"""
        self.live_folder_label.setVisible(state == Qt.CheckState.Checked.value)
        self.refresh_files()
        
    def refresh_files(self):
        """Refresh files based on current folder and subfolder setting"""
        if self.current_folder:
            self.load_files_from_folder(self.current_folder)
            self.folder_label.setText(f"Selected Folder: {self.current_folder}")
            
    def mark_dates_with_files(self):
        """Highlight dates that have files"""
        # Clear existing highlights
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())
        
        # Mark dates that have files
        for date_str in self.audio_files.keys():
            date = QDate.fromString(date_str, "yyyy-MM-dd")
            files = self.audio_files[date_str]
            
            # Get file descriptions (part after YYMMDD_)
            file_descriptions = []
            for file_path in files:
                basename = os.path.basename(file_path)
                desc = basename.split('_', 1)[1] if '_' in basename else "[Unnamed Recording]"
                file_descriptions.append(desc)
            
            # Set date format with count and file info
            self.calendar.setDateWithFiles(date, len(files), file_descriptions)
            
    def has_transcript(self, file_path: str) -> bool:
        """Check if a file has a transcript"""
        return self.app.file_handler.check_transcript_exists(file_path)
            
    def get_file_status(self, file_path: str) -> dict:
        """Get status for a file, loading or creating metadata if needed"""
        if not hasattr(self, 'file_statuses'):
            self.file_statuses = {}
            
        # Use full path as key
        full_path = str(Path(file_path).resolve())
        if full_path not in self.file_statuses:
            if self._debug_mode:
                print(f"\nChecking status for: {full_path}")
                print(f"Original path: {file_path}")
                print(f"Exists: {os.path.exists(full_path)}")
                
            has_transcript = self.app.file_handler.check_transcript_exists(full_path)
            if self._debug_mode:
                print(f"Has transcript: {has_transcript}")
                
            status = {
                "status": {
                    "has_transcript": has_transcript,
                    "file_path": full_path
                },
                "metadata": {}
            }
            self.file_statuses[full_path] = status
            
        return self.file_statuses[file_path]["status"]
        
    def load_files_from_folder(self, folder_path):
        """Load all audio files from selected folder and optionally subfolders"""
        try:
            print(f"Loading files from: {folder_path}")  # Debug print
            
            self.audio_files.clear()
            self.date_files_list.clear()
            self.all_files_list.clear()
            
            mp3_files = []
            transcript_status = {}
            
            try:
                # Get files from selected folder
                folder_files, folder_status = self.app.file_handler.get_mp3_files(
                    folder_path, 
                    include_subfolders=self.include_subfolders.isChecked()
                )
                mp3_files.extend(folder_files)
                transcript_status.update(folder_status)
                
                # Add files from live session folder if checked
                if self.include_live_folder.isChecked() and hasattr(self.app, 'path_manager'):
                    live_path = self.app.path_manager.recordings_dir
                    if os.path.exists(live_path):
                        live_files, live_status = self.app.file_handler.get_mp3_files(
                            live_path,
                            include_subfolders=True  # Always include subfolders for live sessions
                        )
                        mp3_files.extend(live_files)
                        transcript_status.update(live_status)
                print(f"Found files: {mp3_files}")  # Debug print
                
                # Convert all paths to absolute paths
                mp3_files = [os.path.abspath(os.path.join(folder_path, f)) 
                            for f in mp3_files]
                
            except Exception as e:
                print(f"Error getting MP3 files: {str(e)}")
                QMessageBox.critical(self, "Error", f"Failed to get MP3 files: {str(e)}")
                return
            
            print(f"Found files: {mp3_files}")  # Debug print
        
            earliest_date = None
            
            for file_path in mp3_files:
                try:
                    print(f"Processing file: {file_path}")  # Debug print
                    
                    try:
                        # Get date from filename (YYMMDD_filename.mp3)
                        basename = os.path.basename(file_path)
                        print(f"Basename: {basename}")  # Debug print
                        
                        date_match = re.match(r'^(\d{2})(\d{2})(\d{2})_', basename)
                        if not date_match:
                            print(f"File {basename} doesn't match naming convention")  # Debug print
                            continue  # Skip files that don't match naming convention
                    except Exception as e:
                        print(f"Error processing basename for {file_path}: {e}")
                        continue
                
                    year, month, day = date_match.groups()
                    date_str = f"20{year}-{month}-{day}"
                    file_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    print(f"Extracted date: {date_str}")  # Debug print
                    
                    # Track earliest date
                    if earliest_date is None or file_date < earliest_date:
                        earliest_date = file_date
                    
                    try:
                        # Store in audio_files dictionary
                        if date_str not in self.audio_files:
                            self.audio_files[date_str] = []
                        self.audio_files[date_str].append(file_path)
                        
                        # Get file status and add to list with status indicator
                        abs_path = str(Path(file_path).resolve())  # Get canonical path
                        if self._debug_mode:
                            print(f"\nAdding file to list:")
                            print(f"- Original path: {file_path}")
                            print(f"- Absolute path: {abs_path}")
                            print(f"- Exists: {os.path.exists(abs_path)}")
                            
                        status = self.get_file_status(abs_path)
                        status_prefix = "📝 " if status["has_transcript"] else "🎵 "
                        display_name = f"{date_str}: {basename}"
                        item = QListWidgetItem(f"{status_prefix}{display_name}")
                        item.setData(Qt.ItemDataRole.UserRole, abs_path)  # Store full canonical path
                        self.all_files_list.addItem(item)
                        
                        print(f"Added file {basename} for date {date_str}")  # Debug print
                    except Exception as e:
                        print(f"Error adding file {file_path}: {e}")  # Debug print
                        continue
                    
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")  # Debug print
                    continue
            
            print(f"Final audio_files: {self.audio_files}")  # Debug print
            
            # Select earliest date if available
            if earliest_date:
                self.calendar.setSelectedDate(QDate(earliest_date.year, earliest_date.month, earliest_date.day))
                
            self.mark_dates_with_files()
            
        except Exception as e:
            print(f"Error loading folder {folder_path}: {e}")  # Debug print
            QMessageBox.critical(self, "Error", f"Failed to load folder: {str(e)}")
            
            # Select earliest date if available
            if earliest_date:
                self.calendar.setSelectedDate(QDate(earliest_date.year, earliest_date.month, earliest_date.day))
                
            self.mark_dates_with_files()
