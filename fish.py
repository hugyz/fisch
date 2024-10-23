import pyautogui
import time
import random
from pynput import keyboard
import threading
from pynput.keyboard import Controller
import os

# Use an event to signal stopping the macro
stop_event = threading.Event()
shift_held = False
macro_thread = None  # Track the macro thread for instant stopping
keyboard_controller = Controller()  # Controller for low-level key presses using pynput
macro_running = False  # Track if the macro is currently running
training_running = False  # Track if the reinforcement learning is running

# Get the screen size dynamically
screen_width, screen_height = pyautogui.size()

# Define the possible bar regions based on screen size (adjust for your bar locations)
bar_region_1 = (int(screen_width * 0.30), int(screen_height * 0.80))  # Top-left corner of first location
bar_region_2 = (int(screen_width * 0.55), int(screen_height * 0.80))  # Top-left corner of second location

# RGB color range for detecting the white bar
white_color = (255, 255, 255)  # White color for when the gray fish line is inside the bar

# Function to check if a color is close to white (to account for variations)
def is_white_color(color, tolerance=30):
    return all(abs(c - 255) <= tolerance for c in color)

# Function to detect the appearance of the white bar by checking both possible locations
def detect_bar_appearance():
    # Check a pixel in the first possible bar location
    color_1 = pyautogui.pixel(bar_region_1[0], bar_region_1[1])
    
    # Check a pixel in the second possible bar location
    color_2 = pyautogui.pixel(bar_region_2[0], bar_region_2[1])
    
    # Log detected colors for troubleshooting
    print(f"Detected color in region 1: {color_1}")
    print(f"Detected color in region 2: {color_2}")

    # Check if either region has the white color (indicating the bar is visible)
    if is_white_color(color_1) or is_white_color(color_2):
        return True  # The white bar is visible
    return False  # The white bar is not visible in either location

# Function to simulate clicking the screen
def click_screen():
    pyautogui.mouseDown()
    print("held: LBM")
    time.sleep(0.5)
    pyautogui.mouseUp()
    print("released: LBM")
    print("Clicked on the screen.")

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
    time.sleep(0.01)  # Hold 's' key for 0.05 seconds
    keyboard_controller.release('s')
    print("Released: s")

# Function to simulate pressing and holding the 'Enter' key
def press_and_release_enter():
    keyboard_controller.press(keyboard.Key.enter)
    print("Held: Enter")
    time.sleep(0.01)  # Hold Enter key for 0.05 seconds
    keyboard_controller.release(keyboard.Key.enter)
    print("Released: Enter")

# Function to simulate the macro
def execute_macro():
    global continue_spam, macro_running
    continue_spam = True
    macro_running = True  # Macro is now running

    # Step 1: Click the screen
    click_screen()

    # Step 2: Press the backslash key
    press_and_release_backslash()

    print("Macro started: Clicking, pressing backslash, then pressing 's' and 'Enter' repeatedly.")
    
    # Step 3: Repeatedly press 's' and 'Enter' until the white bar is detected or F/Q is pressed
    while continue_spam:
        press_and_release_s()  # Press and hold 's'
        press_and_release_enter()  # Press and hold 'Enter'

        # Check if the white bar has appeared
        if detect_bar_appearance():
            print("White bar detected! Stopping macro and starting reinforcement learning.")
            continue_spam = False  # Stop the macro
            start_rl_agent()  # Call the RL agent

        time.sleep(random.uniform(0.05, 0.1))  # Reduce the delay between 's' and 'Enter' presses

    print("Macro loop stopped by white bar detection or F key.")
    macro_running = False  # Mark macro as stopped

# Function to detect key presses
def on_press(key):
    global shift_held, continue_spam, macro_thread, macro_running, training_running

    try:
        print(f"Key pressed: {key}")  # Log every key press

        # Detect if Shift is pressed and held
        if key == keyboard.Key.shift or key == keyboard.Key.shift_r:
            shift_held = True

        # Detect if Enter is pressed while Shift is held to start the macro
        elif key == keyboard.Key.enter and shift_held:
            print("Keybind detected: Shift + Enter")
            
            # Check if the macro is already running
            if macro_thread is None or not macro_thread.is_alive():
                # Start the macro in a separate thread
                macro_thread = threading.Thread(target=execute_macro)
                macro_thread.start()
            else:
                print("Macro is already running.")

        # Detect F to stop the macro and training manually
        elif key.char == 'f':
            if macro_running or training_running:  # Stop both the macro and training if running
                print("F key pressed: Stopping the macro and training.")
                continue_spam = False  # Signal to stop the macro
                stop_event.set()  # Signal to stop the training

                # Wait for the macro thread to finish
                if macro_thread is not None:
                    macro_thread.join()

                print("Macro and training stopped. Returning to default state.")
                return_to_default_state()
            else:
                print("Macro and training are not running. Press Shift + Enter to start.")

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

# Function to start the RL agent (catch.py)
def start_rl_agent():
    global training_running
    print("Starting the RL agent (catch.py)...")
    training_running = True    
    os.system("python catch.py")  # This will run the catch.py script
    training_running = False

# Function to return to default state (listening for Shift + Enter)
def return_to_default_state():
    print("Listening for Shift + Enter to start the macro, F to stop it, and Q to exit...")

# Main function to start listening for key events
def main():
    print("Listening for Shift + Enter to start the macro, F to stop it, and Q to exit...")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

# Start the listener for key events
if __name__ == "__main__":
    main()
