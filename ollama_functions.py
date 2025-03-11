import os
import platform
import subprocess
import tkinter as tk
from tkinter import simpledialog, messagebox
import threading
import queue
import re

MAX_DEPTH = 5  # Limit the search depth

def find_ollama(gui):
    """
    Finds the Ollama installation directory by scanning the entire hard drive.
    Yields potential paths to the Ollama executable.
    """
    if platform.system() == "Windows":
        drives = [
            d + ":\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(d + ":")
        ]
    else:
        drives = ["/"]  # Start at the root for Linux/macOS

    for drive in drives:
        for root, _, files in os.walk(drive):
            depth = root[len(drive) :].count(os.sep)
            if depth > MAX_DEPTH:
                continue  # Skip directories deeper than MAX_DEPTH

            for file in files:
                if file.lower() == "ollama.exe" or file.lower() == "ollama":
                    path = os.path.join(root, file)
                    gui.log_message(f"Checking path: {path}", gui.checking_color)
                    yield path

def get_ollama_models():
    """
    Runs 'ollama list' and returns a list of available models.
    Returns an empty list if Ollama is not found or no models are available.
    """
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True)
        models = [line.split()[0] for line in result.stdout.splitlines()[1:]]  # Skip header line
        return models
    except FileNotFoundError:
        print("Ollama not found in PATH.")
        return []
    except subprocess.CalledProcessError as e:
        print(f"Error running 'ollama list': {e}")
        return []

def get_running_ollama_models():
    """
    Runs 'ollama ps' and returns a list of running models.
    Returns an empty list if Ollama is not found or no models are running.
    """
    try:
        result = subprocess.run(["ollama", "ps"], capture_output=True, text=True, check=True)
        # Parse the output, skipping the header line
        lines = result.stdout.splitlines()[1:]
        models = []
        for line in lines:
            parts = line.split()
            if len(parts) >= 2:  # Ensure there are at least two words
                model_name = parts[0]  # Model name is the first element
                models.append(model_name)
            else:
                models.append("Unknown")  # Handle cases with fewer elements
        return models
    except FileNotFoundError:
        print("Ollama not found in PATH.")
        return []
    except subprocess.CalledProcessError as e:
        print(f"Error running 'ollama ps': {e}")
        return []

def get_model_information(model_name):
    """
    Runs 'ollama show' and returns the model information.
    Returns None if the model is not found or Ollama is not installed.
    """
    try:
        result = subprocess.run(["ollama", "show", model_name], capture_output=True, text=True, check=True)
        return result.stdout
    except FileNotFoundError:
        print("Ollama not found in PATH.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error running 'ollama show': {e}")
        return None

def get_running_instance_info(model_name):
    """
    Returns instance-specific information for the given running model
    by parsing the output of 'ollama ps'.
    """
    try:
        result = subprocess.run(["ollama", "ps"], capture_output=True, text=True, check=True)
        rows = result.stdout.splitlines()[1:]  # skip header
        for row in rows:
            parts = row.split()
            if parts and parts[0] == model_name:
                return f"Running instance details:\n{row}"
        return ""
    except subprocess.CalledProcessError as e:
        return f"Error retrieving running info via ps: {e}"
    except FileNotFoundError:
        return "Ollama not found. Please ensure it is installed and in your PATH."

def start_search(gui):
    gui.searching = True
    #self.search_button.config(state=tk.DISABLED)
    #self.cancel_button.config(state=tk.NORMAL)
    gui.output_text.config(state=tk.NORMAL)
    gui.output_text.delete("1.0", tk.END)
    gui.output_text.config(state=tk.DISABLED)

    gui.search_thread = threading.Thread(target=gui.search_ollama_thread)
    gui.search_thread.start()

def search_ollama_thread(gui):
    for path in find_ollama(gui):
        if not gui.searching:
            break
        gui.ollama_location = path
        log_message(gui, f"Ollama found at: {path}", gui.found_color)
        save_ollama_location(gui, path)
        break  # Stop after the first found location
    else:
        if gui.searching:
            log_message(gui, "Ollama not found.", gui.not_found_color)

    search_complete(gui)

def cancel_search(gui):
    gui.searching = False
    log_message(gui, "Search cancelled.", gui.cancelled_color)
    search_complete(gui)

def search_complete(gui):
    #self.search_button.config(state=tk.NORMAL)
    #self.cancel_button.config(state=tk.DISABLED)
    gui.searching = False

def log_message(gui, message, color=None):
    gui.output_text.config(state=tk.NORMAL)
    if color:
        gui.output_text.tag_config(color, foreground=color, background=gui.bg_color)
        gui.output_text.insert(tk.END, message + "\n", color)
    else:
        gui.output_text.insert(tk.END, message + "\n")
    gui.output_text.see(tk.END)  # Autoscroll to the bottom
    gui.output_text.config(state=tk.DISABLED)

def save_ollama_location(gui, ollama_path):
    """
    Saves the Ollama installation path to a file.
    """
    if ollama_path:
        with open("ollam-ah.dat", "w") as f:
            f.write(ollama_path)
        log_message(gui, f"Ollama found at: {ollama_path}", gui.found_color)
        log_message(gui, "Ollama location saved to ollam-ah.dat", gui.found_color)
    else:
        log_message(gui, "Ollama not found.", gui.not_found_color)

def populate_models_list(gui):
    models = get_ollama_models()
    if models:
        for model in models:
            gui.models_listbox.insert(tk.END, model)
    else:
        gui.models_listbox.insert(tk.END, "No models found or Ollama not installed.")

def populate_running_models_list(gui):
    """
    Populates the running models listbox with the currently running models.
    """
    gui.running_models_listbox.delete(0, tk.END)  # Clear the listbox
    running_models = get_running_ollama_models()
    if running_models:
        for model in running_models:
            gui.running_models_listbox.insert(tk.END, model)
    else:
        gui.running_models_listbox.insert(tk.END, "No models running or Ollama not installed.")

def run_command(gui, command):
    """
    Runs a command and displays the output in real-time.
    """
    gui.output_text.config(state=tk.NORMAL)
    gui.output_text.delete("1.0", tk.END)  # Clear previous output
    gui.output_text.config(state=tk.DISABLED)

    def enqueue_output(process, queue):
        while True:
            chunk = process.stdout.read(1024)  # switched from stderr to stdout
            if not chunk:
                break
            # No decoding needed, chunk is already a string
            clean_chunk = re.sub(r'\x1b\[[0-9;]*m', '', chunk)
            lines = clean_chunk.splitlines()
            for line in lines:
                queue.put(line)

    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        output_thread = threading.Thread(target=enqueue_output, args=(process, gui.queue))
        output_thread.daemon = True  # Allow the program to exit even if this thread is running
        output_thread.start()
    except FileNotFoundError:
        log_message(gui, "Ollama not found. Please ensure it is installed and in your PATH.", gui.not_found_color)
    except Exception as e:
        log_message(gui, f"Error running command: {e}", gui.not_found_color)
