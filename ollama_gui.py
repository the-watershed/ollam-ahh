import tkinter as tk
from tkinter import scrolledtext, Listbox, ttk
import base64
import queue
import re
import webbrowser
import os
import platform
import time  # Adding time import at the top level
from tkinter import simpledialog

from ollama_commands import pull_model, create_model, serve_ollama, run_selected_model, list_models, show_model, ps_models, cp_model, rm_model
from ollama_functions import get_ollama_models, get_running_ollama_models, get_model_information, find_ollama
from ollama_gui_styling import configure_styles
from ollama_gui_widgets import create_widgets
from ollama_gui_events import bind_events, show_command_info, stop_selected_model, on_resize
from ollama_functions import start_search, search_ollama_thread, cancel_search, search_complete, log_message, save_ollama_location, populate_models_list, populate_running_models_list, run_command
from ollama_gui_listbox import show_model_information as listbox_show_model_information, show_running_model_information as listbox_show_running_model_information, display_model_information

MAX_DEPTH = 5  # Limit the search depth

class OllamaFinderGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Ollama Finder")
        self.master.geometry("900x650")
        
        # --- Modern Blue Color Theme ---
        self.style = ttk.Style()
        self.bg_color = "#f0f4f8"         # Light blue-gray background
        self.text_color = "#333333"       # Dark text for readability
        self.checking_color = "#5b6abf"   # Indigo for checking status
        self.found_color = "#2e7d32"      # Green for found items
        self.not_found_color = "#c62828"  # Red for not found
        self.cancelled_color = "#d84315"  # Orange for cancelled operations
        self.button_color = "#1976d2"     # Microsoft blue
        self.button_text_color = "#ffffff" # White text on buttons
        self.listbox_select_color = "#bbdefb" # Light blue selection
        self.status_color = "#0078d7"     # Status info color (Windows accent blue)
        self.is_dark_mode = False         # Start with light mode by default
        
        # Configure the styles with our new color scheme
        configure_styles(self.style, self.bg_color, self.text_color, self.button_color, self.button_text_color, self.listbox_select_color)

        self.master.configure(bg=self.bg_color)
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        
        # Create main content frame - removes extra frames at the top
        self.main_frame = ttk.Frame(self.master, style="TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create left and right frames in the main content area
        self.left_frame = ttk.Frame(self.main_frame, style="TFrame", relief="flat")
        self.right_frame = ttk.Frame(self.main_frame, style="TFrame", relief="flat")
        
        # Make each section vertically resizable by dragging with the mouse
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        self.main_frame.columnconfigure(0, weight=1)

        self.left_frame.grid(row=0, column=0, sticky="nsew")
        self.right_frame.grid(row=1, column=0, sticky="nsew")
        
        # Create widgets in their respective frames
        create_widgets(self, self.master)

        # --- Variables and Initialization ---
        self.ollama_location = None
        self.searching = False
        self.search_thread = None
        self.selected_model = None
        self.selected_running_model = None
        self.queue = queue.Queue()  # Queue for real-time output
        
        # Model monitoring variables
        self.previous_running_models = []
        self.model_statuses = {}  # Store model status information
        self.monitor_active = True
        self.monitor_interval = 3000  # Check every 3 seconds
        
        # Properly integrate the indicator light and system message into the status bar
        self.status_bar = ttk.Frame(self.master, style="TFrame")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=0)

        self.status_message = ttk.Label(
            self.status_bar,
            text="Model monitoring: Active",
            anchor=tk.W,
            style="Resource.TLabel"
        )
        self.status_message.pack(side=tk.LEFT, padx=5)

        self.status_indicator = tk.Canvas(
            self.status_bar,
            width=12,
            height=12,
            bg=self.bg_color,
            highlightthickness=0
        )
        self.status_indicator.pack(side=tk.RIGHT, padx=5)
        self.status_indicator.create_oval(2, 2, 10, 10, fill=self.found_color, outline="")

        populate_models_list(self)
        populate_running_models_list(self)
        # Automatically select a running model if available
        from ollama_functions import get_running_ollama_models
        running_models = get_running_ollama_models()
        if (running_models):
            self.selected_running_model = running_models[0]
            self.previous_running_models = running_models.copy()
        self.process_queue()
        self.monitor_running_models()  # Start continuous monitoring

        # Adjust layout to eliminate the gap above the Tab features
        self.main_frame.pack_configure(pady=0)

        # Remove any unintended outline or padding
        self.main_frame.configure(relief="flat", borderwidth=0)

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
        self.master.after(100, self.process_queue)

    def update_running_models_periodically(self):
        """
        Updates the running models list every 6 seconds.
        """
        # Update the running models list
        populate_running_models_list(self)
        
        # Schedule the next update
        self.master.after(6000, self.update_running_models_periodically)

    def stop_selected_model(self):
        """
        Stops the currently selected running model by calling the stop_selected_model function
        from the ollama_gui_events module.
        """
        stop_selected_model(self)

    def show_command_info(self, message):
        """
        Displays command information in the UI by calling the show_command_info function
        from the ollama_gui_events module.
        
        Args:
            message (str): The message to display
        """
        show_command_info(self, message)

    def show_model_information(self, event):
        """
        Displays information about the selected model when a model is clicked
        in the models listbox.
        
        Args:
            event: The event object containing information about the click event
        """
        listbox_show_model_information(self, event)

    def show_running_model_information(self, event):
        """
        Displays information about the selected running model when a model is clicked
        in the running models listbox.
        
        Args:
            event: The event object containing information about the click event
        """
        listbox_show_running_model_information(self, event)

    def display_model_information(self, model_info):
        """
        Displays detailed model information in the appropriate UI area.
        
        Args:
            model_info (str): Information about the model to display
        """
        display_model_information(self, model_info)

    def on_resize(self, event=None):
        """
        Handles window resize events to adjust UI elements accordingly.
        
        Args:
            event: The resize event object (optional)
        """
        on_resize(self, event)
        
    # NEW: Add method to allow refreshing the running models list
    def populate_running_models_list(self):
        """
        Updates the running models listbox with the current state of running Ollama models.
        This is a convenience wrapper around the function in ollama_functions module.
        """
        from ollama_functions import populate_running_models_list
        populate_running_models_list(self)

    def refresh_models_list(self):
        """Refresh the list of available models."""
        try:
            populate_models_list(self)
            self.log_message("Models list refreshed successfully.", self.found_color)
        except Exception as e:
            self.log_message(f"Failed to refresh models list: {e}", self.not_found_color)

    def pull_model_command(self):
        """
        Pulls a model from the Ollama repository.
        Delegates to pull_model function in ollama_commands module.
        """
        pull_model(self)

    def create_model_command(self):
        """
        Creates a new model based on existing models.
        Delegates to create_model function in ollama_commands module.
        """
        create_model(self)

    def serve_ollama_command(self):
        """
        Starts the Ollama server if not running.
        Delegates to serve_ollama function in ollama_commands module.
        """
        serve_ollama(self)

    def run_selected_model_command(self):
        """
        Runs the selected model with optional arguments.
        Uses the running model if available; otherwise falls back to the available model.
        Provides detailed diagnostic information in case of errors.
        """
        # Use the running model if available; otherwise, fall back to available model
        if self.selected_running_model:
            model_to_run = self.selected_running_model
        elif self.selected_model:
            model_to_run = self.selected_model
        else:
            import tkinter.messagebox as messagebox
            messagebox.showwarning("No Model Selected", "No running or available model found to run.")
            return

        # Open dialog to get optional arguments, pre-filling with the last used arguments
        initial_args = getattr(self, 'last_run_args', '')  # Retrieve last used arguments or default to an empty string
        optional_args = simpledialog.askstring("Optional Arguments", 
                                              f"Enter optional arguments for running {model_to_run}:",
                                              initialvalue=initial_args,
                                              parent=self.master)

        if optional_args is not None:
            # Save the last used arguments for future use
            self.last_run_args = optional_args

        import subprocess
        cmd = ["ollama", "run", model_to_run]

        # Add optional arguments if provided
        if optional_args:
            cmd.extend(optional_args.split())

        # Execute the command
        self.run_command(cmd)

    def list_models_command(self):
        """
        Lists all available models.
        Delegates to list_models function in ollama_commands module.
        """
        list_models(self)

    def show_model_command(self):
        """
        Shows detailed information about a specific model.
        Delegates to show_model function in ollama_commands module.
        """
        show_model(self)

    def ps_models_command(self):
        """
        Displays the status of all running models.
        Delegates to ps_models function in ollama_commands module.
        """
        ps_models(self)

    def cp_model_command(self):
        """
        Copies a model from one location to another.
        Delegates to cp_model function in ollama_commands module.
        """
        cp_model(self)

    def rm_model_command(self):
        """
        Removes a specified model.
        Delegates to rm_model function in ollama_commands module.
        """
        rm_model(self)

    def run_command(self, command):
        """
        Wrapper method that delegates to the run_command function in the ollama_functions module.
        This avoids duplicating code while maintaining compatibility with existing function calls.
        
        Args:
            command (list): The command to run as a list of strings
        """
        from ollama_functions import run_command
        run_command(self, command)

    def open_more_models(self):
        """
        Placeholder for handling 'More Models' functionality.
        """
        pass

    def log_message(self, message, color=None):
        """
        Logs a message to the output text widget with optional color formatting.
        Delegates to log_message function in ollama_functions module.
        
        Args:
            message (str): The message to log
            color (str, optional): The color to use for the message text
        """
        from ollama_functions import log_message
        log_message(self, message, color)

    def send_chat(self):
        """
        Handles sending a chat message to the running Ollama model using the non-streaming API.
        Implements radiation shielding protocols for deep space communications.
        """
        # System safeguard check - verify life support systems
        user_message = self.chat_entry.get().strip()
        if user_message:
            if not self.selected_running_model:
                import tkinter.messagebox as messagebox
                messagebox.showwarning("ALERT: MODEL OFFLINE", "CRITICAL: No running neural core detected. Initiate model startup sequence immediately.")
                return
                
            # Log message with quantum encryption
            self.chat_text.config(state=tk.NORMAL)
            self.chat_text.insert(tk.END, "CREW: ", "user")
            self.chat_text.insert(tk.END, user_message + "\n", "user")
            self.chat_text.config(state=tk.DISABLED)
            self.chat_entry.delete(0, tk.END)
            
            import requests
            payload = {
                "prompt": user_message,
                "model": self.selected_running_model,
                "system": "You are the ship's AI assistant responding to crew queries."
            }
            
            # Transmission metadata - encode with shield frequency
            debug_info = (
                "    TRANSMISSION DATA:\n"
                "        Neural endpoint: http://localhost:11434/api/chat\n"
                "        Payload encryption: " + str(payload) + "\n"
            )
            
            self.chat_text.config(state=tk.NORMAL)
            self.chat_text.insert(tk.END, debug_info, "debug")
            self.chat_text.insert(tk.END, "\n")
            self.chat_text.config(state=tk.DISABLED)
            
            try:
                # Engage subspace communications
                self.chat_text.config(state=tk.NORMAL)
                self.chat_text.insert(tk.END, "SYSTEM: Establishing neural link... stand by...\n", "system")
                self.chat_text.config(state=tk.DISABLED)
                self.chat_text.see(tk.END)  # Auto-scroll
                self.master.update()  # Force UI update to show waiting message
                
                # Implement radiation shield with 3-layer retry logic
                max_retries = 3
                retry_count = 0
                while retry_count < max_retries:
                    try:
                        response = requests.post(
                            "http://localhost:11434/api/chat",
                            json=payload,
                            headers={"Content-Type": "application/json"},
                            timeout=60
                        )
                        response.raise_for_status()
                        break  # Success, exit retry loop
                    except (requests.ConnectionError, requests.Timeout) as e:
                        retry_count += 1
                        if retry_count < max_retries:
                            self.chat_text.config(state=tk.NORMAL)
                            self.chat_text.insert(tk.END, f"SYSTEM: Communication interference detected. Remodulating shields. Retry {retry_count}/{max_retries}...\n", "system")
                            self.chat_text.config(state=tk.DISABLED)
                            self.chat_text.see(tk.END)
                            self.master.update()
                            import time
                            time.sleep(1)  # Wait before retry
                        else:
                            raise  # Re-raise if max retries reached
                
                data = response.json()
                # Extract neural core response
                content = data.get("message", {}).get("content", "")
                if not content:
                    content = "<No neural response received - check core status>"
                    
                # Display AI response with appropriate signal encoding
                self.chat_text.config(state=tk.NORMAL)
                self.chat_text.insert(tk.END, "SHIP AI: ", "ai")
                self.chat_text.insert(tk.END, content + "\n", "ai")
                
                # Add transmission verification data
                final_debug = (
                    "    TRANSMISSION VERIFICATION:\n"
                    f"        Response integrity: {response.status_code}\n"
                    f"        Quantum fingerprint: {hash(response.text) & 0xFFFFFFFF:08X}\n"
                )
                self.chat_text.insert(tk.END, final_debug, "debug")
                self.chat_text.insert(tk.END, "\n")
                self.chat_text.config(state=tk.DISABLED)
                self.chat_text.see(tk.END)
                
            except Exception as e:
                # Critical system alert with emergency protocols
                error_class = e.__class__.__name__
                self.chat_text.config(state=tk.NORMAL)
                self.chat_text.insert(tk.END, "ALERT: ", "error")
                self.chat_text.insert(tk.END, f"Neural core communication failure - {error_class}\n", "error")
                
                # System diagnostic and recovery protocols
                error_debug = (
                    f"    EMERGENCY DIAGNOSTIC:\n"
                    f"        Exception type: {error_class}\n"
                    f"        Error message: {str(e)}\n"
                    f"        Recovery protocol: Restart neural core or check connection integrity\n"
                )
                self.chat_text.insert(tk.END, error_debug, "debug")
                self.chat_text.insert(tk.END, "\n")
                self.chat_text.config(state=tk.DISABLED)
                self.chat_text.see(tk.END)

    def monitor_running_models(self):
        """
        CRITICAL SHIPBOARD SYSTEM: Neural Core Monitoring Array
        Provides continuous surveillance of all neural cores and model integrity.
        Implements automatic recovery procedures for core fluctuations.
        """
        if not self.monitor_active:
            return
            
        try:
            # Get current models state
            current_running_models = get_running_ollama_models()
            current_available_models = get_ollama_models()
            
            # Initialize if needed
            if not hasattr(self, 'previous_available_models'):
                self.previous_available_models = current_available_models.copy()
                self.log_message("\nSTATUS: Neural core monitoring systems initialized\n", self.status_color)
            
            # Detect changes to reduce UI updates and flickering
            running_models_changed = set(current_running_models) != set(self.previous_running_models)
            available_models_changed = set(current_available_models) != set(self.previous_available_models)
            
            # Only update status indicators when necessary
            if running_models_changed:
                if current_running_models:
                    self.status_indicator.delete("all")
                    self.status_indicator.create_oval(0, 0, 10, 10, fill=self.found_color, outline="")
                    self.status_message.config(text=f"SYSTEM STATUS: {len(current_running_models)} neural core(s) operational")
                else:
                    self.status_indicator.delete("all")
                    self.status_indicator.create_oval(0, 0, 10, 10, fill=self.checking_color, outline="")
                    self.status_message.config(text="ALERT: No neural cores active - ship AI functionality limited")
            
            # Monitor for newly started models
            for model in current_running_models:
                if model not in self.previous_running_models:
                    self.log_message(f"\nSYSTEM: Neural core '{model}' initialization sequence complete\n", self.found_color)
                    try:
                        from plyer import notification
                        notification.notify(
                            title="Neural Core Online",
                            message=f"Core '{model}' is now operational",
                            app_name="Ship Mainframe", 
                            timeout=5
                        )
                    except ImportError:
                        pass
            
            # Monitor for stopped models
            for model in self.previous_running_models:
                if model not in current_running_models:
                    self.log_message(f"\nALERT: Neural core '{model}' has gone offline\n", self.cancelled_color)
                    
                    # Handle selection changes only when necessary
                    if self.selected_running_model == model:
                        self.selected_running_model = None
                        if current_running_models:
                            self.selected_running_model = current_running_models[0]
                            self.log_message(f"\nSYSTEM: Emergency neural pathway established via core: {self.selected_running_model}\n", self.status_color)
                    
                    try:
                        from plyer import notification
                        notification.notify(
                            title="Neural Core Offline",
                            message=f"Core '{model}' requires maintenance",
                            app_name="Ship Mainframe",
                            timeout=5
                        )
                    except ImportError:
                        pass
            
            # Monitor for new available models
            for model in current_available_models:
                if model not in self.previous_available_models:
                    self.log_message(f"\nDATA: New neural pattern detected: '{model}' added to template library\n", self.status_color)
                    try:
                        from plyer import notification
                        notification.notify(
                            title="Neural Pattern Added",
                            message=f"Pattern '{model}' available for core initialization",
                            app_name="Ship Mainframe",
                            timeout=5
                        )
                    except ImportError:
                        pass
            
            # Monitor for removed available models
            for model in self.previous_available_models:
                if model not in current_available_models:
                    self.log_message(f"\nALERT: Neural pattern '{model}' has been removed from template library\n", self.cancelled_color)
                    
                    if self.selected_model == model:
                        self.selected_model = None
                        if current_available_models:
                            self.selected_model = current_available_models[0]
                            self.log_message(f"\nSYSTEM: Automatic pattern selection: {self.selected_model}\n", self.status_color)
                    
                    try:
                        from plyer import notification
                        notification.notify(
                            title="Neural Pattern Removed",
                            message=f"Pattern '{model}' no longer available",
                            app_name="Ship Mainframe",
                            timeout=5
                        )
                    except ImportError:
                        pass
            
            # Only update UI components when actually needed
            if running_models_changed:
                # Update the running models list without causing UI flicker
                self.master.after_idle(lambda: populate_running_models_list(self))
                
                if current_running_models and not self.selected_running_model:
                    self.selected_running_model = current_running_models[0]
            
            if available_models_changed:
                # Update the available models list without causing UI flicker
                self.master.after_idle(lambda: populate_models_list(self))
                
                if current_available_models and not self.selected_model and not self.selected_running_model:
                    self.selected_model = current_available_models[0]
            
            # Store current state for next comparison
            self.previous_running_models = current_running_models.copy()
            self.previous_available_models = current_available_models.copy()
        
        except Exception as e:
            error_class = e.__class__.__name__
            self.log_message(f"\nCRITICAL: Neural monitoring subsystem failure - {error_class}\n", self.not_found_color)
            self.log_message(f"Error details: {str(e)}", self.not_found_color)
        
        # Schedule next check using a different approach to reduce flickering
        self.monitor_task = self.master.after(self.monitor_interval, self.monitor_running_models)

    def toggle_monitoring(self):
        """
        CRITICAL SYSTEM: Neural Core Surveillance Toggle
        Controls activation state of the primary neural monitoring grid.
        Implements emergency protocols for core surveillance systems.
        """
        self.monitor_active = not self.monitor_active
        
        if self.monitor_active:
            # Monitoring systems online - full neural surveillance activated
            self.status_message.config(text="SYSTEM STATUS: Neural monitoring grid active")
            self.status_indicator.delete("all")
            self.status_indicator.create_oval(0, 0, 10, 10, fill=self.found_color, outline="")
            self.monitor_button.config(text="Emergency Suspend")
            self.log_message("\nSYSTEM: Neural monitoring grid activated - all cores under surveillance\n", self.status_color)
            # Reinitialize quantum monitoring algorithms
            self.monitor_running_models()
        else:
            # Emergency shutdown of monitoring systems
            self.status_message.config(text="ALERT: Neural monitoring suspended - reduced system awareness")
            self.status_indicator.delete("all")
            self.status_indicator.create_oval(0, 0, 10, 10, fill=self.not_found_color, outline="")
            self.monitor_button.config(text="Restore Monitoring")
            self.log_message("\nALERT: Neural monitoring grid suspended - system awareness compromised\n", self.cancelled_color)
    
    def adjust_monitoring_interval(self):
        """
        CRITICAL SYSTEM: Neural Surveillance Sensitivity Control
        Modifies the quantum oscillation frequency of the monitoring systems.
        Implements adaptive resource allocation based on power availability.
        """
        from tkinter import simpledialog
        
        new_interval = simpledialog.askinteger(
            "Neural Scan Frequency", 
            "Set neural scan interval (milliseconds):\n\n1000: High power consumption (max sensitivity)\n5000: Normal operation\n10000: Power conservation mode",
            minvalue=1000, 
            maxvalue=10000,
            initialvalue=self.monitor_interval
        )
        
        if new_interval:
            # Implement adaptive power allocation based on scan frequency
            power_status = "OPTIMAL" if new_interval < 3000 else "STANDARD" if new_interval < 7000 else "CONSERVATION"
            
            self.monitor_interval = new_interval
            self.log_message(f"\nSYSTEM: Neural scan frequency adjusted to {new_interval}ms\n", self.status_color)
            self.log_message(f"Power allocation: {power_status} - System sensitivity adjusted accordingly", self.checking_color)
            
            # Update bridge systems with new configuration
            if power_status == "OPTIMAL":
                self.status_message.config(text=f"SYSTEM STATUS: High-resolution neural monitoring active - {new_interval}ms")
            elif power_status == "CONSERVATION":
                self.status_message.config(text=f"SYSTEM STATUS: Power-saving neural monitoring - {new_interval}ms")
            else:
                self.status_message.config(text=f"SYSTEM STATUS: Standard neural monitoring - {new_interval}ms")

    def open_dos_window(self):
        """
        Opens a DOS command prompt (cmd.exe) window in the Ollama installation directory.
        First determines the Ollama location, then opens a command window there.
        """
        import os
        import subprocess
        import shutil
        
        # Find Ollama location
        ollama_path = None
        
        # Check if we already know the location
        if hasattr(self, 'ollama_location') and self.ollama_location:
            ollama_path = self.ollama_location
        
        # If not, look for it in PATH
        if not ollama_path:
            ollama_in_path = shutil.which("ollama")
            if ollama_in_path:
                ollama_path = ollama_in_path
        
        # If still not found, look for the saved location
        if not ollama_path and os.path.exists("ollam-ah.dat"):
            try:
                with open("ollam-ah.dat", "r") as f:
                    ollama_path = f.read().strip()
            except Exception as e:
                self.log_message(f"Error reading Ollama location: {e}", self.not_found_color)
        
        # Extract directory from path if found
        if ollama_path:
            ollama_dir = os.path.dirname(ollama_path)
            try:
                # Start command prompt in the directory
                self.log_message(f"Opening DOS window in {ollama_dir}", self.found_color)
                subprocess.Popen(["cmd.exe", "/K", f"cd /d {ollama_dir} && echo Ollama Directory: %CD%"], 
                                shell=False, creationflags=subprocess.CREATE_NEW_CONSOLE)
            except Exception as e:
                self.log_message(f"Error opening DOS window: {e}", self.not_found_color)
        else:
            # If Ollama location not found, open in current directory
            self.log_message("Ollama location not found. Opening DOS window in current directory.", self.checking_color)
            subprocess.Popen(["cmd.exe", "/K", "echo Ollama Location not found. Current Directory: %CD%"], 
                            shell=False, creationflags=subprocess.CREATE_NEW_CONSOLE)

    def stop_current_operation(self, event=None):
        """Stop the current operation (model execution, etc.)"""
        # This is a placeholder for handling Escape key presses
        # The actual implementation would depend on what operation is running
        self.log_message("Stopping current operation...", self.cancelled_color)

    def search_models(self):
        """Search for models based on the input in the search bar."""
        search_query = self.search_entry.get().strip()
        if not search_query:
            self.log_message("Search query is empty. Please enter a search term.", self.not_found_color)
            return

        # Perform the search (placeholder logic)
        matching_models = [model for model in self.previous_available_models if search_query.lower() in model.lower()]

        if matching_models:
            self.log_message(f"Found {len(matching_models)} matching models:", self.found_color)
            for model in matching_models:
                self.log_message(f"- {model}", self.found_color)
        else:
            self.log_message("No matching models found.", self.not_found_color)

    def copy_model_name(self):
        """Copy the selected model's name to the clipboard."""
        selected_model = self.models_listbox.get(tk.ACTIVE)
        if selected_model:
            self.master.clipboard_clear()
            self.master.clipboard_append(selected_model)
            self.master.update()  # Ensure the clipboard is updated
            self.log_message(f"Copied model name: {selected_model}", self.found_color)
        else:
            self.log_message("No model selected to copy.", self.not_found_color)

    def tag_selected_model(self):
        """Tag the selected model as a favorite or with a custom label."""
        selected_model = self.models_listbox.get(tk.ACTIVE)
        if selected_model:
            tag = simpledialog.askstring("Tag Model", f"Enter a tag for the model '{selected_model}':", parent=self.master)
            if tag:
                self.log_message(f"Tagged model '{selected_model}' with tag: {tag}", self.found_color)
            else:
                self.log_message("Tagging canceled.", self.not_found_color)
        else:
            self.log_message("No model selected to tag.", self.not_found_color)

    def toggle_favorite(self):
        """Toggle the favorite status of the selected model."""
        selected_model = self.models_listbox.get(tk.ACTIVE)
        if selected_model:
            # Placeholder logic for toggling favorite status
            is_favorite = getattr(self, 'favorite_models', {}).get(selected_model, False)
            self.favorite_models[selected_model] = not is_favorite
            status = "added to" if not is_favorite else "removed from"
            self.log_message(f"Model '{selected_model}' {status} favorites.", self.found_color)
        else:
            self.log_message("No model selected to toggle favorite status.", self.not_found_color)

    def export_model_config(self):
        """Export the configuration of the selected model to a file."""
        selected_model = self.models_listbox.get(tk.ACTIVE)
        if selected_model:
            file_path = simpledialog.askstring("Export Configuration", "Enter the file path to save the configuration:", parent=self.master)
            if file_path:
                try:
                    # Placeholder logic for exporting configuration
                    with open(file_path, 'w') as file:
                        file.write(f"Configuration for model: {selected_model}\n")
                        file.write("...model configuration details...")
                    self.log_message(f"Configuration for '{selected_model}' exported to {file_path}", self.found_color)
                except Exception as e:
                    self.log_message(f"Failed to export configuration: {e}", self.not_found_color)
            else:
                self.log_message("Export canceled.", self.not_found_color)
        else:
            self.log_message("No model selected to export configuration.", self.not_found_color)

    def open_modelfile_builder(self):
        """Open a dialog to create a new model file."""
        file_path = simpledialog.askstring("Create Model File", "Enter the file path for the new model:", parent=self.master)
        if file_path:
            try:
                # Placeholder logic for creating a model file
                with open(file_path, 'w') as file:
                    file.write("# New model file\n")
                    file.write("...model details...")
                self.log_message(f"New model file created at: {file_path}", self.found_color)
            except Exception as e:
                self.log_message(f"Failed to create model file: {e}", self.not_found_color)
        else:
            self.log_message("Model file creation canceled.", self.not_found_color)

    def show_models_context_menu(self, event):
        """Display the context menu for the models listbox."""
        try:
            # Ensure an item is selected before showing the context menu
            if self.models_listbox.curselection():
                self.models_context_menu.tk_popup(event.x_root, event.y_root)
            else:
                self.log_message("No model selected to show context menu.", self.not_found_color)
        finally:
            self.models_context_menu.grab_release()

    def show_batch_operations(self):
        """Display a dialog for batch operations on models."""
        try:
            # Placeholder logic for batch operations
            batch_window = tk.Toplevel(self.master)
            batch_window.title("Batch Operations")
            batch_window.geometry("400x300")

            label = ttk.Label(batch_window, text="Batch operations are under development.", font=("Segoe UI", 10))
            label.pack(pady=20)

            close_button = ttk.Button(batch_window, text="Close", command=batch_window.destroy)
            close_button.pack(pady=10)

            self.log_message("Opened batch operations dialog.", self.found_color)
        except Exception as e:
            self.log_message(f"Failed to open batch operations dialog: {e}", self.not_found_color)

    def manage_parameter_presets(self):
        """Open a dialog to manage parameter presets."""
        try:
            presets_window = tk.Toplevel(self.master)
            presets_window.title("Manage Parameter Presets")
            presets_window.geometry("400x300")

            label = ttk.Label(presets_window, text="Parameter presets management is under development.", font=("Segoe UI", 10))
            label.pack(pady=20)

            close_button = ttk.Button(presets_window, text="Close", command=presets_window.destroy)
            close_button.pack(pady=10)

            self.log_message("Opened parameter presets management dialog.", self.found_color)
        except Exception as e:
            self.log_message(f"Failed to open parameter presets management dialog: {e}", self.not_found_color)

    def load_chat_history(self, event=None):
        """Load the selected chat history from the history listbox."""
        selected_history = self.history_listbox.get(tk.ACTIVE)
        if selected_history:
            try:
                # Placeholder logic for loading chat history
                self.chat_text.config(state=tk.NORMAL)
                self.chat_text.delete(1.0, tk.END)
                self.chat_text.insert(tk.END, f"Loaded chat history for: {selected_history}\n")
                self.chat_text.config(state=tk.DISABLED)
                self.log_message(f"Chat history for '{selected_history}' loaded successfully.", self.found_color)
            except Exception as e:
                self.log_message(f"Failed to load chat history: {e}", self.not_found_color)
        else:
            self.log_message("No chat history selected to load.", self.not_found_color)

    def save_chat_history(self):
        """Save the current chat history to a file."""
        file_path = simpledialog.askstring("Save Chat History", "Enter the file path to save the chat history:", parent=self.master)
        if file_path:
            try:
                # Placeholder logic for saving chat history
                with open(file_path, 'w') as file:
                    chat_content = self.chat_text.get(1.0, tk.END).strip()
                    file.write(chat_content)
                self.log_message(f"Chat history saved to {file_path}", self.found_color)
            except Exception as e:
                self.log_message(f"Failed to save chat history: {e}", self.not_found_color)
        else:
            self.log_message("Save chat history canceled.", self.not_found_color)

    def delete_chat_history(self):
        """Delete the selected chat history from the history listbox."""
        selected_history = self.history_listbox.get(tk.ACTIVE)
        if selected_history:
            confirm = tk.messagebox.askyesno("Delete Chat History", f"Are you sure you want to delete the chat history for '{selected_history}'?")
            if confirm:
                try:
                    # Placeholder logic for deleting chat history
                    self.history_listbox.delete(tk.ACTIVE)
                    self.log_message(f"Chat history for '{selected_history}' deleted successfully.", self.found_color)
                except Exception as e:
                    self.log_message(f"Failed to delete chat history: {e}", self.not_found_color)
            else:
                self.log_message("Delete chat history canceled.", self.not_found_color)
        else:
            self.log_message("No chat history selected to delete.", self.not_found_color)

    def toggle_theme(self):
        """Toggle between light and dark themes."""
        self.is_dark_mode = not self.is_dark_mode
        if self.is_dark_mode:
            self.bg_color = "#2e3440"  # Dark background
            self.text_color = "#d8dee9"  # Light text
        else:
            self.bg_color = "#f0f4f8"  # Light background
            self.text_color = "#333333"  # Dark text

        # Update styles
        configure_styles(self.style, self.bg_color, self.text_color, self.button_color, self.button_text_color, self.listbox_select_color)
        self.master.configure(bg=self.bg_color)
        self.log_message("Theme toggled successfully.", self.found_color)

    def show_keyboard_shortcuts(self):
        """Display a dialog with a list of keyboard shortcuts."""
        try:
            shortcuts_window = tk.Toplevel(self.master)
            shortcuts_window.title("Keyboard Shortcuts")
            shortcuts_window.geometry("400x300")

            label = ttk.Label(shortcuts_window, text="Keyboard Shortcuts", font=("Segoe UI", 12, "bold"))
            label.pack(pady=10)

            shortcuts = [
                ("Ctrl+N", "Start a new chat"),
                ("Ctrl+S", "Save chat history"),
                ("Ctrl+O", "Open a model"),
                ("Ctrl+Q", "Quit application"),
                ("Ctrl+F", "Search models"),
            ]

            for key, description in shortcuts:
                shortcut_label = ttk.Label(shortcuts_window, text=f"{key}: {description}", font=("Segoe UI", 10))
                shortcut_label.pack(anchor="w", padx=20, pady=2)

            close_button = ttk.Button(shortcuts_window, text="Close", command=shortcuts_window.destroy)
            close_button.pack(pady=10)

            self.log_message("Opened keyboard shortcuts dialog.", self.found_color)
        except Exception as e:
            self.log_message(f"Failed to open keyboard shortcuts dialog: {e}", self.not_found_color)

    def copy_chat_selection(self):
        """Copy the selected text from the chat to the clipboard."""
        try:
            selected_text = self.chat_text.selection_get()
            self.master.clipboard_clear()
            self.master.clipboard_append(selected_text)
            self.master.update()  # Ensure the clipboard is updated
            self.log_message("Selected chat text copied to clipboard.", self.found_color)
        except tk.TclError:
            self.log_message("No text selected to copy.", self.not_found_color)

    def copy_entire_chat(self):
        """Copy the entire chat content to the clipboard."""
        try:
            chat_content = self.chat_text.get(1.0, tk.END).strip()
            if chat_content:
                self.master.clipboard_clear()
                self.master.clipboard_append(chat_content)
                self.master.update()  # Ensure the clipboard is updated
                self.log_message("Entire chat copied to clipboard.", self.found_color)
            else:
                self.log_message("Chat is empty. Nothing to copy.", self.not_found_color)
        except Exception as e:
            self.log_message(f"Failed to copy chat: {e}", self.not_found_color)

    def clear_chat(self):
        """Clear the chat content in the chat text widget."""
        try:
            self.chat_text.config(state=tk.NORMAL)
            self.chat_text.delete(1.0, tk.END)
            self.chat_text.config(state=tk.DISABLED)
            self.log_message("Chat cleared successfully.", self.found_color)
        except Exception as e:
            self.log_message(f"Failed to clear chat: {e}", self.not_found_color)

    def search_in_chat(self):
        """Search for a specific term in the chat content."""
        try:
            search_term = simpledialog.askstring("Search Chat", "Enter the term to search for:", parent=self.master)
            if search_term:
                chat_content = self.chat_text.get(1.0, tk.END)
                occurrences = [match.start() for match in re.finditer(re.escape(search_term), chat_content)]
                if occurrences:
                    self.chat_text.tag_remove("highlight", 1.0, tk.END)
                    for start in occurrences:
                        end = start + len(search_term)
                        self.chat_text.tag_add("highlight", f"1.0+{start}c", f"1.0+{end}c")
                        self.chat_text.tag_config("highlight", background="yellow")
                    self.log_message(f"Found {len(occurrences)} occurrence(s) of '{search_term}' in chat.", self.found_color)
                else:
                    self.log_message(f"No occurrences of '{search_term}' found in chat.", self.not_found_color)
            else:
                self.log_message("Search canceled.", self.not_found_color)
        except Exception as e:
            self.log_message(f"Failed to search in chat: {e}", self.not_found_color)

    def show_chat_context_menu(self, event):
        """Display the context menu for the chat text widget."""
        try:
            self.chat_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.chat_context_menu.grab_release()

    def start_new_chat(self):
        """Start a new chat by clearing the chat text widget and resetting the state."""
        try:
            self.chat_text.config(state=tk.NORMAL)
            self.chat_text.delete(1.0, tk.END)
            self.chat_text.config(state=tk.DISABLED)
            self.log_message("New chat started.", self.found_color)
        except Exception as e:
            self.log_message(f"Failed to start new chat: {e}", self.not_found_color)

    def remove_help_button(self):
        """Remove the help button from the GUI if it exists."""
        # Assuming the help button is stored as an attribute named 'help_button'
        if hasattr(self, 'help_button') and self.help_button:
            self.help_button.destroy()
            self.help_button = None
            self.log_message("Help button removed successfully.", self.found_color)
