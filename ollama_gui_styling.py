import tkinter.font as font
from tkinter import ttk

def configure_styles(style, bg_color, text_color, button_color, button_text_color, listbox_select_color):
    """
    Configures the styles for the GUI.
    Uses a modern blue-based Windows-like theme for better readability.
    """
    # Standard Windows-like fonts
    default_font = font.Font(family="Segoe UI", size=9)
    small_font = font.Font(family="Segoe UI", size=8)
    heading_font = font.Font(family="Segoe UI", size=10, weight="bold")
    monospace_font = font.Font(family="Consolas", size=9)

    # Base ttk theme - use 'clam' as base for better customization
    style.theme_use('clam')

    # Frame styling
    style.configure("TFrame", background=bg_color)
    
    # Label styling
    style.configure("TLabel", 
                   background=bg_color, 
                   foreground=text_color, 
                   padding=3, 
                   font=default_font)
    
    # Modern button style with better padding and hover effect
    style.configure("TButton", 
                   background=button_color, 
                   foreground=button_text_color, 
                   borderwidth=1, 
                   relief="raised", 
                   padding=(10, 5),
                   font=default_font)
                   
    style.map("TButton", 
              background=[("active", "#5294e2"), ("pressed", "#3a6ea5")],
              foreground=[("active", "#ffffff")])
    
    # Updated listbox style for better contrast
    style.configure("TListbox", 
                   background="#ffffff", 
                   foreground=text_color, 
                   borderwidth=1, 
                   highlightthickness=0,
                   selectbackground=listbox_select_color, 
                   selectforeground="#000000", 
                   font=default_font)
                   
    # Scrollbar with modern look
    style.configure("TScrollbar", 
                   background=bg_color, 
                   arrowcolor=text_color, 
                   borderwidth=0, 
                   troughcolor="#e1e1e1")
    
    style.map("TScrollbar",
              background=[("active", "#d1d1d1"), ("pressed", "#b1b1b1")])
    
    # Entry fields
    style.configure("TEntry", 
                   fieldbackground="#ffffff", 
                   foreground="#000000", 
                   borderwidth=1, 
                   font=default_font,
                   padding=5)
    
    # Text areas
    style.configure("TText", 
                   background="#ffffff", 
                   foreground=text_color, 
                   borderwidth=1, 
                   font=default_font)
    
    # Progress bar with Windows blue accent color
    style.configure("Horizontal.TProgressbar",
                  background="#0078d7",
                  troughcolor="#e1e1e1",
                  borderwidth=0)
                  
    # Tab styling for a modern look - using Windows accent blue
    style.configure("TNotebook", 
                   background=bg_color, 
                   borderwidth=0)
    
    style.configure("TNotebook.Tab", 
                   background="#e1e1e1",
                   foreground="#000000",
                   padding=(10, 4),
                   font=default_font)
                   
    # Active tab styling with Windows accent blue
    style.map("TNotebook.Tab",
             background=[("selected", "#0078d7")],
             foreground=[("selected", "#ffffff")])
             
    # Theme switcher style
    style.configure("Switch.TCheckbutton", 
                   background=bg_color,
                   foreground=text_color,
                   font=default_font)
                   
    # Resource monitor styles
    style.configure("Resource.TLabel", 
                   background="#f0f4f8", 
                   foreground="#0078d7", 
                   font=small_font)
                   
    # Search field style
    style.configure("Search.TEntry",
                   fieldbackground="#ffffff",
                   foreground="#000000",
                   borderwidth=1,
                   font=default_font)
                   
    # Heading style
    style.configure("Heading.TLabel",
                   background=bg_color,
                   foreground="#0d47a1",
                   font=heading_font)
                   
    # Status bar style
    style.configure("Status.TFrame",
                   background="#f0f4f8",
                   relief="sunken")
                   
    # Info text style
    style.configure("Info.TLabel",
                   background=bg_color,
                   foreground="#1565c0",
                   font=small_font)

    # Add compact styling for better space usage
    style.configure("Compact.TButton",
                   padding=(5, 2),
                   font=small_font)

    # Windows 11 style accent button
    style.configure("Accent.TButton",
                   background="#0078d7",
                   foreground="#ffffff",
                   padding=(10, 5),
                   font=default_font)
    style.map("Accent.TButton",
              background=[("active", "#1e88e5"), ("pressed", "#0d47a1")])

    # Modern panel style for sections with subtle shadow effect
    style.configure("Panel.TFrame", 
                   background="#ffffff",
                   relief="flat",
                   borderwidth=1)
                   
    # Updated console style for better readability
    style.configure("Console.TText",
                   background="#f5f5f5",
                   foreground="#333333",
                   font=monospace_font)
                   
    # Windows standard color for separators
    style.configure("TSeparator",
                    background="#e0e0e0")
                    
    # Enhanced command button style
    style.configure("Command.TButton", 
                   background="#2196f3", 
                   foreground="#ffffff", 
                   padding=(8, 4),
                   font=default_font)
    style.map("Command.TButton", 
              background=[("active", "#42a5f5"), ("pressed", "#1976d2")])
              
    # Secondary button style for less important actions
    style.configure("Secondary.TButton", 
                   background="#e0e0e0", 
                   foreground="#333333", 
                   padding=(8, 4),
                   font=default_font)
    style.map("Secondary.TButton", 
              background=[("active", "#f0f0f0"), ("pressed", "#d0d0d0")])
              
    # Group header style
    style.configure("GroupHeader.TLabel",
                    background="#e1f5fe",
                    foreground="#01579b", 
                    font=font.Font(family="Segoe UI", size=9, weight="bold"),
                    padding=(5, 2))
    
    # NEW STYLES FOR BETTER VISUAL HIERARCHY AND EXPERIENCE
    
    # Card style for information panels with subtle border
    style.configure("Card.TFrame",
                   background="#ffffff",
                   relief="solid",
                   borderwidth=1,
                   bordercolor="#e0e0e0")
    
    # Section title style
    style.configure("SectionTitle.TLabel",
                   background=bg_color,
                   foreground="#1565c0",
                   font=font.Font(family="Segoe UI", size=10, weight="bold"),
                   padding=(0, 5, 0, 3))
    
    # Success message style
    style.configure("Success.TLabel",
                   background="#e8f5e9",
                   foreground="#2e7d32",
                   font=default_font,
                   padding=5)
    
    # Error message style
    style.configure("Error.TLabel",
                   background="#ffebee",
                   foreground="#c62828",
                   font=default_font,
                   padding=5)
    
    # Warning message style
    style.configure("Warning.TLabel",
                   background="#fff8e1",
                   foreground="#f57f17",
                   font=default_font,
                   padding=5)
    
    # Info message style
    style.configure("Info.TLabel",
                   background="#e3f2fd",
                   foreground="#1565c0",
                   font=default_font,
                   padding=5)
    
    # Chip style for tags or model names
    style.configure("Chip.TLabel",
                   background="#e3f2fd",
                   foreground="#1565c0",
                   font=small_font,
                   padding=(5, 2),
                   relief="solid",
                   borderwidth=1,
                   bordercolor="#bbdefb")
    
    # Action link style
    style.configure("Link.TLabel",
                   background=bg_color,
                   foreground="#1976d2",
                   font=default_font,
                   cursor="hand2")
    
    # Header frame style
    style.configure("Header.TFrame",
                   background="#e3f2fd",
                   padding=10)
    
    # Footer frame style
    style.configure("Footer.TFrame",
                   background="#f5f5f5",
                   padding=5)
    
    # Enhanced status indicator style
    style.configure("StatusIndicator.TLabel",
                   padding=(2, 0),
                   font=small_font)

