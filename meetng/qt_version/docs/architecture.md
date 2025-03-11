# PowerPlay - AI-Enhanced Meeting Assistant Architecture

## Overview

PowerPlay is a Qt-based application for recording, transcribing, and analyzing meetings in real-time. The application uses a modular architecture with clear separation of concerns between UI components, business logic, and external services.

## Core Components

### 1. Managers

The application uses a manager-based architecture to separate concerns:

- **RecordingManager**: Handles audio recording functionality
  - Manages the AudioRecorderQt class
  - Controls recording state (start, stop, pause, resume)
  - Emits signals for UI updates and audio chunks for processing

- **TranscriptionManager**: Handles real-time transcription
  - Manages the AssemblyAIRealTimeTranscription service
  - Processes audio chunks and retrieves transcription results
  - Detects voice commands/triggers in transcribed text

- **AnalysisManager**: Handles AI analysis of transcribed text
  - Manages the LangChainService for text processing
  - Handles template selection and processing
  - Generates insights and curiosity questions

### 2. Services

Services handle external API interactions and complex processing:

- **AssemblyAIRealTimeTranscription**: Handles real-time transcription using AssemblyAI's API
  - Manages WebSocket connection to AssemblyAI
  - Streams audio data and processes transcription results
  - Includes connection monitoring and automatic reconnection

- **LangChainService**: Handles AI language model interactions
  - Uses OpenAI's API through LangChain
  - Processes text chunks for analysis
  - Manages conversation context and templates

### 3. UI Components

The UI is organized into tabs and components:

- **RecordingTab**: Main interface for recording and real-time transcription
  - Controls for recording, pausing, and stopping
  - Real-time transcript display
  - Analysis results display

- **ImportTab**: Interface for importing and processing audio files
  - File selection and batch processing
  - Transcription service selection
  - Processing options

- **CuriosityTabWidget**: Interface for exploring AI-generated questions
  - Displays questions based on transcript content
  - Allows user to answer questions for further insights

### 4. Utilities

Utility classes provide common functionality:

- **AudioRecorderQt**: Low-level audio recording with PyAudio
  - Captures audio from microphone
  - Provides audio level monitoring
  - Handles file format conversion

- **ConfigurationService**: Centralized configuration management
  - Loads settings from environment variables and config files
  - Provides typed access to configuration values
  - Handles default values and validation

- **Logger**: Centralized logging system
  - Configurable log levels
  - File and console output
  - Context-aware logging

## Signal Flow

The application uses Qt's signal/slot mechanism for communication between components:

1. **Audio Recording Flow**:
   - RecordingManager.audio_chunk_ready → TranscriptionManager.process_audio_chunk
   - RecordingManager.audio_level_changed → UI updates (level indicators)
   - RecordingManager.recording_started/stopped/paused/resumed → UI state updates

2. **Transcription Flow**:
   - TranscriptionManager.transcription_ready → UI updates (transcript display)
   - TranscriptionManager.trigger_detected → RecordingTab voice command handling

3. **Analysis Flow**:
   - AnalysisManager.analysis_complete → UI updates (analysis display)
   - AnalysisManager.questions_ready → CuriosityTabWidget updates

## Threading Model

The application uses a combination of Qt's event loop and Python's threading:

- UI operations run on the main thread
- Long-running operations (recording stop, analysis) run in background threads
- Qt's signal/slot mechanism with QueuedConnection ensures thread safety
- QTimer is used for periodic operations (audio chunk processing, UI updates)

## Configuration and Settings

Settings are managed through:

- Environment variables (.env file)
- QSettings for persistent user preferences
- ConfigurationService for centralized access

## Error Handling

The application uses a consistent error handling pattern:

- Exceptions are caught at appropriate boundaries
- Errors are logged with context
- User-friendly error messages are displayed via signals
- Critical errors trigger appropriate UI state changes
- Automatic recovery is attempted where possible (e.g., transcription reconnection)

## File Management

The application organizes files as follows:

- Recordings: Stored as MP3 files with timestamp-based naming
- Transcripts: Stored as text files alongside recordings
- Analysis: Stored as text files with metadata headers
- Sessions: Grouped by user-defined session names

## Future Extensibility

The architecture is designed for extensibility:

- New transcription services can be added by implementing a common interface
- New analysis templates can be added without code changes
- New UI tabs can be added by extending the tab widget system
- New voice commands can be configured through the settings system
