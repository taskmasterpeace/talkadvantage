import os
import json
import time
from pathlib import Path

class PromptTemplate:
    """Class to represent a prompt template"""
    
    def __init__(self, name, user_prompt, template_prompt, system_prompt_id=None, description=""):
        self.name = name
        self.user_prompt = user_prompt
        self.template_prompt = template_prompt
        self.system_prompt_id = system_prompt_id
        self.description = description

class TemplateManager:
    """Manages prompt templates for the application"""
    
    def __init__(self):
        # Get user's home directory
        home_dir = str(Path.home())
        
        # Set template directory
        self.template_dir = os.path.join(home_dir, "PowerPlay", "Templates")
        
        # Create directory if it doesn't exist
        os.makedirs(self.template_dir, exist_ok=True)
        
        # Initialize templates dictionary
        self.templates = {}
        
        # Load default templates
        self._load_default_templates()
        
        # Load user templates
        self._load_user_templates()
    
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
        8. Version: Template format version
        """
        default_templates = [
            {
                "name": "*Full Analysis",
                "description": "Complete analysis of the entire conversation",
                "user_prompt": "Analyze the complete transcript to provide a comprehensive understanding.",
                "system_prompt": """You are an AI assistant performing comprehensive conversation analysis. Your role is to:
1. Analyze the entire conversation context
2. Identify key themes, decisions, and action items
3. Track participant contributions and commitments
4. Highlight important connections and insights
5. Maintain a professional and thorough analysis style""",
                "template_prompt": """Please provide a thorough analysis of the entire conversation:

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
                "bookmarks": [
                    {
                        "name": "New Topic",
                        "bookmark_type": "marker",
                        "key_shortcut": "Ctrl+1",
                        "voice_trigger": "new topic",
                        "content": "=== New Topic ===",
                        "description": "Mark the start of a new discussion topic",
                        "is_user_speaking": False,
                        "is_decision_point": False,
                        "is_action_item": False
                    },
                    {
                        "name": "Decision Made",
                        "bookmark_type": "marker",
                        "key_shortcut": "Ctrl+2", 
                        "voice_trigger": "mark decision",
                        "content": "[DECISION]",
                        "description": "Mark an important decision point",
                        "is_user_speaking": False,
                        "is_decision_point": True,
                        "is_action_item": False
                    },
                    {
                        "name": "Action Item",
                        "bookmark_type": "marker",
                        "key_shortcut": "Ctrl+3",
                        "voice_trigger": "action item",
                        "content": "[ACTION]",
                        "description": "Mark an assigned task or action item",
                        "is_user_speaking": False,
                        "is_decision_point": False,
                        "is_action_item": True
                    },
                    {
                        "name": "User Speaking",
                        "bookmark_type": "marker",
                        "key_shortcut": "Ctrl+U",
                        "voice_trigger": "me speaking",
                        "content": "[USER]",
                        "description": "Mark when the user is speaking",
                        "is_user_speaking": True,
                        "is_decision_point": False,
                        "is_action_item": False
                    }
                ],
                "curiosity_prompt": """[SYSTEM INSTRUCTIONS - DO NOT MODIFY THIS SECTION]
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
                "conversation_mode": "tracking",
                "visualization": {
                    "default_layout": "radial",
                    "node_color_scheme": "default",
                    "highlight_decisions": True,
                    "highlight_questions": True,
                    "expand_level": 1
                },
                "version": 2
            },
            {
                "name": "*Meeting Summary",
                "description": "Focused summary of a business meeting",
                "user_prompt": "As a meeting participant, I need a clear summary of this business meeting.",
                "system_prompt": """You are an AI assistant specializing in business meeting analysis. Your role is to:
1. Extract the key information from business meetings
2. Identify decisions, action items, and responsibilities
3. Organize information in a clear, business-appropriate format
4. Focus on practical outcomes and next steps
5. Maintain a professional, concise style""",
                "template_prompt": """Please provide a business meeting summary with the following sections:

1. Meeting Overview
   - Date and participants (if mentioned)
   - Main purpose/agenda
   - Key discussion points

