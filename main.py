# path main.py
from __future__ import annotations
import pathlib
from dataclasses import dataclass, field
from typing import Callable, Optional, List, Any
import os

from numpy.f2py.cfuncs import callbacks

# Set TF_CPP_MIN_LOG_LEVEL environment variable to suppress TensorFlow messages
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # remove it for debugging
import platform
import logging
from enum import Enum, auto
import keyboard
from queue import Queue
from dotenv import load_dotenv, set_key

# Import MusicnnSettings from musicnn_tagger/config.py
from musicnn_tagger.config import MusicnnSettings
# Import LastFMSettings from lastfm_tagger.config
from lastfm_tagger.config import LastFMSettings

import multiprocessing  # Import for multiprocessing
import time
import sys  # For flushing output
import queue  # Import the queue module
# Import worker_process function
from music_tagger import worker_process


# Replace BaseSettings with a regular class
class AppSettings:
    """
    Global application settings container, loaded from and saved to .env file using dotenv.
    """
    # Removed model_config

    auto_apply_tags: bool
    default_music_dir: Optional[str]

    def __init__(self):
        # Load environment variables from .env file in the parent directory
        self.dotenv_path = pathlib.Path(__file__).parent / '.env'
        load_dotenv(dotenv_path=self.dotenv_path, encoding='utf-8', verbose=False)  # Load .env

        # Initialize settings from environment variables or defaults
        self.auto_apply_tags = os.getenv("AUTO_APPLY_TAGS", 'False').lower() == 'true'  # Default to False if not set
        self.default_music_dir = os.getenv("DEFAULT_MUSIC_DIR")  # Can be None if not set

    def save_settings(self):
        """Save current settings to .env file."""
        set_key(self.dotenv_path, "AUTO_APPLY_TAGS", str(self.auto_apply_tags).upper())  # Save auto_apply_tags
        if self.default_music_dir:  # Only save if not None
            set_key(self.dotenv_path, "DEFAULT_MUSIC_DIR", self.default_music_dir)
        else:  # Remove from .env if None
            set_key(self.dotenv_path, "DEFAULT_MUSIC_DIR", '')  # Empty string will be read as None next time
        logger.debug("AppSettings saved to .env")


# Configure logging with ISO timestamp
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class MenuItemType(Enum):
    """Enumeration defining types of menu items."""
    SUBMENU = auto()
    TOGGLE = auto()
    VALUE = auto()
    ACTION = auto()


@dataclass
class MenuItem:
    """Represents a menu item with navigation and interaction properties."""
    text: str
    type: MenuItemType
    value: Any = None
    children: List['MenuItem'] = field(default_factory=list)
    parent: Optional['MenuItem'] = None
    callback: Optional[Callable] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    step: Optional[float] = None


