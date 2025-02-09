#!filepath: musicnn_tagger/config.py
import pathlib

# Removed pydantic_settings imports
# from pydantic_settings import BaseSettings, SettingsConfigDict
# from pydantic import Field
import os
# Import dotenv
from dotenv import load_dotenv, dotenv_values, set_key
import logging

# Replace BaseSettings with a regular class
class MusicnnSettings:
    """
    Configuration settings for the Musicnn AI tagger engine, loaded from and saved to .env file using dotenv.
    """

    enabled: bool
    model_count: int
    threshold_weight: float
    genres_count: int


    def __init__(self):
        # Load environment variables from .env file in the parent directory
        self.dotenv_path = pathlib.Path(__file__).parent.parent / '.env'
        load_dotenv(dotenv_path=self.dotenv_path, encoding='utf-8', verbose=False) # Load .env

        # Initialize settings from environment variables or defaults
        self.enabled = os.getenv("MUSICNN_ENABLED", 'True').lower() == 'true' # Default to True if not set
        self.model_count = int(os.getenv("MUSICNN_MODEL_COUNT", '1')) # Default to 1, convert to int
        self.threshold_weight = float(os.getenv("MUSICNN_THRESHOLD_WEIGHT", '0.5')) # Default to 0.5, convert to float
        self.genres_count = int(os.getenv("MUSICNN_GENRES_COUNT", '5')) # Default to 5, convert to int
        self.model_validate() # Validate after initialization

    def save_settings(self):
        """Save current settings to .env file."""
        set_key(self.dotenv_path, "MUSICNN_ENABLED", str(self.enabled).upper())
        set_key(self.dotenv_path, "MUSICNN_MODEL_COUNT", str(self.model_count))
        set_key(self.dotenv_path, "MUSICNN_THRESHOLD_WEIGHT", str(self.threshold_weight))
        set_key(self.dotenv_path, "MUSICNN_GENRES_COUNT", str(self.genres_count))
        logging.debug("MusicnnSettings saved to .env")


    def model_validate(self) -> None: # Removed settings parameter as it's self now
        """
        Validate settings constraints.

        Raises:
            ValueError: If any settings are outside valid ranges
        """
        if not isinstance(self.model_count, int) or not 1 <= self.model_count <= 5:
            raise ValueError("Model count must be an integer between 1 and 5")
        if not 0 <= self.threshold_weight <= 1:
            raise ValueError("Threshold weight must be between 0 and 1")
        if not isinstance(self.genres_count, int) or not 1 <= self.genres_count <= 10: # Example max genres count
            raise ValueError("Musicnn genres count must be an integer between 1 and 10")