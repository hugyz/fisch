from PIL import ImageGrab, Image
import os

def apply_grouped_color_map(image_path, output_path, threshold=10):
    """Apply a color map that groups pixels with similar RGB values (within a threshold)."""
    image = Image.open(image_path)

    # Convert the image to RGB
    rgb_image = image.convert("RGB")  # Ensure the image is in RGB mode

    # Create a new image for the color mapping
    color_mapped_image = Image.new("RGB", rgb_image.size)
    pixels = color_mapped_image.load()

    # Helper function to check if two colors are within the given threshold
    def is_similar(color1, color2, threshold):
        return all(abs(c1 - c2) <= threshold for c1, c2 in zip(color1, color2))

    # Store unique colors for mapping
    unique_colors = []

    for i in range(rgb_image.size[0]):
        for j in range(rgb_image.size[1]):
            current_pixel = rgb_image.getpixel((i, j))

            # Check if this pixel is similar to any already mapped colors
            mapped_color = None
            for color in unique_colors:
                if is_similar(current_pixel, color, threshold):
                    mapped_color = color
                    break

            if mapped_color:
                # Assign the mapped color
                pixels[i, j] = mapped_color
            else:
                # New unique color, add it to the list and assign it
                unique_colors.append(current_pixel)
                pixels[i, j] = current_pixel

    # Save the color-mapped image
    color_mapped_image.save(output_path)
    print(f"Applied grouped color map to {image_path} and saved as {output_path}")

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
    bar_region = (406, 626, 960, 627)

    # Capture the specified regions and save them in 'ss' folder
    screenshot = ImageGrab.grab(bbox=big_bar_region)
    screenshot.save(f"{folder_name}/is_big_bar_there.png")

    screenshot_1 = ImageGrab.grab(bbox=line_region)
    screenshot_1.save(f"{folder_name}/line.png")

    screenshot_2 = ImageGrab.grab(bbox=bar_region)
    screenshot_2.save(f"{folder_name}/bar.png")

    print("Screenshots taken and saved.")

    # Apply grouped color map to the bar image and save it in 'ss' folder
    apply_grouped_color_map(f"{folder_name}/bar.png", f"{folder_name}/bar_color.png", threshold=10)

# Ensure that the program runs the main function on execution
if __name__ == "__main__":
    main()
