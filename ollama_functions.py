import os
import platform
import subprocess
import tkinter as tk
from tkinter import simpledialog, messagebox
import threading
import queue
import re
import time  # Added missing import for sleep functionality
import shutil  # Added missing import
import requests  # added import

MAX_DEPTH = 5  # Limit the search depth

def find_ollama(gui):
    """
    Finds the Ollama installation directory by scanning common installation locations first,
    then falling back to a broader search if needed.
    Yields potential paths to the Ollama executable.
    """
    # Define common installation locations to check first
    common_locations = []
    
    if platform.system() == "Windows":
        # Common Windows installation locations
        common_locations = [
            os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "Ollama"),
            os.path.join(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"), "Ollama"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Ollama"),
            os.path.join(os.environ.get("APPDATA", ""), "Ollama"),
            os.path.join(os.environ.get("USERPROFILE", ""), "Ollama"),
        ]
    else:
        # Common Unix-like installation locations
        common_locations = [
            "/usr/local/bin",
            "/usr/bin",
            "/opt/ollama",
            os.path.expanduser("~/ollama"),
            os.path.expanduser("~/.local/bin")
        ]
    
    # First check if ollama is in PATH
    ollama_in_path = shutil.which("ollama")
    if ollama_in_path:
        gui.log_message(f"Ollama found in PATH: {ollama_in_path}", gui.checking_color)
        yield ollama_in_path
        return  # Exit early if found in PATH
        
    # Check common installation locations first
    for location in common_locations:
        if os.path.exists(location):
            gui.log_message(f"Checking common location: {location}", gui.checking_color)
            executable_name = "ollama.exe" if platform.system() == "Windows" else "ollama"
            path = os.path.join(location, executable_name)
            if os.path.exists(path):
                gui.log_message(f"Found Ollama at common location: {path}", gui.checking_color)
                yield path
                return  # Exit early if found in common location
    
    # If not found in common locations, do a more extensive search
    gui.log_message("Ollama not found in common locations. Starting broader search (this may take time)...", gui.checking_color)
    
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
    """
    Populates the models listbox with the available models.
    Clears the existing list first to prevent duplicates.
    """
    # Clear the listbox first to prevent duplicates
    gui.models_listbox.delete(0, tk.END)
    
    # Get and add the models
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
    Runs a command and displays the output in real-time to mimic a DOS window.
    Shows the command prompt, echoes the command, and displays formatted output.
    """
    gui.output_text.config(state=tk.NORMAL)
    gui.output_text.delete("1.0", tk.END)  # Clear previous output
    
    # Create DOS-like command tags
    gui.output_text.tag_config("prompt", foreground="#CCCCCC")
    gui.output_text.tag_config("command", foreground="#FFFFFF", font=("Courier New", 10, "bold"))
    gui.output_text.tag_config("output", foreground="#00FF00")
    gui.output_text.tag_config("error", foreground="#FF6666")
    
    # Create a DOS-like command prompt
    current_dir = os.getcwd()
    # Format the command prompt to look like DOS: C:\path\to\dir>
    gui.output_text.insert(tk.END, f"{current_dir}>", "prompt")
    # Echo the command that's being run
    cmd_str = " ".join(command)
    gui.output_text.insert(tk.END, f"{cmd_str}\n\n", "command")
    gui.output_text.see(tk.END)
    gui.output_text.config(state=tk.DISABLED)
    gui.master.update()  # Force update to show command before output starts

    def enqueue_output(process, out_queue, err_queue):
        # Capture and process stdout
        for line in iter(process.stdout.readline, ''):
            if line:
                # Remove ANSI color codes and control characters
                clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line)
                clean_line = re.sub(r'[\r\n]+', '\n', clean_line)
                out_queue.put(clean_line)
        
        # Capture and process stderr
        for line in iter(process.stderr.readline, ''):
            if line:
                # Remove ANSI color codes and control characters
                clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line)
                clean_line = re.sub(r'[\r\n]+', '\n', clean_line)
                err_queue.put(clean_line)

    try:
        # Create separate queues for stdout and stderr
        out_queue = queue.Queue()
        err_queue = queue.Queue()
        
        # Use line buffering for more responsive output
        process = subprocess.Popen(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            bufsize=1,
            universal_newlines=True
        )
        
        # Start thread to capture output
        output_thread = threading.Thread(
            target=enqueue_output, 
            args=(process, out_queue, err_queue)
        )
        output_thread.daemon = True
        output_thread.start()
        
        # Process output in real-time
        while process.poll() is None or not (out_queue.empty() and err_queue.empty()):
            # Process stdout
            try:
                while True:
                    line = out_queue.get_nowait()
                    gui.output_text.config(state=tk.NORMAL)
                    gui.output_text.insert(tk.END, line, "output")
                    gui.output_text.see(tk.END)
                    gui.output_text.config(state=tk.DISABLED)
                    gui.master.update()
            except queue.Empty:
                pass
                
            # Process stderr
            try:
                while True:
                    line = err_queue.get_nowait()
                    gui.output_text.config(state=tk.NORMAL)
                    gui.output_text.insert(tk.END, line, "error")
                    gui.output_text.see(tk.END)
                    gui.output_text.config(state=tk.DISABLED)
                    gui.master.update()
            except queue.Empty:
                pass
                
            # Brief pause to prevent CPU hogging
            time.sleep(0.05)
            gui.master.update()
        
        # Add exit code information like DOS
        exit_code = process.returncode
        gui.output_text.config(state=tk.NORMAL)
        if exit_code == 0:
            gui.output_text.insert(tk.END, f"\nCommand completed successfully with exit code {exit_code}\n", "output")
        else:
            gui.output_text.insert(tk.END, f"\nCommand failed with exit code {exit_code}\n", "error")
        
        # Add another command prompt at the end
        gui.output_text.insert(tk.END, f"\n{current_dir}>", "prompt")
        gui.output_text.see(tk.END)
        gui.output_text.config(state=tk.DISABLED)
        
    except FileNotFoundError:
        gui.output_text.config(state=tk.NORMAL)
        gui.output_text.insert(tk.END, "'{}' is not recognized as an internal or external command,\noperable program or batch file.\n".format(command[0]), "error")
        gui.output_text.insert(tk.END, f"\n{current_dir}>", "prompt")
        gui.output_text.see(tk.END)
        gui.output_text.config(state=tk.DISABLED)
    except Exception as e:
        gui.output_text.config(state=tk.NORMAL)
        gui.output_text.insert(tk.END, f"Error executing command: {e}\n", "error")
        gui.output_text.insert(tk.END, f"\n{current_dir}>", "prompt")
        gui.output_text.see(tk.END)
        gui.output_text.config(state=tk.DISABLED)

def chat_with_ai(message):
    """
    Communicates with the AI model using the generate endpoint.
    Sends a POST request to http://localhost:11434/api/generate with parameters for model, prompt, and stream.
    Returns the AI response.
    """
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "smollm2:135m",
        "prompt": message,
        "stream": False
    }
    try:
        response = requests.post(url, json=payload, verify=False)
        response.raise_for_status()
        # Assuming the returned JSON contains a field "completion" for the answer.
        return response.json().get("completion", "No completion field returned")
    except Exception as e:
        return f"Error communicating with AI: {e}"
