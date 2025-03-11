# PowerPlay Proactive Meeting Agent

A Python-based desktop application for real-time meeting transcription, analysis, and insights using AI.

## Core Features

- Real-time audio transcription using AssemblyAI
- Live AI analysis of conversation content
- Speaker diarization (speaker identification)
- Template-based insight generation
- Customizable analysis templates
- Multi-format audio support (MP3, WAV, M4A)

## Recording Features

- Real-time audio recording with visual feedback
- Adjustable processing intervals (10s, 45s, 5m, 10m)
- Audio level monitoring
- Speaker diarization toggle
- Automatic punctuation and formatting
- Timestamp markers
- Function key shortcuts for marking important moments

## Analysis System

The application uses a sophisticated three-part prompting system for AI analysis:

### System Prompt (Base)
- Core instruction set for the AI
- Handles technical aspects like chunk processing
- Maintains context across transcript segments
- Not editable by users

### User Prompt
The User Prompt defines WHO you are and WHY you need the analysis. It provides context about your role and needs.

Examples:
```
As a project manager, I need to track action items and responsibilities assigned during the meeting.

As a medical professional, I need to identify key diagnostic discussions and treatment decisions.

As a legal professional, I need to track important statements and agreements made during negotiations.
```

### Template Prompt
The Template Prompt defines HOW you want the information structured and WHAT specific aspects to analyze.

Examples:
```
Analyze this segment and provide:
1. Key Discussion Points (bullet points)
2. Action Items (with assignee and deadline)
3. Decisions Made
4. Follow-up Questions

Structure the analysis as:
- Technical Requirements: [List]
- Implementation Details: [List]
- Risk Factors: [List]
- Next Steps: [List]

Provide a summary with:
- Patient Symptoms
- Diagnostic Discussion
- Treatment Recommendations
- Follow-up Plan
```

## Template Management

- Create and edit custom templates
- Save templates for reuse
- Switch templates during live sessions
- Template categories for different use cases

## Real-time Display

- Split-screen interface showing:
  * Live transcript with speaker identification
  * AI insights and analysis
- Visual audio level indicator
- Recording status and duration
- Word count and statistics

## Requirements

- Python 3.8+
- See requirements.txt for Python package dependencies
- OpenAI API key (for LangChain integration)
- AssemblyAI API key (for real-time transcription)

## Installation

1. Clone the repository:
```bash
git clone [your-repo-url]
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a .env file with your API keys:
```
OPENAI_API_KEY=your_key_here
ASSEMBLYAI_API_KEY=your_key_here
```

## Usage

Run the main application:
```bash
python transcription_app.py
```

## Advanced Features

- Speaker Statistics: Track speaking time and participation
- Export Options: Save transcripts and analysis in multiple formats
- Search/Filter: Find specific content in transcripts
- Confidence Highlighting: Visual indication of transcription confidence
- Auto-save: Periodic saving of transcripts and analysis

## License

MIT License - See LICENSE file for details
# PowerPlay - AI-Enhanced Meeting Assistant

PowerPlay is an advanced AI-powered application designed to enhance your meeting experience by providing real-time transcription, analysis, and insights from your conversations.

## Features

- **Real-time Transcription**: Capture meeting content accurately using AssemblyAI's powerful speech recognition
- **AI Analysis**: Get intelligent summaries, action items, and decision tracking using OpenAI's language models
- **Curiosity Engine**: Gain deeper insights through contextual questions about your meetings
- **Modern Qt Interface**: Enjoy a clean, responsive user experience with dark mode support

## Getting Started

### Prerequisites

- Python 3.8 or higher
- PyQt6 for the user interface
- OpenAI API key
- AssemblyAI API key

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Launch the application:
   ```
   python main.py
   ```

### First-time Setup

1. When you first launch PowerPlay, you'll be prompted to enter your API keys
2. Go to Settings to configure:
   - API keys (OpenAI and AssemblyAI)
   - Model selection
   - Interface preferences
   - Curiosity Engine settings

## Using PowerPlay

### Main Interface

The main window provides access to all PowerPlay features:
- Start/stop recording
- View real-time transcription
- Select analysis templates
- Access settings and help

### Analysis Templates

Choose from several built-in templates:
- **Meeting Summary**: Get a concise overview of key points
- **Action Items**: Extract tasks and assignments
- **Decision Tracking**: Identify and log decisions made

### Curiosity Engine

The Curiosity Engine generates contextual questions about your meetings to help you:
- Gain deeper insights
- Clarify important points
- Uncover underlying context

Questions appear in a dialog and can be:
- Yes/No questions
- Multiple choice questions
- Multiple choice with custom answers

### Settings

Configure PowerPlay through the Settings dialog:
- API keys management
- Model selection (GPT-4o Mini, GPT-4o, GPT-o1)
- Dark mode toggle
- Curiosity Engine customization
- Debug options

## Troubleshooting

If you encounter issues:
1. Check your API keys in Settings
2. Ensure your internet connection is stable
3. Try restarting the application
4. Check the console for error messages if debug mode is enabled

## Privacy & Security

PowerPlay takes your privacy seriously:
- API keys are stored securely in your local settings database
- Transcripts are processed using your personal API accounts
- No data is shared with third parties without your consent

## License

[License information]

## Acknowledgments

- OpenAI for providing the language models
- AssemblyAI for speech recognition capabilities
- PyQt6 for the user interface framework
