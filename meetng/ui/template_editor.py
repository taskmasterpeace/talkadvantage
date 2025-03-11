import tkinter as tk
from tkinter import ttk, messagebox
from services.template_manager import PromptTemplate

class TemplateEditorWindow(tk.Toplevel):
    def __init__(self, master, template_manager):
        super().__init__(master)
        self.title("Template Editor")
        self.template_manager = template_manager
        
        # Make window modal
        self.transient(master)
        self.grab_set()
        
        # Create main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Template list frame (left side)
        list_frame = ttk.LabelFrame(main_frame, text="Templates")
        list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        self.template_listbox = tk.Listbox(list_frame, width=30)
        self.template_listbox.pack(fill=tk.Y, expand=True)
        self.template_listbox.bind('<<ListboxSelect>>', self.on_template_select)
        
        # Buttons under listbox
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="New", command=self.new_template).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Delete", command=self.delete_template).pack(side=tk.LEFT, padx=2)
        
        # Editor frame (right side)
        editor_frame = ttk.LabelFrame(main_frame, text="Edit Template")
        editor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Template fields
        ttk.Label(editor_frame, text="Name:").pack(anchor=tk.W)
        self.name_entry = ttk.Entry(editor_frame)
        self.name_entry.pack(fill=tk.X, pady=2)
        
        ttk.Label(editor_frame, text="Description:").pack(anchor=tk.W)
        self.description_text = tk.Text(editor_frame, height=2)
        self.description_text.pack(fill=tk.X, pady=2)
        
        ttk.Label(editor_frame, text="User Prompt:").pack(anchor=tk.W)
        self.user_text = tk.Text(editor_frame, height=4)
        self.user_text.pack(fill=tk.X, pady=2)
        
        ttk.Label(editor_frame, text="Template Prompt:").pack(anchor=tk.W)
        self.template_text = tk.Text(editor_frame, height=4)
        self.template_text.pack(fill=tk.X, pady=2)
        
        # Save button
        ttk.Button(editor_frame, text="Save Changes", 
                  command=self.save_template).pack(pady=10)
        
        # Load templates
        self.load_templates()
        
    def load_templates(self):
        self.template_listbox.delete(0, tk.END)
        for name in self.template_manager.get_template_names():
            self.template_listbox.insert(tk.END, name)
            
    def on_template_select(self, event):
        selection = self.template_listbox.curselection()
        if not selection:
            return
            
        name = self.template_listbox.get(selection[0])
        template = self.template_manager.get_template(name)
        if template:
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, template.name)
            
            self.description_text.delete('1.0', tk.END)
            self.description_text.insert('1.0', template.description)
            
            self.user_text.delete('1.0', tk.END)
            self.user_text.insert('1.0', template.user_prompt)
            
            self.template_text.delete('1.0', tk.END)
            self.template_text.insert('1.0', template.template_prompt)
            
    def new_template(self):
        self.name_entry.delete(0, tk.END)
        self.description_text.delete('1.0', tk.END)
        self.user_text.delete('1.0', tk.END)
        self.template_text.delete('1.0', tk.END)
        
    def save_template(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Template name is required")
            return
            
        template = PromptTemplate(
            name=name,
            description=self.description_text.get('1.0', 'end-1c'),
            user_prompt=self.user_text.get('1.0', 'end-1c'),
            template_prompt=self.template_text.get('1.0', 'end-1c')
        )
        
        if self.template_manager.save_template(template):
            self.load_templates()
            messagebox.showinfo("Success", "Template saved successfully")
        else:
            messagebox.showerror("Error", "Failed to save template")
            
    def delete_template(self):
        selection = self.template_listbox.curselection()
        if not selection:
            return
            
        name = self.template_listbox.get(selection[0])
        if messagebox.askyesno("Confirm Delete", 
                             f"Are you sure you want to delete template '{name}'?"):
            if self.template_manager.delete_template(name):
                self.load_templates()
                self.new_template()  # Clear the form
