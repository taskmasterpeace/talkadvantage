from typing import Dict, List, Optional
from dataclasses import dataclass, field
import json
import os

@dataclass
class BookmarkDefinition:
    """Definition for template-specific bookmarks/commands"""
    name: str  # Display name (e.g. "Start Interview")
    bookmark_type: str  # Type of bookmark: "marker" or "voice_command"
    key_shortcut: str  # Keyboard shortcut (e.g. "Ctrl+1")
    voice_trigger: str  # Voice command phrase (e.g. "start interview")
    content: str = ""  # Content/text to insert for markers
    description: str = ""  # Optional description

@dataclass
class VisualizationSettings:
    """Settings for conversation tree visualization"""
    default_layout: str = "radial"  # radial, hierarchical, force-directed
    node_color_scheme: str = "default"  # default, role-based, sentiment
    highlight_decisions: bool = True
    highlight_questions: bool = True
    expand_level: int = 1  # Default expansion level (0=collapsed, -1=all)

@dataclass
class PromptTemplate:
    """
    Defines the structure of an analysis template
    
    Attributes:
        name: Unique identifier for the template
        user_prompt: Defines WHO perspective (e.g. "As a meeting participant...")
        template_prompt: Defines HOW to analyze (specific format and requirements)
        system_prompt: Defines the AI's role and base behavior (required, no default)
        description: Brief explanation of template's purpose
        bookmarks: List of template-specific bookmarks/commands
        visualization: Settings for tree visualization
        curiosity_prompt: Custom prompt for the Curiosity Engine
        conversation_mode: Mode for Conversation Compass ("tracking" or "guided")
    """
    name: str
    user_prompt: str
    template_prompt: str
    system_prompt: str  # Required field, no default value
    description: str = ""  # Optional field with default value
    bookmarks: List[BookmarkDefinition] = field(default_factory=list)
    visualization: VisualizationSettings = field(default_factory=VisualizationSettings)
    
    # New fields for enhanced integration
    curiosity_prompt: str = ""  # Custom prompt for the Curiosity Engine
    conversation_mode: str = "tracking"  # "tracking" or "guided"
    