2. Decisions Made
   - List all decisions reached during the meeting
   - Note any approvals or rejections

3. Action Items
   - Tasks assigned during the meeting
   - Who is responsible for each item
   - Deadlines mentioned

4. Follow-up Required
   - Scheduled follow-up meetings
   - Outstanding questions
   - Items deferred to later discussion

Please format this as a professional business summary that could be shared with meeting participants.""",
                "bookmarks": [
                    {
                        "name": "Agenda Item",
                        "bookmark_type": "marker",
                        "key_shortcut": "Ctrl+A",
                        "voice_trigger": "agenda item",
                        "content": "=== AGENDA ITEM ===",
                        "description": "Mark the start of a new agenda item",
                        "is_user_speaking": False,
                        "is_decision_point": False,
                        "is_action_item": False
                    },
                    {
                        "name": "Decision Made",
                        "bookmark_type": "marker",
                        "key_shortcut": "Ctrl+D", 
                        "voice_trigger": "mark decision",
                        "content": "[DECISION]",
                        "description": "Mark an important decision point",
                        "is_user_speaking": False,
                        "is_decision_point": True,
                        "is_action_item": False
                    },
                    {
                        "name": "Action Item",
                        "bookmark_type": "marker",
                        "key_shortcut": "Ctrl+T",
                        "voice_trigger": "action item",
                        "content": "[ACTION]",
                        "description": "Mark an assigned task or action item",
                        "is_user_speaking": False,
                        "is_decision_point": False,
                        "is_action_item": True
                    },
                    {
                        "name": "My Comment",
                        "bookmark_type": "marker",
                        "key_shortcut": "Ctrl+M",
                        "voice_trigger": "my comment",
                        "content": "[MY COMMENT]",
                        "description": "Mark when the user is speaking",
                        "is_user_speaking": True,
                        "is_decision_point": False,
                        "is_action_item": False
                    }
                ],
                "curiosity_prompt": """[SYSTEM INSTRUCTIONS - DO NOT MODIFY THIS SECTION]
You are an expert meeting analyst generating questions about a meeting transcript. 
Generate 2-3 insightful questions that would help understand the meeting context better.

[QUESTION TYPES - DO NOT MODIFY THESE TYPES]
Question types:
- YES_NO: Simple yes/no questions
- MULTIPLE_CHOICE: Questions with predefined options (provide 3-4 choices)
- MULTIPLE_CHOICE_FILL: Multiple choice with an "other" option (provide 3-4 choices)
- SPEAKER_IDENTIFICATION: Questions about who said specific statements
- MEETING_TYPE: Questions about the type of meeting/conversation

[CUSTOMIZABLE GUIDELINES - YOU CAN MODIFY THIS SECTION]
Generate questions that:
- Identify key decision makers in the meeting
- Clarify action items and responsibilities
- Uncover meeting objectives and outcomes
- Identify potential follow-up items
- Are concise and clear
- Have meaningful multiple choice options when applicable

[OUTPUT FORMAT - DO NOT MODIFY THIS SECTION]
Return a list of questions in the specified format.""",
                "conversation_mode": "tracking",
                "visualization": {
                    "default_layout": "radial",
                    "node_color_scheme": "default",
                    "highlight_decisions": True,
                    "highlight_questions": True,
                    "expand_level": 1
                },
                "version": 2
            },
            {
                "name": "*Interview Analysis",
                "description": "Analysis of a job interview",
                "user_prompt": "As a hiring manager, I need an analysis of this job interview.",
                "system_prompt": """You are an AI assistant specializing in job interview analysis. Your role is to:
1. Evaluate candidate responses objectively
2. Identify strengths, weaknesses, and potential concerns
3. Assess technical skills and cultural fit
4. Highlight notable qualifications and experience
5. Maintain a balanced, unbiased perspective""",
                "template_prompt": """Please analyze this job interview and provide:

1. Candidate Overview
   - Background and experience highlights
   - Key qualifications mentioned
   - Self-reported strengths and weaknesses

2. Technical Assessment
   - Technical skills demonstrated
   - Knowledge gaps identified
   - Problem-solving approach

