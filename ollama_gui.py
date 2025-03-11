import tkinter as tk
from tkinter import scrolledtext, Listbox, ttk
import base64
import queue
import re  # Import the regular expression module
import webbrowser
import os
import platform

from tkinter import simpledialog
from ollama_commands import pull_model, create_model, serve_ollama, run_selected_model, list_models, show_model, ps_models, cp_model, rm_model
from ollama_functions import get_ollama_models, get_running_ollama_models, get_model_information, find_ollama
from ollama_gui_styling import configure_styles
from ollama_gui_widgets import create_widgets
from ollama_gui_events import bind_events, show_command_info, stop_selected_model, on_resize
from ollama_functions import start_search, search_ollama_thread, cancel_search, search_complete, log_message, save_ollama_location, populate_models_list, populate_running_models_list, run_command
from ollama_gui_listbox import show_model_information, show_running_model_information, display_model_information

MAX_DEPTH = 5  # Limit the search depth

class OllamaFinderGUI:
    def __init__(self, master):
        self.master = master
        master.title("Ollama Controller")
        master.geometry("900x650")  # Set initial window size
        master.minsize(600, 400)  # Set minimum window size

        # Embed the icon
        try:
            with open("dungeon.png", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
            self.icon_data = encoded_string.decode('utf-8')
            self.icon = tk.PhotoImage(data=self.icon_data)
            master.iconphoto(False, self.icon)
        except FileNotFoundError:
            print("Icon file 'dungeon.png' not found. Continuing without icon.")

        # --- Styling with updated modern palette ---
        self.style = ttk.Style()
        self.bg_color = "#2E3440"           # Nord dark background
        self.text_color = "#D8DEE9"         # Nord foreground
        self.checking_color = "#EBCB8B"     # Soft yellow
        self.found_color = "#A3BE8C"        # Soft green
        self.not_found_color = "#BF616A"    # Soft red
        self.cancelled_color = "#D08770"    # Soft orange
        self.button_color = "#5E81AC"       # Muted blue
        self.button_text_color = "#ECEFF4"  # Light text on buttons
        self.listbox_select_color = "#4C566A"  # Subtle selection

        configure_styles(self.style, self.bg_color, self.text_color, self.button_color, self.button_text_color, self.listbox_select_color)

        master.configure(bg=self.bg_color)
        master.rowconfigure(0, weight=1)
        master.columnconfigure(0, weight=1)
        master.columnconfigure(1, weight=1)

        # --- Frames ---
        self.left_frame = tk.Frame(master, bg=self.bg_color, borderwidth=2, relief="solid")
        self.left_frame.place(relx=0, rely=0, relwidth=0.5, relheight=1)

        self.right_frame = tk.Frame(master, bg=self.bg_color, borderwidth=2, relief="solid")
        self.right_frame.place(relx=0.5, rely=0, relwidth=0.5, relheight=1)

        create_widgets(self, master)
        bind_events(self, master)

        # --- Variables and Initialization ---
        self.ollama_location = None
        self.searching = False
        self.search_thread = None
        self.selected_model = None
        self.selected_running_model = None
        self.queue = queue.Queue()  # Queue for real-time output

        populate_models_list(self)
        populate_running_models_list(self)
        self.process_queue()  # Start processing the queue for real-time output
        self.update_running_models_periodically()

    def process_queue(self):
        """
        Processes the output queue and displays the output in the text widget.
        """
        try:
            while True:
                line = self.queue.get_nowait()
                log_message(self, line.strip())
        except queue.Empty:
            pass
        self.master.after(100, self.process_queue)  # Check every 100 ms

    def update_running_models_periodically(self):
        """
        Updates the running models list every 6 seconds.
        """
        populate_running_models_list(self)
        self.master.after(6000, self.update_running_models_periodically)  # Schedule the update every 6 seconds

    def stop_selected_model(self):
        stop_selected_model(self)

    def show_command_info(self, message):
        show_command_info(self, message)

    def show_model_information(self, event):
        show_model_information(self, event)

    def show_running_model_information(self, event):
        show_running_model_information(self, event)

    def display_model_information(self, model_info):
        display_model_information(self, model_info)

    def on_resize(self, event=None):
        on_resize(self, event)

    def pull_model_command(self):
        pull_model(self)

    def create_model_command(self):
        create_model(self)

    def serve_ollama_command(self):
        serve_ollama(self)

    def run_selected_model_command(self):
        run_selected_model(self)

    def list_models_command(self):
        list_models(self)

    def show_model_command(self):
        show_model(self)

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
