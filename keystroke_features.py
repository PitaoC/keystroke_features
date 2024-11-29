import time
from pynput import keyboard
import tkinter as tk
from threading import Thread

# Initialize variables for keystroke data
key_press_times = {}
key_release_times = {}
key_durations = []  # K1: Duration (dwell time)
latency_times = []  # K2: Latency (flight time)
down_down_times = []  # K3: Down-Down Time
up_up_times = []  # K4: Up-Up Time
time_since_last_keypress = []  # K5: Time Since Last Keypress
typing_speeds = []  # K6: Typing Speed (words per minute)

total_keys = 0
last_key_release_time = None

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


def categorize_key(key):
    """Helper function to categorize a key."""
    if isinstance(key, keyboard.Key):
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


def calculate_features(key):
    """Calculate K1–K6 features dynamically."""
    global last_key_release_time

    # K1: Duration (dwell time)
    if key in key_press_times and key in key_release_times:
        duration = key_release_times[key] - key_press_times[key]
        key_durations.append(duration)

    # K2: Latency (flight time)
    if len(key_release_times) > 1:
        last_key, current_key = list(key_release_times.keys())[-2:]
        if last_key in key_release_times and current_key in key_press_times:
            latency = key_press_times[current_key] - key_release_times[last_key]
            latency_times.append(latency)

    # K3: Down-Down Time
    if len(key_press_times) > 1:
        keys = list(key_press_times.keys())[-2:]
        if all(k in key_press_times for k in keys):
            down_down_time = key_press_times[keys[1]] - key_press_times[keys[0]]
            down_down_times.append(down_down_time)

    # K4: Up-Up Time
    if len(key_release_times) > 1:
        keys = list(key_release_times.keys())[-2:]
        if all(k in key_release_times for k in keys):
            up_up_time = key_release_times[keys[1]] - key_release_times[keys[0]]
            up_up_times.append(up_up_time)

    # K5: Time Since Last Keypress
    if last_key_release_time is not None:
        time_since_last = key_press_times[key] - last_key_release_time
        time_since_last_keypress.append(time_since_last)
    last_key_release_time = key_release_times.get(key)

    # K6: Typing Speed (WPM)
    if len(key_durations) > 0:
        typing_speed = 1 / key_durations[-1] * 60 / 5  # Approximate WPM
        typing_speeds.append(typing_speed)


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
    key_release_times[key] = time.time()

    calculate_features(key)
    update_ui()


# UI Update
def update_ui():
    """Updates the GUI with the latest keystroke data."""
    total_keys_label.config(text=f"Total Keys: {total_keys}")
    key_counts_label.config(text=f"Key Counts: {key_counts}")
    k1_label.config(text=f"K1 (Durations): {key_durations[-5:]}")
    k2_label.config(text=f"K2 (Latencies): {latency_times[-5:]}")
    k3_label.config(text=f"K3 (Down-Down): {down_down_times[-5:]}")
    k4_label.config(text=f"K4 (Up-Up): {up_up_times[-5:]}")
    k5_label.config(text=f"K5 (Time Since Last Keypress): {time_since_last_keypress[-5:]}")
    k6_label.config(text=f"K6 (Typing Speeds): {typing_speeds[-5:]}")


# Listener Thread
def start_listener():
    """Starts the keyboard listener in a separate thread."""
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


# GUI Setup
def create_ui():
    """Creates the tkinter UI."""
    global total_keys_label, key_counts_label, k1_label, k2_label, k3_label, k4_label, k5_label, k6_label

    root = tk.Tk()
    root.title("Keystroke Feature Tracker")

    # Labels for displaying data
    total_keys_label = tk.Label(root, text="Total Keys: 0", font=("Arial", 12))
    total_keys_label.pack()

    key_counts_label = tk.Label(root, text="Key Counts: {}", font=("Arial", 12))
    key_counts_label.pack()

    k1_label = tk.Label(root, text="K1 (Durations): []", font=("Arial", 12))
    k1_label.pack()

    k2_label = tk.Label(root, text="K2 (Latencies): []", font=("Arial", 12))
    k2_label.pack()

    k3_label = tk.Label(root, text="K3 (Down-Down): []", font=("Arial", 12))
    k3_label.pack()

    k4_label = tk.Label(root, text="K4 (Up-Up): []", font=("Arial", 12))
    k4_label.pack()

    k5_label = tk.Label(root, text="K5 (Time Since Last Keypress): []", font=("Arial", 12))
    k5_label.pack()

    k6_label = tk.Label(root, text="K6 (Typing Speeds): []", font=("Arial", 12))
    k6_label.pack()

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