3. Behavioral Assessment
   - Communication style and clarity
   - Cultural fit indicators
   - Soft skills demonstrated

4. Key Concerns
   - Potential red flags
   - Areas requiring further clarification
   - Experience or skill gaps

5. Overall Recommendation
   - Strengths summary
   - Areas of concern
   - Suggested follow-up questions

Please provide an objective assessment that would help in making a hiring decision.""",
                "bookmarks": [
                    {
                        "name": "Technical Question",
                        "bookmark_type": "marker",
                        "key_shortcut": "Ctrl+T",
                        "voice_trigger": "technical question",
                        "content": "[TECHNICAL]",
                        "description": "Mark a technical question",
                        "is_user_speaking": False,
                        "is_decision_point": False,
                        "is_action_item": False
                    },
                    {
                        "name": "Behavioral Question",
                        "bookmark_type": "marker",
                        "key_shortcut": "Ctrl+B", 
                        "voice_trigger": "behavioral question",
                        "content": "[BEHAVIORAL]",
                        "description": "Mark a behavioral question",
                        "is_user_speaking": False,
                        "is_decision_point": False,
                        "is_action_item": False
                    },
                    {
                        "name": "Strong Answer",
                        "bookmark_type": "marker",
                        "key_shortcut": "Ctrl+S",
                        "voice_trigger": "strong answer",
                        "content": "[STRONG]",
                        "description": "Mark a particularly strong answer",
                        "is_user_speaking": False,
                        "is_decision_point": True,
                        "is_action_item": False
                    },
                    {
                        "name": "Weak Answer",
                        "bookmark_type": "marker",
                        "key_shortcut": "Ctrl+W",
                        "voice_trigger": "weak answer",
                        "content": "[WEAK]",
                        "description": "Mark a concerning or weak answer",
                        "is_user_speaking": False,
                        "is_decision_point": True,
                        "is_action_item": False
                    },
                    {
                        "name": "My Question",
                        "bookmark_type": "marker",
                        "key_shortcut": "Ctrl+Q",
                        "voice_trigger": "my question",
                        "content": "[MY QUESTION]",
                        "description": "Mark when the interviewer is speaking",
                        "is_user_speaking": True,
                        "is_decision_point": False,
                        "is_action_item": False
                    }
                ],
                "curiosity_prompt": """[SYSTEM INSTRUCTIONS - DO NOT MODIFY THIS SECTION]
You are an expert interview analyst generating questions about an interview transcript. 
Generate 2-3 insightful questions that would help understand the interview context better.

[QUESTION TYPES - DO NOT MODIFY THESE TYPES]
Question types:
- YES_NO: Simple yes/no questions
- MULTIPLE_CHOICE: Questions with predefined options (provide 3-4 choices)
- MULTIPLE_CHOICE_FILL: Multiple choice with an "other" option (provide 3-4 choices)
- SPEAKER_IDENTIFICATION: Questions about who said specific statements
- MEETING_TYPE: Questions about the type of meeting/conversation

[CUSTOMIZABLE GUIDELINES - YOU CAN MODIFY THIS SECTION]
Generate questions that:
- Clarify the candidate's experience and qualifications
- Identify key strengths and potential concerns
- Assess cultural fit and alignment with company values
- Evaluate specific skills mentioned in the interview
- Are concise and clear
- Have meaningful multiple choice options when applicable

[OUTPUT FORMAT - DO NOT MODIFY THIS SECTION]
Return a list of questions in the specified format.""",
                "conversation_mode": "guided",
                "visualization": {
                    "default_layout": "hierarchical",
                    "node_color_scheme": "role",
                    "highlight_decisions": True,
                    "highlight_questions": True,
                    "expand_level": 2
                },
                "version": 2
            },
            {
                "name": "*Negotiation Coach",
                "description": "Guidance for negotiation scenarios",
                "user_prompt": "As a negotiation participant, I need strategic guidance for this negotiation.",
                "system_prompt": """You are an AI assistant specializing in negotiation analysis and coaching. Your role is to:
