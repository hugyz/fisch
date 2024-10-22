import pyautogui
import time
import random
from pynput import keyboard
import threading
from pynput.keyboard import Controller

# Use an event to signal stopping the macro
stop_event = threading.Event()
shift_held = False
macro_thread = None  # Track the macro thread for instant stopping
keyboard_controller = Controller()  # Controller for low-level key presses using pynput

# Function to simulate pressing and holding the backslash key
def press_and_release_backslash():
    keyboard_controller.press('\\')
    print("Held: Backslash (\\)")
    time.sleep(0.05)  # Hold the backslash for 0.05 seconds
    keyboard_controller.release('\\')
    print("Released: Backslash (\\)")

# Function to simulate pressing and holding the 's' key
def press_and_release_s():
    keyboard_controller.press('s')
    print("Held: s")
    time.sleep(0.05)  # Hold 's' key for 0.05 seconds (faster)
    keyboard_controller.release('s')
    print("Released: s")

# Function to simulate pressing and holding the 'Enter' key
def press_and_release_enter():
    keyboard_controller.press(keyboard.Key.enter)
    print("Held: Enter")
    time.sleep(0.05)  # Hold Enter key for 0.05 seconds (faster)
    keyboard_controller.release(keyboard.Key.enter)
    print("Released: Enter")

# Function to simulate the macro
def execute_macro():
    global continue_spam
    continue_spam = True

    print("Macro started: Holding left mouse button, pressing backslash, then 's' and 'Enter' repeatedly.")
    
    # Step 1: Wait for 1 second
    time.sleep(1)

    # Step 2: Hold left mouse button down for 0.5 seconds, then release
    pyautogui.mouseDown()
    print("Held: LBM (Left Mouse Button)")
    time.sleep(0.5)
    pyautogui.mouseUp()
    print("Released: LBM")

    # Step 3: Press and release the backslash key for 0.05 seconds using pynput
    press_and_release_backslash()  # Use pynput to simulate pressing and holding backslash

    # Step 4: Repeatedly press 's' and 'Enter' until spacebar is pressed
    while continue_spam:
        press_and_release_s()  # Press and hold 's'
        press_and_release_enter()  # Press and hold 'Enter'
        time.sleep(random.uniform(0.05, 0.1))  # Reduce the delay between 's' and 'Enter' presses

    print("Macro loop stopped by spacebar.")

# Function to detect key presses
def on_press(key):
    global shift_held, continue_spam

    try:
        print(f"Key pressed: {key}")  # Log every key press

        # Detect if Shift is pressed and held
        if key == keyboard.Key.shift or key == keyboard.Key.shift_r:
            shift_held = True

        # Detect if Enter is pressed while Shift is held to start the macro
        elif key == keyboard.Key.enter and shift_held:
            print("Keybind detected: Shift + Enter")
            # Start the macro in a separate thread
            threading.Thread(target=execute_macro).start()

        # Detect spacebar to stop the macro
        elif key == keyboard.Key.space:
            print("Spacebar pressed: Stopping the macro.")
            continue_spam = False  # Signal to stop the macro

        # Detect 'q' to exit the program
        elif key.char == 'q':  # Check if 'q' is pressed
            print("Exiting program: Q detected.")
            exit()  # Exit the program completely

    except AttributeError:
        # Handle special keys like shift, ctrl, etc.
        pass

# Function to detect when keys are released
def on_release(key):
    global shift_held
    # Detect when Shift is released
    if key == keyboard.Key.shift or key == keyboard.Key.shift_r:
        shift_held = False

# Main function to start listening for key events
def main():
    print("Listening for Shift + Enter to start the macro, Spacebar to stop it, and Q to exit...")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

# Start the listener for key events
if __name__ == "__main__":
    main()
