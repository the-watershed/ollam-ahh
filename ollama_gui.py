# ollama_gui.py
import subprocess
import tkinter as tk
from tkinter import messagebox

from ollama_commands import cp_model, ps_models, rm_model, show_model
class OllamaFinderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ollama Finder")
        self.pack()

        # Create a label
        self.label = tk.Label(self.root, text="Select the model to run", font=("Arial", 16))
        self.label.pack(pady=20)

        # Create an entry field for the model name
        self.model_entry = tk.Entry(self.root)
        self.model_entry.pack(pady=5)

        # Create a button to find Ollama models
        self.find_button = tk.Button(self.root, text="Find Model", font=("Arial", 14), command=self.find_ollama_model)
        self.find_button.pack(pady=10)

    def find_ollama_model(self):
        model_name = self.model_entry.get()
        if not model_name:
            messagebox.showerror("Error", "Please enter a model name.")
            return

        # Perform the search for Ollama models
        try:
            show_model(self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to find model: {e}")

    def ps_models_command(self):
        ps_models(self)

    def cp_model_command(self):
        cp_model(self)

    def rm_model_command(self):
        rm_model(self)

    def run_command(self, command):
        from ollama_functions import run_command
        run_command(self, command)

    def open_more_models(self):
        """
        Placeholder for handling 'More Models' functionality.
        """
        pass

    def log_message(self, message, color=None):
        from ollama_functions import log_message
        log_message(self, message, color)

    def find_ollama_model(self):
        model_name = self.model_entry.get()
        if not model_name:
            messagebox.showerror("Error", "Please enter a model name.")
            return

        # Perform the search for Ollama models
        try:
            show_model(self)
            # Run the command to find Ollama models using pip
            result = subprocess.run(['pip', 'search', model_name], capture_output=True, text=True)
            if result.returncode == 0:
                messagebox.showinfo("Found Models", f"Model found:\n{result.stdout}")
            else:
                messagebox.showerror("Error", f"No models found for {model_name}.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to find model: {e}")
