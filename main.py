#!filepath: music_tagger.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, Optional, List, Any
import os
# Set TF_CPP_MIN_LOG_LEVEL environment variable to suppress TensorFlow messages
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # remove it for debugging
import platform
import logging
from enum import Enum, auto
import json
from pathlib import Path
import keyboard
import time
from dataclasses import asdict
import sys
import threading
from queue import Queue


logger = logging.getLogger(__name__)
# Create a formatter to define the log format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# Create a file handler to write logs to a file
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.DEBUG) # Set log level to DEBUG for detailed logs
file_handler.setFormatter(formatter)
logger.addHandler(file_handler) # Add file handler to logger

@dataclass
class MusiccnSettings:
    """
    Configuration settings for the Musiccn AI tagger engine.

    Attributes:
        enabled (bool): Toggle for Musiccn AI tagger functionality
        model_count (int): Number of AI models to use (1-5)
        threshold_weight (float): Minimum confidence threshold for genre predictions
    """
    enabled: bool = True
    model_count: int = 1
    threshold_weight: float = 0.5

    def validate(self) -> None:
        """
        Validate settings constraints.

        Raises:
            ValueError: If any settings are outside valid ranges
        """
        if not isinstance(self.model_count, int) or not 1 <= self.model_count <= 5:
            raise ValueError("Model count must be an integer between 1 and 5")
        if not 0 <= self.threshold_weight <= 1:
            raise ValueError("Threshold weight must be between 0 and 1")

@dataclass
class LastFMSettings:
    """
    Configuration settings for the LastFM data grabber.

    Attributes:
        enabled (bool): Toggle for LastFM integration
        threshold_weight (float): Minimum confidence threshold for genre data
    """
    enabled: bool = True
    threshold_weight: float = 0.5

    def validate(self) -> None:
        """
        Validate settings constraints.

        Raises:
            ValueError: If threshold weight is outside valid range
        """
        if not 0 <= self.threshold_weight <= 1:
            raise ValueError("Threshold weight must be between 0 and 1")

@dataclass
class ProcessingEngineSettings:
    """
    Aggregate settings for all processing engines.

    Attributes:
        musiccn (MusiccnSettings): Musiccn AI tagger configuration
        lastfm (LastFMSettings): LastFM grabber configuration
    """
    musiccn: MusiccnSettings = field(default_factory=MusiccnSettings)
    lastfm: LastFMSettings = field(default_factory=LastFMSettings)

    def validate(self) -> None:
        """Validate all processing engine settings."""
        self.musiccn.validate()
        self.lastfm.validate()

