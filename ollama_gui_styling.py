import tkinter.font as font
from tkinter import ttk

def configure_styles(style, bg_color, text_color, button_color, button_text_color, listbox_select_color):
    """
    Configures the styles for the GUI.
    """
    default_font = font.Font(family="Segoe UI", size=9)

    style.configure("TLabel", background=bg_color, foreground=text_color, padding=4, font=default_font)
    style.configure("TButton", background=button_color, foreground=button_text_color, borderwidth=0, relief="raised", padding=(10, 5), font=default_font)
    style.map("TButton", background=[("active", "#657b83")])  # Darker on hover
    style.configure("TListbox", background=bg_color, foreground=text_color, borderwidth=0, highlightthickness=0, selectbackground=listbox_select_color, selectforeground=text_color, font=default_font)
    style.configure("TScrollbar", background=bg_color, borderwidth=0)
    style.configure("TEntry", fieldbackground=bg_color, foreground=text_color, borderwidth=0, font=default_font)
    style.configure("TText", background=bg_color, foreground=text_color, borderwidth=0, font=default_font)
