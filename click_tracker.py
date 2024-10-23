from pynput import keyboard
import time
import threading

class SpacebarTracker:
    def __init__(self):
        self.start_time = None
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.running = True
        self.holding = False

    def on_press(self, key):
        if key == keyboard.Key.space and not self.holding:
            self.start_time = time.time()
            self.holding = True
        elif key == keyboard.KeyCode.from_char('f'):
            self.running = False
            return False

    def on_release(self, key):
        if key == keyboard.Key.space and self.holding:
            self.holding = False
            print(f"\nSpacebar released")

    def print_hold_time(self):
        while self.running:
            if self.holding:
                current_time = time.time() - self.start_time
                print(f"\rSpacebar held for {current_time:.2f} seconds", end="", flush=True)
            time.sleep(0.1)

    def run(self):
        print("Press and hold the spacebar to track duration.")
        print("Press 'F' to exit the program.")
        
        time_thread = threading.Thread(target=self.print_hold_time)
        time_thread.start()

        with self.keyboard_listener as listener:
            listener.join()

        time_thread.join()

if __name__ == "__main__":
    tracker = SpacebarTracker()
    tracker.run()