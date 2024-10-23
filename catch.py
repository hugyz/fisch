import pyautogui
import time
import threading
from PIL import ImageGrab, Image
import os
from pynput.keyboard import Controller

# Constants
BIG_BAR_LENGTH = 552  # PIXELS
BAR_LENGTH = 193  # PIXELS
LINE_LENGTH = 6  # PIXELS

# Use an event to signal stopping the macro
stop_event = threading.Event()
keyboard_controller = Controller()  # Controller for low-level key presses using pynput

# Get the screen size dynamically
screen_width, screen_height = pyautogui.size()

# Function to check if a color is within a broader dark gradient range
def is_dark_color(r, g, b, threshold=50):
    return (r + g + b) / 3 < threshold  # Average RGB value for dark colors

# Function to detect the appearance of the bar gradient (dark colors)
def is_gradient_bar_present(image_path, dark_color_threshold=50, required_dark_pixels_ratio=0.10):
    """Check if the bar in is_big_bar_there.png contains a gradient of dark colors."""
    image = Image.open(image_path)
    pixels = image.load()
    width, height = image.size

    dark_pixel_count = 0
    total_pixels = width * height

    # Count the number of dark gradient pixels
    for x in range(width):
        for y in range(height):
            r, g, b = pixels[x, y]
            if is_dark_color(r, g, b, dark_color_threshold):
                dark_pixel_count += 1

    # Calculate the ratio of dark pixels to total pixels
    dark_pixels_ratio = dark_pixel_count / total_pixels

    print(f"Dark pixels ratio: {dark_pixels_ratio:.2f}")

    # If the ratio of dark pixels exceeds the required threshold, the bar is detected
    if dark_pixels_ratio >= required_dark_pixels_ratio:
        print(f"Gradient bar detected with {dark_pixels_ratio * 100:.2f}% of the region being dark.")
        return True
    else:
        print(f"No gradient bar detected. Only {dark_pixels_ratio * 100:.2f}% of the region is dark.")
        return False

# Function to extract the top line from the bar image
def extract_top_line(image_path, output_path):
    """Extract the top line of pixels from an image and save it as a new image."""
    image = Image.open(image_path)
    width, height = image.size
    top_line = image.crop((0, 0, width, 1))
    top_line.save(output_path)
    print(f"Top line of {image_path} saved as {output_path}")

def find_line_midpoint(image_path, line_length):
    """Find the midpoint of the red line in line_color.png."""
    image = Image.open(image_path)
    pixels = image.load()
    width, height = image.size

    for x in range(width - line_length + 1):
        if all(pixels[x + i, 0] == (255, 0, 0) for i in range(line_length)):
            midpoint = x + (line_length // 2)
            print(f"Midpoint of the line is at: {midpoint}")
            return midpoint
    print("Line not found.")
    return None

def find_bar_midpoint(image_path, bar_length):
    """Find the midpoint of the blue bar in bar_color_ceiling.png."""
    image = Image.open(image_path)
    pixels = image.load()
    width, height = image.size
    consecutive_blue = 0

    for x in range(width):
        if pixels[x, 0] == (0, 0, 255):
            consecutive_blue += 1
        else:
            consecutive_blue = 0  # Reset counter if not blue

        if consecutive_blue == (bar_length - 5):
            midpoint = x - (bar_length // 2)
            print(f"Midpoint of the bar is at: {midpoint}")
            return midpoint
    print("Bar not found.")
    return None

def apply_line_color_map(image_path, output_path, grey_rgb=(67, 75, 91), threshold=5):
    """Map grey (67, 75, 91) to red and everything else to blue for line_color."""
    image = Image.open(image_path)
    rgb_image = image.convert("RGB")
    rb_image = Image.new("RGB", rgb_image.size)
    pixels = rb_image.load()

    def is_grey(color, grey_rgb, threshold):
        return all(abs(c1 - c2) <= threshold for c1, c2 in zip(color, grey_rgb))

    for i in range(rgb_image.size[0]):
        for j in range(rgb_image.size[1]):
            r, g, b = rgb_image.getpixel((i, j))
            if is_grey((r, g, b), grey_rgb, threshold):
                pixels[i, j] = (255, 0, 0)  # Red for grey
            else:
                pixels[i, j] = (0, 0, 255)  # Blue for everything else

    rb_image.save(output_path)
    print(f"Applied red/blue map to {image_path} and saved as {output_path}")

def apply_bar_color_map(image_path, output_path, threshold=5):
    """Map red, green, gradient, white to red and everything else to blue for bar_color."""
    image = Image.open(image_path)
    rgb_image = image.convert("RGB")
    rb_image = Image.new("RGB", rgb_image.size)
    pixels = rb_image.load()

    def is_within_threshold(color1, color2, threshold):
        return all(abs(c1 - c2) <= threshold for c1, c2 in zip(color1, color2))

    for i in range(rgb_image.size[0]):
        for j in range(rgb_image.size[1]):
            r, g, b = rgb_image.getpixel((i, j))
            if (is_within_threshold((r, g, b), (255, 0, 0), threshold) or
                is_within_threshold((r, g, b), (0, 255, 0), threshold) or
                (0 <= r <= 255 and 0 <= g <= 255 and abs(r - g) <= threshold) or
                is_within_threshold((r, g, b), (255, 255, 255), threshold)):
                pixels[i, j] = (255, 0, 0)  # Red
            else:
                pixels[i, j] = (0, 0, 255)  # Blue

    rb_image.save(output_path)
    print(f"Applied red/blue map to {image_path} and saved as {output_path}")

def ensure_folder_exists(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"Folder '{folder_name}' created.")
    else:
        print(f"Folder '{folder_name}' already exists.")

def main():
    folder_name = "ss"
    ensure_folder_exists(folder_name)

    big_bar_region = (407, 585, 959, 642)
    line_region = (407, 628, 959, 629)
    bar_region = (407, 603, 959, 625)

    counter = 0  # Initialize a counter for the loop

    while True:
        screenshot_big_bar = ImageGrab.grab(bbox=big_bar_region)
        screenshot_big_bar.save(f"{folder_name}/is_big_bar_there.png")

        # Check if the gradient bar is present with adjusted threshold
        if not is_gradient_bar_present(f"{folder_name}/is_big_bar_there.png", dark_color_threshold=50, required_dark_pixels_ratio=0.10):
            print(f"Gradient bar not found. Program terminated after {counter} iterations.")
            return

        screenshot_1 = ImageGrab.grab(bbox=line_region)
        screenshot_1.save(f"{folder_name}/line.png")
        screenshot_2 = ImageGrab.grab(bbox=bar_region)
        screenshot_2.save(f"{folder_name}/bar.png")

        apply_line_color_map(f"{folder_name}/line.png", f"{folder_name}/line_color.png", threshold=5)
        apply_bar_color_map(f"{folder_name}/bar.png", f"{folder_name}/bar_color.png", threshold=5)
        extract_top_line(f"{folder_name}/bar_color.png", f"{folder_name}/bar_color_ceiling.png")

        line_midpoint = find_line_midpoint(f"{folder_name}/line_color.png", LINE_LENGTH)
        bar_midpoint = find_bar_midpoint(f"{folder_name}/bar_color_ceiling.png", BAR_LENGTH)

        if line_midpoint is not None and bar_midpoint is not None:
            print(f"Line Midpoint: {line_midpoint}, Bar Midpoint: {bar_midpoint}")

        # Increment the counter and print it
        counter += 1
        print(f"Loop iteration: {counter}")

        time.sleep(1) 


if __name__ == "__main__":
    main()