@dataclass
class Settings:
    """
    Global application settings container.

    Attributes:
        processing_engine (ProcessingEngineSettings): Processing engine configurations
        auto_apply_tags (bool): Automatic tag application toggle
        default_music_dir (Optional[str]): Default directory for music files
    """
    processing_engine: ProcessingEngineSettings = field(default_factory=ProcessingEngineSettings)
    auto_apply_tags: bool = False
    default_music_dir: Optional[str] = None

    @classmethod
    def load(cls, file_path: str = "settings.json") -> Settings:
        """
        Load settings from JSON file with proper type conversion.

        Args:
            file_path (str): Path to settings JSON file

        Returns:
            Settings: Instantiated settings object with loaded values
        """
        try:
            if Path(file_path).exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    # Reconstruct nested settings objects
                    musiccn = MusiccnSettings(**data.get('processing_engine', {}).get('musiccn', {}))
                    lastfm = LastFMSettings(**data.get('processing_engine', {}).get('lastfm', {}))

                    processing_engine = ProcessingEngineSettings(
                        musiccn=musiccn,
                        lastfm=lastfm
                    )

                    return cls(
                        processing_engine=processing_engine,
                        auto_apply_tags=data.get('auto_apply_tags', False),
                        default_music_dir=data.get('default_music_dir')
                    )
        except Exception as e:
            logger.error(f"Error loading settings from {file_path}: {e}")
            logger.info("Using default settings")

        return cls()

    def save(self, file_path: str = "settings.json") -> None:
        """
        Save settings to JSON file with validation.

        Args:
            file_path (str): Path to settings JSON file

        Raises:
            ValueError: If settings validation fails
        """
        try:
            # Validate all settings before saving
            self.processing_engine.validate()

            # Prepare settings dictionary
            settings_dict = {
                'processing_engine': {
                    'musiccn': {
                        'enabled': self.processing_engine.musiccn.enabled,
                        'model_count': self.processing_engine.musiccn.model_count,
                        'threshold_weight': self.processing_engine.musiccn.threshold_weight
                    },
                    'lastfm': {
                        'enabled': self.processing_engine.lastfm.enabled,
                        'threshold_weight': self.processing_engine.lastfm.threshold_weight
                    }
                },
                'auto_apply_tags': self.auto_apply_tags,
                'default_music_dir': self.default_music_dir
            }

            # Save with proper formatting
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(settings_dict, f, indent=4, ensure_ascii=False)

            logger.debug(f"Settings successfully saved to {file_path}")

        except Exception as e:
            logger.error(f"Error saving settings to {file_path}: {e}")
            raise

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

    def __init__(self, settings: Settings, music_tagger: 'MusicTagger'):
        """
        Initialize the interactive menu system.

        Args:
            settings: Application settings instance
            music_tagger: MusicTagger instance to process directories
        """
        self.settings = settings
        self.root_directory = ''
        self.music_tagger = music_tagger # Store MusicTagger instance
        self.current_menu: List[MenuItem] = []
        self.selected_index = 0
        self.event_queue = Queue()
        self._setup_root_menu()

    def _setup_root_menu(self) -> None:
        """Initialize the root menu structure with all submenus and items."""
        root_items = [
            MenuItem(
                text="Select Music Root Folder",
                type=MenuItemType.ACTION,
                callback=self._select_folder
            ),
            MenuItem(
                text="Process Directory", # New menu item to trigger directory processing
                type=MenuItemType.ACTION,
                callback=self._process_music_directory
            ),
            MenuItem(
                text="Settings",
                type=MenuItemType.SUBMENU,
                children=[], # Children will be populated next
            ),
            MenuItem(
                text="Exit",
                type=MenuItemType.ACTION,
                callback=self._exit_program
            )
        ]

        settings_submenu = root_items[2] # Get the 'Settings' submenu item
        settings_submenu.children = [
            MenuItem(
                text="Processing Engine",
                type=MenuItemType.SUBMENU,
                children=[], # Children will be populated next
                parent=settings_submenu # Set parent for back navigation
            ),
            MenuItem(
                text="Auto-apply Tags",
                type=MenuItemType.TOGGLE,
                value=lambda: self.settings.auto_apply_tags,
                callback=self._toggle_auto_apply,
                parent=settings_submenu # Set parent for back navigation
            )
        ]

        processing_engine_submenu = settings_submenu.children[0] # Get 'Processing Engine' submenu
        processing_engine_submenu.children = [
            MenuItem(
                text="Musiccn AI Tagger",
                type=MenuItemType.SUBMENU,
                children=[], # Children will be populated next
                parent=settings_submenu # Set parent for back navigation
            ),
            MenuItem(
                text="LastFM Grabber",
                type=MenuItemType.SUBMENU,
                children=[], # Children will be populated next
                parent=settings_submenu # Set parent for back navigation
            )
        ]
        musiccn_submenu = processing_engine_submenu.children[0] # Get 'Musiccn AI Tagger' submenu
        musiccn_submenu.children = [
            MenuItem(
                text="Enable/Disable",
                type=MenuItemType.TOGGLE,
                value=lambda: self.settings.processing_engine.musiccn.enabled,
                callback=self._toggle_musiccn,
                parent=processing_engine_submenu # Set parent for back navigation
            ),
            MenuItem(
                text="Models Count",
                type=MenuItemType.VALUE,
                value=lambda: self.settings.processing_engine.musiccn.model_count,
                min_value=1,
                max_value=5,
                step=1,
                callback=self._set_musiccn_model_count,
                parent=processing_engine_submenu # Set parent for back navigation
            ),
            MenuItem(
                text="Threshold Weight",
                type=MenuItemType.VALUE,
                value=lambda: self.settings.processing_engine.musiccn.threshold_weight,
                min_value=0.0,
                max_value=1.0,
                step=0.1,
                callback=self._set_musiccn_threshold,
                parent=processing_engine_submenu # Set parent for back navigation
            )
        ]
        lastfm_submenu = processing_engine_submenu.children[1] # Get 'LastFM Grabber' submenu
        lastfm_submenu.children = [
            MenuItem(
                text="Enable/Disable",
                type=MenuItemType.TOGGLE,
                value=lambda: self.settings.processing_engine.lastfm.enabled,
                callback=self._toggle_lastfm,
                parent=processing_engine_submenu # Set parent for back navigation
            ),
            MenuItem(
                text="Threshold Weight",
                type=MenuItemType.VALUE,
                value=lambda: self.settings.processing_engine.lastfm.threshold_weight,
                min_value=0.0,
                max_value=1.0,
                step=0.1,
                callback=self._set_lastfm_threshold,
                parent=processing_engine_submenu # Set parent for back navigation
            )
        ]

        self.root_menu = root_items # Assign the constructed root menu
        self.current_menu = self.root_menu

    def _clear_screen(self) -> None:
        """Clear the console screen in a cross-platform manner."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def _draw_menu(self) -> None:
        """Render the current menu state to the console."""
        self._clear_screen()
        print("\nMusic Tagger Menu")
        print("================")

        if self.settings.default_music_dir:
            print(f"Default music dir: {self.settings.default_music_dir}")
            from music_tagger import MusicTagger
            MusicTagger().get_music_files_count(self.settings.default_music_dir)
            if self.settings.auto_apply_tags:
                print(f"Auto apply tags setting state is ON [u can change it on settings]")
            print("================\n\n")

        for i, item in enumerate(self.current_menu):
            prefix = "→ " if i == self.selected_index else "  "

            if item.type == MenuItemType.TOGGLE:
                value = item.value()
                status = "ON" if value else "OFF"
                print(f"{prefix}{item.text} [{status}]")
            elif item.type == MenuItemType.VALUE:
                value = item.value()
                print(f"{prefix}{item.text}: {value}")
            else:
                print(f"{prefix}{item.text}")

        print("\nUse ↑↓ to navigate, ← → to modify values\nEnter to select, <—Backspace to go back to parent menu\nEsc to go root menu") # Updated navigation instructions

    def _handle_input(self) -> bool:
        """
        Handle keyboard input events.

        Returns:
            bool: False if the menu should exit, True otherwise
        """
        while True:
            event = keyboard.read_event(suppress=True)
            if event.event_type == keyboard.KEY_UP: # Changed to KEY_UP for more reliable key press detection
                if event.name == 'up':
                    self.selected_index = (self.selected_index - 1) % len(self.current_menu)
                    break
                elif event.name == 'down':
                    self.selected_index = (self.selected_index + 1) % len(self.current_menu)
                    break
                elif event.name == 'enter':
                    return self._handle_selection()
                elif event.name == 'right': # Use right arrow for value change
                    return self._handle_value_change_increase()
                elif event.name == 'left': # Use left arrow for value change
                    return self._handle_value_change_decrease()
                elif event.name == 'esc':
                    return self._handle_escape()
                elif event.name == 'backspace': # Use backspace for back navigation
                    return self._handle_back()
        return True

    def _handle_selection(self) -> bool:
        """
        Handle menu item selection.

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

        return True

    def _handle_escape(self) -> bool:
        """
        Handle navigation back to root menu.

        Returns:
            bool: True to continue menu operation
        """
        if self.current_menu != self.root_menu: # Go back to root
            self.current_menu = self.root_menu
            self.selected_index = 0
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
    

        # Check if the current menu has a parent
        if self.current_menu and self.current_menu[0].parent:
            parent_menu_item = self.current_menu[0].parent

            if parent_menu_item.text =='Settings':
                if self.current_menu != self.root_menu: # Go back to root
                    self.current_menu = self.root_menu
                    self.selected_index = 0
                return True

            self.current_menu = parent_menu_item.children
            self.selected_index = self.selected_index # Reset index to the top of the parent menu
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

            if isinstance(new_value,float):
                    new_value = round(new_value,1)
            item.callback(new_value)
        self._save_settings()
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


            new_value = max(0.0, current_value - step) # Use max to ensure value >= 0, and 0.0 to handle float correctly.

            if item.min_value is not None: # Apply min_value constraint if present
                 new_value = max(new_value, item.min_value)

            if item.max_value is not None:
                new_value = min(new_value, item.max_value)


            if isinstance(new_value,float):
                    new_value = round(new_value,1)
            item.callback(new_value)
        self._save_settings()
        return True

    def _process_music_directory(self) -> bool:
        """
        Handle the music directory processing action.

        Gets the music directory from settings or user input, and then
        calls the music tagger to process the directory.

        Returns:
            bool: True to continue menu operation
        """
        music_directory = self.settings.default_music_dir
        auto_apply_tags = self.settings.auto_apply_tags
        if not music_directory:
            logger.info("No default music directory set. Please select one first.")
            self._select_folder() # Force select folder if not set
            music_directory = self.settings.default_music_dir # Get again after selection
            if not music_directory: # User might still cancel
                logger.info("Music directory selection cancelled. Processing aborted.")
                return True # Back to menu

        if not os.path.isdir(music_directory):
            logger.error(f"Invalid music directory: {music_directory}")
            self.settings.default_music_dir = None # Reset invalid directory
            self.settings.save()
            logger.info("Default music directory setting has been reset.")
            return True # Back to menu

        logger.info(f"Starting music genre tagging process for directory: {music_directory} with AI genre suggestions.")
        print(f"\nStarting music genre tagging process for directory: {music_directory}...")
        print("You will be prompted to enter genre for each music file. AI suggestions will be provided.")
        try:
            self.music_tagger.process_directory(music_directory, auto_apply_tags) # Call music tagger's process directory
            print(f"\nMusic genre tagging process completed for directory: {music_directory}")
            logger.info(f"Music genre tagging process completed for directory: {music_directory}")
        except Exception as e:
            logger.error(f"Error during directory processing: {e}")
            print(f"An error occurred during processing: {e}")

        input("\nPress Enter to continue...") # Pause to show completion message
        return True # Back to menu

    def _select_folder(self) -> bool:
        """
        Handle music folder selection with platform-specific dialog support.

        Implements cross-platform folder selection using GUI dialog on Windows
        and terminal input on other platforms. Updates application settings
        with selected directory.

        Returns:
            bool: True if folder selection successful or cancelled, False on critical error
        """
        logger.debug("Entering _select_folder") # Debug log at start
        directory = None # Initialize directory to None
        try: # Add try-except block to catch potential Tkinter errors
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

            # Update settings with new directory
            self.settings.default_music_dir = directory
            self.settings.save()

            logger.info(f"Selected music directory: {directory}")
            logger.debug("Exiting _select_folder successfully") # Debug log at end
            return True

        except Exception as e: # Catch any error during folder selection
            logger.error(f"Critical error in folder selection: {e}")
            logger.debug("Exiting _select_folder with error") # Debug log at error exit
            return True


    def _get_console_input(self) -> Optional[str]:
        """
        Get directory path through console input.

        Implements a user-friendly console input mechanism with proper
        error handling and input validation.

        Returns:
            Optional[str]: Selected directory path or None if cancelled
        """
        logger.debug("Entering _get_console_input") # Debug log at start
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

    # Callback methods
    def _toggle_musiccn(self) -> None:
        self.settings.processing_engine.musiccn.enabled = not self.settings.processing_engine.musiccn.enabled
        self._save_settings()

    def _set_musiccn_model_count(self, value: int) -> None:
        self.settings.processing_engine.musiccn.model_count = int(value)
        self._save_settings()

    def _set_musiccn_threshold(self, value: float) -> None:
        self.settings.processing_engine.musiccn.threshold_weight = value
        self._save_settings()

    def _toggle_lastfm(self) -> None:
        self.settings.processing_engine.lastfm.enabled = not self.settings.processing_engine.lastfm.enabled
        self._save_settings()

    def _set_lastfm_threshold(self, value: float) -> None:
        self.settings.processing_engine.lastfm.threshold_weight = value
        self._save_settings()

    def _toggle_auto_apply(self) -> None:
        self.settings.auto_apply_tags = not self.settings.auto_apply_tags
        self._save_settings()

    def _save_settings(self) -> bool:
        self.settings.save()
        logger.info("Settings saved successfully")
        return True

    def _exit_program(self) -> bool:
        """Exit the program with proper cleanup."""
        self.settings.save()
        logger.info("Exiting program")
        return False

# Update the MusicTaggerMenu class to use the new interactive menu
class MusicTaggerMenu:
    def __init__(self, music_tagger: 'MusicTagger'):
        self.music_tagger = music_tagger
        self.settings = Settings.load()
        self.menu = InteractiveMenu(self.settings, self.music_tagger) # Pass MusicTagger instance to menu

    def display_menu(self) -> None:
        """Start the interactive menu system."""
        self.menu.run()

if __name__ == "__main__":
    from music_tagger import MusicTagger
    menu = MusicTaggerMenu(MusicTagger())
    menu.display_menu()