def get_dark_mode_colors():
    """
    Returns a dictionary of dark mode colors.
    """
    return {
        "bg_color": "#2d2d2d",            # Dark background
        "text_color": "#e0e0e0",          # Light text for dark background
        "checking_color": "#7986cb",      # Indigo for checking status (darker)
        "found_color": "#4caf50",         # Green for found items
        "not_found_color": "#f44336",     # Red for not found
        "cancelled_color": "#ff9800",     # Orange for cancelled operations
        "button_color": "#3f51b5",        # Darker blue for buttons
        "button_text_color": "#ffffff",   # White text on buttons
        "listbox_select_color": "#3f51b5" # Dark blue selection
    }

def get_light_mode_colors():
    """
    Returns a dictionary of light mode colors.
    """
    return {
        "bg_color": "#f0f4f8",         # Light blue-gray background
        "text_color": "#333333",       # Dark text for readability
        "checking_color": "#5b6abf",   # Indigo for checking status
        "found_color": "#2e7d32",      # Green for found items
        "not_found_color": "#c62828",  # Red for not found
        "cancelled_color": "#d84315",  # Orange for cancelled operations
        "button_color": "#1976d2",     # Microsoft blue
        "button_text_color": "#ffffff", # White text on buttons
        "listbox_select_color": "#bbdefb" # Light blue selection
    }
