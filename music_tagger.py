#!filepath: music_tagger.py
import os
import logging
from typing import List, Callable, Optional, Union, Tuple

import mutagen
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen.mp4 import MP4

from musicnn_tagger import get_init_extractor
from lastfm_tagger import get_tags_and_weights

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MusicTagger:
    """
    A class to handle music file tagging operations, integrating AI-based and Last.fm genre suggestions,
    and supporting multiple genres. Enhanced metadata extraction and detailed debug logging.
    """
    def __init__(self) -> None:
        """Initializes the MusicTagger."""
        pass

    def set_genre_tag(self, file_path: str, genres: Union[str, List[str]]) -> bool:
        """Sets the genre tag(s) for a music file using mutagen.mp4."""
        try:
            if isinstance(genres, str):
                genre_list = [genres]
            elif isinstance(genres, list):
                genre_list = genres
            else:
                logging.error(f"Invalid genre format: {genres}. Expected string or list.")
                return False

            if file_path.lower().endswith('.mp3'):
                try:
                    audio = EasyID3(file_path)
                except mutagen.id3._util.ID3NoHeaderError:
                    audio = MP3(file_path, ID3=EasyID3)
                audio['genre'] = genre_list
                audio.save()
            elif file_path.lower().endswith('.m4a'):
                audio = MP4(file_path)
                audio['\xa9gen'] = genre_list
                audio.save()
            else:
                logging.error(f"Unsupported file format for tagging: {file_path}")
                return False

            logging.info(f"Genre tag(s) set to '{genres}' for file: {file_path}")
            return True
        except Exception as e:
            logging.error(f"Error processing genre tag for file {file_path}: {e}")
            return False

    def process_music_file(self, file_path: str) -> bool:
        """Processes a single music file with AI and Last.fm genre suggestions."""
        ai_genres = get_init_extractor(music_path=file_path, ai_model_count=3, max_genres_return_count=5, min_weight=0.2)
        suggested_genres_ai = list(ai_genres.keys())

        filename = os.path.basename(file_path)
        artist_name, track_name = self._extract_metadata_from_file(file_path)
        if not artist_name or not track_name:
            logging.warning("Could not extract artist and track from metadata, falling back to filename parsing.")
            artist_name, track_name = self._extract_artist_track_from_filename(filename)

        logging.info(f"Extracted Artist Name: '{artist_name}', Track Name: '{track_name}' for Last.fm") # Debug log

        lastfm_tags_weights = get_tags_and_weights(artist_name, track_name, topN=5, min_weight=60)
        suggested_genres_lastfm = [tag_name for tag_name, _ in lastfm_tags_weights]

        suggested_genres_all = suggested_genres_ai + suggested_genres_lastfm
        suggested_genres_all_unique = sorted(list(set(suggested_genres_all)), key=suggested_genres_all.index)

        print(f"AI Suggested genres: {suggested_genres_ai}")
        print(f"Last.fm Suggested genres: {suggested_genres_lastfm}")

        while True:
            prompt_text = f"Enter genre(s) for '{file_path}'"
            if suggested_genres_all_unique:
                prompt_text += f" (or choose from suggestions: {', '.join(suggested_genres_all_unique)}, or type comma-separated genres, or 'skip' to skip file): "
            else:
                prompt_text += " (or type comma-separated genres, or 'skip' to skip file): "

            genre_input: str = input(prompt_text).strip()
            if genre_input.lower() == 'skip':
                logging.info(f"Skipping file: {file_path}")
                return False
            if genre_input:
                if "," in genre_input:
                    genres = [genre.strip() for genre in genre_input.split(",")]
                elif genre_input in suggested_genres_all_unique:
                    genres = genre_input
                else:
                    genres = genre_input
                break
            else:
                print("Genre cannot be empty. Please enter a genre or type 'skip'.")

        logging.info(f"Processing file: {file_path}, setting genre(s) to: {genres}")
        return self.set_genre_tag(file_path, genres)

    def _extract_artist_track_from_filename(self, filename: str) -> Tuple[str, str]:
        """Extracts artist and track name from filename using heuristics."""
        track_name = filename
        artist_name = ""
        separators = [' - ', '-', '—', '_']

        for sep in separators:
            if sep in filename:
                parts = filename.split(sep, 1)
                artist_name = parts[0].strip()
                track_name = parts[1].strip()
                break

        track_name = os.path.splitext(track_name)[0]
        return artist_name, track_name

    def _extract_metadata_from_file(self, file_path: str) -> Tuple[str, str]:
        """Extracts artist and track name from music file metadata using mutagen with verbose logging."""
        artist_name = ""
        track_name = ""
        try:
            if file_path.lower().endswith('.mp3'):
                audio = EasyID3(file_path)
                logging.debug(f"EasyID3 tags: {audio.keys()}") # Log all EasyID3 tags found
                artist_list = audio.get('artist', []) or audio.get('ARTIST', []) or audio.get('TPE1', []) or audio.get('TPE2', []) or audio.get('TOPE', []) # Added more artist tags
                title_list = audio.get('title', []) or audio.get('TITLE', []) or audio.get('TIT2', []) # Added TIT2 (ID3v2 Title)
            elif file_path.lower().endswith('.m4a'):
                audio = MP4(file_path)
                logging.debug(f"MP4 tags: {audio.keys()}") # Log all MP4 tags found
                artist_list = audio.get('\xa9ART', []) or audio.get('aART', []) or audio.get('ART', []) or audio.get('\xa9albArtist', []) or audio.get('©ART', []) # Added more m4a artist tags
                title_list = audio.get('\xa9nam', []) or audio.get('\xa9Title', []) or audio.get('TITLE', []) or audio.get('\xa9title', []) # Added more m4a title tags
            else:
                return "", ""

            artist_name_list = [str(artist).strip() for artist in artist_list if artist] # Ensure artist names are strings and not None
            track_name_list = [str(title).strip() for title in title_list if title] # Ensure track names are strings and not None

            artist_name = ' '.join(artist_name_list) if artist_name_list else ""
            track_name = ' '.join(track_name_list) if track_name_list else ""

            logging.debug(f"Metadata Artist Tags: {artist_list}, Extracted Artist Name: '{artist_name}'") # Debug log metadata extraction
            logging.debug(f"Metadata Title Tags: {title_list}, Extracted Track Name: '{track_name}'") # Debug log metadata extraction


        except Exception as e:
            logging.error(f"Error extracting metadata from {file_path}: {e}")
            return "", ""

        return artist_name.strip(), track_name.strip()

    def find_music_files(self, root_dir: str) -> List[str]:
        """Recursively finds music files (.mp3, .m4a) within a root directory."""
        music_files: list[str] = []
        extensions = ['.mp3', '.m4a']

        for root, _, files in os.walk(root_dir):
            for file in files:
                if any(file.lower().endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    music_files.append(file_path)
        return music_files

    def process_directory(self, root_dir: str) -> None:
        """Recursively processes music files in a directory and sets their genre and lyrics tags."""
        music_files = self.find_music_files(root_dir)
        logging.info(f"Found {len(music_files)} music files in {root_dir}")

        for file_path in music_files:
            self.process_music_file(file_path)