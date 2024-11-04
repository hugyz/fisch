import time
import threading
from pynput import keyboard

# Event for stopping the spamming thread
stop_event = threading.Event()
spam_thread = None  # Reference to the spamming thread
shift_held = False  # Track if Shift is being held

# Function to spam the Enter key
def spam_enter():
    print("Spamming Enter... Press Shift + F to stop.")
    while not stop_event.is_set():
        keyboard.Controller().press(keyboard.Key.enter)
        keyboard.Controller().release(keyboard.Key.enter)

# Function to start spamming in a separate thread
def start_spamming():
    global spam_thread
    if spam_thread is None or not spam_thread.is_alive():
        print("Starting Enter spam...")
        stop_event.clear()  # Ensure the stop event is clear
        spam_thread = threading.Thread(target=spam_enter)
        spam_thread.start()

# Function to stop spamming
def stop_spamming():
    global spam_thread
    if spam_thread and spam_thread.is_alive():
        print("Stopping Enter spam...")
        stop_event.set()  # Signal the spamming thread to stop
        spam_thread.join()  # Wait for the thread to finish

# Function to handle key press events
def on_press(key):
    global shift_held
    # Detect if Shift is pressed
    if key == keyboard.Key.shift:
        shift_held = True
    # Detect Shift + Enter to start spamming
    elif key == keyboard.Key.enter and shift_held:
        start_spamming()
    # Detect Shift + F to stop spamming
    elif key == keyboard.KeyCode.from_char('f') and shift_held:
        stop_spamming()

# Function to handle key release events
def on_release(key):
    global shift_held
    # Detect when Shift is released
    if key == keyboard.Key.shift:
        shift_held = False

# Main function to start the listener
def main():
    print("Press Shift + Enter to start spamming Enter, and Shift + F to stop.")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

if __name__ == "__main__":
    main()
