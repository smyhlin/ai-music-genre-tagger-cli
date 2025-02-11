#!filepath: music_tagger.py
import os
import logging
from typing import List, Callable, Optional, Union, Tuple, Dict

import mutagen
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen.mp4 import MP4
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.oggopus import OggOpus
from mutagen.oggflac import OggFLAC
from mutagen.oggspeex import OggSpeex
from mutagen.wave import WAVE
from mutagen.aiff import AIFF
from mutagen.asf import ASF
from mutagen.apev2 import APEv2
from mutagen.wavpack import WavPack

# Import necessary modules for handling TextFrame in WAV files
from mutagen.id3 import ID3, TCON, TextFrame, Encoding

from musicnn_tagger import get_musicnn_tags
from lastfm_tagger import get_lastfm_tags

import colorama
from colorama import Fore, Back, Style
import concurrent.futures  # Import for concurrency
import multiprocessing

colorama.init()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Color constants
C_AI = Fore.CYAN
C_LASTFM = Fore.MAGENTA
C_PROMPT = Fore.YELLOW
C_GENRE_SUGGESTION = Fore.GREEN
C_RESET = Style.RESET_ALL
C_BOLD = Style.BRIGHT


def colored_print(color: str, text: str) -> None:
    """Prints text in the specified color."""
    print(color + text + C_RESET)

def worker_process(input_queue: multiprocessing.Queue, output_queue: multiprocessing.Queue, musicnn_settings: 'musicnn_tagger.config.MusicnnSettings'):
    """
    This function runs in a separate process.  It takes file paths from
    the input queue, processes them using get_musicnn_tags, and puts the
    results (file_path, genre_dict) into the output queue.
    """
    print(f"Worker process started (PID: {os.getpid()})")  # Indicate process start

    while True:
        file_path = input_queue.get()
        if file_path is None:  # Termination signal
            print(f"Worker process (PID: {os.getpid()}) exiting.") # Indicate process exit
            break  # Exit the loop

        print(f"Worker (PID: {os.getpid()}) processing: {file_path}")  # Indicate file processing

        try:
            ai_genres_dict = get_musicnn_tags(
                music_path=file_path,
                ai_model_count=musicnn_settings.model_count,
                ai_genres_count=musicnn_settings.genres_count,
                max_genres_return_count=5,
                min_weight=musicnn_settings.threshold_weight
            )
            output_queue.put((file_path, ai_genres_dict))  # Send results back
            print(f"Worker (PID: {os.getpid()}) finished processing: {file_path}") # Indicate processing complete
        except Exception as e:
            logger.error(f"Worker process error processing {file_path}: {e}")
            #  Send an error message. Put something in the output queue,
            #  or the main process might hang waiting for results.
            output_queue.put((file_path, {})) # Put empty result in queue.

