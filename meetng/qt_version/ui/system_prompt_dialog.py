from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QTextEdit, QListWidget,
    QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt
from qt_version.utils.system_prompt_manager import SystemPromptManager, SystemPrompt

class SystemPromptDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("System/Assistant Prompt Manager")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        
        # Initialize prompt manager
        self.prompt_manager = SystemPromptManager()
        
        layout = QVBoxLayout()
        
        # Prompt List with Add/Delete buttons
        list_layout = QHBoxLayout()
        
        list_group = QGroupBox("System Prompts")
        list_inner_layout = QVBoxLayout()
        
        self.prompt_list = QListWidget()
        self.prompt_list.currentItemChanged.connect(self.on_prompt_selected)
        list_inner_layout.addWidget(self.prompt_list)
        
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add New")
        self.add_btn.clicked.connect(self.add_new_prompt)
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete_prompt)
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.delete_btn)
        list_inner_layout.addLayout(button_layout)
        
        list_group.setLayout(list_inner_layout)
        layout.addWidget(list_group)
        
        # Editor
        editor_group = QGroupBox("Edit System Prompt")
        editor_layout = QVBoxLayout()
        
        self.name_edit = QLineEdit()
        editor_layout.addWidget(QLabel("Name:"))
        editor_layout.addWidget(self.name_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(60)
        editor_layout.addWidget(QLabel("Description:"))
        editor_layout.addWidget(self.description_edit)
        
        self.prompt_edit = QTextEdit()
        editor_layout.addWidget(QLabel("System/Assistant Prompt:"))
        editor_layout.addWidget(self.prompt_edit)
        
        editor_group.setLayout(editor_layout)
        layout.addWidget(editor_group)
        
        # Save/Cancel buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_prompt)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Load existing prompts
        self.load_prompts()
        
    def load_prompts(self):
        """Load existing system prompts into list"""
        self.prompt_list.clear()
        prompts = self.prompt_manager.get_all_prompts()
        for prompt in prompts:
            self.prompt_list.addItem(prompt.name)
        
    def on_prompt_selected(self, current, previous):
        """Handle prompt selection"""
        if not current:
            return
            
        prompt = self.prompt_manager.get_prompt(current.text())
        if prompt:
            self.name_edit.setText(prompt.name)
            self.description_edit.setText(prompt.description)
            self.prompt_edit.setText(prompt.content)
        
    def add_new_prompt(self):
        """Add new prompt"""
        self.name_edit.clear()
        self.description_edit.clear()
        self.prompt_edit.clear()
        self.prompt_list.clearSelection()
        
    def delete_prompt(self):
        """Delete selected prompt"""
        current = self.prompt_list.currentItem()
        if not current:
            return
            
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the prompt '{current.text()}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self.prompt_manager.delete_prompt(current.text()):
                    self.prompt_list.takeItem(self.prompt_list.row(current))
                    self.name_edit.clear()
                    self.description_edit.clear()
                    self.prompt_edit.clear()
                else:
                    QMessageBox.warning(self, "Error", "Cannot delete default prompt")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete prompt: {str(e)}")
            
    def save_prompt(self):
        """Save current prompt"""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Please enter a name for the prompt")
            return
            
        description = self.description_edit.toPlainText().strip()
        prompt_text = self.prompt_edit.toPlainText().strip()
        
        if not prompt_text:
            QMessageBox.warning(self, "Error", "Please enter the prompt text")
            return
            
        prompt = SystemPrompt(
            name=name,
            description=description,
            content=prompt_text
        )
        
        try:
            self.prompt_manager.save_prompt(prompt)
            self.load_prompts()  # Refresh list
            QMessageBox.information(self, "Success", "Prompt saved successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save prompt: {str(e)}")