class InteractiveMenu:
    """
    Interactive menu system with arrow key navigation and real-time updates.

    Implements a hierarchical menu structure with keyboard navigation
    and dynamic value updates.
    """

    def __init__(self, settings: AppSettings, musicnn_settings: MusicnnSettings, lastfm_settings: LastFMSettings,
                 music_tagger: 'MusicTagger'):  # Use AppSettings, MusicnnSettings, and LastFMSettings
        """
        Initialize the interactive menu system.

        Args:
            settings: Application settings instance (AppSettings)
            musicnn_settings: Musicnn settings instance (MusicnnSettings)
            lastfm_settings: LastFM settings instance (LastFMSettings)
            music_tagger: MusicTagger instance to process directories
        """
        self.settings = settings
        self.musicnn_settings = musicnn_settings  # Store Musicnn settings
        self.lastfm_settings = lastfm_settings  # Store LastFM settings
        self.root_directory = ''
        self.music_tagger = music_tagger  # Store MusicTagger instance
        self.current_menu: List[MenuItem] = []
        self.selected_index = 1
        self.event_queue = Queue()
        self._setup_root_menu()

        # Multiprocessing Queues and Processes
        self.input_queue = multiprocessing.Queue()
        self.output_queue = multiprocessing.Queue()
        self.processes = []  # List to hold worker processes

    def _setup_root_menu(self) -> None:
        """Initialize the root menu structure with all submenus and items."""
        root_items = [
            MenuItem(
                text="-- Music Tagger Menu --",  # Placeholder "header" item
                type=MenuItemType.ACTION,  # Use ACTION type
                callback=None  # No action when selected
            ),
            MenuItem(
                text="Select Music Root Folder",
                type=MenuItemType.ACTION,
                callback=self._select_folder
            ),
            MenuItem(
                text="Process Directory",  # New menu item to trigger directory processing
                type=MenuItemType.ACTION,
                callback=self._process_music_directory
            ),
            MenuItem(
                text="Settings",
                type=MenuItemType.SUBMENU,
                children=[],  # Children will be populated next
            ),
            MenuItem(
                text="Exit",
                type=MenuItemType.ACTION,
                callback=self._exit_program
            )
        ]

        settings_submenu = root_items[3]  # Get the 'Settings' submenu item
        settings_submenu.children = [
            MenuItem(
                text="Processing Engine",
                type=MenuItemType.SUBMENU,
                children=[],  # Children will be populated next
                parent=settings_submenu  # Set parent for back navigation
            ),
            MenuItem(
                text="Auto-apply Tags",
                type=MenuItemType.TOGGLE,
                value=lambda: self.settings.auto_apply_tags,
                callback=self._toggle_auto_apply,
                parent=settings_submenu  # Set parent for back navigation
            )
        ]

        processing_engine_submenu = settings_submenu.children[0]  # Get 'Processing Engine' submenu
        processing_engine_submenu.children = [
            MenuItem(
                text="Musicnn AI Tagger",
                type=MenuItemType.SUBMENU,
                children=[],  # Children will be populated next
                parent=settings_submenu  # Set parent for back navigation
            ),
            MenuItem(
                text="LastFM Grabber",
                type=MenuItemType.SUBMENU,
                children=[],  # Children will be populated next
                parent=settings_submenu  # Set parent for back navigation
            )
        ]
        musiccn_submenu = processing_engine_submenu.children[0]  # Get 'Musicnn AI Tagger' submenu
        musiccn_submenu.children = [
            MenuItem(
                text="Enable/Disable",
                type=MenuItemType.TOGGLE,
                value=lambda: self.musicnn_settings.enabled,  # Use musicnn_settings
                callback=self._toggle_musiccn_enabled,  # Updated callback name
                parent=processing_engine_submenu  # Set parent for back navigation
            ),
            MenuItem(
                text="Models Count",
                type=MenuItemType.VALUE,
                value=lambda: self.musicnn_settings.model_count,  # Use musicnn_settings
                min_value=1,
                max_value=5,
                step=1,
                callback=self._set_musiccn_model_count,
                parent=processing_engine_submenu  # Set parent for back navigation
            ),
            MenuItem(
                text="Threshold Weight",
                type=MenuItemType.VALUE,
                value=lambda: self.musicnn_settings.threshold_weight,  # Use musicnn_settings
                min_value=0.0,
                max_value=1.0,
                step=0.1,
                callback=self._set_musiccn_threshold_weight,  # Updated callback name
                parent=processing_engine_submenu  # Set parent for back navigation
            ),
            MenuItem(  # New menu item for genres count
                text="Genres Count",
                type=MenuItemType.VALUE,
                value=lambda: self.musicnn_settings.genres_count,  # Use musicnn_settings
                min_value=1,
                max_value=10,  # Example max genres count
                step=1,
                callback=self._set_musiccn_genres_count,  # New callback
                parent=processing_engine_submenu
            ),
        ]
        lastfm_submenu = processing_engine_submenu.children[1]  # Get 'LastFM Grabber' submenu
        lastfm_submenu.children = [
            MenuItem(
                text="Enable/Disable",
                type=MenuItemType.TOGGLE,
                value=lambda: self.lastfm_settings.enabled,  # Use lastfm_settings
                callback=self._toggle_lastfm_enabled,  # Updated callback name
                parent=processing_engine_submenu  # Set parent for back navigation
            ),
            MenuItem(
                text="Threshold Weight",
                type=MenuItemType.VALUE,
                value=lambda: self.lastfm_settings.threshold_weight,  # Use lastfm_settings
                min_value=0.0,
                max_value=1.0,
                step=0.1,
                callback=self._set_lastfm_threshold_weight,  # Updated callback name
                parent=processing_engine_submenu  # Set parent for back navigation
            )
        ]

        self.root_menu = root_items  # Assign the constructed root menu
        self.current_menu = self.root_menu

    def _clear_screen(self) -> None:
        """Clear the console screen in a cross-platform manner."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def _draw_menu(self) -> None:
        """Render the current menu state to the console."""
        self._clear_screen()
        if self.settings.default_music_dir:
            print(f"Default music dir: {self.settings.default_music_dir}")
            from music_tagger import MusicTagger
            MusicTagger().get_music_files_count(self.settings.default_music_dir)
            if self.settings.auto_apply_tags:
                print(f"Auto apply tags setting state is ON [u can change it on settings]")
            print("================\n")

        for i, item in enumerate(self.current_menu):
            if item.text == "-- Music Tagger Menu --":  # Check for the placeholder item
                prefix = "  "  # Always use space prefix for placeholder
            else:
                prefix = "→ " if i == self.selected_index else "  " # Standard prefix logic

            if item.type == MenuItemType.TOGGLE:
                value = item.value()
                status = "ON" if value else "OFF"
                print(f"{prefix}{item.text} [{status}]")
            elif item.type == MenuItemType.VALUE:
                value = item.value()
                print(f"{prefix}{item.text}: {value}")
            else:
                print(f"{prefix}{item.text}")

        print(
            "\nUse ↑↓ to navigate, ← → to modify values\nEnter to select, <—Backspace to go back to parent menu\nEsc to go root menu")  # Updated navigation instructions
    def _handle_input(self) -> bool:
        """
        Handle keyboard input events.

        Returns:
            bool: False if the menu should exit, True otherwise
        """
        while True:
            event = keyboard.read_event(suppress=True)
            if event.event_type == keyboard.KEY_UP:  # Changed to KEY_UP for more reliable key press detection
                if event.name == 'up':
                    original_index = self.selected_index
                    self.selected_index = (self.selected_index - 1) % len(self.current_menu)
                    if self.current_menu[self.selected_index].text == "-- Music Tagger Menu --": # Skip placeholder
                        self.selected_index = (self.selected_index - 1) % len(self.current_menu)
                        if self.selected_index == original_index: # Handle case where only item is placeholder or menu is empty
                            self.selected_index = 1 # Reset to top or handle as needed

                    break
                elif event.name == 'down':
                    original_index = self.selected_index
                    self.selected_index = (self.selected_index + 1) % len(self.current_menu)
                    if self.current_menu[self.selected_index].text == "-- Music Tagger Menu --": # Skip placeholder
                        self.selected_index = (self.selected_index + 1) % len(self.current_menu)
                        if self.selected_index == original_index: # Handle case where only item is placeholder or menu is empty
                            self.selected_index = 1 # Reset to top or handle as needed
                    break
                elif event.name == 'enter':
                    return self._handle_selection()
                elif event.name == 'right':  # Use right arrow for value change
                    return self._handle_value_change_increase()
                elif event.name == 'left':  # Use left arrow for value change
                    return self._handle_value_change_decrease()
                elif event.name == 'esc':
                    return self._handle_escape()
                elif event.name == 'backspace':  # Use backspace for back navigation
                    return self._handle_back()
        return True

    def _handle_selection(self) -> bool:
        """
        Handle menu item selection.
