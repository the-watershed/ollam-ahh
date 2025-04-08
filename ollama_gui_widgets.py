import tkinter as tk
from tkinter import scrolledtext, Listbox, ttk
import webbrowser

class HoverTooltip:
    """
    A floating tooltip that follows the mouse and displays a clickable link if ALT is pressed.
    """
    def __init__(self, parent):
        self.parent = parent
        self.tooltip = None
        self.link_url = None
        self.anchored = False

    def show_tooltip(self, event, text, link_url):
        self.link_url = link_url
        if self.tooltip:
            self.hide_tooltip()

        self.tooltip = tk.Toplevel(self.parent.master)
        self.tooltip.overrideredirect(True)
        self.tooltip.config(bg="#073642")  # or any desired background

        self.label = ttk.Label(self.tooltip, text=text, background="#073642", foreground="#fdf6e3")
        self.label.pack(padx=5, pady=5)

        # Bind to track motion inside the tooltip
        self.tooltip.bind("<Motion>", self._on_tooltip_motion)
        # Bind click to open link if ALT is pressed
        self.tooltip.bind("<Button-1>", self._on_tooltip_click)

        self._position_tooltip(event)

        # Track mouse movement outside tooltip to follow cursor
        self.parent.master.bind("<Motion>", self._on_mouse_move)

    def hide_tooltip(self):
        if self.tooltip:
            self.parent.master.unbind("<Motion>")
            self.tooltip.destroy()
            self.tooltip = None

    def _on_mouse_move(self, event):
        if not self.anchored:
            self._position_tooltip(event)

    def _position_tooltip(self, event):
        x = event.x_root + 10
        y = event.y_root + 10
        self.tooltip.geometry(f"+{x}+{y}")

    def _on_tooltip_motion(self, event):
        # Check if ALT is held
        if (event.state & 0x20000) != 0:
            if not self.anchored:
                self.anchored = True
            self.label.configure(foreground="blue", font=("", 9, "underline"))
        else:
            if self.anchored:
                self.anchored = False
            self.label.configure(foreground="#fdf6e3", font=("", 9, "normal"))

    def _on_tooltip_click(self, event):
        # Check if ALT is held
        if (event.state & 0x20000) != 0 and self.link_url:
            webbrowser.open(self.link_url)

