"""
UI style constants for consistent styling across the application.
"""

# GroupBox styles
GROUPBOX_STYLE = """
    QGroupBox {
        font-weight: bold;
        border: 2px solid #ccc;
        border-radius: 6px;
        margin-top: 6px;
        padding-top: 5px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 7px;
        padding: 0 5px;
    }
"""

# Button styles
RECORD_BUTTON_STYLE = """
    QPushButton {
        background-color: #e53935;
        color: white;
        font-weight: bold;
        padding: 4px 12px;
        border-radius: 16px;
        min-width: 90px;
    }
    QPushButton:hover {
        background-color: #c62828;
    }
    QPushButton:disabled {
        background-color: #ffcdd2;
    }
"""

PAUSE_BUTTON_STYLE = """
    QPushButton {
        background-color: #546e7a;
        color: white;
        font-weight: bold;
        padding: 4px 12px;
        border-radius: 16px;
        min-width: 90px;
    }
    QPushButton:hover {
        background-color: #455a64;
    }
    QPushButton:disabled {
        background-color: #cfd8dc;
    }
"""

STOP_BUTTON_STYLE = """
    QPushButton {
        background-color: #37474f;
        color: white;
        font-weight: bold;
        padding: 4px 12px;
        border-radius: 16px;
        min-width: 90px;
    }
    QPushButton:hover {
        background-color: #263238;
    }
    QPushButton:disabled {
        background-color: #cfd8dc;
    }
"""

MUTE_BUTTON_STYLE = """
    QPushButton {
        background-color: #78909c;
        color: white;
        font-weight: bold;
        padding: 4px 12px;
        border-radius: 16px;
        min-width: 90px;
    }
    QPushButton:hover {
        background-color: #607d8b;
    }
    QPushButton:checked {
        background-color: #e53935;
    }
    QPushButton:disabled {
        background-color: #cfd8dc;
    }
"""

FULL_ANALYSIS_BUTTON_STYLE = """
    QPushButton {
        background-color: #2196F3;
        color: white;
        font-weight: bold;
        padding: 4px 12px;
        border-radius: 4px;
    }
    QPushButton:hover {
        background-color: #1976D2;
    }
"""

# Input field styles
SESSION_NAME_STYLE = """
    QLineEdit {
        font-size: 12pt;
        font-weight: bold;
        padding: 4px;
        border: 1px solid #ccc;
        border-radius: 4px;
        background-color: white;
        color: #333333;
    }
    QLineEdit:focus {
        border: 2px solid #546e7a;
        background-color: #f5f5f5;
    }
    QLineEdit::placeholder {
        color: #9e9e9e;
    }
"""

# Status indicator styles
STATUS_INDICATOR_STYLE = """
    background-color: #ccc;
    border-radius: 10px;
"""

STATUS_INDICATOR_RECORDING_STYLE = """
    background-color: #f44336;
    border-radius: 10px;
    animation: pulse 1.5s infinite;
"""

STATUS_INDICATOR_PAUSED_STYLE = """
    background-color: #FFC107;
    border-radius: 10px;
"""

# Timer display style
TIMER_DISPLAY_STYLE = """
    font-size: 18pt;
    font-weight: bold;
    color: #333;
    padding: 0 5px;
    min-width: 120px;
"""

# Markdown content styles
MARKDOWN_STYLE = """
    h1 { font-size: 18pt; margin-top: 6px; margin-bottom: 6px; }
    h2 { font-size: 16pt; margin-top: 6px; margin-bottom: 6px; }
    h3 { font-size: 14pt; margin-top: 6px; margin-bottom: 6px; }
    p { margin-top: 4px; margin-bottom: 4px; }
    ul, ol { margin-top: 4px; margin-bottom: 4px; }
    code { background-color: #f0f0f0; padding: 2px 4px; border-radius: 3px; }
    pre { background-color: #f0f0f0; padding: 8px; border-radius: 3px; }
"""

# Status label styles
STATUS_LABEL_STYLE = "color: #666;"
STATUS_LABEL_ERROR_STYLE = "color: #f44336;"
STATUS_LABEL_SUCCESS_STYLE = "color: #4caf50;"
STATUS_LABEL_WARNING_STYLE = "color: #ff9800;"