asd
        Returns:
            bool: False if the menu should exit, True otherwise
        """
        item = self.current_menu[self.selected_index]

        if item.type == MenuItemType.SUBMENU:
            self.current_menu = item.children
            self.selected_index = 0
        elif item.type == MenuItemType.ACTION:
            if item.callback:
                return item.callback()
        elif item.type == MenuItemType.TOGGLE:
            if item.callback:
                item.callback()
                if item.text == "Auto-apply Tags":  # Specific handling for "Auto-apply Tags"
                    self.settings.save_settings()  # Save AppSettings on toggle

        return True

    def _handle_escape(self) -> bool:
        """
        Handle navigation back to root menu.

        Returns:
            bool: True to continue menu operation
        """
        if self.current_menu != self.root_menu:  # Go back to root
            self.current_menu = self.root_menu
            self.selected_index = 1
        return True

    def _handle_back(self) -> bool:
        """
        Handle navigation back to parent menu.

        Returns:
            bool: True to continue menu operation
        """
        if not self.current_menu:
            logger.debug("_handle_back: current_menu is empty, returning True")
            return True

        if self.current_menu == self.root_menu:
            logger.info("_handle_back: Current menu is root menu, returning True")
            return True
        logger.info(self.current_menu)
        # Check if the current menu has a parent
        if self.current_menu and self.current_menu[0].parent:
            parent_menu_item = self.current_menu[0].parent

            if parent_menu_item.text == 'Settings' and self.current_menu[0].text == 'Processing Engine':
                if self.current_menu != self.root_menu:  # Go back to root
                    self.current_menu = self.root_menu
                    self.selected_index = 1
                return True

            self.current_menu = parent_menu_item.children
        else:
            logger.info("_handle_back: No parent menu found or current_menu is empty or has no parent, staying in current menu.")

        return True

    def _handle_value_change_increase(self) -> bool:
        """
        Handle value modification for numeric menu items - increase value.

        Returns:
            bool: True to continue menu operation
        """
        item = self.current_menu[self.selected_index]
        if item.type == MenuItemType.VALUE and item.callback:
            current_value = item.value()
            step = item.step or 1

            if keyboard.is_pressed('shift'):
                step *= 10

            new_value = current_value + step
            if item.max_value is not None:
                new_value = min(new_value, item.max_value)

            if isinstance(new_value, float):
                new_value = round(new_value, 1)
            item.callback(new_value)
            if item.text == "Models Count":
                self.musicnn_settings.save_settings()  # Save MusicnnSettings
            elif item.text == "Threshold Weight" and item.parent.text == "Musicnn AI Tagger":
                self.musicnn_settings.save_settings()  # Save MusicnnSettings
            elif item.text == "Genres Count":
                self.musicnn_settings.save_settings()  # Save MusicnnSettings
            elif item.text == "Threshold Weight" and item.parent.text == "LastFM Grabber":
                self.lastfm_settings.save_settings()  # Save LastFMSettings

        return True

    def _handle_value_change_decrease(self) -> bool:
        """
        Handle value modification for numeric menu items - decrease value.

        Returns:
            bool: True to continue menu operation
        """
        item = self.current_menu[self.selected_index]
        if item.type == MenuItemType.VALUE and item.callback:
            current_value = item.value()
            step = item.step or 1

            if keyboard.is_pressed('shift'):
                step *= 10

            new_value = max(0.0, current_value - step)  # Use max to ensure value >= 0, and 0.0 to handle float correctly.

            if item.min_value is not None:  # Apply min_value constraint if present
                new_value = max(new_value, item.min_value)

            if item.max_value is not None:
                new_value = min(new_value, item.max_value)

            if isinstance(new_value, float):
                new_value = round(new_value, 1)
            item.callback(new_value)
            if item.text == "Models Count":
                self.musicnn_settings.save_settings()  # Save MusicnnSettings
            elif item.text == "Threshold Weight" and item.parent.text == "Musicnn AI Tagger":
                self.musicnn_settings.save_settings()  # Save MusicnnSettings
            elif item.text == "Genres Count":
                self.musicnn_settings.save_settings()  # Save MusicnnSettings
            elif item.text == "Threshold Weight" and item.parent.text == "LastFM Grabber":
                self.lastfm_settings.save_settings()  # Save LastFMSettings
        return True

    def _start_workers(self, musicnn_settings: MusicnnSettings, num_workers: int = 3):
        """Starts the worker processes."""
        for _ in range(num_workers):
            p = multiprocessing.Process(target=worker_process, args=(self.input_queue, self.output_queue, musicnn_settings))
            p.start()
            self.processes.append(p)

    def _stop_workers(self):
        """Signals worker processes to terminate and waits for them."""
        for _ in self.processes:
            self.input_queue.put(None)  # Send termination signal
        for p in self.processes:
            p.join()  # Wait for processes to finish
        self.processes = []

    def _process_music_directory(self) -> bool:
        """
        Handle the music directory processing action.

        Gets the music directory from settings or user input, and then
        calls the music tagger to process the directory.  This now manages
        the multiprocessing components.

        Returns:
            bool: True to continue menu operation
        """
        music_directory = self.settings.default_music_dir
        auto_apply_tags = self.settings.auto_apply_tags
        musicnn_settings = self.musicnn_settings  # Use stored musicnn_settings
        lastfm_settings = self.lastfm_settings  # Use stored lastfm_settings

        if not music_directory:
            logger.info("No default music directory set. Please select one first.")
            self._select_folder()  # Force select folder if not set
            music_directory = self.settings.default_music_dir  # Get again after selection
            if not music_directory:  # User might still cancel
                logger.info("Music directory selection cancelled. Processing aborted.")
                return True  # Back to menu

        if not os.path.isdir(music_directory):
            logger.error(f"Invalid music directory: {music_directory}")
            self.settings.default_music_dir = None  # Reset invalid directory
            self.settings.save_settings()  # Save settings to remove invalid path

            logger.info("Default music directory setting has been reset.")
            return True  # Back to menu

        safe_music_directory_for_logging = ''.join(c if ord(c) < 128 else '?' for c in music_directory)
        logger.info(f"Starting music genre tagging process for directory: {safe_music_directory_for_logging} with AI genre suggestions.")
        print(f"\nStarting music genre tagging process for directory: {music_directory}...")
        print("AI genre analysis is running in the background for all music files. This may take a while.")  # Informative message

        music_files = self.music_tagger.find_music_files(music_directory)
        print(f"🔎 Found {len(music_files)} supported music files in {music_directory}")

        # Start worker processes
        self._start_workers(self.musicnn_settings)

        # Populate the input queue
        for file_path in music_files:
            self.input_queue.put(file_path)

        processed_count = 0
        while processed_count < len(music_files):
            # Check for results from workers, without blocking
            while not self.output_queue.empty():
                try:
                    file_path, ai_genres_dict = self.output_queue.get_nowait()
                    self.music_tagger.ai_genre_suggestions_cache[file_path] = ai_genres_dict
                    logger.debug(f"Cached AI results for: {file_path}")
                except queue.Empty:
                    break # No more messages in the queue at the moment.

            current_file = music_files[processed_count]

            if current_file in self.music_tagger.ai_genre_suggestions_cache:
                # Process the file (cached results are available!)
                self.music_tagger.process_music_file(current_file, self.settings.auto_apply_tags, self.musicnn_settings, self.lastfm_settings)
                processed_count += 1
            else:
                # Removed loading animation, wait directly for result.
                time.sleep(0.2)  # Brief pause before checking again

        # Stop worker processes
        self._stop_workers()

        print(f"\nMusic genre tagging process completed for directory: {music_directory}")
        logger.info(f"Music genre tagging process completed for directory: {music_directory}")

        input("\nPress Enter to continue...")  # Pause to show completion message
        self.selected_index = 0  # Reset selected index to the first item
        return True  # Return to menu after processing

    def _select_folder(self) -> bool:
        """
        Handle music folder selection with platform-specific dialog support.

        Implements cross-platform folder selection using GUI dialog on Windows
        and terminal input on other platforms. Updates application settings
        with selected directory and saves to .env.

        Returns:
            bool: True if folder selection successful or cancelled, False on critical error
        """
        logger.debug("Entering _select_folder")  # Debug log at start
        directory = None  # Initialize directory to None
        try:  # Add try-except block to catch potential Tkinter errors
            if platform.system() == "Windows":
                logger.debug("Platform is Windows, attempting GUI folder selection")
                try:
                    import tkinter as tk
                    from tkinter import filedialog

                    root = tk.Tk()
                    root.withdraw()  # Hide the main window
                    root.attributes('-topmost', True)  # Ensure dialog is on top

                    initial_dir = (self.settings.default_music_dir
                                   or os.path.expanduser("~/Music")
                                   or os.path.expanduser("~"))

                    logger.debug(f"Initial directory for dialog: {initial_dir}")
                    directory = filedialog.askdirectory(
                        title="Select Music Directory",
                        initialdir=initial_dir,
                        mustexist=True
                    )
                    logger.debug(f"Folder dialog returned: {directory}")

                    root.destroy()
                    logger.debug("Tkinter root destroyed")

                    if not directory:  # User cancelled selection
                        logger.info("Folder selection cancelled by user")
                        return True

                except ImportError:
                    logger.warning("GUI dialog not available, falling back to console input")
                    directory = self._get_console_input()
                except Exception as e:
                    logger.error(f"Error in GUI folder selection: {e}")
                    directory = self._get_console_input()
            else:
                logger.debug("Platform is not Windows, using console input for folder selection")
                directory = self._get_console_input()

            if not directory:
                logger.info("No directory selected")
                return True

            if not os.path.isdir(directory):
                logger.error(f"Invalid directory path: {directory}")
                return True

            # Update settings with new directory and save
            self.settings.default_music_dir = directory
            self.settings.save_settings()  # Save AppSettings to .env

            logger.info(f"Selected music directory: {directory}")
            logger.debug("Exiting _select_folder successfully")  # Debug log at end
            return True

        except Exception as e:  # Catch any error during folder selection
            logger.error(f"Critical error in folder selection: {e}")
            logger.debug("Exiting _select_folder with error")  # Debug log at error exit
            return True

    def _get_console_input(self) -> Optional[str]:
        """
        Get directory path through console input.

        Implements a user-friendly console input mechanism with proper
        error handling and input validation.

        Returns:
            Optional[str]: Selected directory path or None if cancelled
        """
        logger.debug("Entering _get_console_input")  # Debug log at start
        try:
            print("\nEnter the path to your music directory")
            print("(Press Enter with empty input to cancel)")

            directory = input("Path: ").strip()
            logger.debug(f"Console input received: '{directory}'")

            if not directory:
                logger.info("Directory selection cancelled")
                return None

            # Expand user home directory if present
            directory = os.path.expanduser(directory)

            # Convert to absolute path
            directory = os.path.abspath(directory)
            logger.debug(f"Returning directory path: '{directory}'")
            return directory

        except KeyboardInterrupt:
            logger.info("\nDirectory selection cancelled by user")
            logger.debug("Exiting _get_console_input with KeyboardInterrupt")
            return None
        except Exception as e:
            logger.error(f"Error during console input: {e}")
            logger.debug("Exiting _get_console_input with error")
            return None

    def run(self) -> None:
        """Run the interactive menu system."""
        running = True
        while running:
            self._draw_menu()
            running = self._handle_input()

    # Callback methods - Updated to use separate settings classes
    def _toggle_musiccn_enabled(self) -> None:
        self.musicnn_settings.enabled = not self.musicnn_settings.enabled  # Use musicnn_settings
        self.musicnn_settings.save_settings()  # Save Musicnn settings

    def _set_musiccn_model_count(self, value: int) -> None:
        self.musicnn_settings.model_count = int(value)  # Use musicnn_settings
        self.musicnn_settings.save_settings()  # Save Musicnn settings

    def _set_musiccn_threshold_weight(self, value: float) -> None:
        self.musicnn_settings.threshold_weight = value  # Use musicnn_settings
        self.musicnn_settings.save_settings()  # Save Musicnn settings

    def _set_musiccn_genres_count(self, value: int) -> None:  # New callback for genres count
        self.musicnn_settings.genres_count = int(value)  # Use musicnn_settings
        self.musicnn_settings.save_settings()  # Save Musicnn settingss

    def _toggle_lastfm_enabled(self) -> None:
        self.lastfm_settings.enabled = not self.lastfm_settings.enabled  # Use lastfm_settings
        self.lastfm_settings.save_settings()  # Save LastFM settings

    def _set_lastfm_threshold_weight(self, value: float) -> None:
        self.lastfm_settings.threshold_weight = value  # Use lastfm_settings
        self.lastfm_settings.save_settings()  # Save LastFM settings

    def _toggle_auto_apply(self) -> None:
        self.settings.auto_apply_tags = not self.settings.auto_apply_tags
        self.settings.save_settings()  # Save AppSettings

    def _exit_program(self) -> bool:
        """Exit the program with proper cleanup."""
        logger.info("Exiting program")
        self._stop_workers() # Terminate worker processes on exit
        return False

# Update the MusicTaggerMenu class to use the new interactive menu
class MusicTaggerMenu:
    def __init__(self, music_tagger: 'MusicTagger'):
        self.music_tagger = music_tagger
        self.app_settings = AppSettings()  # Load AppSettings from .env
        self.musicnn_settings = MusicnnSettings()  # Load MusicnnSettings from .env
        self.lastfm_settings = LastFMSettings()  # Load LastFMSettings from .env
        self.menu = InteractiveMenu(self.app_settings, self.musicnn_settings, self.lastfm_settings,
                                    self.music_tagger)  # Pass all settings instances to menu

    def display_menu(self) -> None:
        """Start the interactive menu system."""
        self.menu.run()

if __name__ == "__main__":
    from music_tagger import MusicTagger
    menu = MusicTaggerMenu(MusicTagger())
    menu.display_menu()