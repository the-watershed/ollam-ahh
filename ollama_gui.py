import tkinter as tk
from tkinter import scrolledtext, Listbox, ttk
import base64
import queue
import re
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
from ollama_gui_listbox import show_model_information as listbox_show_model_information, show_running_model_information as listbox_show_running_model_information, display_model_information

MAX_DEPTH = 5  # Limit the search depth

class OllamaFinderGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Ollama Finder")
        self.master.geometry("900x650")
        # Removed self.pack() because the class does not inherit from a widget

        # --- Styling & Colors ---
        self.style = ttk.Style()
        self.bg_color = "#002b36"         # Solarized Dark Base02
        self.text_color = "#839496"       # Solarized Dark Base0
        self.checking_color = "#b58900"     # Solarized Dark Yellow
        self.found_color = "#859900"      # Solarized Dark Green
        self.not_found_color = "#dc322f"  # Solarized Dark Red
        self.cancelled_color = "#cb4b16"    # Solarized Dark Orange
        self.button_color = "#586e75"     # Solarized Dark Base01
        self.button_text_color = "#000000" 
        self.listbox_select_color = "#073642"
        self.status_color = "#2aa198"     # Solarized Dark Cyan for status
        configure_styles(self.style, self.bg_color, self.text_color, self.button_color, self.button_text_color, self.listbox_select_color)

        self.master.configure(bg=self.bg_color)
        self.master.rowconfigure(0, weight=1)
        # Remove fixed column configuration
        # self.master.columnconfigure(0, weight=1)
        # self.master.columnconfigure(1, weight=1)
        # self.master.columnconfigure(2, weight=1)
        
        # --- Panels as resizable PanedWindow ---
        self.paned_window = tk.PanedWindow(self.master, orient=tk.HORIZONTAL, bg=self.bg_color)
        self.paned_window.pack(fill=tk.BOTH, expand=1)
        
        self.left_frame = tk.Frame(self.paned_window, bg=self.bg_color, borderwidth=2, relief="solid")
        self.paned_window.add(self.left_frame, minsize=200)
        
        self.right_frame = tk.Frame(self.paned_window, bg=self.bg_color, borderwidth=2, relief="solid")
        self.paned_window.add(self.right_frame, minsize=200)
        
        self.chat_frame = tk.Frame(self.paned_window, bg=self.bg_color, borderwidth=2, relief="solid")
        self.paned_window.add(self.chat_frame, minsize=200)

        create_widgets(self, self.master)
        bind_events(self, self.master)

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
        
        # Add status bar for monitoring
        self.status_bar = tk.Label(
            self.master, 
            text="Model monitoring: Active", 
            bd=1, 
            relief=tk.SUNKEN, 
            anchor=tk.W,
            bg=self.bg_color,
            fg=self.status_color
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Status indicator dot
        self.status_indicator_frame = tk.Frame(self.status_bar, bg=self.bg_color)
        self.status_indicator_frame.pack(side=tk.RIGHT, padx=5)
        self.status_indicator = tk.Canvas(
            self.status_indicator_frame, 
            width=10, 
            height=10, 
            bg=self.bg_color, 
            highlightthickness=0
        )
        self.status_indicator.pack(side=tk.RIGHT, padx=5)
        self.status_indicator.create_oval(0, 0, 10, 10, fill=self.found_color, outline="")

        populate_models_list(self)
        populate_running_models_list(self)
        # Automatically select a running model if available
        from ollama_functions import get_running_ollama_models
        running_models = get_running_ollama_models()  # Removed 'self' argument
        if (running_models):
            self.selected_running_model = running_models[0]
            self.previous_running_models = running_models.copy()
        self.process_queue()
        self.monitor_running_models()  # Start continuous monitoring

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
            
        # Open dialog to get optional arguments
        optional_args = simpledialog.askstring("Optional Arguments", 
                                              f"Enter optional arguments for running {model_to_run}:",
                                              parent=self.master)
        
        import subprocess
        cmd = ["ollama", "run", model_to_run]
        
        # Add optional arguments if provided
        if optional_args:
            cmd.extend(optional_args.split())
        
        # Create a readable execution string to display in the output
        execution_string = "ollama.exe " + " ".join(cmd[1:])
        
        try:
            # Display the execution string in the output window
            self.chat_text.config(state=tk.NORMAL)
            self.chat_text.insert(tk.END, f"\n> Executing: {execution_string}\n\n")
            self.chat_text.config(state=tk.DISABLED)
            
            result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
            output = result.stdout
            
            # Handle errors by capturing stderr output too
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else "Unknown error occurred"
                output = f"Error: Command returned exit code {result.returncode}\n\nStderr: {error_msg}"
                
                # Try to provide more helpful diagnostics
                if "no such model" in error_msg.lower() or "not found" in error_msg.lower():
                    output += f"\n\nDiagnostic: The model '{model_to_run}' may not exist locally. Try pulling it first with 'ollama pull {model_to_run}'."
                elif "connection refused" in error_msg.lower():
                    output += "\n\nDiagnostic: Ollama server may not be running. Please start the Ollama service."
            
            debug_info = (
                "    DEBUG Info:\n"
                f"        Command: {cmd}\n"
                f"        Optional Arguments: {optional_args if optional_args else 'None'}\n"
                f"        Exit Code: {result.returncode}\n"
                f"        Stdout: {result.stdout}\n"
                f"        Stderr: {result.stderr}\n"
            )
        except Exception as e:
            output = f"Error: {e}"
            debug_info = f"    DEBUG Info:\n        Exception: {e}\n"
        
        # Display run command output in the Chat with AI window with clear formatting
        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.insert(tk.END, "=== Command Output ===\n")
        self.chat_text.insert(tk.END, output + "\n")
        self.chat_text.insert(tk.END, "=== End of Output ===\n\n")
        self.chat_text.tag_config("debug", foreground="light grey")
        self.chat_text.insert(tk.END, debug_info, "debug")
        self.chat_text.insert(tk.END, "\n")
        self.chat_text.see(tk.END)  # Scroll to show the output
        self.chat_text.config(state=tk.DISABLED)

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
            
        try:  # Implement emergency fault tolerance
            # Engage quantum scanners for model detection
            current_running_models = get_running_ollama_models()
            current_available_models = get_ollama_models()
            
            # Initialize stabilization matrix if needed
            if not hasattr(self, 'previous_available_models'):
                self.previous_available_models = current_available_models.copy()
                self.log_message("\nSTATUS: Neural core monitoring systems initialized\n", self.status_color)
            
            # Update bridge status indicators
            if current_running_models:
                # Green indicator: Neural cores operational
                self.status_indicator.delete("all")
                self.status_indicator.create_oval(0, 0, 10, 10, fill=self.found_color, outline="")
                self.status_bar.config(text=f"SYSTEM STATUS: {len(current_running_models)} neural core(s) operational")
            else:
                # Yellow indicator: Neural cores offline
                self.status_indicator.delete("all")
                self.status_indicator.create_oval(0, 0, 10, 10, fill=self.checking_color, outline="")
                self.status_bar.config(text="ALERT: No neural cores active - ship AI functionality limited")
                
            # === Neural Core Activation Monitor ===
            for model in current_running_models:
                if model not in self.previous_running_models:
                    # New neural core activated - implement synchronization protocols
                    self.log_message(f"\nSYSTEM: Neural core '{model}' initialization sequence complete\n", self.found_color)
                    
                    # Deploy emergency notification buoys
                    try:
                        from plyer import notification
                        notification.notify(
                            title="Neural Core Online",
                            message=f"Core '{model}' is now operational",
                            app_name="Ship Mainframe",
                            timeout=5
                        )
                    except ImportError:
                        # Notification systems offline, log to backup systems
                        pass
            
            # === Neural Core Deactivation Monitor ===
            for model in self.previous_running_models:
                if model not in current_running_models:
                    # Neural core shutdown detected - implement contingency protocols
                    self.log_message(f"\nALERT: Neural core '{model}' has gone offline\n", self.cancelled_color)
                    
                    # Implement automated failover systems
                    if self.selected_running_model == model:
                        self.selected_running_model = None
                        if current_running_models:
                            # Engage backup neural pathways
                            self.selected_running_model = current_running_models[0]
                            self.log_message(f"\nSYSTEM: Emergency neural pathway established via core: {self.selected_running_model}\n", self.status_color)
                    
                    # Deploy emergency notification buoys
                    try:
                        from plyer import notification
                        notification.notify(
                            title="Neural Core Offline",
                            message=f"Core '{model}' requires maintenance",
                            app_name="Ship Mainframe",
                            timeout=5
                        )
                    except ImportError:
                        # Notification systems offline, continue with core protocols
                        pass
            
            # === Model Library Integrity Monitor ===
            # Check for newly added neural pattern templates
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
            
            # Check for removed neural pattern templates
            for model in self.previous_available_models:
                if model not in current_available_models:
                    self.log_message(f"\nALERT: Neural pattern '{model}' has been removed from template library\n", self.cancelled_color)
                    
                    # Implement automatic adaptation protocol
                    if self.selected_model == model:
                        self.selected_model = None
                        if current_available_models:
                            # Select alternative pattern
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
            
            # Update neural interface if changes detected - implement quantum entanglement
            if current_running_models != self.previous_running_models:
                populate_running_models_list(self)
                
                # Implement automatic core selection protocols
                if current_running_models and not self.selected_running_model:
                    self.selected_running_model = current_running_models[0]
                    self.log_message("\nSYSTEM: Primary neural pathway established\n", self.found_color)
            
            if current_available_models != self.previous_available_models:
                populate_models_list(self)
                
                # Implement automatic pattern selection protocols
                if current_available_models and not self.selected_model and not self.selected_running_model:
                    self.selected_model = current_available_models[0]
            
            # Update quantum memory banks for next diagnostic cycle
            self.previous_running_models = current_running_models.copy()
            self.previous_available_models = current_available_models.copy()
        
        except Exception as e:
            # Emergency fault containment protocols
            error_class = e.__class__.__name__
            self.log_message(f"\nCRITICAL: Neural monitoring subsystem failure - {error_class}\n", self.not_found_color)
            self.log_message(f"Error details: {str(e)}", self.not_found_color)
            # Attempt emergency restart of monitoring systems
            self.log_message("SYSTEM: Attempting emergency monitoring system recovery...", self.checking_color)
        
        finally:
            # Ensure continued operation regardless of error state
            # Schedule next quantum diagnostic scan
            self.master.after(self.monitor_interval, self.monitor_running_models)

    def toggle_monitoring(self):
        """
        CRITICAL SYSTEM: Neural Core Surveillance Toggle
        Controls activation state of the primary neural monitoring grid.
        Implements emergency protocols for core surveillance systems.
        """
        self.monitor_active = not self.monitor_active
        
        if self.monitor_active:
            # Monitoring systems online - full neural surveillance activated
            self.status_bar.config(text="SYSTEM STATUS: Neural monitoring grid active")
            self.status_indicator.delete("all")
            self.status_indicator.create_oval(0, 0, 10, 10, fill=self.found_color, outline="")
            self.monitor_button.config(text="Emergency Suspend")
            self.log_message("\nSYSTEM: Neural monitoring grid activated - all cores under surveillance\n", self.status_color)
            # Reinitialize quantum monitoring algorithms
            self.monitor_running_models()
        else:
            # Emergency shutdown of monitoring systems
            self.status_bar.config(text="ALERT: Neural monitoring suspended - reduced system awareness")
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
                self.status_bar.config(text=f"SYSTEM STATUS: High-resolution neural monitoring active - {new_interval}ms")
            elif power_status == "CONSERVATION":
                self.status_bar.config(text=f"SYSTEM STATUS: Power-saving neural monitoring - {new_interval}ms")
            else:
                self.status_bar.config(text=f"SYSTEM STATUS: Standard neural monitoring - {new_interval}ms")
