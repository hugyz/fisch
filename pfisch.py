#!/usr/bin/env python3
import os
import numpy as np
import cv2
import time
import threading
from PIL import ImageGrab
from pynput import keyboard
from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Controller as MouseController, Button

keyboard_controller = KeyboardController()
mouse_controller = MouseController()
macro_lock = threading.Lock()

def print_debug(*args):
    print("[DEBUG]", *args)

def create_initial_state():
    """Initializes a fresh state dictionary."""
    return {
        "macro_active": False,
        "listener_active": True,
        "switch": False,
        "center": None,
        "shift_pressed": False,
        "space_held": False  # Track if spacebar is currently held down
    }

def fisch_env_config():
    """Defines the configuration for regions and thresholds."""
    return {
        "bar_region": (405, 600, 960, 625),
        "center_region": (405, 590, 960, 591),
        "bar_length": 250,
        "min_area": 20 * (250 // 2 - 15),
        "max_area": 20 * (250 + 15),
        "arrow_radius": 102,
    }

def get_contour_dims(contour):
    return cv2.boundingRect(contour)

def call_func_with_handling(func, *args, retries=10, **kwargs):
    """Handles retries for a given function."""
    if retries <= 0:
        print_debug(f"Failed to call {func.__name__} after retries.")
        return None
    try:
        return func(*args, **kwargs)
    except Exception as e:
        print_debug(f"Error in {func.__name__}: {e}")
        time.sleep(1)
        return call_func_with_handling(func, *args, retries=retries - 1, **kwargs)

def take_screenshot(region):
    """Captures a screenshot of a specified region."""
    try:
        return np.array(ImageGrab.grab(bbox=region))
    except Exception as e:
        print_debug(f"Screenshot error: {e}")
        return None

def compute_sleep_time(dist):
    """Calculates sleep time for smoother movements based on distance."""
    thresholds = [
        (300, 0.3),
        (200, 0.25),
        (100, 0.18),
        (50, 0.12),
        (0, 0.1),
        (-50, 0.07),
        (-100, 0.04),
    ]
    return next((t[1] for t in thresholds if dist > t[0]), 0)

def perform_action(sleep_time, state):
    """Smoothly controls the bar movement with adjusted hold times for spacebar."""
    if sleep_time > 0:
        if not state["space_held"]:
            keyboard_controller.press(' ')
            state["space_held"] = True
            print_debug("Spacebar pressed.")
        time.sleep(sleep_time)
    else:
        if state["space_held"]:
            keyboard_controller.release(' ')
            state["space_held"] = False
            print_debug("Spacebar released.")

def find_fish_center_x(config):
    """Identifies the fish center's x-coordinate based on a specified color range."""
    screenshot = call_func_with_handling(take_screenshot, config["center_region"])
    if screenshot is None:
        return None

    fish_image = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    target_color_range = ((80, 65, 58), (100, 85, 78))

    for x in range(fish_image.shape[1]):
        b, g, r = fish_image[0, x]
        if all(target_color_range[0][i] <= pixel <= target_color_range[1][i] for i, pixel in enumerate((b, g, r))):
            print_debug(f"Fish center found at X position: {x}")
            return x
    return None

def find_bar_center_x(config, state):
    """Locates the center x-coordinate of the bar based on contour detection."""
    image = call_func_with_handling(take_screenshot, config["bar_region"])
    if image is None:
        print_debug("Failed to capture bar region.")
        return state

    hsv_image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    lower_bound = np.array([0, 0, 100])
    upper_bound = np.array([180, 150, 255])
    mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        print_debug("No contours found for the bar. Resetting center.")
        state["center"] = None
        return state

    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    min_area, max_area = config["min_area"], config["max_area"]

    for contour in contours:
        contour_area = cv2.contourArea(contour)
        x, _, w, _ = get_contour_dims(contour)
        if min_area <= contour_area <= max_area:
            state["center"] = x + w // 2
            print_debug(f"Bar center updated to: {state['center']}")
            return state

    print_debug("No valid contours found for the bar.")
    return state

def displacement(x, y):
    if y is None:
        print_debug("Bar center is None, cannot calculate displacement.")
        return None
    disp = x - y
    print_debug(f"Calculated displacement: {disp}")
    return disp

def execute_macro(state):
    """Performs the macro actions with a lock to ensure single execution."""
    with macro_lock:
        print_debug("Starting macro execution.")

        # Mouse press and release using pynput
        mouse_controller.press(Button.left)
        time.sleep(0.5)
        mouse_controller.release(Button.left)
        time.sleep(1)
        
        for i in range(0,5):
            # Press and release the backslash key with added delay for consistency
            keyboard_controller.press('\\')
            time.sleep(0.5)  # Adjust this delay if backslash is inconsistent
            keyboard_controller.release('\\')

        while state["macro_active"]:
            keyboard_controller.press('s')
            keyboard_controller.release('s')
            keyboard_controller.press(keyboard.Key.enter)
            keyboard_controller.release(keyboard.Key.enter)

def on_press(state, key):
    if key == keyboard.Key.shift:
        state["shift_pressed"] = True
    elif key == keyboard.Key.enter and state["shift_pressed"]:
        print_debug("Shift + Enter pressed, toggling macro.")
        if not state["macro_active"]:
            state["switch"] = True
            state["macro_active"] = True
            threading.Thread(target=execute_macro, args=(state,)).start()
    elif key == keyboard.KeyCode.from_char("q"):
        print_debug("Exiting program via 'Q' key.")
        os._exit(0)  # Ensure os is correctly imported
    return state

def on_release(state, key):
    if key == keyboard.Key.shift:
        state["shift_pressed"] = False
    return state

def run_fisch_env():
    config = fisch_env_config()
    state = create_initial_state()

    def on_press_handler(key):
        nonlocal state
        state = on_press(state, key)

    def on_release_handler(key):
        nonlocal state
        state = on_release(state, key)

    with keyboard.Listener(on_press=on_press_handler, on_release=on_release_handler) as listener:
        try:
            while state["listener_active"]:
                fish_center_x = find_fish_center_x(config)

                if fish_center_x is not None:
                    print_debug(f"Fish center at {fish_center_x}")
                    bar_center = find_bar_center_x(config, state).get("center")
                    if bar_center is None:
                        print_debug("Bar center could not be located.")
                    else:
                        sleep_time = compute_sleep_time(displacement(fish_center_x, bar_center))
                        print_debug(f"Calculated sleep time: {sleep_time}")
                        perform_action(sleep_time, state)

                elif state["switch"] and not state["macro_active"]:
                    print_debug("Switch toggled and macro inactive. Starting macro.")
                    time.sleep(3)
                    state["macro_active"] = True
                    threading.Thread(target=execute_macro, args=(state,)).start()

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except KeyboardInterrupt:
            print("Execution interrupted.")

if __name__ == "__main__":
    run_fisch_env()
