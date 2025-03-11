import tkinter as tk
from tkinter import messagebox
import subprocess
from ollama_functions import get_model_information
from ollama_gui_listbox import show_model_information, show_running_model_information, display_model_information

def bind_events(self, master):
    master.bind("<Configure>", self.on_resize)
    self.models_listbox.bind("<<ListboxSelect>>", lambda event: show_model_information(self, event))
    self.running_models_listbox.bind("<<ListboxSelect>>", lambda event: show_running_model_information(self, event))

def show_command_info(self, message):
    """
    Displays the command information in the model information text widget.
    """
    self.model_info_text.config(state=tk.NORMAL)
    self.model_info_text.delete("1.0", tk.END)
    self.model_info_text.insert("1.0", message)
    self.model_info_text.config(state=tk.DISABLED)

def stop_selected_model(self):
    if self.selected_running_model:
        try:
            subprocess.run(["ollama", "stop", self.selected_running_model], check=True)
            self.log_message(f"Stopping model: {self.selected_running_model}", self.cancelled_color)
            self.populate_running_models_list()  # Refresh the list
            self.stop_button.config(state=tk.DISABLED)
            self.selected_running_model = None
            display_model_information(self, "")
        except FileNotFoundError:
            messagebox.showerror("Error", "Ollama not found. Please ensure it is installed and in your PATH.")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Error stopping model: {e}")
    else:
        messagebox.showinfo("Info", "No running model selected. Please select a model from the list.")

def on_resize(self, event=None):
    """
    Handles the window resize event.
    """
    pass
