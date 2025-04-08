from tkinter import simpledialog, messagebox
import subprocess
from ollama_functions import log_message

def pull_model(gui):
    """
    Pulls a model.
    """
    model_name = simpledialog.askstring("Pull Model", "Enter model name to pull:")
    if (model_name):
        log_message(gui, f"Pulling model: {model_name}", gui.checking_color)
        gui.run_command(["ollama", "pull", model_name])

def create_model(gui):
    """
    Creates a model.
    """
    model_name = simpledialog.askstring("Create Model", "Enter model name:")
    if (model_name):
        file_path = simpledialog.askstring("Create Model", "Enter path to Modelfile:")
        if (file_path):
            log_message(gui, f"Creating model: {model_name} from {file_path}", gui.checking_color)
            gui.run_command(["ollama", "create", model_name, "-f", file_path])

def serve_ollama(gui):
    log_message(gui, "Starting Ollama server...", gui.checking_color)
    gui.run_command(["ollama", "serve"])

def run_selected_model(gui):
    """
    Runs the currently selected running model.
    """
    if gui.selected_running_model:
        log_message(gui, f"Running model: {gui.selected_running_model}", gui.found_color)
        log_message(gui, "Outputs will appear in the 'Output' pane.", gui.found_color)
        gui.run_command(["ollama", "run", gui.selected_running_model])
    else:
        messagebox.showinfo("Info", "No running model selected. Please select a running model from the list.")

def list_models(gui):
    """
    Lists the available models.
    """
    log_message(gui, "Listing available models...", gui.checking_color)
    gui.run_command(["ollama", "list"])

def show_model(gui):
    """
    Shows information about the selected model.
    """
    if (gui.selected_model):
        log_message(gui, f"Showing information for model: {gui.selected_model}", gui.checking_color)
        gui.run_command(["ollama", "show", gui.selected_model])
    else:
        messagebox.showinfo("Info", "No model selected. Please select a model from the list.")

def ps_models(gui):
    """
    Lists the running models.
    """
    log_message(gui, "Listing running models...", gui.checking_color)
    gui.run_command(["ollama", "ps"])

def cp_model(gui):
    """
    Copies a model.
    """
    source_model = simpledialog.askstring("Copy Model", "Enter source model name:")
    if (source_model):
        destination_model = simpledialog.askstring("Copy Model", "Enter destination model name:")
        if (destination_model):
            log_message(gui, f"Copying model: {source_model} to {destination_model}", gui.checking_color)
            gui.run_command(["ollama", "cp", source_model, destination_model])

def rm_model(gui):
    """
    Removes a model.
    """
    model_name = simpledialog.askstring("Remove Model", "Enter model name to remove:")
    if (model_name):
        log_message(gui, f"Removing model: {model_name}", gui.checking_color)
        gui.run_command(["ollama", "rm", model_name])
