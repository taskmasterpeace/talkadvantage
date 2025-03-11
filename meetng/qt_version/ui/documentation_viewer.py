from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTextBrowser, QSplitter, QTreeWidget, QTreeWidgetItem,
    QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QIcon, QFont
import os

class DocumentationViewer(QWidget):
    """Widget for displaying application documentation"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        # Main layout
        main_layout = QHBoxLayout(self)
        
        # Create splitter for navigation and content
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Navigation panel (left side)
        nav_panel = QFrame()
        nav_layout = QVBoxLayout(nav_panel)
        
        # Title for navigation
        nav_title = QLabel("Documentation")
        nav_title.setStyleSheet("""
            QLabel {
                font-size: 16pt;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px 5px;
            }
        """)
        nav_layout.addWidget(nav_title)
        
        # Tree widget for navigation
        self.nav_tree = QTreeWidget()
        self.nav_tree.setHeaderHidden(True)
        self.nav_tree.setAnimated(True)
        self.nav_tree.setFont(QFont("Segoe UI", 10))
        self.nav_tree.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 5px;
                background-color: #f8f9fa;
            }
            QTreeWidget::item {
                padding: 5px;
                border-radius: 3px;
            }
            QTreeWidget::item:selected {
                background-color: #9b59b6;
                color: white;
            }
            QTreeWidget::item:hover {
                background-color: #e0e0e0;
            }
        """)
        self.nav_tree.itemClicked.connect(self.on_nav_item_clicked)
        nav_layout.addWidget(self.nav_tree)
        
        # Content panel (right side)
        content_panel = QFrame()
        content_layout = QVBoxLayout(content_panel)
        
        # Content title
        self.content_title = QLabel("Welcome to PowerPlay Documentation")
        self.content_title.setStyleSheet("""
            QLabel {
                font-size: 18pt;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px 5px;
                border-bottom: 1px solid #ddd;
            }
        """)
        content_layout.addWidget(self.content_title)
        
        # Content browser
        self.content_browser = QTextBrowser()
        self.content_browser.setOpenExternalLinks(True)
        self.content_browser.setStyleSheet("""
            QTextBrowser {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                background-color: white;
                font-family: 'Segoe UI', sans-serif;
                font-size: 11pt;
                line-height: 1.5;
            }
        """)
        content_layout.addWidget(self.content_browser)
        
        # Add panels to splitter
        splitter.addWidget(nav_panel)
        splitter.addWidget(content_panel)
        
        # Set initial sizes (30% navigation, 70% content)
        splitter.setSizes([300, 700])
        
        # Add splitter to main layout
        main_layout.addWidget(splitter)
        
        # Populate navigation tree
        self.populate_navigation()
        
        # Load welcome content
        self.load_welcome_content()
        
    def populate_navigation(self):
        """Populate the navigation tree with documentation sections"""
        # Getting Started
        getting_started = QTreeWidgetItem(self.nav_tree, ["Getting Started"])
        getting_started.setIcon(0, QIcon("qt_version/resources/icons/start.png"))
        QTreeWidgetItem(getting_started, ["Welcome"])
        QTreeWidgetItem(getting_started, ["Quick Start Guide"])
        QTreeWidgetItem(getting_started, ["Key Features"])
        
        # Features
        features = QTreeWidgetItem(self.nav_tree, ["Features"])
        features.setIcon(0, QIcon("qt_version/resources/icons/features.png"))
        
        # Audio Import
        audio_import = QTreeWidgetItem(features, ["Audio Import"])
        QTreeWidgetItem(audio_import, ["Supported Formats"])
        QTreeWidgetItem(audio_import, ["Batch Processing"])
        
        # Live Recording
        live_recording = QTreeWidgetItem(features, ["Live Recording"])
        QTreeWidgetItem(live_recording, ["Recording Controls"])
        QTreeWidgetItem(live_recording, ["Real-time Transcription"])
        
        # AI Analysis
        ai_analysis = QTreeWidgetItem(features, ["AI Analysis"])
        QTreeWidgetItem(ai_analysis, ["Analysis Templates"])
        QTreeWidgetItem(ai_analysis, ["Template Wizard"])
        QTreeWidgetItem(ai_analysis, ["Conversation Compass"])
        QTreeWidgetItem(ai_analysis, ["Curiosity Engine"])
        
        # Library Management
        library = QTreeWidgetItem(features, ["Library Management"])
        QTreeWidgetItem(library, ["Organizing Recordings"])
        QTreeWidgetItem(library, ["Search and Filter"])
        
        # Advanced Topics
        advanced = QTreeWidgetItem(self.nav_tree, ["Advanced Topics"])
        advanced.setIcon(0, QIcon("qt_version/resources/icons/advanced.png"))
        QTreeWidgetItem(advanced, ["Custom Templates"])
        QTreeWidgetItem(advanced, ["API Configuration"])
        QTreeWidgetItem(advanced, ["Performance Optimization"])
        
        # Troubleshooting
        troubleshooting = QTreeWidgetItem(self.nav_tree, ["Troubleshooting"])
        troubleshooting.setIcon(0, QIcon("qt_version/resources/icons/troubleshoot.png"))
        QTreeWidgetItem(troubleshooting, ["Common Issues"])
        QTreeWidgetItem(troubleshooting, ["Error Messages"])
        QTreeWidgetItem(troubleshooting, ["Support Resources"])
        
        # Expand the first level
        self.nav_tree.expandItem(getting_started)
        
    def on_nav_item_clicked(self, item, column):
        """Handle navigation item click"""
        # Get the full path of the clicked item
        path = []
        current = item
        while current is not None:
            path.insert(0, current.text(0))
            current = current.parent()
            
        # Update content based on path
        self.update_content(path)
        
    def update_content(self, path):
        """Update content based on navigation path"""
        # Update title
        if len(path) > 0:
            self.content_title.setText(" > ".join(path))
        
        # Load content based on path
        content = self.get_content_for_path(path)
        self.content_browser.setHtml(content)
        
    def get_content_for_path(self, path):
        """Get HTML content for the given navigation path"""
        # This would ideally load from files or a database
        # For now, we'll use hardcoded content for demonstration
        
        # Welcome page
        if len(path) == 2 and path[0] == "Getting Started" and path[1] == "Welcome":
            return self.get_welcome_content()
            
        # Template Wizard
        elif len(path) == 3 and path[0] == "Features" and path[1] == "AI Analysis" and path[2] == "Template Wizard":
            return self.get_template_wizard_content()
            
        # Conversation Compass
        elif len(path) == 3 and path[0] == "Features" and path[1] == "AI Analysis" and path[2] == "Conversation Compass":
            return self.get_conversation_compass_content()
            
        # Curiosity Engine
        elif len(path) == 3 and path[0] == "Features" and path[1] == "AI Analysis" and path[2] == "Curiosity Engine":
            return self.get_curiosity_engine_content()
            
        # Default content with path info
        else:
            return f"""
            <h1>{" > ".join(path)}</h1>
            <p>Documentation for this section is under development.</p>
            <p>This will contain detailed information about {path[-1]}.</p>
            """
    
    def load_welcome_content(self):
        """Load the welcome content"""
        welcome_content = self.get_welcome_content()
        self.content_browser.setHtml(welcome_content)
        
    def get_welcome_content(self):
        """Get the welcome page content"""
        return """
        <div style="max-width: 800px; margin: 0 auto;">
            <h1 style="color: #9b59b6; text-align: center;">Welcome to PowerPlay</h1>
            
            <p style="font-size: 16px; line-height: 1.6;">
                PowerPlay is an AI-enhanced meeting assistant designed to help you capture, analyze, 
                and extract insights from your conversations. Whether you're recording meetings, 
                interviews, or any important discussion, PowerPlay helps you focus on the 
                conversation while it handles the documentation.
            </p>
            
            <h2 style="color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 10px;">
                Key Features
            </h2>
            
            <ul style="font-size: 15px; line-height: 1.6;">
                <li><strong>Audio Import</strong> - Process existing audio files from various sources</li>
                <li><strong>Live Recording</strong> - Record and transcribe conversations in real-time</li>
                <li><strong>AI Analysis</strong> - Extract insights, decisions, and action items automatically</li>
                <li><strong>Template Wizard</strong> - Create custom AI assistants for specific conversation types</li>
                <li><strong>Conversation Compass</strong> - Visualize and navigate complex discussions</li>
                <li><strong>Curiosity Engine</strong> - Generate insightful questions to enhance understanding</li>
                <li><strong>Library Management</strong> - Organize and search your recordings efficiently</li>
            </ul>
            
            <h2 style="color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 10px;">
                Getting Started
            </h2>
            
            <p style="font-size: 15px; line-height: 1.6;">
                To begin using PowerPlay, you'll need to:
            </p>
            
            <ol style="font-size: 15px; line-height: 1.6;">
                <li>Configure your API keys in Settings</li>
                <li>Choose whether to import existing audio or start a new recording</li>
                <li>Select an analysis template or create a custom one with the Template Wizard</li>
                <li>Review and save your analyzed conversations in the Library</li>
            </ol>
            
            <p style="font-size: 15px; line-height: 1.6; margin-top: 30px; text-align: center; color: #7f8c8d;">
                Explore the documentation sections on the left to learn more about specific features.
            </p>
        </div>
        """
        
    def get_template_wizard_content(self):
        """Get the Template Wizard documentation content"""
        return """
        <div style="max-width: 800px; margin: 0 auto;">
            <h1 style="color: #9b59b6;">Template Wizard</h1>
            
            <p style="font-size: 16px; line-height: 1.6;">
                The Template Wizard helps you create customized AI assistant profiles tailored to specific 
                conversation types and analysis needs. These templates determine how the AI analyzes and 
                responds to your conversations.
            </p>
            
            <h2 style="color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 10px;">
                How It Works
            </h2>
            
            <p style="font-size: 15px; line-height: 1.6;">
                The wizard guides you through a series of questions to understand your needs:
            </p>
            
            <ol style="font-size: 15px; line-height: 1.6;">
                <li><strong>Expert Type</strong> - Choose the primary expertise needed (Meeting Analyst, Executive Coach, etc.)</li>
                <li><strong>Desired Outcomes</strong> - Define what results you want to achieve</li>
                <li><strong>Engagement Style</strong> - Specify how the AI should interact with the content</li>
                <li><strong>Focus Areas</strong> - Identify elements that need special attention</li>
                <li><strong>Recommendation Type</strong> - Define what guidance would be most valuable</li>
                <li><strong>Conversation Mode</strong> - Choose between tracking or guided conversation analysis</li>
                <li><strong>Bookmark Types</strong> - Select special markers for important content</li>
                <li><strong>Curiosity Focus</strong> - Define what the Curiosity Engine should emphasize</li>
            </ol>
            
            <h2 style="color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 10px;">
                Using Templates
            </h2>
            
            <p style="font-size: 15px; line-height: 1.6;">
                After creating templates with the wizard:
            </p>
            
            <ul style="font-size: 15px; line-height: 1.6;">
                <li>Templates appear in the template selection dropdown in various parts of the application</li>
                <li>Apply templates to new recordings or existing transcripts</li>
                <li>Templates affect how the Conversation Compass visualizes discussions</li>
                <li>Templates configure what questions the Curiosity Engine generates</li>
                <li>Templates determine what bookmarks are available for marking important points</li>
            </ul>
            
            <div style="background-color: #f8f9fa; border-left: 4px solid #9b59b6; padding: 15px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #2c3e50;">Pro Tip</h3>
                <p style="margin-bottom: 0;">
                    Create different templates for different meeting types. For example, use a "Decision Meeting" 
                    template for meetings where important choices are made, and a "Brainstorming Session" template 
                    for creative discussions.
                </p>
            </div>
        </div>
        """
        
    def get_conversation_compass_content(self):
        """Get the Conversation Compass documentation content"""
        return """
        <div style="max-width: 800px; margin: 0 auto;">
            <h1 style="color: #9b59b6;">Conversation Compass</h1>
            
            <p style="font-size: 16px; line-height: 1.6;">
                The Conversation Compass is a powerful visualization tool that helps you navigate and understand 
                complex conversations. It creates an interactive map of your discussion, showing relationships 
                between topics, questions, and decisions.
            </p>
            
            <h2 style="color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 10px;">
                Key Features
            </h2>
            
            <ul style="font-size: 15px; line-height: 1.6;">
                <li><strong>Topic Visualization</strong> - See how conversation topics relate to each other</li>
                <li><strong>Decision Highlighting</strong> - Easily identify where important decisions were made</li>
                <li><strong>Question Tracking</strong> - Follow questions and their answers throughout the discussion</li>
                <li><strong>Interactive Navigation</strong> - Click on nodes to jump to that part of the transcript</li>
                <li><strong>Multiple Layouts</strong> - View conversations as radial maps, hierarchies, or force-directed graphs</li>
            </ul>
            
            <h2 style="color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 10px;">
                Conversation Modes
            </h2>
            
            <p style="font-size: 15px; line-height: 1.6;">
                The Conversation Compass supports two primary modes:
            </p>
            
            <div style="display: flex; margin: 20px 0;">
                <div style="flex: 1; background-color: #f8f9fa; padding: 15px; margin-right: 10px; border-radius: 5px;">
                    <h3 style="color: #2c3e50; margin-top: 0;">Tracking Mode</h3>
                    <p style="font-size: 14px; line-height: 1.5;">
                        Follows the natural flow of conversation. Best for open discussions, brainstorming sessions, 
                        and free-flowing meetings. Creates a radial or force-directed visualization.
                    </p>
                </div>
                <div style="flex: 1; background-color: #f8f9fa; padding: 15px; margin-left: 10px; border-radius: 5px;">
                    <h3 style="color: #2c3e50; margin-top: 0;">Guided Mode</h3>
                    <p style="font-size: 14px; line-height: 1.5;">
                        Helps direct the conversation toward specific goals. Best for interviews, negotiations, 
                        and structured meetings. Creates a hierarchical visualization.
                    </p>
                </div>
            </div>
            
            <h2 style="color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 10px;">
                Using the Compass
            </h2>
            
            <ol style="font-size: 15px; line-height: 1.6;">
                <li>Select a template that defines the conversation mode</li>
                <li>As the conversation progresses, the Compass builds a visual map</li>
                <li>Use the zoom and pan controls to navigate large conversations</li>
                <li>Click on nodes to jump to specific parts of the transcript</li>
                <li>Use the layout options to change how the conversation is visualized</li>
                <li>Export visualizations for use in reports or presentations</li>
            </ol>
        </div>
        """
        
    def get_curiosity_engine_content(self):
        """Get the Curiosity Engine documentation content"""
        return """
        <div style="max-width: 800px; margin: 0 auto;">
            <h1 style="color: #9b59b6;">Curiosity Engine</h1>
            
            <p style="font-size: 16px; line-height: 1.6;">
                The Curiosity Engine generates insightful questions about your conversations to enhance 
                understanding and uncover hidden context. It helps you think more deeply about the content 
                and fills in missing information.
            </p>
            
            <h2 style="color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 10px;">
                How It Works
            </h2>
            
            <p style="font-size: 15px; line-height: 1.6;">
                The Curiosity Engine analyzes your conversation and generates questions based on:
            </p>
            
            <ul style="font-size: 15px; line-height: 1.6;">
                <li><strong>Content Gaps</strong> - Identifies missing information that would help understanding</li>
                <li><strong>Ambiguities</strong> - Finds unclear statements that need clarification</li>
                <li><strong>Implied Context</strong> - Detects assumptions that might need verification</li>
                <li><strong>Decision Factors</strong> - Explores reasoning behind decisions</li>
                <li><strong>Template Focus</strong> - Emphasizes areas specified in your template</li>
            </ul>
            
            <h2 style="color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 10px;">
                Question Types
            </h2>
            
            <p style="font-size: 15px; line-height: 1.6;">
                The engine generates several types of questions:
            </p>
            
            <ul style="font-size: 15px; line-height: 1.6;">
                <li><strong>Yes/No</strong> - Simple binary questions to confirm understanding</li>
                <li><strong>Multiple Choice</strong> - Questions with predefined options</li>
                <li><strong>Multiple Choice with Fill-in</strong> - Options plus an "other" field</li>
                <li><strong>Speaker Identification</strong> - Questions about who said what</li>
                <li><strong>Meeting Type</strong> - Questions about the nature of the conversation</li>
            </ul>
            
            <h2 style="color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 10px;">
                Using the Engine
            </h2>
            
            <ol style="font-size: 15px; line-height: 1.6;">
                <li>After analyzing a conversation, click the "Generate Questions" button</li>
                <li>Review the questions and provide answers based on your knowledge</li>
                <li>The system incorporates your answers to enhance the analysis</li>
                <li>Questions and answers are saved with the conversation</li>
            </ol>
            
            <div style="background-color: #f8f9fa; border-left: 4px solid #9b59b6; padding: 15px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #2c3e50;">Pro Tip</h3>
                <p style="margin-bottom: 0;">
                    Use the Template Wizard to customize what the Curiosity Engine focuses on. For example, 
                    in a decision-making meeting, configure it to ask more questions about the factors that 
                    influenced decisions.
                </p>
            </div>
        </div>
        """
