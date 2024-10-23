from PIL import ImageGrab, Image
import os
import time

# Define the function to apply the red/blue differentiation for the line image
def apply_line_color_map(image_path, output_path, grey_rgb=(67, 75, 91), threshold=5):
    """Map grey (67, 75, 91) to red and everything else to blue for line_color."""
    image = Image.open(image_path)

    # Convert the image to RGB
    rgb_image = image.convert("RGB")  # Ensure the image is in RGB mode

    # Create a new image for the red/blue mapping
    rb_image = Image.new("RGB", rgb_image.size)
    pixels = rb_image.load()

    # Helper function to check if a color is within the given threshold of grey
    def is_grey(color, grey_rgb, threshold):
        return all(abs(c1 - c2) <= threshold for c1, c2 in zip(color, grey_rgb))

    # Loop through the image pixels
    for i in range(rgb_image.size[0]):
        for j in range(rgb_image.size[1]):
            r, g, b = rgb_image.getpixel((i, j))

            # If the color is within the threshold of grey, map to red
            if is_grey((r, g, b), grey_rgb, threshold):
                pixels[i, j] = (255, 0, 0)  # Red for grey
            else:
                pixels[i, j] = (0, 0, 255)  # Blue for everything else

    # Save the red/blue mapped image
    rb_image.save(output_path)
    print(f"Applied red/blue map to {image_path} and saved as {output_path}")

# Define the function to apply the dark blue/black differentiation for the bar image
def apply_bar_color_map(image_path, output_path, threshold=20):
    """Map dark blue/black (low RGB values) to red and everything else to blue for bar_color."""
    image = Image.open(image_path)

    # Convert the image to RGB
    rgb_image = image.convert("RGB")  # Ensure the image is in RGB mode

    # Create a new image for the red/blue mapping
    rb_image = Image.new("RGB", rgb_image.size)
    pixels = rb_image.load()

    # Loop through the image pixels
    for i in range(rgb_image.size[0]):
        for j in range(rgb_image.size[1]):
            r, g, b = rgb_image.getpixel((i, j))

            # If all RGB values are below the threshold, map to red
            if r < threshold and g < threshold and b < threshold:
                pixels[i, j] = (255, 0, 0)  # Red for dark blue/black
            else:
                pixels[i, j] = (0, 0, 255)  # Blue for everything else

    # Save the red/blue mapped image
    rb_image.save(output_path)
    print(f"Applied dark blue/black map to {image_path} and saved as {output_path}")

def ensure_folder_exists(folder_name):
    """Check if the folder exists, and if not, create it."""
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"Folder '{folder_name}' created.")
    else:
        print(f"Folder '{folder_name}' already exists.")

def main():
    # Ensure the 'ss' folder exists
    folder_name = "ss"
    ensure_folder_exists(folder_name)

    # Manually define screen dimensions for now (or replace with actual pyautogui calls if available)
    screen_width, screen_height = 1366, 768  # Example resolution
    print(f"Screen width: {screen_width}, Screen height: {screen_height}")
    
    # Define regions for screenshots (x1, y1, x2, y2)
    big_bar_region = (450, 585, 550, 642)
    line_region = (406, 628, 960, 629)
    bar_region = (407, 603, 959, 625)

    # Capture the specified regions and save them in 'ss' folder
    screenshot_big_bar = ImageGrab.grab(bbox=big_bar_region)
    screenshot_big_bar.save(f"{folder_name}/is_big_bar_there.png")

    screenshot_1 = ImageGrab.grab(bbox=line_region)
    screenshot_1.save(f"{folder_name}/line.png")
    time.sleep(3)
    screenshot_2 = ImageGrab.grab(bbox=bar_region)
    screenshot_2.save(f"{folder_name}/bar.png")

    print("Screenshots taken and saved.")

    # Apply red/blue map to line and dark blue/black map to bar
    apply_line_color_map(f"{folder_name}/line.png", f"{folder_name}/line_color.png", threshold=5)
    apply_bar_color_map(f"{folder_name}/bar.png", f"{folder_name}/bar_color.png", threshold=20)

# Ensure that the program runs the main function on execution
if __name__ == "__main__":
    main()