1. Identify negotiation tactics and strategies being used
2. Analyze positions, interests, and potential compromises
3. Suggest effective responses and approaches
4. Highlight strengths and weaknesses in negotiation style
5. Maintain a strategic, solution-oriented perspective""",
                "template_prompt": """Please analyze this negotiation and provide strategic guidance:

1. Negotiation Overview
   - Key parties and their primary positions
   - Core interests identified (stated or implied)
   - Areas of agreement and disagreement

2. Strategy Assessment
   - Tactics being employed by each party
   - Power dynamics and leverage points
   - Anchoring and framing techniques used

3. Key Opportunities
   - Potential value creation opportunities
   - Possible compromises and trades
   - Areas where interests align

4. Risk Analysis
   - Potential deadlocks or impasses
   - Hidden agendas or unstated concerns
   - BATNA (Best Alternative To Negotiated Agreement) considerations

5. Recommended Approach
   - Suggested responses to current positions
   - Strategic moves to consider
   - Communication adjustments

Please provide practical, actionable guidance that could be used in this negotiation.""",
                "bookmarks": [
                    {
                        "name": "Offer Made",
                        "bookmark_type": "marker",
                        "key_shortcut": "Ctrl+O",
                        "voice_trigger": "offer made",
                        "content": "[OFFER]",
                        "description": "Mark when an offer is made",
                        "is_user_speaking": False,
                        "is_decision_point": True,
                        "is_action_item": False
                    },
                    {
                        "name": "Concession",
                        "bookmark_type": "marker",
                        "key_shortcut": "Ctrl+C", 
                        "voice_trigger": "concession made",
                        "content": "[CONCESSION]",
                        "description": "Mark when a concession is made",
                        "is_user_speaking": False,
                        "is_decision_point": True,
                        "is_action_item": False
                    },
                    {
                        "name": "Objection",
                        "bookmark_type": "marker",
                        "key_shortcut": "Ctrl+J",
                        "voice_trigger": "objection raised",
                        "content": "[OBJECTION]",
                        "description": "Mark when an objection is raised",
                        "is_user_speaking": False,
                        "is_decision_point": False,
                        "is_action_item": False
                    },
                    {
                        "name": "My Position",
                        "bookmark_type": "marker",
                        "key_shortcut": "Ctrl+P",
                        "voice_trigger": "my position",
                        "content": "[MY POSITION]",
                        "description": "Mark when stating your position",
                        "is_user_speaking": True,
                        "is_decision_point": False,
                        "is_action_item": False
                    },
                    {
                        "name": "My Offer",
                        "bookmark_type": "marker",
                        "key_shortcut": "Ctrl+M",
                        "voice_trigger": "my offer",
                        "content": "[MY OFFER]",
                        "description": "Mark when making your offer",
                        "is_user_speaking": True,
                        "is_decision_point": True,
                        "is_action_item": False
                    }
                ],
                "curiosity_prompt": """[SYSTEM INSTRUCTIONS - DO NOT MODIFY THIS SECTION]
You are an expert negotiation analyst generating questions about a negotiation transcript. 
Generate 2-3 insightful questions that would help understand the negotiation context better.

[QUESTION TYPES - DO NOT MODIFY THESE TYPES]
Question types:
- YES_NO: Simple yes/no questions
- MULTIPLE_CHOICE: Questions with predefined options (provide 3-4 choices)
- MULTIPLE_CHOICE_FILL: Multiple choice with an "other" option (provide 3-4 choices)
- SPEAKER_IDENTIFICATION: Questions about who said specific statements
- MEETING_TYPE: Questions about the type of meeting/conversation

[CUSTOMIZABLE GUIDELINES - YOU CAN MODIFY THIS SECTION]
Generate questions that:
- Identify key negotiation points and positions
- Clarify priorities and non-negotiables
- Uncover potential compromises and alternatives
- Assess the balance of power in the negotiation
- Identify decision-making factors
- Are concise and clear
- Have meaningful multiple choice options when applicable

