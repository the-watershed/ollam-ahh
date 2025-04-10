import tkinter as tk
from tkinter import messagebox
from ollama_functions import get_model_information, get_running_instance_info

def show_model_information(self, event):
    selection = self.models_listbox.curselection()
    if selection:
        self.selected_model = self.models_listbox.get(selection[0])
        model_info = get_model_information(self.selected_model)
        display_model_information(self, model_info)
        # Enable the Run button if it exists
        if hasattr(self, 'run_button'):
            self.run_button.config(state=tk.NORMAL)
    else:
        # Disable the Run button if it exists
        if hasattr(self, 'run_button'):
            self.run_button.config(state=tk.DISABLED)
        self.selected_model = None

def show_running_model_information(self, event):
    selection = self.running_models_listbox.curselection()
    if selection:
        self.selected_running_model = self.running_models_listbox.get(selection[0])
        base_info = get_model_information(self.selected_running_model)
        instance_info = get_running_instance_info(self.selected_running_model)
        model_info = base_info if base_info else ""
        model_info += f"\n\n{instance_info}" if instance_info else ""

        # Output to output_text instead of model_info_text
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        if model_info:
            self.output_text.insert(tk.END, model_info)
        else:
            self.output_text.insert(tk.END, "Could not retrieve model information.")
        self.output_text.config(state=tk.DISABLED)

        # Enable the Stop button if it exists
        if hasattr(self, 'stop_button'):
            self.stop_button.config(state=tk.NORMAL)
    else:
        # Disable the Stop button if it exists
        if hasattr(self, 'stop_button'):
            self.stop_button.config(state=tk.DISABLED)
        self.selected_running_model = None

        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, "No running model selected.")
        self.output_text.config(state=tk.DISABLED)

def display_model_information(self, model_info):
    self.model_info_text.config(state=tk.NORMAL)
    self.model_info_text.delete("1.0", tk.END)  # Clear previous information
    if model_info:
        self.model_info_text.insert(tk.END, model_info)
    else:
        self.model_info_text.insert(tk.END, "Could not retrieve model information.")
    self.model_info_text.config(state=tk.DISABLED)
