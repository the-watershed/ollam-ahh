from tkinter import simpledialog, messagebox
import subprocess
from ollama_functions import log_message, populate_models_list

def get_selected_model(gui):
    """
    Helper function to get the selected model, prioritizing running models over available models.
    Returns the selected model name or None if no model is selected.
    """
    if gui.selected_running_model:
        return gui.selected_running_model
    elif gui.selected_model:
        return gui.selected_model
    else:
        return None

def pull_model(gui):
    """
    Pulls a model. Will use the selected model as the default value if available.
    """
    default_model = get_selected_model(gui) or ""
    model_name = simpledialog.askstring("Pull Model", "Enter model name to pull:", initialvalue=default_model)
    if model_name:
        log_message(gui, f"Pulling model: {model_name}", gui.checking_color)
        gui.run_command(["ollama", "pull", model_name])

def create_model(gui):
    """
    Creates a model. Will use the selected model as the default value if available.
    """
    default_model = get_selected_model(gui) or ""
    model_name = simpledialog.askstring("Create Model", "Enter model name:", initialvalue=default_model)
    if model_name:
        file_path = simpledialog.askstring("Create Model", "Enter path to Modelfile:")
        if file_path:
            log_message(gui, f"Creating model: {model_name} from {file_path}", gui.checking_color)
            gui.run_command(["ollama", "create", model_name, "-f", file_path])

def serve_ollama(gui):
    """
    Starts the Ollama server.
    """
    log_message(gui, "Starting Ollama server...", gui.checking_color)
    gui.run_command(["ollama", "serve"])

def run_selected_model(gui):
    """
    Runs the currently selected model (running or available).
    """
    model_to_run = get_selected_model(gui)
    if model_to_run:
        log_message(gui, f"Running model: {model_to_run}", gui.found_color)
        log_message(gui, "Outputs will appear in the 'Output' pane.", gui.found_color)
        gui.run_command(["ollama", "run", model_to_run])
    else:
        messagebox.showinfo("Info", "No model selected. Please select a model from either list.")

def list_models(gui):
    """
    Lists the available models.
    """
    log_message(gui, "Listing available models...", gui.checking_color)
    gui.run_command(["ollama", "list"])

def show_model(gui):
    """
    Shows information about the selected model. Attempts to use any selected model.
    """
    model_to_show = get_selected_model(gui)
    if model_to_show:
        log_message(gui, f"Showing information for model: {model_to_show}", gui.checking_color)
        gui.run_command(["ollama", "show", model_to_show])
    else:
        messagebox.showinfo("Info", "No model selected. Please select a model from either list.")

def ps_models(gui):
    """
    Lists the running models.
    """
    log_message(gui, "Listing running models...", gui.checking_color)
    gui.run_command(["ollama", "ps"])

def cp_model(gui):
    """
    Copies a model. Will use the selected model as the source by default if available.
    """
    default_model = get_selected_model(gui) or ""
    source_model = simpledialog.askstring("Copy Model", "Enter source model name:", initialvalue=default_model)
    if source_model:
        destination_model = simpledialog.askstring("Copy Model", "Enter destination model name:")
        if destination_model:
            log_message(gui, f"Copying model: {source_model} to {destination_model}", gui.checking_color)
            gui.run_command(["ollama", "cp", source_model, destination_model])

def rm_model(gui):
    """
    Removes a model. Will use the selected model as the default value if available.
    """
    default_model = get_selected_model(gui) or ""
    model_name = simpledialog.askstring("Remove Model", "Enter model name to remove:", initialvalue=default_model)
    if model_name:
        # Add confirmation to prevent accidental deletion
        confirm = messagebox.askyesno("Confirm Deletion", 
                                    f"Are you sure you want to remove model '{model_name}'? This action cannot be undone.",
                                    icon=messagebox.WARNING)
        if confirm:
            log_message(gui, f"Removing model: {model_name}", gui.checking_color)
            gui.run_command(["ollama", "rm", model_name])
            # Refresh the available models list after deletion
            populate_models_list(gui)
        else:
            log_message(gui, f"Removal of model '{model_name}' cancelled.", gui.cancelled_color)