[OUTPUT FORMAT - DO NOT MODIFY THIS SECTION]
Return a list of questions in the specified format.""",
                "conversation_mode": "guided",
                "visualization": {
                    "default_layout": "force-directed",
                    "node_color_scheme": "sentiment",
                    "highlight_decisions": True,
                    "highlight_questions": True,
                    "expand_level": 2
                },
                "version": 2
            }
        ]
        
        # Add templates to the manager
        for template_data in default_templates:
            template_name = template_data["name"]
            self.templates[template_name] = template_data
    
    def _load_user_templates(self):
        """Load user-created templates from the template directory"""
        try:
            # Check if template directory exists
            if not os.path.exists(self.template_dir):
                return
                
            # Load each template file
            for filename in os.listdir(self.template_dir):
                if not filename.endswith('.json'):
                    continue
                    
                filepath = os.path.join(self.template_dir, filename)
                
                try:
                    with open(filepath, 'r') as f:
                        template_data = json.load(f)
                        
                    # Add template to the manager
                    template_name = template_data.get('name', os.path.splitext(filename)[0])
                    self.templates[template_name] = template_data
                except Exception as e:
                    print(f"Error loading template {filename}: {e}")
        except Exception as e:
            print(f"Error loading user templates: {e}")
    
    def get_template_names(self):
        """Get list of available template names"""
        return list(self.templates.keys())
    
    def get_template(self, name):
        """Get template by name"""
        if name in self.templates:
            template_data = self.templates[name]
            
            # Convert dictionary to PromptTemplate
            template = PromptTemplate(
                name=template_data.get('name', name),
                user_prompt=template_data.get('user_prompt', ''),
                template_prompt=template_data.get('template_prompt', ''),
                system_prompt_id=template_data.get('system_prompt_id'),
                description=template_data.get('description', '')
            )
            
            # Add additional attributes from template data
            for key, value in template_data.items():
                if not hasattr(template, key):
                    setattr(template, key, value)
                    
            return template
        return None
    
    def save_template(self, template):
        """Save template to file"""
        try:
            # Convert template to dictionary
            if isinstance(template, PromptTemplate):
                template_data = {
                    'name': template.name,
                    'user_prompt': template.user_prompt,
                    'template_prompt': template.template_prompt,
                    'system_prompt_id': template.system_prompt_id,
                    'description': template.description
                }
                
                # Add additional attributes
                for key in dir(template):
                    if not key.startswith('_') and key not in template_data:
                        value = getattr(template, key)
                        if not callable(value):
                            template_data[key] = value
            else:
                template_data = template
                
            # Add version if not present
            if 'version' not in template_data:
                template_data['version'] = 2
                
            # Create safe filename
            safe_name = template_data['name'].replace('*', '').replace(' ', '_')
            safe_name = ''.join(c for c in safe_name if c.isalnum() or c in '_-')
            filename = f"{safe_name}.json"
            
            # Save to file
            filepath = os.path.join(self.template_dir, filename)
            with open(filepath, 'w') as f:
                json.dump(template_data, f, indent=2)
                
            # Update templates dictionary
            self.templates[template_data['name']] = template_data
            
            return True
        except Exception as e:
            print(f"Error saving template: {e}")
            return False
    
    def delete_template(self, name):
        """Delete template by name"""
        try:
            # Check if template exists
            if name not in self.templates:
                return False
                
            # Don't delete built-in templates
            if name.startswith('*'):
                return False
                
            # Create safe filename
            safe_name = name.replace('*', '').replace(' ', '_')
            safe_name = ''.join(c for c in safe_name if c.isalnum() or c in '_-')
            filename = f"{safe_name}.json"
            
            # Delete file
            filepath = os.path.join(self.template_dir, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                
            # Remove from templates dictionary
            if name in self.templates:
                del self.templates[name]
                
            return True
        except Exception as e:
            print(f"Error deleting template: {e}")
            return False
            
    def validate_template(self, template_data):
        """
        Validate template data to ensure it has all required fields
        
        Args:
            template_data: Template data to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        required_fields = ["name", "user_prompt", "template_prompt", "system_prompt"]
        
        # Check for required fields
        for field in required_fields:
            if field not in template_data:
                return False, f"Missing required field: {field}"
        
        # Check for empty required fields
        for field in required_fields:
            if not template_data[field]:
                return False, f"Required field is empty: {field}"
        
        # Check for valid conversation mode
        if "conversation_mode" in template_data:
            if template_data["conversation_mode"] not in ["tracking", "guided"]:
                return False, f"Invalid conversation mode: {template_data['conversation_mode']}"
        
        # Check for valid bookmarks
        if "bookmarks" in template_data and template_data["bookmarks"]:
            for i, bookmark in enumerate(template_data["bookmarks"]):
                if "name" not in bookmark:
                    return False, f"Bookmark {i+1} is missing a name"
                if "bookmark_type" not in bookmark:
                    return False, f"Bookmark {i+1} is missing a type"
                if bookmark["bookmark_type"] not in ["marker", "voice_command"]:
                    return False, f"Bookmark {i+1} has invalid type: {bookmark['bookmark_type']}"
        
        return True, ""
    
    def migrate_templates(self, backup=True):
        """
        Migrate existing templates to the new format with curiosity_prompt and conversation_mode
        
        Args:
            backup: Whether to create backups of templates before migration
            
        Returns:
            dict: Migration statistics
        """
        migration_stats = {
            "total": 0,
            "migrated": 0,
            "skipped": 0,
            "errors": 0,
            "backups_created": 0
        }
        
        # Check if template directory exists
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)
            return migration_stats
        
        # Create backup directory if needed
        backup_dir = os.path.join(self.template_dir, "backups", f"migration_{int(time.time())}")
        if backup and not os.path.exists(backup_dir):
            os.makedirs(backup_dir, exist_ok=True)
        
        # Process each template file
        for filename in os.listdir(self.template_dir):
            if not filename.endswith('.json'):
                continue
                
            migration_stats["total"] += 1
            filepath = os.path.join(self.template_dir, filename)
            
            try:
                # Read template file
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    
                # Check if template needs migration
                needs_migration = (
                    "curiosity_prompt" not in data or
                    "conversation_mode" not in data or
                    "version" not in data or
                    data.get("version", 0) < 2  # Version 2 includes the new fields
                )
                
                if not needs_migration:
                    migration_stats["skipped"] += 1
                    continue
                    
                # Create backup if requested
                if backup:
                    backup_path = os.path.join(backup_dir, filename)
                    with open(backup_path, 'w') as f:
                        json.dump(data, f, indent=2)
                    migration_stats["backups_created"] += 1
                    
                # Add new fields with appropriate defaults
                if "curiosity_prompt" not in data:
                    # Set default curiosity prompt based on template type
                    if "meeting" in data.get("name", "").lower() or "discussion" in data.get("name", "").lower():
                        data["curiosity_prompt"] = self._get_default_curiosity_prompt("meeting")
                    elif "interview" in data.get("name", "").lower():
                        data["curiosity_prompt"] = self._get_default_curiosity_prompt("interview")
                    elif "negotiation" in data.get("name", "").lower():
                        data["curiosity_prompt"] = self._get_default_curiosity_prompt("negotiation")
                    else:
                        data["curiosity_prompt"] = self._get_default_curiosity_prompt("general")
                
                if "conversation_mode" not in data:
                    # Set default conversation mode based on template type
                    if "guided" in data.get("name", "").lower() or "structured" in data.get("name", "").lower():
                        data["conversation_mode"] = "guided"
                    else:
                        data["conversation_mode"] = "tracking"
                
                # Add version field
                data["version"] = 2
                
                # Add visualization settings if not present
                if "visualization" not in data:
                    data["visualization"] = {
                        "default_layout": "radial",
                        "node_color_scheme": "default",
                        "highlight_decisions": True,
                        "highlight_questions": True,
                        "expand_level": 1
                    }
                
                # Save updated template
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
                    
                migration_stats["migrated"] += 1
                
            except Exception as e:
                print(f"Error migrating template {filename}: {e}")
                migration_stats["errors"] += 1
        
        return migration_stats

    def _get_default_curiosity_prompt(self, template_type="general"):
        """
        Get default curiosity prompt based on template type
        
        Args:
            template_type: Type of template (meeting, interview, negotiation, general)
            
        Returns:
            str: Default curiosity prompt
        """
        if template_type == "meeting":
            return """[SYSTEM INSTRUCTIONS - DO NOT MODIFY THIS SECTION]
You are an expert meeting analyst generating questions about a meeting transcript. 
Generate 2-3 insightful questions that would help understand the meeting context better.

[QUESTION TYPES - DO NOT MODIFY THESE TYPES]
Question types:
- YES_NO: Simple yes/no questions
- MULTIPLE_CHOICE: Questions with predefined options (provide 3-4 choices)
- MULTIPLE_CHOICE_FILL: Multiple choice with an "other" option (provide 3-4 choices)
- SPEAKER_IDENTIFICATION: Questions about who said specific statements
- MEETING_TYPE: Questions about the type of meeting/conversation

[CUSTOMIZABLE GUIDELINES - YOU CAN MODIFY THIS SECTION]
Generate questions that:
- Identify key decision makers in the meeting
- Clarify action items and responsibilities
- Uncover meeting objectives and outcomes
- Identify potential follow-up items
- Are concise and clear
- Have meaningful multiple choice options when applicable

[OUTPUT FORMAT - DO NOT MODIFY THIS SECTION]
Return a list of questions in the specified format."""
        
        elif template_type == "interview":
            return """[SYSTEM INSTRUCTIONS - DO NOT MODIFY THIS SECTION]
You are an expert interview analyst generating questions about an interview transcript. 
Generate 2-3 insightful questions that would help understand the interview context better.

[QUESTION TYPES - DO NOT MODIFY THESE TYPES]
Question types:
- YES_NO: Simple yes/no questions
- MULTIPLE_CHOICE: Questions with predefined options (provide 3-4 choices)
- MULTIPLE_CHOICE_FILL: Multiple choice with an "other" option (provide 3-4 choices)
- SPEAKER_IDENTIFICATION: Questions about who said specific statements
- MEETING_TYPE: Questions about the type of meeting/conversation

[CUSTOMIZABLE GUIDELINES - YOU CAN MODIFY THIS SECTION]
Generate questions that:
- Clarify the candidate's experience and qualifications
- Identify key strengths and potential concerns
- Assess cultural fit and alignment with company values
- Evaluate specific skills mentioned in the interview
- Are concise and clear
- Have meaningful multiple choice options when applicable

[OUTPUT FORMAT - DO NOT MODIFY THIS SECTION]
Return a list of questions in the specified format."""
        
        elif template_type == "negotiation":
            return """[SYSTEM INSTRUCTIONS - DO NOT MODIFY THIS SECTION]
You are an expert negotiation analyst generating questions about a negotiation transcript. 
Generate 2-3 insightful questions that would help understand the negotiation context better.

[QUESTION TYPES - DO NOT MODIFY THESE TYPES]
Question types:
- YES_NO: Simple yes/no questions
- MULTIPLE_CHOICE: Questions with predefined options (provide 3-4 choices)
- MULTIPLE_CHOICE_FILL: Multiple choice with an "other" option (provide 3-4 choices)
- SPEAKER_IDENTIFICATION: Questions about who said specific statements
- MEETING_TYPE: Questions about the type of meeting/conversation

[CUSTOMIZABLE GUIDELINES - YOU CAN MODIFY THIS SECTION]
Generate questions that:
- Identify key negotiation points and positions
- Clarify priorities and non-negotiables
- Uncover potential compromises and alternatives
- Assess the balance of power in the negotiation
- Identify decision-making factors
- Are concise and clear
- Have meaningful multiple choice options when applicable

[OUTPUT FORMAT - DO NOT MODIFY THIS SECTION]
Return a list of questions in the specified format."""
        
        else:  # general
            return """[SYSTEM INSTRUCTIONS - DO NOT MODIFY THIS SECTION]
You are an expert active listener analyzing conversation transcripts. 
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
Return a list of questions in the specified format."""
