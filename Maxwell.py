import os
import time
import webbrowser
import msvcrt
import random
from pathlib import Path

URL = "https://www.youtube.com/watch?v=YRvOePz2OqQ&t=28s"
ALT_URL = "https://www.youtube.com/watch?v=gfJmJVpafFo"

def create_maxwell_file():
    """Creates Maxwell.txt in a random user folder."""
    # List of potential target directories
    folders = ["Documents", "Downloads", "Music", "Pictures", "Videos"]
    target_folder = random.choice(folders)
    
    # Construct the path safely using Path
    file_path = Path.home() / target_folder / "Maxwell.txt"
    
    try:
        with open(file_path, "w") as f:
            for _ in range(100):
                f.write("o ee a e o ee a e\n")
        return file_path
    except Exception:
        # Fallback to Desktop if a folder is restricted
        return "Desktop"

def run_prank():
    # 1. Create the text document immediately on startup
    saved_location = create_maxwell_file()
    
    # 2. Clear screen and start the infinite scroll
    os.system("cls" if os.name == "nt" else "clear")
    
    print(f"--- Maxwell has arrived ---")
    time.sleep(0.5)

    while True:
        # The 100ms infinite print
        print("o ee a e o ee a e")
        time.sleep(0.1)

        # 3. Detect ANY key press to open the URL
        if msvcrt.kbhit():
            msvcrt.getch()  # Clear the key buffer
            
            # 0.000001% chance (1 in 100,000,000) to play the alt video
            if random.random() < 0.00000001:
                webbrowser.open(ALT_URL)
            else:
                webbrowser.open(URL)

            # No location message anymore

if __name__ == "__main__":
    run_prank()