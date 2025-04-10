import tkinter as tk
from main import start_gui
import logging
import time
import os

def test_buttons_and_features():
    """Test all buttons and features of the GUI with a dialog showing each step."""
    # Ensure the logs directory exists
    logs_dir = os.path.join(os.getcwd(), 'logs')
    os.makedirs(logs_dir, exist_ok=True)

    # Create a log file to store results in the logs directory
    log_file = os.path.join(logs_dir, "troubleshooting_results.log")
    
    # Ensure logging writes to both the log file and the console
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, mode='w', encoding='utf-8'),  # Ensure UTF-8 encoding
            logging.StreamHandler()
        ]
    )

    logging.info(f"Log file created at: {log_file}")
    logging.info("Starting troubleshooting routine...")

    # Start the GUI in a test mode
    root = tk.Tk()
    root.geometry("900x650")
    gui = start_gui()

    # Create a dialog to show progress
    progress_dialog = tk.Toplevel(root)
    progress_dialog.title("Troubleshooting Progress")
    progress_label = tk.Label(progress_dialog, text="Starting tests...", font=("Segoe UI", 10))
    progress_label.pack(padx=20, pady=20)

    # Update the progress dialog to display results
    results_text = tk.Text(progress_dialog, wrap=tk.WORD, height=20, width=50)
    results_text.pack(padx=10, pady=10)
    results_text.insert(tk.END, "Starting troubleshooting routine...\n")
    results_text.config(state=tk.DISABLED)

    def log_to_dialog(message):
        results_text.config(state=tk.NORMAL)
        results_text.insert(tk.END, message + "\n")
        results_text.config(state=tk.DISABLED)
        results_text.see(tk.END)

    try:
        # Simulate button clicks and feature interactions
        for widget in gui.master.winfo_children():
            try:
                if isinstance(widget, tk.Button):
                    log_to_dialog(f"Testing button: {widget.cget('text')}")
                    progress_label.config(text=f"Testing button: {widget.cget('text')}")
                    progress_dialog.update()
                    time.sleep(1)  # Add a 1-second delay between tests
                    widget.invoke()
                    logging.info(f"Button '{widget.cget('text')}' tested successfully.")
                # Add more widget types and interactions as needed
            except Exception as e:
                error_message = f"Error testing widget {widget}: {e}"
                log_to_dialog(error_message)
                logging.error(error_message)

        log_to_dialog("Troubleshooting routine completed successfully.")
        logging.info("Troubleshooting routine completed successfully.")
    except Exception as e:
        error_message = f"Error during troubleshooting: {e}"
        log_to_dialog(error_message)
        logging.error(error_message)
    finally:
        time.sleep(2)  # Allow the user to see the final message
        progress_dialog.destroy()
        root.destroy()

    # Notify the user where the results are saved
    print(f"Troubleshooting results saved to {log_file}")

if __name__ == "__main__":
    test_buttons_and_features()