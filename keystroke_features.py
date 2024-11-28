import time
from pynput import keyboard
import tkinter as tk
from threading import Thread

# Initialize variables for keystroke data
key_press_times = {}
key_release_times = {}
key_durations = []
timing_data = []
total_keys = 0

key_counts = {
    "delete": 0,
    "enter": 0,
    "letter": 0,
    "number": 0,
    "arrow": 0,
    "tab": 0,
    "spacebar": 0,
    "function": 0,
    "uppercase": 0,
    "punctuation": 0,
    "special": 0,
}

typing_speeds = []
pause_durations = []


def categorize_key(key):
    """Helper function to categorize a key."""
    if isinstance(key, keyboard.Key):
        # Handle special keys
        if key == keyboard.Key.backspace:
            return "delete"
        elif key == keyboard.Key.enter:
            return "enter"
        elif key == keyboard.Key.tab:
            return "tab"
        elif key == keyboard.Key.space:
            return "spacebar"
        elif key in [keyboard.Key.up, keyboard.Key.down, keyboard.Key.left, keyboard.Key.right]:
            return "arrow"
        elif key in [
            keyboard.Key.alt,
            keyboard.Key.alt_l,
            keyboard.Key.alt_r,
            keyboard.Key.ctrl,
            keyboard.Key.ctrl_l,
            keyboard.Key.ctrl_r,
            keyboard.Key.shift,
            keyboard.Key.shift_l,
            keyboard.Key.shift_r,
            keyboard.Key.cmd,
            keyboard.Key.cmd_r,
        ]:
            return "function"
        else:
            return "special"
    elif hasattr(key, "char") and key.char is not None:
        # Handle character keys
        char = key.char
        if char.isalpha():
            if char.isupper():
                return "uppercase"
            return "letter"
        elif char.isdigit():
            return "number"
        elif char in "!@#$%^&*()_+-=[]{}|;:'\",.<>?/":
            return "punctuation"
    return "special"


# Event Handlers
def on_press(key):
    """Handles key press events."""
    global total_keys
    key_press_times[key] = time.time()
    total_keys += 1

    category = categorize_key(key)
    if category in key_counts:
        key_counts[category] += 1

    update_ui()


def on_release(key):
    """Handles key release events."""
    if key in key_press_times:
        key_release_times[key] = time.time()
        duration = key_release_times[key] - key_press_times[key]
        key_durations.append(duration)

        # Typing speed calculation
        if hasattr(key, "char") and key.char is not None:
            typing_speeds.append(1 / duration * 60 / 5)

        # Pause durations
        if len(key_release_times) > 1:
            pause_durations.append(
                list(key_release_times.values())[-1] - list(key_release_times.values())[-2]
            )

    update_ui()


# UI Update
def update_ui():
    """Updates the GUI with the latest keystroke data."""
    total_keys_label.config(text=f"Total Keys: {total_keys}")
    key_counts_label.config(text=f"Key Counts: {key_counts}")
    durations_label.config(text=f"Key Durations: {key_durations[-5:]}")
    typing_speeds_label.config(text=f"Typing Speeds (WPM): {typing_speeds[-5:]}")
    pause_durations_label.config(text=f"Pause Durations: {pause_durations[-5:]}")


# Listener Thread
def start_listener():
    """Starts the keyboard listener in a separate thread."""
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


# GUI Setup
def create_ui():
    """Creates the tkinter UI."""
    global total_keys_label, key_counts_label, durations_label, typing_speeds_label, pause_durations_label

    root = tk.Tk()
    root.title("Keystroke Feature Tracker")

    # Labels for displaying data
    total_keys_label = tk.Label(root, text="Total Keys: 0", font=("Arial", 12))
    total_keys_label.pack()

    key_counts_label = tk.Label(root, text="Key Counts: {}", font=("Arial", 12))
    key_counts_label.pack()

    durations_label = tk.Label(root, text="Key Durations: []", font=("Arial", 12))
    durations_label.pack()

    typing_speeds_label = tk.Label(root, text="Typing Speeds (WPM): []", font=("Arial", 12))
    typing_speeds_label.pack()

    pause_durations_label = tk.Label(root, text="Pause Durations: []", font=("Arial", 12))
    pause_durations_label.pack()

    # Run the tkinter main loop
    root.mainloop()


# Main Execution
if __name__ == "__main__":
    print("Starting GUI and keyboard listener...")

    # Start the GUI in a separate thread
    ui_thread = Thread(target=create_ui)
    ui_thread.daemon = True
    ui_thread.start()

    # Start the keyboard listener
    try:
        start_listener()
    except KeyboardInterrupt:
        print("\nStopped listening.")