class MusicTagger:
    """
    A class to handle music file tagging operations, integrating AI-based and Last.fm genre suggestions,
    and supporting a wide range of audio file formats.
    """

    SUPPORTED_FORMATS: Dict[str, Dict[str, Union[Callable, List[str]]]] = {
        '.mp3': {'module': EasyID3, 'alt_module': MP3, 'genre_tag': ['genre'], 'artist_tags': ['artist', 'ARTIST', 'TPE1', 'TPE2', 'TOPE'], 'title_tags': ['title', 'TITLE', 'TIT2']},
        '.m4a': {'module': MP4, 'genre_tag': ['\xa9gen'], 'artist_tags': ['\xa9ART', 'aART', 'ART', '\xa9albArtist', '©ART'], 'title_tags': ['\xa9nam', '\xa9Title', 'TITLE', '\xa9title']},
        '.flac': {'module': FLAC, 'genre_tag': ['GENRE'], 'artist_tags': ['artist', 'ARTIST'], 'title_tags': ['title', 'TITLE']},
        '.ogg': {'module': OggVorbis, 'genre_tag': ['genre'], 'artist_tags': ['artist', 'ARTIST'], 'title_tags': ['title', 'TITLE']}, # OggVorbis for .ogg, more specific types like opus, flac, speex handled below
        '.opus': {'module': OggOpus, 'genre_tag': ['genre'], 'artist_tags': ['artist', 'ARTIST'], 'title_tags': ['title', 'TITLE']},
        '.oga': {'module': OggFLAC, 'genre_tag': ['genre'], 'artist_tags': ['artist', 'ARTIST'], 'title_tags': ['title', 'TITLE']}, # .oga is often Ogg FLAC
        '.spx': {'module': OggSpeex, 'genre_tag': ['genre'], 'artist_tags': ['artist', 'ARTIST'], 'title_tags': ['title', 'TITLE']},
        '.wav': {'module': WAVE, 'genre_tag': ['genre'], 'artist_tags': ['artist', 'ARTIST'], 'title_tags': ['title', 'TITLE']}, # WAVE might need special handling for genres - check mutagen docs if needed
        '.aiff': {'module': AIFF, 'genre_tag': ['genre'], 'artist_tags': ['artist', 'ARTIST'], 'title_tags': ['title', 'TITLE']}, # AIFF genre support might be limited
        '.aif': {'module': AIFF, 'genre_tag': ['genre'], 'artist_tags': ['artist', 'ARTIST'], 'title_tags': ['title', 'TITLE']}, # AIFF genre support might be limited
        '.asf': {'module': ASF, 'genre_tag': ['genre'], 'artist_tags': ['author', 'Author', 'ARTIST'], 'title_tags': ['title', 'Title', 'TITLE']}, # ASF/WMA/WMV
        '.wma': {'module': ASF, 'genre_tag': ['genre'], 'artist_tags': ['author', 'Author', 'ARTIST'], 'title_tags': ['title', 'Title', 'TITLE']}, # WMA - using ASF module
        '.wmv': {'module': ASF, 'genre_tag': ['genre'], 'artist_tags': ['author', 'Author', 'ARTIST'], 'title_tags': ['title', 'Title', 'TITLE']}, # WMV - using ASF module
        '.ape': {'module': APEv2, 'genre_tag': ['Genre'], 'artist_tags': ['Artist'], 'title_tags': ['Title']},
        '.wv': {'module': WavPack, 'genre_tag': ['genre'], 'artist_tags': ['artist', 'ARTIST'], 'title_tags': ['title', 'TITLE']}, # .wv for WavPack
    }

    def __init__(self) -> None:
        """Initializes the MusicTagger and the AI genre suggestions cache."""
        self.ai_genre_suggestions_cache: Dict[str, Dict[str, float]] = {} # Cache for AI genre suggestions

    def set_genre_tag(self, file_path: str, genres: Union[str, List[str]]) -> bool:
        """
        Sets the genre tag(s) for a music file, supporting various file formats.

        Args:
            file_path (str): Path to the music file.
            genres (Union[str, List[str]]): Genre or list of genres to set.

        Returns:
            bool: True if genre tag(s) were set successfully, False otherwise.
        """
        try:
            if isinstance(genres, str):
                genre_list = [genres]
            elif isinstance(genres, list):
                genre_list = genres
            else:
                logger.error(f"Invalid genre format: {genres}. Expected string or list.")
                return False

            ext = os.path.splitext(file_path)[1].lower()
            if ext not in self.SUPPORTED_FORMATS:
                logger.error(f"Unsupported file format for tagging: {file_path}")
                return False

            format_config = self.SUPPORTED_FORMATS[ext]
            module = format_config['module']
            genre_tag_keys = format_config['genre_tag']

            try:
                audio = module(file_path)
            except mutagen.MutagenError as e: # Catch general mutagen errors, e.g., for MP3 files without header
                if ext == '.mp3' and format_config.get('alt_module'): # Special handling for MP3 with missing header
                    audio = format_config['alt_module'](file_path, ID3=EasyID3)
                else:
                    logger.error(f"Error opening file {file_path} with mutagen: {e}")
                    return False

            if ext == '.wav':
                try:
                    audio_id3 = ID3(file_path)
                except mutagen.id3._util.ID3NoHeaderError:
                    audio_id3 = ID3()

                genre_frame = TCON(encoding=Encoding.UTF8, text=genre_list) # Use TCON for genre, UTF8 encoding
                audio_id3['TCON'] = genre_frame # Assign genre frame
                audio_id3.save(file_path) # Save ID3 tags to WAV file
                logger.info(f"Genre tag(s) set to '{genres}' for WAV file: {file_path}")
                return True

            elif isinstance(audio, EasyID3): #EasyID3 uses list for genre
                audio['genre'] = genre_list
            else: # Other formats might expect a single string or handle lists differently.
                # Setting the first genre tag key with the list of genres.
                # Mutagen might handle list to string conversion internally if needed, or take the first item.
                if genre_tag_keys and genre_tag_keys[0]:
                    audio[genre_tag_keys[0]] = genre_list

            audio.save()
            logger.info(f"Genre tag(s) set to '{genres}' for file: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Error processing genre tag for file {file_path}: {e}")
            return False
    def _extract_artist_track_from_filename(self, filename: str) -> Tuple[str, str]:
        """
        Extracts artist and track name from filename using heuristics.

        Args:
            filename (str): The filename.

        Returns:
            Tuple[str, str]: Artist name and track name extracted from the filename.
        """
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

    def _deduplicate_name(self, name: str) -> str:
        """
        Removes duplicate words from a string to clean up artist or track names.
        For example, "Mr.Kitty Mr.Kitty" becomes "Mr.Kitty".
        """
        if not name:
            return ""
        words = name.split()
        unique_words = list(dict.fromkeys(words)) # Preserve order while removing duplicates
        return " ".join(unique_words)

    def _remove_file_extension_from_track(self, track_name: str) -> str:
        """
        Removes file extension from track name if it's incorrectly included.
        For example, "After Dark.mp3" becomes "After Dark".
        """
        base_track_name = os.path.splitext(track_name)[0]
        return base_track_name

    def _extract_metadata_from_file(self, file_path: str) -> Tuple[str, str]:
        """
        Extracts artist and track name from music file metadata using mutagen.
        Includes deduplication of artist and track names and removes file extension from track name.

        Args:
            file_path (str): Path to the music file.

        Returns:
            Tuple[str, str]: Artist name and track name extracted from metadata, or empty strings if extraction fails.
        """
        artist_name = ""
        track_name = ""
        ext = os.path.splitext(file_path)[1].lower()

        if ext not in self.SUPPORTED_FORMATS:
            logger.debug(f"Unsupported format for metadata extraction: {file_path}")
            return "", ""

        format_config = self.SUPPORTED_FORMATS[ext]
        module = format_config['module']
        artist_tag_keys = format_config['artist_tags']
        title_tag_keys = format_config['title_tags']

        try:
            audio = module(file_path)
            logger.debug(f"Tags for {file_path} ({ext}): {audio.keys()}")

            artist_list = []
            for tag in artist_tag_keys:
                artist_list.extend(audio.get(tag, []))

            title_list = []
            for tag in title_tag_keys:
                title_list.extend(audio.get(tag, []))

            artist_name_list = [str(artist).strip() for artist in artist_list if artist]
            track_name_list = [str(title).strip() for title in title_list if title]

            artist_name = ' '.join(artist_name_list) if artist_name_list else ""
            track_name = ' '.join(track_name_list) if track_name_list else ""

            # Apply deduplication and extension removal
            artist_name = self._deduplicate_name(artist_name)
            track_name = self._deduplicate_name(track_name)
            track_name = self._remove_file_extension_from_track(track_name)


            logger.debug(f"Metadata Artist Tags: {artist_list}, Extracted Artist Name: '{artist_name}'")
            logger.debug(f"Metadata Title Tags: {title_list}, Extracted Track Name: '{track_name}'")

        except Exception as e:
            logger.error(f"Error extracting metadata from {file_path}: {e}")
            return "", ""

        return artist_name.strip(), track_name.strip()
    def process_music_file(self, file_path: str, auto_apply_tags: bool, musicnn_settings: 'musicnn_tagger.config.MusicnnSettings', lastfm_settings: 'lastfm_tagger.config.Settings') -> bool:
        """
        Processes a single music file with AI and Last.fm genre suggestions, then sets the genre tag.
        Retrieves AI genre suggestions from cache. No loading animation or print here.

        Args:
            file_path (str): Path to the music file.
            auto_apply_tags (bool): If True, automatically apply suggested tags.
            musicnn_settings (MusicnnSettings): Settings for Musicnn tagger.
            lastfm_settings (LastFMSettings): Settings for LastFM tagger.

        Returns:
            bool: True if the file was processed (genre tag set or skipped), False if processing failed.
        """
        suggested_genres_ai = []
        suggested_genres_lastfm = []

        # Retrieve AI genre suggestions from cache
        if file_path in self.ai_genre_suggestions_cache:
            logger.debug(f"Using cached AI genre suggestions for: {file_path}") # Debug log instead of info
            ai_genres_dict = self.ai_genre_suggestions_cache[file_path]
            suggested_genres_ai = list(ai_genres_dict.keys())
        else:
            logger.error(f"AI genre suggestions not found in cache for: {file_path}. This should not happen if pre-fetching is enabled.")
            ai_genres_dict = {} # Fallback to empty dict to avoid errors

        filename = os.path.basename(file_path)
        artist_name, track_name = self._extract_metadata_from_file(file_path)

        if not artist_name or not track_name:
            logger.warning("Could not extract artist and track from metadata, falling back to filename parsing.")
            artist_name, track_name = self._extract_artist_track_from_filename(filename)

        logger.info(f"Extracted Artist Name: '{artist_name}', Track Name: '{track_name}' for Last.fm")

        if lastfm_settings.enabled: # Conditionally use lastfm tagger
            lastfm_tags_weights = get_lastfm_tags(
                artist_name,
                track_name,
                top_n=5, # Fixed value, not from settings
                min_weight=lastfm_settings.threshold_weight * 100 # LastFM weight is percentage based
            )
            suggested_genres_lastfm = [tag_name for tag_name, _ in lastfm_tags_weights]

        suggested_genres_all = suggested_genres_ai + suggested_genres_lastfm
        suggested_genres_all_unique = sorted(list(set(suggested_genres_all)), key=suggested_genres_all.index)

        colored_print(C_AI, f"{C_BOLD}AI Suggested genres:{C_RESET}")
        if suggested_genres_ai or suggested_genres_lastfm:
            max_len = max(len(suggested_genres_ai), len(suggested_genres_lastfm))
            ai_header = f"{C_AI}AI Genres{C_RESET}"
            lastfm_header = f"{C_LASTFM}Last.fm Genres{C_RESET}"
            print(f"| {ai_header:<20} | {lastfm_header:<20} |")
            print(f"|{'-'*22}|{'-'*22}|")

            for i in range(max_len):
                ai_genre = suggested_genres_ai[i] if i < len(suggested_genres_ai) else ""
                lastfm_genre = suggested_genres_lastfm[i] if i < len(suggested_genres_lastfm) else ""
                print(f"| {C_AI}{ai_genre:<20}{C_RESET} | {C_LASTFM}{lastfm_genre:<20}{C_RESET} |")
        else:
            colored_print(C_AI, "No genres suggested from AI or Last.fm.")

        while True:
            prompt_genres_list = suggested_genres_all_unique if suggested_genres_all_unique else ['no suggestions']
            prompt_genres_colored = f"{C_GENRE_SUGGESTION}{', '.join(prompt_genres_list)}{C_RESET}"
            prompt_text = f"{C_PROMPT}Enter genre(s) for {C_BOLD}'{filename}'{C_RESET}{C_PROMPT} (suggestions: {prompt_genres_colored}, or type comma-separated genres, or '{C_BOLD}skip{C_RESET}{C_PROMPT}' to skip file): {C_RESET}"

            if not auto_apply_tags:
                genre_input: str = input(prompt_text).strip()
                if genre_input.lower() == 'skip':
                    logger.info(f"Skipping file: {file_path}")
                    return False
                if genre_input:
                    if "," in genre_input:
                        genres = [genre.strip() for genre in genre_input.split(",")]
                    else:
                        genres = genre_input # Allow single genre without comma to be treated as string
                    break
                else:
                    print("Genre cannot be empty. Please enter a genre or type 'skip'.")
            else: # Autoaply if option is ON
                if suggested_genres_all_unique: # Apply AI/LastFM suggested genres if auto-apply is on and suggestions exist
                    genres = suggested_genres_all_unique
                    break
                else: # If auto-apply is on but no suggestions, skip the file
                    logger.info(f"Auto-apply tags is ON, but no genres suggested. Skipping file: {file_path}")
                    return False # Indicate skipped, but not an error

        logger.info(f"Processing file: {file_path}, setting genre(s) to: {genres}")
        return self.set_genre_tag(file_path, genres)

    def find_music_files(self, root_dir: str) -> List[str]:
        """
        Recursively finds music files of supported formats within a root directory.

        Args:
            root_dir (str): The root directory to search in.

        Returns:
            List[str]: A list of file paths for supported music files.
        """
        music_files: list[str] = []
        extensions = list(self.SUPPORTED_FORMATS.keys())

        for root, _, files in os.walk(root_dir):
            for file in files:
                if any(file.lower().endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    music_files.append(file_path)
        return music_files


    def process_directory(self, root_dir: str, auto_apply_tags: bool, musicnn_settings: 'musicnn_tagger.config.MusicnnSettings', lastfm_settings: 'lastfm_tagger.config.Settings') -> None:
        """
        Recursively finds music files and returns paths.  The actual processing
        is now handled by the main process and worker processes.
        """
        music_files = self.find_music_files(root_dir)
        print(f"🔎 Found {len(music_files)} supported music files")  # No colors here


    def get_music_files_count(self, root_dir: str):
        music_files = self.find_music_files(root_dir)
        print(f"🔎 Found {C_PROMPT}{len(music_files)}{C_RESET}{C_BOLD} supported{C_RESET} music files")

if __name__ == "__main__":
    music_tagger = MusicTagger()
    music_dir = r"music_root_folder_path"  # Replace with your music directory
    # Example settings - in real usage, these should come from your settings management
    from main import MusicnnSettings, LastFMSettings  # Import from main temporarily for standalone test - in real app, these will be passed from main
    musicnn_settings = MusicnnSettings()
    lastfm_settings = LastFMSettings()
    music_tagger.process_directory(music_dir, False, musicnn_settings, lastfm_settings)