def create_widgets(self, master):
    """
    Creates the widgets for the GUI.
    """
    # --- Left Frame Widgets ---
    # Available Models
    self.models_label = ttk.Label(self.left_frame, text="Available Models:", font=("TkDefaultFont", 10, "bold"), foreground="#fdf6e3")
    self.models_label.pack(side=tk.TOP, fill=tk.X, pady=5)

    self.models_listbox = Listbox(self.left_frame, bg=self.bg_color, fg=self.text_color, borderwidth=0, highlightthickness=0)
    self.models_listbox.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)
    self.models_listbox.bind("<<ListboxSelect>>", self.show_model_information)

    # Running Models
    self.running_models_label = ttk.Label(self.left_frame, text="Running Models:", font=("TkDefaultFont", 10, "bold"), foreground="#fdf6e3")
    self.running_models_label.pack(side=tk.TOP, fill=tk.X, pady=5)

    self.running_models_listbox = Listbox(self.left_frame, bg=self.bg_color, fg=self.text_color, borderwidth=0, highlightthickness=0)
    self.running_models_listbox.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)
    self.running_models_listbox.bind("<<ListboxSelect>>", self.show_running_model_information)

    # --- Right Frame Widgets ---
    # Model Information
    self.model_info_label = ttk.Label(self.right_frame, text="Model Information:", font=("TkDefaultFont", 10, "bold"), foreground="#fdf6e3")
    self.model_info_label.pack(side=tk.TOP, fill=tk.X, pady=5)

    self.model_info_text = scrolledtext.ScrolledText(
        self.right_frame, height=10, wrap=tk.WORD, bg="#000000", fg="#00FF00" # DOS-like font
    )
    self.model_info_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)
    self.model_info_text.config(state=tk.DISABLED)

    # Output Text
    self.output_label = ttk.Label(self.right_frame, text="Output:", font=("TkDefaultFont", 10, "bold"), foreground="#fdf6e3")
    self.output_label.pack(side=tk.TOP, fill=tk.X, pady=5)

    self.output_text = scrolledtext.ScrolledText(
        self.right_frame, height=10, wrap=tk.WORD, bg="black", fg="#00FF00", font=("Courier New", 10) # DOS-like font
    )
    self.output_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)
    self.output_text.config(state=tk.DISABLED)

    # Command Buttons
    self.button_frame = tk.Frame(self.right_frame, bg=self.bg_color)
    self.button_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

    button_width = 8  # Set a smaller, fixed width for the buttons

    self.tooltip = HoverTooltip(self)

    self.pull_button = ttk.Button(self.button_frame, text="Pull", width=button_width, command=self.pull_model_command)
    self.pull_button.grid(row=0, column=0, padx=5, pady=5)
    self.pull_button.bind("<Enter>", lambda e: self.tooltip.show_tooltip(e, "Pull a model.\nClick link for docs.", "https://ollama.ai/docs"))
    self.pull_button.bind("<Leave>", lambda e: self.tooltip.hide_tooltip())

    self.create_button = ttk.Button(self.button_frame, text="Create", width=button_width, command=self.create_model_command)
    self.create_button.grid(row=0, column=1, padx=5, pady=5)
    self.create_button.bind("<Enter>", lambda e: self.tooltip.show_tooltip(e, "Create a model.\nClick link for docs.", "https://ollama.ai/docs"))
    self.create_button.bind("<Leave>", lambda e: self.tooltip.hide_tooltip())

    self.serve_button = ttk.Button(self.button_frame, text="Serve", width=button_width, command=self.serve_ollama_command)
    self.serve_button.grid(row=0, column=2, padx=5, pady=5)
    self.serve_button.bind("<Enter>", lambda e: self.tooltip.show_tooltip(e, "Start Ollama server.\nClick link for docs.", "https://ollama.ai/docs"))
    self.serve_button.bind("<Leave>", lambda e: self.tooltip.hide_tooltip())

    self.run_button_2 = ttk.Button(self.button_frame, text="Run", width=button_width, command=self.run_selected_model_command)
    self.run_button_2.grid(row=1, column=0, padx=5, pady=5)
    self.run_button_2.bind("<Enter>", lambda e: self.tooltip.show_tooltip(e, "Run a model.\nClick link for docs.", "https://ollama.ai/docs"))
    self.run_button_2.bind("<Leave>", lambda e: self.tooltip.hide_tooltip())

    self.list_button = ttk.Button(self.button_frame, text="List", width=button_width, command=self.list_models_command)
    self.list_button.grid(row=1, column=1, padx=5, pady=5)
    self.list_button.bind("<Enter>", lambda e: self.tooltip.show_tooltip(e, "List available models.\nClick link for docs.", "https://ollama.ai/docs"))
    self.list_button.bind("<Leave>", lambda e: self.tooltip.hide_tooltip())

    self.show_button = ttk.Button(self.button_frame, text="Show", width=button_width, command=self.show_model_command)
    self.show_button.grid(row=1, column=2, padx=5, pady=5)
    self.show_button.bind("<Enter>", lambda e: self.tooltip.show_tooltip(e, "Show information about a model.\nClick link for docs.", "https://ollama.ai/docs"))
    self.show_button.bind("<Leave>", lambda e: self.tooltip.hide_tooltip())

    self.ps_button = ttk.Button(self.button_frame, text="PS", width=button_width, command=self.ps_models_command)
    self.ps_button.grid(row=2, column=0, padx=5, pady=5)
    self.ps_button.bind("<Enter>", lambda e: self.tooltip.show_tooltip(e, "List running models.\nClick link for docs.", "https://ollama.ai/docs"))
    self.ps_button.bind("<Leave>", lambda e: self.tooltip.hide_tooltip())

    self.stop_button_2 = ttk.Button(self.button_frame, text="Stop", width=button_width, command=self.stop_selected_model)
    self.stop_button_2.grid(row=2, column=1, padx=5, pady=5)
    self.stop_button_2.bind("<Enter>", lambda e: self.tooltip.show_tooltip(e, "Stop a running model.\nClick link for docs.", "https://ollama.ai/docs"))
    self.stop_button_2.bind("<Leave>", lambda e: self.tooltip.hide_tooltip())

    self.cp_button = ttk.Button(self.button_frame, text="CP", width=button_width, command=self.cp_model_command)
    self.cp_button.grid(row=2, column=2, padx=5, pady=5)
    self.cp_button.bind("<Enter>", lambda e: self.tooltip.show_tooltip(e, "Copy a model.\nClick link for docs.", "https://ollama.ai/docs"))
    self.cp_button.bind("<Leave>", lambda e: self.tooltip.hide_tooltip())

    self.rm_button = ttk.Button(self.button_frame, text="RM", width=button_width, command=self.rm_model_command)
    self.rm_button.grid(row=3, column=0, padx=5, pady=5)
    self.rm_button.bind("<Enter>", lambda e: self.tooltip.show_tooltip(e, "Remove a model.\nClick link for docs.", "https://ollama.ai/docs"))
    self.rm_button.bind("<Leave>", lambda e: self.tooltip.hide_tooltip())

    self.more_models_button = ttk.Button(self.button_frame, text="More Models", width=button_width, command=self.open_more_models)
    self.more_models_button.grid(row=3, column=1, padx=5, pady=5)
    self.more_models_button.bind("<Enter>", lambda e: self.tooltip.show_tooltip(e, "More models.\nClick link for docs.", "https://ollama.ai/docs"))
    self.more_models_button.bind("<Leave>", lambda e: self.tooltip.hide_tooltip())

    # Add a legend at the bottom of the right frame
    legend_frame = tk.Frame(self.right_frame, bg=self.bg_color)
    legend_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

    legend_label = ttk.Label(legend_frame, text="Legend:", font=("TkDefaultFont", 10, "bold"),
                             foreground="#fdf6e3", background=self.bg_color)
    legend_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)

    checking_label = ttk.Label(legend_frame, text="Checking", foreground=self.checking_color, background=self.bg_color)
    checking_label.grid(row=1, column=0, sticky="w", padx=5)

    found_label = ttk.Label(legend_frame, text="Found", foreground=self.found_color, background=self.bg_color)
    found_label.grid(row=1, column=1, sticky="w", padx=10)

    not_found_label = ttk.Label(legend_frame, text="Not Found", foreground=self.not_found_color, background=self.bg_color)
    not_found_label.grid(row=1, column=2, sticky="w", padx=10)

    cancelled_label = ttk.Label(legend_frame, text="Cancelled", foreground=self.cancelled_color, background=self.bg_color)
    cancelled_label.grid(row=1, column=3, sticky="w", padx=10)

    # --- New Chat Window ---
    # Create chat window in the chat_frame (newly added in ollama_gui.py)
    self.chat_label = ttk.Label(self.chat_frame, text="Chat with AI:", font=("TkDefaultFont", 10, "bold"), foreground="#fdf6e3", background=self.bg_color)
    self.chat_label.pack(side=tk.TOP, fill=tk.X, pady=5)
    
    # Modified to use black background with color-coded text
    self.chat_text = scrolledtext.ScrolledText(
        self.chat_frame, 
        wrap=tk.WORD, 
        bg="black", 
        fg="#00FF00",  # Default text color (green)
        font=("Courier New", 10)  # Monospace font for better readability
    )
    self.chat_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
    self.chat_text.config(state=tk.DISABLED)
    
    # Create tags for color-coded text
    self.chat_text.tag_config("user", foreground="#4DA6FF")  # Blue for user messages
    self.chat_text.tag_config("ai", foreground="#00FF00")    # Green for AI responses
    self.chat_text.tag_config("system", foreground="#FFD700")  # Gold for system messages
    self.chat_text.tag_config("error", foreground="#FF5555")   # Red for errors
    self.chat_text.tag_config("debug", foreground="#888888")   # Gray for debug info
    
    # Match entry color scheme with chat window
    self.chat_entry = tk.Entry(self.chat_frame, bg="#222222", fg="#FFFFFF", insertbackground="#FFFFFF")
    self.chat_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
    self.chat_button = ttk.Button(self.chat_frame, text="Send", command=self.send_chat)
    self.chat_button.pack(side=tk.TOP, padx=5, pady=5)

    # --- Model Monitoring Controls ---
    self.monitoring_frame = tk.Frame(self.chat_frame, bg=self.bg_color)
    self.monitoring_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5, padx=5)
    
    self.monitoring_label = ttk.Label(
        self.monitoring_frame, 
        text="Model Monitoring:", 
        font=("TkDefaultFont", 9, "bold"),
        foreground="#fdf6e3", 
        background=self.bg_color
    )
    self.monitoring_label.pack(side=tk.LEFT, padx=5, pady=5)
    
    self.monitor_button = ttk.Button(
        self.monitoring_frame, 
        text="Pause Monitoring", 
        width=12, 
        command=self.toggle_monitoring
    )
    self.monitor_button.pack(side=tk.LEFT, padx=5, pady=5)
    
    self.interval_button = ttk.Button(
        self.monitoring_frame, 
        text="Set Interval", 
        width=12, 
        command=self.adjust_monitoring_interval
    )
    self.interval_button.pack(side=tk.LEFT, padx=5, pady=5)
    
    # Add tooltips for monitoring buttons
    self.monitor_button.bind("<Enter>", lambda e: self.tooltip.show_tooltip(e, "Toggle continuous model monitoring on/off", ""))
    self.monitor_button.bind("<Leave>", lambda e: self.tooltip.hide_tooltip())
    
    self.interval_button.bind("<Enter>", lambda e: self.tooltip.show_tooltip(e, "Adjust how frequently models are checked (milliseconds)", ""))
    self.interval_button.bind("<Leave>", lambda e: self.tooltip.hide_tooltip())

def bind_events(self, master):
    master.bind("<Configure>", self.on_resize)
    self.models_listbox.bind("<<ListboxSelect>>", self.show_model_information)
    self.running_models_listbox.bind("<<ListboxSelect>>", self.show_running_model_information)
