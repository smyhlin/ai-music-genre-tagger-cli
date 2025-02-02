#!filepath: main.py
import os
# Set TF_CPP_MIN_LOG_LEVEL environment variable to suppress TensorFlow messages
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # remove it for debugging

from music_tagger import MusicTagger

if __name__ == "__main__":

    music_tagger = MusicTagger()
    music_directory = r"D:\GITHB\FNAF2\test_fldr"  # Replace with the actual path to your music directory

    if not os.path.isdir(music_directory):
        print(f"Error: Directory '{music_directory}' does not exist.")
    else:
        print("Starting music genre tagging process with AI genre suggestions.")
        print("You will be prompted to enter genre for each music file. AI suggestions will be provided.")
        music_tagger.process_directory(music_directory)
        print(f"Music genre tagging process completed for directory: {music_directory}")