# main.py
import tkinter as tk
from ollama_gui import OllamaFinderGUI
import subprocess
import os
import sys
import logging
import shutil

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def check_ollama_installation():
    """Check if ollama is installed and accessible"""
    try:
        # Check if ollama is in PATH
        if shutil.which("ollama") is None:
            logging.error("Ollama executable not found in PATH")
            return False
        
        # Test basic ollama command
        result = subprocess.run(["ollama", "list"], 
                               capture_output=True, 
                               text=True, 
                               encoding="utf-8")
        
        if result.returncode != 0:
            logging.error(f"Ollama test command failed: {result.stderr}")
            return False
        
        return True
    except Exception as e:
        logging.error(f"Error checking Ollama installation: {e}")
        return False

def start_gui():
    """Start the GUI"""
    logging.debug("Starting GUI")
    
    # Check ollama installation before starting GUI
    if not check_ollama_installation():
        import tkinter.messagebox as messagebox
        messagebox.showerror("Ollama Not Found", 
                            "Ollama is not installed or not accessible.\n"
                            "Please install Ollama and make sure it's in your PATH.")
        logging.warning("Starting GUI without confirmed Ollama installation")
    
    root = tk.Tk()
    root.geometry("900x650")  # Updated window size for a modern look
    gui = OllamaFinderGUI(root)
    try:
        root.mainloop()
    except Exception as e:
        logging.error(f"Error starting GUI: {e}")

if __name__ == "__main__":
    start_gui()