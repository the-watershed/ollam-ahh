# main.py
import tkinter as tk
from ollama_gui import OllamaFinderGUI
import subprocess
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def start_gui():
    logging.debug("Starting GUI")
    root = tk.Tk()
    root.geometry("900x650")  # Updated window size for a modern look
    gui = OllamaFinderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    start_gui()