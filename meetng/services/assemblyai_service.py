import os
import assemblyai as aai
from .base_service import TranscriptionService

class AssemblyAITranscriptionService(TranscriptionService):
    def __init__(self):
        super().__init__()
        self.transcriber = None
        
    def get_env_key(self):
        return 'ASSEMBLYAI_API_KEY'
        
    def setup(self, api_key=None):
        if super().setup(api_key):
            aai.settings.api_key = self._api_key
            self.transcriber = aai.Transcriber()
            return True
        return False
        
    def transcribe(self, file_path: str, config: dict = None) -> str:
        """
        Transcribe an audio file using AssemblyAI.
        
        Args:
            file_path: Path to the audio file
            config: Configuration dictionary with transcription options
            
        Returns:
            Formatted transcript text
            
        Raises:
            ValueError: If transcriber is not initialized or config is invalid
            AssemblyAIError: If transcription fails
            IOError: If file cannot be accessed
        """
        print(f"AssemblyAI: Starting transcription for {file_path}")
        if not self.transcriber:
            raise ValueError("AssemblyAI transcriber not initialized")
            
        if not os.path.exists(file_path):
            raise IOError(f"Audio file not found: {file_path}")
            
        # Ensure config exists
        config = config or {}
            
        try:
            # Configure enabled features
            config_params = {
                'speech_model': (aai.SpeechModel.best 
                               if config.get('model') == 'best' 
                               else aai.SpeechModel.nano)
            }
            
            # Add optional features
            feature_mapping = {
                'speaker_labels': 'speaker_detection',
                'auto_chapters': 'chapters',
                'entity_detection': 'entity',
                'auto_highlights': 'keyphrases',
                'summarization': 'summary'
            }
            
            for aai_feature, config_key in feature_mapping.items():
                if config.get(config_key):
                    config_params[aai_feature] = True
                    
            if self._debug_mode:
                print(f"AssemblyAI: Using config params: {config_params}")
            
            transcription_config = aai.TranscriptionConfig(**config_params)
            
            try:
                transcript = self.transcriber.transcribe(
                    file_path,
                    transcription_config
                )
            except aai.TranscriptionError as e:
                raise ValueError(f"Transcription failed: {str(e)}")
            
            if transcript.status == aai.TranscriptStatus.error:
                raise ValueError(f"Transcription failed: {transcript.error}")
                
            # Build formatted output
            formatted_transcript = self.format_transcript(transcript, config)
            if self._debug_mode:
                print(f"Generated transcript length: {len(formatted_transcript)} chars")
            return formatted_transcript
            
        except Exception as e:
            print(f"AssemblyAI: Error during transcription: {str(e)}")
            raise
            
    def format_transcript(self, transcript, config):
        """Format the transcript with all enabled features"""
        formatted_text = []
            
        def format_timestamp(ms):
            """Convert milliseconds to HH:MM:SS format"""
            seconds = int(ms / 1000)
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
        # Add summary if enabled
        if config.get('summary') and transcript.summary:
            formatted_text.append("=== Summary ===")
            formatted_text.append(transcript.summary)
            formatted_text.append("\n")
            
        # Add chapters if enabled
        if config.get('chapters') and transcript.chapters:
            formatted_text.append("=== Chapters ===")
            for chapter in transcript.chapters:
                formatted_text.append(f"{chapter.headline}")
                formatted_text.append(f"Start: {chapter.start}ms")
                formatted_text.append(f"Summary: {chapter.summary}")
                formatted_text.append("")
            formatted_text.append("\n")
            
        # Add entities if enabled
        if config.get('entity') and transcript.entities:
            formatted_text.append("=== Entities ===")
            for entity in transcript.entities:
                formatted_text.append(f"{entity.text} ({entity.entity_type})")
            formatted_text.append("\n")
            
        # Add key phrases if enabled
        if config.get('keyphrases') and transcript.key_phrases:
            formatted_text.append("=== Key Phrases ===")
            for phrase in transcript.key_phrases:
                formatted_text.append(phrase)
            formatted_text.append("\n")
            
        # Add main transcript
        formatted_text.append("=== Transcript ===")
        if config.get('speaker_labels'):
            for utterance in transcript.utterances:
                start_time = format_timestamp(utterance.start) if config.get('timestamps') else ""
                prefix = f"[{start_time}] " if start_time else ""
                formatted_text.append(f"{prefix}Speaker {utterance.speaker}: {utterance.text}")
        else:
            if config.get('timestamps'):
                # Get sentences with timestamps
                for sentence in transcript.get_sentences():
                    start_time = format_timestamp(sentence.start)
                    formatted_text.append(f"[{start_time}] {sentence.text}")
            else:
                formatted_text.append(transcript.text)
            
        return "\n".join(formatted_text)
