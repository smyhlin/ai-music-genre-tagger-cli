#!filepath: main.py
import os
# Set TF_CPP_MIN_LOG_LEVEL environment variable to suppress TensorFlow messages
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # remove it for debugging
import platform
from music_tagger import MusicTagger


def get_music_directory():
    """
    Asks the user for the music directory path, using a folder dialog on Windows if possible.

    Returns:
        str: The music directory path, or None if the user cancels or an error occurs.
    """
    music_directory = None

    if platform.system() == "Windows":
        try:
            import tkinter
            from tkinter import filedialog

            root = tkinter.Tk()
            root.withdraw()  # Hide the main tkinter window

            music_directory = filedialog.askdirectory(
                title="Select Music Directory",
                initialdir=os.path.expanduser("~"),  # Start in the user's home directory
                mustexist=True
            )
            root.destroy() # Cleanly close tkinter

        except ImportError:
            print("Tkinter is not available. Please enter the music directory path manually.")
            music_directory = input("Enter the path to your music directory: ").strip()
        except Exception as e:
            print(f"An error occurred while using the folder dialog: {e}")
            music_directory = input("Enter the path to your music directory: ").strip()
    else:
        music_directory = input("Enter the path to your music directory: ").strip()

    return music_directory


if __name__ == "__main__":
    music_tagger = MusicTagger()

    music_directory = get_music_directory()

    if not music_directory:
        print("No music directory selected. Exiting.")
    elif not os.path.isdir(music_directory):
        print(f"Error: Directory '{music_directory}' does not exist or is not a valid directory.")
    else:
        print(f"Starting music genre tagging process for directory: {music_directory} with AI genre suggestions.")
        print("You will be prompted to enter genre for each music file. AI suggestions will be provided.")
        music_tagger.process_directory(music_directory)
        print(f"Music genre tagging process completed for directory: {music_directory}")