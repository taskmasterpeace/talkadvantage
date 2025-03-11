from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QListWidget, QListWidgetItem, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal

class TemplateChooserDialog(QDialog):
    """Dialog for choosing between generated templates"""
    
    template_selected = pyqtSignal(dict)
    
    def __init__(self, parent=None, templates=None):
        super().__init__(parent)
        self.setWindowTitle("Choose Template")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        
        self.templates = templates or []
        self.selected_template = None
        
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Choose a Template")
        header.setStyleSheet("""
            QLabel {
                font-size: 16pt;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(header)
        
        # Split view layout
        split_layout = QHBoxLayout()
        
        # Template list on the left
        list_layout = QVBoxLayout()
        list_label = QLabel("Available Templates")
        list_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        list_layout.addWidget(list_label)
        
        self.template_list = QListWidget()
        self.template_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
                min-width: 200px;
                max-width: 300px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        self.template_list.currentItemChanged.connect(self.on_template_selected)
        
        # Add templates to list
        for template in self.templates:
            item = QListWidgetItem(template.get('name', 'Unnamed Template'))
            item.setData(Qt.ItemDataRole.UserRole, template)
            self.template_list.addItem(item)
            
        list_layout.addWidget(self.template_list)
        split_layout.addLayout(list_layout)
        
        # Template details on the right
        details_layout = QVBoxLayout()
        details_label = QLabel("Template Details")
        details_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        details_layout.addWidget(details_label)
        
        self.details_edit = QTextEdit()
        self.details_edit.setReadOnly(True)
        self.details_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                background-color: #f8f9fa;
                font-family: system-ui;
                line-height: 1.4;
            }
        """)
        details_layout.addWidget(self.details_edit)
        split_layout.addLayout(details_layout)
        
        layout.addLayout(split_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        select_btn = QPushButton("Select Template")
        select_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        select_btn.clicked.connect(self.accept_template)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(select_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Select first template by default
        if self.template_list.count() > 0:
            self.template_list.setCurrentRow(0)
            
    def on_template_selected(self, current, previous):
        """Handle template selection change"""
        if not current:
            return
            
        template = current.data(Qt.ItemDataRole.UserRole)
        if not template:
            return
            
        # Format template details as HTML
        details = f"""
        <div style='font-family: system-ui;'>
            <h2 style='color: #2c3e50; margin-top: 0;'>{template.get('name', 'Unnamed Template')}</h2>
            
            <div style='margin-bottom: 15px;'>
                <h3 style='color: #2c3e50; margin: 0;'>Description</h3>
                <p style='margin-top: 5px;'>{template.get('description', 'No description available')}</p>
            </div>
            
            <div style='margin-bottom: 15px;'>
                <h3 style='color: #2c3e50; margin: 0;'>User Context</h3>
                <p style='margin-top: 5px;'>{template.get('user', 'No user context defined')}</p>
            </div>
            
            <div style='margin-bottom: 15px;'>
                <h3 style='color: #2c3e50; margin: 0;'>System Prompt</h3>
                <div style='background: #fff; padding: 8px; border-radius: 4px; margin-top: 5px; border: 1px solid #eee;'>
                    {str(template.get('system_prompt', 'No system prompt defined')).replace('\n', '<br>')}
                </div>
            </div>
            
            <div style='margin-bottom: 15px;'>
                <h3 style='color: #2c3e50; margin: 0;'>Template Instructions</h3>
                <div style='background: #fff; padding: 8px; border-radius: 4px; margin-top: 5px; border: 1px solid #eee;'>
                    {str(template.get('template', 'No template defined')).replace('\n', '<br>')}
                </div>
            </div>
            
            <div style='margin-bottom: 15px;'>
                <h3 style='color: #2c3e50; margin: 0;'>Recommended Bookmarks</h3>
                <div style='background: #fff; padding: 8px; border-radius: 4px; margin-top: 5px; border: 1px solid #eee;'>
                    {'<br>'.join([
                        f"• {bm['name'] if isinstance(bm, dict) else bm} " +
                        (f"[{bm.get('key_shortcut', '')}] - {bm.get('description', '')}"
                         if isinstance(bm, dict) else "")
                        for bm in template.get('bookmarks', [])
                    ]) or 'No bookmarks defined'}
                </div>
            </div>
        </div>
        """
        
        self.details_edit.setHtml(details)
        self.selected_template = template
        
    def accept_template(self):
        """Accept and emit selected template"""
        if self.selected_template:
            self.template_selected.emit(self.selected_template)
        self.accept()
        
    def get_selected_template(self):
        """Return the selected template"""
        return self.selected_template
