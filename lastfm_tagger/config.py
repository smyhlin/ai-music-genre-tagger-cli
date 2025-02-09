#!filepath: lastfm_tagger/config.py
import os
import pathlib
from dotenv import load_dotenv, set_key
import logging


class LastFMSettings:
    """
    Settings class for managing application configurations for lastfm_tagger using dotenv.
    It loads settings from and saves settings to environment variables in .env.
    """

    lastfm_api_key: str
    enabled: bool
    threshold_weight: float
    lastfm_api_base_url: str

    def __init__(self):
        # Load environment variables from .env file in the parent directory
        self.dotenv_path = pathlib.Path(__file__).parent.parent / '.env'
        load_dotenv(dotenv_path=self.dotenv_path, encoding='utf-8', verbose=False) # Load .env

        # Initialize settings from environment variables or defaults
        self.lastfm_api_key = os.environ.get("LASTFM_API_KEY")
        if not self.lastfm_api_key:
            raise Exception("LASTFM_API_KEY environment variable is not set or is empty.")
        self.enabled = os.getenv("LASTFM_ENABLED", 'True').lower() == 'true' # Default to True if not set
        self.threshold_weight = float(os.getenv("LASTFM_THRESHOLD_WEIGHT", '0.5')) # Default to 0.5, convert to float
        self.lastfm_api_base_url =  "http://ws.audioscrobbler.com/2.0" # Default URL

    def save_settings(self):
        """Save current settings to .env file."""
        set_key(self.dotenv_path, "LASTFM_ENABLED", str(self.enabled).upper())
        set_key(self.dotenv_path, "LASTFM_THRESHOLD_WEIGHT", str(self.threshold_weight))
        logging.debug("LastFMSettings saved to .env")
