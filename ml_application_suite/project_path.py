import sys
import os

# Set the main project directory (main folder)
MAIN_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))

# Add the main directory to sys.path so it can be accessed anywhere
sys.path.append(MAIN_DIRECTORY)

# Optional: Print the main directory for debugging
print(f"Main directory set to: {MAIN_DIRECTORY}")