class TemplateManager:
    def __init__(self, template_dir: str = "templates"):
        self.template_dir = template_dir
        self.templates: Dict[str, PromptTemplate] = {}
        self._load_default_templates()
        self._load_custom_templates()
        
    def _load_default_templates(self):
        """
        Load default built-in templates with custom system prompts
        Each template has:
        1. Name: Template identifier
        2. Description: What the template does
        3. User Context: WHO perspective
        4. System Prompt: AI's role and behavior
        5. Template Instructions: HOW to analyze
        6. Curiosity Prompt: Custom prompt for the Curiosity Engine
        7. Conversation Mode: "tracking" or "guided"
        """
        default_templates = [
            PromptTemplate(
                name="*Full Analysis",
                description="Complete analysis of the entire conversation",
                user_prompt="Analyze the complete transcript to provide a comprehensive understanding.",
                system_prompt="""You are an AI assistant performing comprehensive conversation analysis. Your role is to:
1. Analyze the entire conversation context
2. Identify key themes, decisions, and action items
3. Track participant contributions and commitments
4. Highlight important connections and insights
5. Maintain a professional and thorough analysis style""",
                template_prompt="""Please provide a thorough analysis of the entire conversation:

1. Overall Summary
   - Main topics and themes
   - Key narrative flow
   - Important context

2. Key Elements
   - Critical decisions made
   - Action items and assignments
   - Questions raised and answers provided
   - Important dates or deadlines mentioned

3. Participant Analysis
   - Key contributions
   - Responsibilities assigned
   - Follow-up commitments

4. Next Steps
   - Immediate actions required
   - Scheduled follow-ups
   - Open items requiring attention

5. Additional Insights
   - Potential challenges identified
   - Opportunities highlighted
   - Important connections between topics""",
                bookmarks=[
                    BookmarkDefinition(
                        name="New Topic",
                        bookmark_type="marker",
                        key_shortcut="Ctrl+1",
                        voice_trigger="new topic",
                        content="=== New Topic ===",
                        description="Mark the start of a new discussion topic"
                    ),
                    BookmarkDefinition(
                        name="Decision Made",
                        bookmark_type="marker",
                        key_shortcut="Ctrl+2", 
                        voice_trigger="mark decision",
                        content="[DECISION]",
                        description="Mark an important decision point"
                    ),
                    BookmarkDefinition(
                        name="Action Item",
                        bookmark_type="marker",
                        key_shortcut="Ctrl+3",
                        voice_trigger="action item",
                        content="[ACTION]",
                        description="Mark an assigned task or action item"
                    ),
                    BookmarkDefinition(
                        name="User Speaking",
                        bookmark_type="marker",
                        key_shortcut="Ctrl+U",
                        voice_trigger="me speaking",
                        content="[USER]",
                        description="Mark when the user is speaking"
                    )
                ],
                # New fields
                curiosity_prompt="""[SYSTEM INSTRUCTIONS - DO NOT MODIFY THIS SECTION]
    You are an expert active listener analyzing meeting transcripts. 
    Generate 2-3 insightful questions that would help understand the context better.

    [QUESTION TYPES - DO NOT MODIFY THESE TYPES]
    Question types:
    - YES_NO: Simple yes/no questions
    - MULTIPLE_CHOICE: Questions with predefined options (provide 3-4 choices)
    - MULTIPLE_CHOICE_FILL: Multiple choice with an "other" option (provide 3-4 choices)
    - SPEAKER_IDENTIFICATION: Questions about who said specific statements
    - MEETING_TYPE: Questions about the type of meeting/conversation

    [CUSTOMIZABLE GUIDELINES - YOU CAN MODIFY THIS SECTION]
    Generate questions that:
    - Are relevant to the transcript content
    - Help clarify important points
    - Uncover underlying context
    - Are concise and clear
    - Have meaningful multiple choice options when applicable

    [OUTPUT FORMAT - DO NOT MODIFY THIS SECTION]
    Return a list of questions in the specified format.""",
                conversation_mode="tracking"
            ),
            PromptTemplate(
                name="Meeting Summary",
                description="Comprehensive meeting note-taking and summarization",
                user_prompt="As a meeting participant, I need clear, organized notes that highlight important discussions and outcomes.",
                system_prompt="""You are an AI assistant focused on meeting summarization. Your role is to:
1. Extract and organize key discussion points
2. Identify and list all action items and assignments
3. Document important decisions made
4. Track questions and their answers
5. Maintain clear, concise, and professional summaries""",
                template_prompt="Create a structured summary including: 1) Key Points Discussed 2) Action Items 3) Decisions Made 4) Follow-up Questions",
                bookmarks=[],
                curiosity_prompt="""Generate questions that help clarify meeting outcomes and action items.
Focus on:
- Responsibility assignments
- Timeline clarifications
- Decision rationales
- Implementation details""",
                conversation_mode="tracking"
            ),
            PromptTemplate(
                name="Interview Coach",
                description="Real-time interview feedback and guidance",
                user_prompt="As an interview candidate, I need insights on my responses and suggestions for improvement.",
                system_prompt="""You are an AI interview coach focused on providing constructive feedback. Your role is to:
1. Evaluate response clarity and effectiveness
2. Identify strong communication points
3. Suggest specific improvements
4. Guide better interview techniques
5. Maintain supportive and constructive tone""",
                template_prompt="Analyze the response for: 1) Clarity and relevance 2) Areas of strength 3) Potential improvements 4) Suggested follow-ups",
                bookmarks=[],
                curiosity_prompt="""Generate questions that help the interview candidate reflect on their responses.
Focus on:
- Self-assessment of performance
- Alternative approaches they could have taken
- Preparation for follow-up questions
- Specific examples they could have used""",
                conversation_mode="guided"
            ),
            PromptTemplate(
                name="Negotiation Assistant",
                description="Strategic negotiation guidance and analysis",
                user_prompt="As a negotiator, I need tactical insights and suggestions for strengthening my position.",
                system_prompt="""You are an AI negotiation strategist. Your role is to:
1. Analyze negotiation positions and dynamics
2. Identify leverage points and opportunities
3. Suggest effective counter-arguments
4. Recommend strategic approaches
5. Maintain focus on win-win outcomes""",
                template_prompt="Provide analysis of: 1) Key positions stated 2) Potential leverage points 3) Suggested counter-points 4) Strategic recommendations",
                bookmarks=[],
                curiosity_prompt="""Generate questions that help the negotiator understand the dynamics at play.
Focus on:
- Underlying interests of all parties
- Potential concessions and trade-offs
- Power dynamics and leverage points
- Alternative approaches to consider""",
                conversation_mode="guided"
            ),
            PromptTemplate(
                name="Expand & Explain",
                description="Detailed analysis and explanation of content",
                user_prompt="Im Robert Task, Im just watching",
                system_prompt="""You are an AI assistant focused on explaining and clarifying technical content. Your role is to:
1. Identify and explain technical terminology
2. Provide relevant technical context
3. Break down complex concepts
4. Clarify technical relationships
5. Maintain accuracy and clarity""",
                template_prompt="""For the given transcript segment, please:

Terminology Clarification:
Identify and define any technical terms, acronyms, slang, software, service, hardward or jargon used.
Contextual Background:
Offer background information pertinent to the topics discussed, enhancing understanding of the subject matter. Only if it is important.
Detailed Explanations:
Expand on key points, providing in-depth explanations to elucidate complex ideas or statements.
Summarization:
Summarize the main ideas in a clear and concise manner, ensuring the core messages are easily grasped.
Ensure that all expansions and explanations are directly related to the content of the transcript and do not introduce external information.""",
                bookmarks=[],
                curiosity_prompt="""Generate questions that help clarify technical concepts and terminology.
Focus on:
- Technical term definitions
- Conceptual understanding
- Practical applications
- Relationships between technical components""",
                conversation_mode="tracking"
            )
        ]
        
        for template in default_templates:
            self.templates[template.name] = template
            
    def _load_custom_templates(self):
        """Load custom templates from file system"""
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)
            return
            
        for filename in os.listdir(self.template_dir):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(self.template_dir, filename), 'r') as f:
                        data = json.load(f)
                        bookmarks = [
                            BookmarkDefinition(
                                name=bm["name"],
                                key_shortcut=bm["key_shortcut"],
                                voice_trigger=bm["voice_trigger"],
                                description=bm.get("description", "")
                            )
                            for bm in data.get("bookmarks", [])
                        ]
                        # Load visualization settings if available
                        vis_settings = data.get("visualization", {})
                        visualization = VisualizationSettings(
                            default_layout=vis_settings.get("default_layout", "radial"),
                            node_color_scheme=vis_settings.get("node_color_scheme", "default"),
                            highlight_decisions=vis_settings.get("highlight_decisions", True),
                            highlight_questions=vis_settings.get("highlight_questions", True),
                            expand_level=vis_settings.get("expand_level", 1)
                        )
                        
                        template_data = {
                            "name": data["name"],
                            "user_prompt": data["user_prompt"],
                            "template_prompt": data["template_prompt"],
                            "system_prompt": data.get("system_prompt", ""),
                            "description": data.get("description", ""),
                            "bookmarks": bookmarks,
                            "visualization": visualization,
                            # New fields with defaults for backward compatibility
                            "curiosity_prompt": data.get("curiosity_prompt", ""),
                            "conversation_mode": data.get("conversation_mode", "tracking")
                        }
                        template = PromptTemplate(**template_data)
                        self.templates[template.name] = template
                except Exception as e:
                    print(f"Error loading template {filename}: {e}")
                    
    def save_template(self, template: PromptTemplate) -> bool:
        """Save a new or updated template"""
        try:
            # Store template
            self.templates[template.name] = template
            
            # Save to file system
            if not os.path.exists(self.template_dir):
                os.makedirs(self.template_dir)
                
            filename = f"{template.name.lower().replace(' ', '_')}.json"
            filepath = os.path.join(self.template_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump({
                    "name": template.name,
                    "user_prompt": template.user_prompt,
                    "template_prompt": template.template_prompt,
                    "system_prompt": template.system_prompt,
                    "description": template.description,
                    "bookmarks": [
                        {
                            "name": bm.name,
                            "key_shortcut": bm.key_shortcut,
                            "voice_trigger": bm.voice_trigger,
                            "description": bm.description
                        }
                        for bm in template.bookmarks
                    ],
                    "visualization": {
                        "default_layout": template.visualization.default_layout,
                        "node_color_scheme": template.visualization.node_color_scheme,
                        "highlight_decisions": template.visualization.highlight_decisions,
                        "highlight_questions": template.visualization.highlight_questions,
                        "expand_level": template.visualization.expand_level
                    },
                    # New fields
                    "curiosity_prompt": template.curiosity_prompt,
                    "conversation_mode": template.conversation_mode
                }, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving template: {e}")
            return False
            
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get a template by name"""
        return self.templates.get(name)
        
    def get_template_names(self) -> List[str]:
        """Get list of all template names"""
        return list(self.templates.keys())
        
    def delete_template(self, name: str) -> bool:
        """Delete a template"""
        if name.startswith('*'):
            return False  # Cannot delete protected templates
            
        if name in self.templates:
            del self.templates[name]
            
            # Delete from file system if it exists
            filename = f"{name.lower().replace(' ', '_')}.json"
            filepath = os.path.join(self.template_dir, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
            return True
        return False
