import pyautogui
import time
import random
from pynput import keyboard
import threading
import cv2
import numpy as np
from PIL import ImageGrab
from pynput.keyboard import Controller

# Use an event to signal stopping the macro
stop_event = threading.Event()
shift_held = False
macro_thread = None  # Track the macro thread for instant stopping
keyboard_controller = Controller()  # Controller for low-level key presses using pynput

# Define the region of the bars on screen (adjust based on your game screen)
state_bar_region = (700, 800, 1200, 850)  # Coordinates to capture the big state bar
progress_bar_region = (700, 900, 1200, 920)  # Coordinates for the small progress bar
gray_line_region = (750, 820, 1100, 840)  # Coordinates of where the gray line moves

# Capture the game bar area from a screenshot
def capture_state_bar_area():
    screenshot = ImageGrab.grab(bbox=state_bar_region)  # Capture the big state bar
    screenshot = np.array(screenshot)
    return cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

# Capture the gray line area
def capture_gray_line_area():
    screenshot = ImageGrab.grab(bbox=gray_line_region)  # Capture the gray line area
    screenshot = np.array(screenshot)
    return cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

# Capture the small bottom progress bar
def capture_progress_bar_area():
    screenshot = ImageGrab.grab(bbox=progress_bar_region)  # Capture the progress bar
    screenshot = np.array(screenshot)
    return cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

# Detect if the progress bar is fully white
def is_progress_bar_white():
    progress_bar_image = capture_progress_bar_area()
    gray_small_bar = cv2.cvtColor(progress_bar_image, cv2.COLOR_BGR2GRAY)
    _, thresholded = cv2.threshold(gray_small_bar, 240, 255, cv2.THRESH_BINARY)
    # Check if most of the small bar is white (90% or more)
    white_pixels = np.sum(thresholded == 255)
    total_pixels = thresholded.size
    return white_pixels / total_pixels > 0.9

# Detect the gray fish line's position
def detect_fish_line(image):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply a threshold to detect the gray line
    _, thresholded = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    # Find contours of the gray line
    contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Find the largest contour which should be the gray line
        fish_line_contour = max(contours, key=cv2.contourArea)
        
        # Get the bounding box of the gray fish line
        x, y, w, h = cv2.boundingRect(fish_line_contour)
        return x, w  # Return the x position and width of the gray line

    return None, None

# Detect the white part of the inner bar in the state bar
def detect_white_bar(image):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Threshold to detect the white part of the bar
    _, thresholded = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)

    # Find contours of the white bar
    contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Find the largest contour which should be the white bar
        bar_contour = max(contours, key=cv2.contourArea)
        
        # Get the bounding box of the white bar
        x, y, w, h = cv2.boundingRect(bar_contour)
        return x, w  # Return the x position and width of the white bar

    return None, None

# Function to adjust the bar by holding/releasing the spacebar based on the gray line's position
def adjust_bar_with_space():
    while not is_progress_bar_white():  # Repeat until the progress bar becomes fully white
        state_bar_image = capture_state_bar_area()
        gray_line_image = capture_gray_line_area()

        white_bar_x, white_bar_w = detect_white_bar(state_bar_image)
        gray_line_x, gray_line_w = detect_fish_line(gray_line_image)

        if white_bar_x is not None and gray_line_x is not None:
            # If the gray line is outside the white bar (red bar shown)
            if not (white_bar_x <= gray_line_x <= (white_bar_x + white_bar_w - gray_line_w)):
                # Gray line is outside the white bar, hold the spacebar to move right
                keyboard_controller.press('space')
                print("Holding spacebar: Moving inner bar to the right")
            else:
                # Gray line is inside the white bar, release the spacebar to move left
                keyboard_controller.release('space')
                print("Released spacebar: Moving inner bar to the left")

        time.sleep(0.05)

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

    # Step 4: Adjust the bar using the spacebar until the gray line is inside the white bar, repeatedly
    adjust_bar_with_space()

    # Step 5: Repeatedly press 's' and 'Enter' until spacebar is pressed
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
    # Detect when either Shift key is released
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
