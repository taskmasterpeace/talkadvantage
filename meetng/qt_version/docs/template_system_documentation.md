# Template System Documentation

## Overview

The template system allows you to create customized AI assistant profiles for different conversation analysis scenarios. Each template defines how the AI analyzes and responds to conversation transcripts, with specialized behaviors for different use cases like meetings, interviews, or negotiations.

## Template Components

Each template consists of these key components:

### 1. Basic Information
- **Name**: Unique identifier for the template
- **Description**: Brief explanation of the template's purpose and use case

### 2. Core Prompts
- **System Prompt**: Defines the AI's role, expertise, and general behavior
- **User Prompt**: Provides context from the user's perspective (WHO perspective)
- **Template Prompt**: Specifies the analysis structure and output format (HOW to analyze)

### 3. Enhanced Features
- **Curiosity Prompt**: Customizes how the Curiosity Engine generates questions
- **Conversation Mode**: Controls how the Conversation Compass tracks discussion flow
- **Bookmarks**: Special markers for important conversation elements
- **Visualization Settings**: Controls how conversation maps are displayed

## Conversation Modes

Templates support two conversation modes:

### Tracking Mode
- Follows the natural flow of conversation
- Creates a radial or organic conversation map
- Best for: Open discussions, brainstorming, general meetings
- Default visualization: Radial layout

### Guided Mode
- Helps direct conversation toward specific goals
- Creates a more hierarchical conversation map
- Best for: Interviews, negotiations, structured discussions
- Default visualization: Hierarchical layout

## Special Bookmark Types

Bookmarks allow you to mark important elements in conversations. Three special types have enhanced functionality:

### User Speaking Markers
- Identify when you are speaking in the conversation
- Help distinguish your contributions from others
- Example: `[USER]`, `[MY COMMENT]`, `[MY QUESTION]`

### Decision Point Markers
- Highlight when important decisions are made
- Appear highlighted in conversation maps
- Example: `[DECISION]`, `[APPROVED]`, `[STRONG]`

### Action Item Markers
- Track tasks and assignments
- Can be extracted into action item lists
- Example: `[ACTION]`, `[TASK]`, `[FOLLOW-UP]`

## Curiosity Engine Customization

The Curiosity Engine generates questions to help understand conversation context. You can customize its focus areas:

- **Context Clarification**: Questions about unclear points
- **Decision Making**: Questions about how decisions were reached
- **Action Items**: Questions about tasks and responsibilities
- **Participant Roles**: Questions about who said what
- **Meeting Type**: Questions about the nature of the conversation

## Template Examples

### Meeting Summary Template
Best for capturing key points from business meetings:
- System Prompt: Positions AI as a meeting analyst
- Bookmarks: Agenda items, decisions, action items
- Conversation Mode: Typically tracking mode
- Focus: Extracting decisions and action items

### Interview Analysis Template
Best for evaluating job candidates:
- System Prompt: Positions AI as an interview evaluator
- Bookmarks: Technical questions, behavioral questions, strong/weak answers
- Conversation Mode: Typically guided mode
- Focus: Assessing candidate qualifications and fit

### Negotiation Coach Template
Best for analyzing negotiation dynamics:
- System Prompt: Positions AI as a negotiation expert
- Bookmarks: Offers, concessions, objections
- Conversation Mode: Typically guided mode
- Focus: Identifying positions, interests, and strategies

## Best Practices

1. **Be Specific**: Clearly define the AI's role and expertise in the system prompt
2. **Structure Output**: Use the template prompt to specify exactly how responses should be formatted
3. **Use Bookmarks**: Create custom bookmarks for your specific use case
4. **Choose the Right Mode**: Use tracking mode for open discussions, guided mode for structured conversations
5. **Customize Curiosity**: Focus the Curiosity Engine on the most relevant question types

## Troubleshooting

### Template Not Working as Expected
- Ensure system prompt clearly defines the AI's role and expertise
- Check that template prompt provides clear structure for responses
- Verify that conversation mode matches your use case

### Conversation Map Issues
- Adjust visualization settings for better readability
- Try different layouts based on conversation structure
- Ensure special bookmarks are properly configured

### Curiosity Questions Not Relevant
- Customize the curiosity prompt to focus on specific areas
- Provide more context in the conversation transcript
- Use more specific language in your template description

## Advanced Techniques

### Template Chaining
Use multiple templates for different stages of analysis:
1. Start with a general template for initial understanding
2. Switch to specialized templates for deeper analysis
3. Finish with a summary template to consolidate insights

### Custom Visualization
Adjust visualization settings for different conversation types:
- Use radial layouts for brainstorming sessions
- Use hierarchical layouts for structured interviews
- Use force-directed layouts for complex negotiations

### Hybrid Modes
Combine elements of tracking and guided modes:
- Start in tracking mode to capture natural flow
- Switch to guided mode for specific segments
- Return to tracking mode for open-ended portions
