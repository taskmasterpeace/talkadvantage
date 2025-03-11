from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QFrame, QSizePolicy, QScrollArea, QCheckBox,
    QLineEdit, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QPainter, QImage
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from wordcloud import WordCloud
import numpy as np
from collections import Counter
import re
import os

class WordCloudWidget(QWidget):
    """Widget for displaying and interacting with a word cloud visualization"""
    
    word_clicked = pyqtSignal(str)  # Signal emitted when a word is clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.word_counts = Counter()
        # Simple stopwords list instead of using NLTK
        self.stopwords = {'a', 'an', 'the', 'and', 'or', 'but', 'if', 'then', 'else', 'when',
                         'at', 'from', 'by', 'for', 'with', 'about', 'against', 'between',
                         'into', 'through', 'during', 'before', 'after', 'above', 'below',
                         'to', 'of', 'in', 'on', 'off', 'over', 'under', 'again', 'further',
                         'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how',
                         'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other',
                         'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
                         'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don',
                         'should', 'now', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours',
                         'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves',
                         'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself',
                         'it', 'its', 'itself', 'they', 'them', 'their', 'theirs',
                         'themselves', 'what', 'which', 'who', 'whom', 'this', 'that',
                         'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been',
                         'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did',
                         'doing', 'would', 'should', 'could', 'ought', 'i\'m', 'you\'re',
                         'he\'s', 'she\'s', 'it\'s', 'we\'re', 'they\'re', 'i\'ve',
                         'you\'ve', 'we\'ve', 'they\'ve', 'i\'d', 'you\'d', 'he\'d',
                         'she\'d', 'we\'d', 'they\'d', 'i\'ll', 'you\'ll', 'he\'ll',
                         'she\'ll', 'we\'ll', 'they\'ll', 'isn\'t', 'aren\'t', 'wasn\'t',
                         'weren\'t', 'hasn\'t', 'haven\'t', 'hadn\'t', 'doesn\'t', 'don\'t',
                         'didn\'t', 'won\'t', 'wouldn\'t', 'shan\'t', 'shouldn\'t', 'can\'t',
                         'cannot', 'couldn\'t', 'mustn\'t', 'let\'s', 'that\'s', 'who\'s',
                         'what\'s', 'here\'s', 'there\'s', 'when\'s', 'where\'s', 'why\'s',
                         'how\'s', 'um', 'uh', 'er', 'ah', 'like', 'okay', 'right', 'yeah'}
        self.custom_stopwords = set()
        self.min_word_length = 3
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.regenerate_btn = QPushButton("Regenerate")
        self.regenerate_btn.clicked.connect(self.regenerate_wordcloud)
        controls_layout.addWidget(self.regenerate_btn)
        
        self.status_label = QLabel("No data loaded")
        controls_layout.addWidget(self.status_label, 1)  # Stretch to fill space
        
        layout.addLayout(controls_layout)
        
        # Settings panel
        settings_group = QGroupBox("Word Cloud Settings")
        settings_layout = QFormLayout()
        
        # Min word length
        self.min_length_input = QLineEdit()
        self.min_length_input.setText(str(self.min_word_length))
        self.min_length_input.setMaximumWidth(50)
        self.min_length_input.textChanged.connect(self.update_min_length)
        settings_layout.addRow("Min Word Length:", self.min_length_input)
        
        # Custom stopwords
        self.custom_stopwords_input = QLineEdit()
        self.custom_stopwords_input.setPlaceholderText("Enter comma-separated words to exclude")
        self.custom_stopwords_input.textChanged.connect(self.update_custom_stopwords)
        settings_layout.addRow("Custom Stopwords:", self.custom_stopwords_input)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Word cloud display area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.canvas.mpl_connect('button_press_event', self.on_word_click)
        
        self.scroll_area.setWidget(self.canvas)
        layout.addWidget(self.scroll_area)
        
        # Initialize with empty plot
        self.ax = self.figure.add_subplot(111)
        self.ax.set_axis_off()
        self.ax.text(0.5, 0.5, "No data available", 
                    horizontalalignment='center',
                    verticalalignment='center',
                    transform=self.ax.transAxes,
                    fontsize=14)
        self.canvas.draw()
        
    def update_min_length(self, text):
        """Update minimum word length"""
        try:
            self.min_word_length = max(1, int(text))
        except ValueError:
            self.min_word_length = 3
            self.min_length_input.setText("3")
            
    def update_custom_stopwords(self, text):
        """Update custom stopwords list"""
        words = [w.strip().lower() for w in text.split(',') if w.strip()]
        self.custom_stopwords = set(words)
            
    def process_transcripts(self, transcripts):
        """Process transcript text to extract word frequencies"""
        if not transcripts:
            self.status_label.setText("No transcripts selected")
            return False
            
        self.word_counts = Counter()
        total_words = 0
        
        for path, meta in transcripts.items():
            try:
                # Try to load transcript content
                transcript_path = path
                if not path.endswith('_transcript.txt'):
                    # If not, look for associated transcript
                    transcript_path = path.replace('.mp3', '_transcript.txt')
                
                if os.path.exists(transcript_path):
                    with open(transcript_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Process words
                    words = self.preprocess_text(content)
                    self.word_counts.update(words)
                    total_words += len(words)
            except Exception as e:
                print(f"Error processing transcript {path}: {e}")
                
        if not self.word_counts:
            self.status_label.setText("No words found in transcripts")
            return False
            
        self.status_label.setText(f"Processed {len(transcripts)} transcripts with {total_words} words")
        return True
        
    def preprocess_text(self, text):
        """Preprocess text by tokenizing and removing stopwords"""
        # Simple word tokenization
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # Filter words: remove stopwords, custom stopwords, and short words
        filtered_words = [
            word for word in words 
            if word not in self.stopwords 
            and word not in self.custom_stopwords
            and len(word) >= self.min_word_length
        ]
        return filtered_words
        
    def generate_wordcloud(self):
        """Generate and display the word cloud"""
        if not self.word_counts:
            return
            
        # Clear the figure
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        
        # Generate word cloud
        wordcloud = WordCloud(
            width=800, 
            height=600, 
            background_color='white',
            max_words=200,
            contour_width=1,
            contour_color='steelblue'
        ).generate_from_frequencies(self.word_counts)
        
        # Store word positions for click detection
        self.word_positions = wordcloud.layout_
        
        # Display the word cloud
        self.ax.imshow(wordcloud, interpolation='bilinear')
        self.ax.set_axis_off()
        self.figure.tight_layout(pad=0)
        self.canvas.draw()
        
    def regenerate_wordcloud(self):
        """Regenerate the word cloud with current settings"""
        self.generate_wordcloud()
        
    def on_word_click(self, event):
        """Handle click events on the word cloud"""
        if event.xdata is None or event.ydata is None or not hasattr(self, 'word_positions'):
            return
            
        # Convert matplotlib coordinates to image coordinates
        x, y = int(event.xdata), int(event.ydata)
        
        # Find the closest word to the click position
        min_dist = float('inf')
        closest_word = None
        
        for word, (word_x, word_y, _) in self.word_positions.items():
            dist = (word_x - x)**2 + (word_y - y)**2
            if dist < min_dist:
                min_dist = dist
                closest_word = word
                
        # Emit signal with the clicked word if it's close enough
        if closest_word and min_dist < 1000:  # Threshold for considering a click on a word
            self.word_clicked.emit(closest_word)
            print(f"Word clicked: {closest_word}")
            
    def clear(self):
        """Clear the word cloud"""
        self.word_counts = Counter()
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        self.ax.set_axis_off()
        self.ax.text(0.5, 0.5, "No data available", 
                    horizontalalignment='center',
                    verticalalignment='center',
                    transform=self.ax.transAxes,
                    fontsize=14)
        self.canvas.draw()
        self.status_label.setText("No data loaded")


class TopWordsWidget(QWidget):
    """Widget for displaying top words as a bar chart"""
    
    word_clicked = pyqtSignal(str)  # Signal emitted when a word is clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.word_counts = Counter()
        self.top_n = 20  # Default number of top words to show
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        controls_layout.addWidget(QLabel("Top Words:"))
        self.top_n_input = QLineEdit()
        self.top_n_input.setText(str(self.top_n))
        self.top_n_input.setMaximumWidth(50)
        self.top_n_input.textChanged.connect(self.update_top_n)
        controls_layout.addWidget(self.top_n_input)
        
        self.regenerate_btn = QPushButton("Regenerate")
        self.regenerate_btn.clicked.connect(self.regenerate_chart)
        controls_layout.addWidget(self.regenerate_btn)
        
        self.status_label = QLabel("No data loaded")
        controls_layout.addWidget(self.status_label, 1)  # Stretch to fill space
        
        layout.addLayout(controls_layout)
        
        # Chart display area
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.canvas.mpl_connect('button_press_event', self.on_bar_click)
        
        layout.addWidget(self.canvas)
        
        # Initialize with empty plot
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Top Words")
        self.ax.text(0.5, 0.5, "No data available", 
                    horizontalalignment='center',
                    verticalalignment='center',
                    transform=self.ax.transAxes,
                    fontsize=14)
        self.canvas.draw()
        
    def update_top_n(self, text):
        """Update number of top words to display"""
        try:
            self.top_n = max(5, min(100, int(text)))
        except ValueError:
            self.top_n = 20
            self.top_n_input.setText("20")
            
    def set_word_counts(self, word_counts):
        """Set word counts data"""
        self.word_counts = word_counts
        self.status_label.setText(f"Total unique words: {len(word_counts)}")
        
    def generate_chart(self):
        """Generate and display the bar chart of top words"""
        if not self.word_counts:
            return
            
        # Clear the figure
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        
        # Get top N words
        top_words = dict(self.word_counts.most_common(self.top_n))
        
        # Create bar chart
        bars = self.ax.bar(list(top_words.keys()), list(top_words.values()))
        
        # Add labels and title
        self.ax.set_title(f"Top {self.top_n} Words")
        self.ax.set_xlabel("Words")
        self.ax.set_ylabel("Frequency")
        
        # Rotate x-axis labels for better readability
        plt.setp(self.ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        
        # Store bar positions for click detection
        self.bars = bars
        self.bar_labels = list(top_words.keys())
        
        # Adjust layout
        self.figure.tight_layout()
        self.canvas.draw()
        
    def regenerate_chart(self):
        """Regenerate the chart with current settings"""
        self.generate_chart()
        
    def on_bar_click(self, event):
        """Handle click events on the bar chart"""
        if event.xdata is None or event.ydata is None or not hasattr(self, 'bars'):
            return
            
        # Check if click is on a bar
        for i, bar in enumerate(self.bars):
            if bar.contains(event)[0]:
                word = self.bar_labels[i]
                self.word_clicked.emit(word)
                print(f"Bar clicked: {word}")
                break
                
    def clear(self):
        """Clear the chart"""
        self.word_counts = Counter()
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Top Words")
        self.ax.text(0.5, 0.5, "No data available", 
                    horizontalalignment='center',
                    verticalalignment='center',
                    transform=self.ax.transAxes,
                    fontsize=14)
        self.canvas.draw()
        self.status_label.setText("No data loaded")
