import tkinter as tk
from tkinter import scrolledtext, Listbox, ttk, filedialog, simpledialog
import webbrowser
import os
import json
from ollama_system_monitor import SystemMonitor, ModelMetricsMonitor

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

        self.label = ttk.Label(self.tooltip, text=text, background="#073642", foreground="#fdf6e3", font=("TkDefaultFont", 7))
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
            self.label.configure(foreground="blue", font=("", 7, "underline"))
        else:
            if self.anchored:
                self.anchored = False
            self.label.configure(foreground="#fdf6e3", font=("", 7, "normal"))

    def _on_tooltip_click(self, event):
        # Check if ALT is held
        if (event.state & 0x20000) != 0 and self.link_url:
            webbrowser.open(self.link_url)

def create_left_frame(self):
    """Creates the left frame with model selection and information displays"""
    # Reduce size by 25%
    button_width = 15  # Reduced from 20
    button_height = 1  # Reduced from 1.5 or 2

    self.left_frame = ttk.Frame(self.master, style="Panel.TFrame")
    self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=10, pady=10)
    
    # Create a notebook/tabbed interface for different model operations
    model_notebook = ttk.Notebook(self.left_frame)
    model_notebook.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
    
    # Models tab
    models_tab = ttk.Frame(model_notebook)
    model_notebook.add(models_tab, text="Models")
    
    # Add search bar at the top
    search_frame = ttk.Frame(models_tab)
    search_frame.pack(fill=tk.X, padx=0, pady=5)
    
    self.search_entry = ttk.Entry(search_frame, style="Search.TEntry", font=("Segoe UI", 8))
    self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=0, pady=0)
    self.search_entry.bind("<Return>", lambda e: self.search_models())
    
    search_btn = ttk.Button(search_frame, text="🔍", width=3, style="Compact.TButton", command=self.search_models)
    search_btn.pack(side=tk.RIGHT, padx=0, pady=0)
    
    # Create a frame for the category filter buttons
    category_frame = ttk.Frame(models_tab)
    category_frame.pack(fill=tk.X, padx=0, pady=3)
    
    # Add category filter buttons - using compact style
    categories = ["All", "Favorites", "Large", "Small", "Chat", "Code"]
    
    for category in categories:
        btn = ttk.Button(
            category_frame, 
            text=category, 
            width=5, 
            style="Compact.TButton",
            command=lambda cat=category: self.filter_models_by_category(cat)
        )
        btn.pack(side=tk.LEFT, padx=2, pady=0)
    
    # Models listbox with scrollbar
    self.models_listbox = tk.Listbox(
        models_tab,
        bg="#ffffff",
        fg="#333333",
        selectbackground=self.listbox_select_color,
        selectforeground="#ffffff",
        relief=tk.FLAT,
        highlightthickness=0,
        bd=1,
        font=("Segoe UI", 8),
        height=10
    )
    self.models_listbox.pack(fill=tk.BOTH, expand=True, padx=0, pady=5)
    
    # Create a right-click context menu for models
    self.models_context_menu = tk.Menu(
        self.models_listbox,
        tearoff=0,
        bg="#ffffff",
        fg="#333333",
        activebackground=self.listbox_select_color,
        activeforeground="#ffffff",
        font=("Segoe UI", 8)
    )
    self.models_context_menu.add_command(label="Copy Model Name", command=self.copy_model_name)
    self.models_context_menu.add_command(label="Tag Model", command=self.tag_selected_model)
    self.models_context_menu.add_command(label="Toggle Favorite", command=self.toggle_favorite)
    self.models_context_menu.add_separator()
    self.models_context_menu.add_command(label="Export Configuration", command=self.export_model_config)
    self.models_context_menu.add_separator()
    self.models_context_menu.add_command(label="Create Model", command=self.open_modelfile_builder)
    
    # Bind the context menu to right-click
    self.models_listbox.bind("<Button-3>", self.show_models_context_menu)
    
    # Scrollbar for models listbox
    models_scrollbar = ttk.Scrollbar(models_tab, orient=tk.VERTICAL, command=self.models_listbox.yview)
    models_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    self.models_listbox.config(yscrollcommand=models_scrollbar.set)
    
    # Bind selection event
    self.models_listbox.bind('<<ListboxSelect>>', lambda event: self.show_model_information(event))
    
    # Additional action buttons
    model_actions_frame = ttk.Frame(models_tab)
    model_actions_frame.pack(fill=tk.X, padx=0, pady=5)
    
    refresh_btn = ttk.Button(model_actions_frame, text="Refresh", width=button_width//2, style="Secondary.TButton", command=self.refresh_models_list)
    refresh_btn.pack(side=tk.LEFT, padx=2, pady=0)
    
    batch_btn = ttk.Button(model_actions_frame, text="Batch...", width=button_width//2, style="Secondary.TButton", command=self.show_batch_operations)
    batch_btn.pack(side=tk.LEFT, padx=2, pady=0)
    
    # Running Models Tab
    running_tab = ttk.Frame(model_notebook)
    model_notebook.add(running_tab, text="Running")
    
    # Running models listbox
    self.running_models_listbox = tk.Listbox(
        running_tab,
        bg="#ffffff",
        fg="#333333",
        selectbackground=self.listbox_select_color,
        selectforeground="#ffffff",
        relief=tk.FLAT,
        highlightthickness=0,
        bd=1,
        font=("Segoe UI", 8),
        height=10
    )
    self.running_models_listbox.pack(fill=tk.BOTH, expand=True, padx=0, pady=5)
    
    # Scrollbar for running models listbox
    running_scrollbar = ttk.Scrollbar(running_tab, orient=tk.VERTICAL, command=self.running_models_listbox.yview)
    running_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    self.running_models_listbox.config(yscrollcommand=running_scrollbar.set)
    
    # Bind selection event
    self.running_models_listbox.bind('<<ListboxSelect>>', lambda event: self.show_running_model_information(event))
    
    # Parameter Presets Tab
    params_tab = ttk.Frame(model_notebook)
    model_notebook.add(params_tab, text="Params")
    
    # Parameter presets manager
    presets_btn = ttk.Button(params_tab, text="Manage Presets", style="Secondary.TButton", command=self.manage_parameter_presets)
    presets_btn.pack(fill=tk.X, padx=5, pady=5)
    
    # Default parameters
    params_frame = ttk.LabelFrame(params_tab, text="Parameters", padding=5)
    params_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Create parameter input fields - using smaller text and compact layout
    param_labels = ["Temp:", "Top P:", "Top K:"]
    param_defaults = ["0.7", "0.9", "40"]
    
    self.param_entries = {}
    
    for i, (label, default) in enumerate(zip(param_labels, param_defaults)):
        row_frame = ttk.Frame(params_frame)
        row_frame.pack(fill=tk.X, padx=2, pady=2)
        
        lbl = ttk.Label(row_frame, text=label, font=("Segoe UI", 8))
        lbl.pack(side=tk.LEFT, padx=2)
        
        entry = ttk.Entry(row_frame, width=6, font=("Segoe UI", 8))
        entry.insert(0, default)
        entry.pack(side=tk.RIGHT, padx=2)
        
        self.param_entries[label.lower().rstrip(':')] = entry
    
    # History tab
    history_tab = ttk.Frame(model_notebook)
    model_notebook.add(history_tab, text="History")
    
    # Chat history listbox
    self.history_listbox = tk.Listbox(
        history_tab,
        bg="#ffffff",
        fg="#333333",
        selectbackground=self.listbox_select_color,
        selectforeground="#ffffff",
        relief=tk.FLAT,
        highlightthickness=0,
        bd=1,
        font=("Segoe UI", 8),
        height=10
    )
    self.history_listbox.pack(fill=tk.BOTH, expand=True, padx=0, pady=5)
    
    # Scrollbar for history listbox
    history_scrollbar = ttk.Scrollbar(history_tab, orient=tk.VERTICAL, command=self.history_listbox.yview)
    history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    self.history_listbox.config(yscrollcommand=history_scrollbar.set)
    
    # Bind double-click to load history
    self.history_listbox.bind('<Double-1>', self.load_chat_history)
    
    # History action buttons
    history_actions_frame = ttk.Frame(history_tab)
    history_actions_frame.pack(fill=tk.X, padx=0, pady=5)
    
    load_history_btn = ttk.Button(history_actions_frame, text="Load", width=button_width//3, style="Secondary.TButton", command=self.load_chat_history)
    load_history_btn.pack(side=tk.LEFT, padx=2, pady=0)
    
    save_history_btn = ttk.Button(history_actions_frame, text="Save", width=button_width//3, style="Secondary.TButton", command=self.save_chat_history)
    save_history_btn.pack(side=tk.LEFT, padx=2, pady=0)
    
    delete_history_btn = ttk.Button(history_actions_frame, text="Delete", width=button_width//3, style="Secondary.TButton", command=self.delete_chat_history)
    delete_history_btn.pack(side=tk.LEFT, padx=2, pady=0)
    
    # System Monitor Section
    self.system_monitor_frame = ttk.Frame(self.left_frame, style="Panel.TFrame")
    self.system_monitor_frame.pack(fill=tk.X, padx=0, pady=5)
    
    # Model Metrics Section
    self.model_metrics_frame = ttk.Frame(self.left_frame, style="Panel.TFrame")
    self.model_metrics_frame.pack(fill=tk.X, padx=0, pady=5)
    
    # Model information display
    model_info_label = ttk.Label(self.left_frame, text="Model Information:", style="GroupHeader.TLabel")
    model_info_label.pack(anchor=tk.W, padx=0, pady=(5, 0))
    
    self.model_info_text = tk.Text(
        self.left_frame,
        height=5,
        bg="#f5f5f5",
        fg="#333333",
        relief=tk.FLAT,
        highlightthickness=0,
        bd=1,
        font=("Consolas", 8),
        wrap=tk.WORD
    )
    self.model_info_text.pack(fill=tk.BOTH, expand=False, padx=0, pady=5)
    self.model_info_text.config(state=tk.DISABLED)
    
    # Buttons for model operations - reduced size
    button_frame = ttk.Frame(self.left_frame)
    button_frame.pack(fill=tk.X, padx=0, pady=5)
    
    # Model operation buttons - arranged in a grid layout for better organization
    self.model_actions = {
        "Pull": self.pull_model_command,
        "Run": self.run_selected_model_command,
        "Stop": self.stop_current_operation,
        "Remove": self.rm_model_command
    }
    
    # First row of buttons
    top_button_frame = ttk.Frame(button_frame)
    top_button_frame.pack(fill=tk.X, padx=0, pady=2)
    
    # Convert dict_items to list before slicing
    model_actions_list = list(self.model_actions.items())
    
    for idx, (label, command) in enumerate(model_actions_list[:2]):
        style = "Accent.TButton" if label == "Run" else "Secondary.TButton"
        btn = ttk.Button(top_button_frame, text=label, width=button_width, style=style, command=command)
        btn.pack(side=tk.LEFT, padx=2, pady=0, expand=True, fill=tk.X)
        
    # Second row of buttons
    bottom_button_frame = ttk.Frame(button_frame)
    bottom_button_frame.pack(fill=tk.X, padx=0, pady=2)
    
    for idx, (label, command) in enumerate(model_actions_list[2:]):
        style = "Secondary.TButton"
        if label == "Stop":
            style = "Command.TButton" 
        btn = ttk.Button(bottom_button_frame, text=label, width=button_width, style=style, command=command)
        btn.pack(side=tk.LEFT, padx=2, pady=0, expand=True, fill=tk.X)
        
    # Theme toggle switch
    theme_frame = ttk.Frame(self.left_frame)
    theme_frame.pack(fill=tk.X, padx=0, pady=5)
    
    self.theme_var = tk.BooleanVar(value=not self.is_dark_mode)  # False = dark, True = light
    
    theme_switch = ttk.Checkbutton(
        theme_frame, 
        text="Light Theme", 
        style="Switch.TCheckbutton",
        variable=self.theme_var,
        command=self.toggle_theme
    )
    theme_switch.pack(side=tk.RIGHT, padx=0)
    
    # Help button (for keyboard shortcuts)
    help_btn = ttk.Button(theme_frame, text="?", width=3, style="Secondary.TButton", command=self.show_keyboard_shortcuts)
    help_btn.pack(side=tk.LEFT, padx=0)

def create_right_frame(self):
    """Creates the right frame with output display and command input"""
    # Using a more modern panel style
    self.right_frame = ttk.Frame(self.master, style="Panel.TFrame")
    self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Ensure the tab features' height fills the entire window
    self.right_frame.pack_propagate(False)
    
    # Initialize the tabs_notebook attribute
    self.tabs_notebook = ttk.Notebook(self.right_frame)
    self.tabs_notebook.pack(fill=tk.BOTH, expand=True)
    
    # Create a notebook for multiple tabs
    self.tabs_notebook = ttk.Notebook(self.right_frame)
    self.tabs_notebook.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
    
    # Initialize the tab control for the right frame
    self.tab_control = ttk.Notebook(self.right_frame)
    self.tab_control.pack(fill=tk.BOTH, expand=True)
    
    # Command Output Tab
    cmd_tab = ttk.Frame(self.tabs_notebook)
    self.tabs_notebook.add(cmd_tab, text="Command Output")
    
    # Remove the input label to eliminate any additional square above the Command Output tab
    # input_label = ttk.Label(cmd_tab, text="Command:", style="Info.TLabel")
    # input_label.pack(anchor=tk.W, padx=0, pady=0)
    
    # Output text widget
    self.output_text = tk.Text(
        cmd_tab,
        height=20,
        bg="#f5f5f5",
        fg="#333333",
        insertbackground="#333333",
        relief=tk.FLAT,
        highlightthickness=0,
        bd=1,
        font=("Consolas", 9),
        wrap=tk.WORD
    )
    self.output_text.pack(fill=tk.BOTH, expand=True, padx=0, pady=5)
    
    # Configure tags for different message types
    self.output_text.tag_configure("checking", foreground=self.checking_color)
    self.output_text.tag_configure("found", foreground=self.found_color)
    self.output_text.tag_configure("not_found", foreground=self.not_found_color)
    self.output_text.tag_configure("cancelled", foreground=self.cancelled_color)
    
    # Command input
    self.command_entry = ttk.Entry(cmd_tab, font=("Segoe UI", 9))
    self.command_entry.pack(fill=tk.X, padx=0, pady=5)
    self.command_entry.bind("<Return>", self.run_command)
    
    # Command buttons - use modern button styles and fix duplicate buttons
    cmd_button_frame = ttk.Frame(cmd_tab)
    cmd_button_frame.pack(fill=tk.X, padx=0, pady=5)
    
    # Initialize the clear button
    self.clear_button = ttk.Button(cmd_button_frame, text="Clear", width=10, style="Secondary.TButton", command=lambda e=None: self.output_text.delete(1.0, tk.END))
    self.clear_button.pack(side=tk.LEFT, padx=5, pady=5)
    
    # Initialize the question mark button
    self.question_mark_button = ttk.Button(cmd_button_frame, text="?", width=3, style="Secondary.TButton", command=self.show_keyboard_shortcuts)
    self.question_mark_button.pack(side=tk.LEFT, padx=5, pady=5)

    commands = [
        ("Stop", "Command.TButton", self.stop_current_operation)
    ]
    
    for text, style, command in commands:
        btn = ttk.Button(cmd_button_frame, text=text, width=10, style=style, command=command)
        btn.pack(side=tk.LEFT, padx=2, pady=0)
    
    # Ensure tab features fill the window area
    self.tab_control.pack(fill=tk.BOTH, expand=True)
    
    # Chat Tab
    self.chat_frame = ttk.Frame(self.tabs_notebook)
    self.tabs_notebook.add(self.chat_frame, text="Chat")
    
    # Chat display
    chat_output_frame = ttk.Frame(self.chat_frame)
    chat_output_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=5)
    
    # Chat text widget
    self.chat_text = tk.Text(
        chat_output_frame,
        height=20,
        bg="#f5f5f5",
        fg="#333333",
        insertbackground="#333333",
        relief=tk.FLAT,
        highlightthickness=0,
        bd=1,
        font=("Segoe UI", 9),
        wrap=tk.WORD
    )
    self.chat_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=0, pady=0)
    self.chat_text.config(state=tk.DISABLED)
    
    # Chat scrollbar
    chat_scrollbar = ttk.Scrollbar(chat_output_frame, orient=tk.VERTICAL, command=self.chat_text.yview)
    chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    self.chat_text.config(yscrollcommand=chat_scrollbar.set)
    
    # Chat context menu
    self.chat_context_menu = tk.Menu(
        self.chat_text,
        tearoff=0,
        bg="#ffffff",
        fg="#333333",
        activebackground=self.listbox_select_color,
        activeforeground="#ffffff",
        font=("Segoe UI", 8)
    )
    self.chat_context_menu.add_command(label="Copy Selection", command=self.copy_chat_selection)
    self.chat_context_menu.add_command(label="Copy All", command=self.copy_entire_chat)
    self.chat_context_menu.add_separator()
    self.chat_context_menu.add_command(label="Clear", command=self.clear_chat)
    self.chat_context_menu.add_command(label="Search...", command=self.search_in_chat)
    
    # Bind the context menu to right-click
    self.chat_text.bind("<Button-3>", self.show_chat_context_menu)
    
    # Configure tags for chat styling
    self.chat_text.tag_configure("user", foreground="#1976d2")  # User messages in blue
    self.chat_text.tag_configure("assistant", foreground="#388e3c")  # Assistant messages in green
    self.chat_text.tag_configure("system", foreground="#e65100")  # System messages in orange
    self.chat_text.tag_configure("error", foreground="#d32f2f")  # Error messages in red
    
    # System prompt and model selection
    system_frame = ttk.Frame(self.chat_frame)
    system_frame.pack(fill=tk.X, padx=0, pady=5)
    
    system_label = ttk.Label(system_frame, text="System:", width=6, style="Info.TLabel")
    system_label.pack(side=tk.LEFT, padx=0, pady=0)
    
    self.system_prompt = ttk.Entry(system_frame, font=("Segoe UI", 9))
    self.system_prompt.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, pady=0)
    self.system_prompt.insert(0, "You are a helpful assistant.")
    
    model_label = ttk.Label(system_frame, text="Model:", style="Info.TLabel")
    model_label.pack(side=tk.LEFT, padx=(5, 0), pady=0)
    
    self.chat_model_var = tk.StringVar()
    self.chat_model_dropdown = ttk.Combobox(system_frame, textvariable=self.chat_model_var, width=15, font=("Segoe UI", 9))
    self.chat_model_dropdown.pack(side=tk.LEFT, padx=2, pady=0)
    
    # Chat input area
    chat_input_frame = ttk.Frame(self.chat_frame)
    chat_input_frame.pack(fill=tk.X, padx=0, pady=5)
    
    self.chat_entry = tk.Text(
        chat_input_frame,
        height=3,
        bg="#ffffff",
        fg="#333333",
        insertbackground="#333333",
        relief=tk.FLAT,
        highlightthickness=0,
        bd=1,
        font=("Segoe UI", 9),
        wrap=tk.WORD
    )
    self.chat_entry.pack(fill=tk.X, padx=0, pady=5)
    self.chat_entry.bind("<Control-Return>", self.send_chat)
    
    # Chat action buttons - fixed duplication and used consistent styling
    chat_button_frame = ttk.Frame(self.chat_frame)
    chat_button_frame.pack(fill=tk.X, padx=0, pady=0)
    
    chat_actions = [
        ("Send", "Accent.TButton", self.send_chat),
        ("New Chat", "Secondary.TButton", self.start_new_chat),
        ("Stop", "Command.TButton", self.stop_current_operation)  # Fixed to use stop_current_operation
    ]
    
    for text, style, command in chat_actions:
        btn = ttk.Button(chat_button_frame, text=text, width=10, style=style, command=command)
        btn.pack(side=tk.LEFT, padx=2, pady=0)

def create_status_bar(self):
    """Creates the status bar at the bottom of the window"""
    self.status_frame = ttk.Frame(self.master, style="Status.TFrame")
    self.status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=0, pady=0)
    
    # Status message on left
    self.status_message = ttk.Label(
        self.status_frame, 
        text="Ready", 
        style="Info.TLabel"
    )
    self.status_message.pack(side=tk.LEFT, padx=5, pady=2)
    
    # Version info on right
    version_label = ttk.Label(
        self.status_frame, 
        text="Ollama Finder v1.2", 
        font=("Segoe UI", 7)
    )
    version_label.pack(side=tk.RIGHT, padx=5, pady=2)

def create_widgets(self, master):
    """
    Creates all widgets for the OllamaFinderGUI.
    This function calls the other widget creation functions.
    
    Args:
        self: The OllamaFinderGUI instance
        master: The master tkinter window
    """
    create_left_frame(self)
    create_right_frame(self)
    create_status_bar(self)
    
    # Create tooltip handler
    self.tooltip = HoverTooltip(self)
    
    # Create system monitor - passing self as the parent application instance
    self.system_monitor = SystemMonitor(self)
    
    # Model metrics (initialized but updated later)
    self.model_metrics = ModelMetricsMonitor(self)