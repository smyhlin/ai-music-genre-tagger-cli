# path musicnn_tagger/config.py
from dataclasses import dataclass, field
import os
from dotenv import load_dotenv, set_key
import pathlib
import logging
from typing import Dict
import json  # Import json for serialization

logger = logging.getLogger(__name__)

@dataclass
class MusicnnSettings:
    """
    Settings for the Musicnn AI tagger, loaded from and saved to .env file,
    including persistence for the enabled_models dictionary.
    """
    enabled: bool = True
    threshold_weight: float = 0.2
    genres_count: int = 5
    enabled_models: Dict[str, bool] = field(default_factory=lambda: {
        'MSD_musicnn_big': True,
        'MTT_musicnn': True,
        'MTT_vgg': True,
        'MSD_musicnn': True,
        'MSD_vgg': True
    })

    def __post_init__(self):
        """
        Initialize MusicnnSettings by loading values from .env file,
        including enabled_models.
        """
        self.dotenv_path = pathlib.Path(__file__).parent.parent / '.env'
        load_dotenv(dotenv_path=self.dotenv_path, encoding='utf-8', verbose=False) # Load .env

        self.enabled = os.getenv("MUSICNN_ENABLED", 'True').lower() == 'true'
        self.threshold_weight = float(os.getenv("MUSICNN_THRESHOLD_WEIGHT", 0.2))
        self.genres_count = int(os.getenv("MUSICNN_GENRES_COUNT", 5))

        # Load enabled_models from .env as a JSON string and parse it
        enabled_models_str = os.getenv("MUSICNN_ENABLED_MODELS")
        if enabled_models_str:
            try:
                self.enabled_models = json.loads(enabled_models_str)
                if not isinstance(self.enabled_models, dict): # Basic validation after loading
                    logger.warning("Invalid format for MUSICNN_ENABLED_MODELS in .env, using default models.")
                    self.enabled_models = self.default_enabled_models() # Fallback to default if loading fails
            except json.JSONDecodeError:
                logger.warning("Could not decode MUSICNN_ENABLED_MODELS from .env, using default models.")
                self.enabled_models = self.default_enabled_models() # Fallback to default on decode error
        else:
            self.enabled_models = self.default_enabled_models() # Use default if not in .env


    def save_settings(self):
        """
        Save current Musicnn settings to .env file, including enabled_models.
        """
        set_key(self.dotenv_path, "MUSICNN_ENABLED", str(self.enabled).upper())
        set_key(self.dotenv_path, "MUSICNN_THRESHOLD_WEIGHT", str(self.threshold_weight))
        set_key(self.dotenv_path, "MUSICNN_GENRES_COUNT", str(self.genres_count))

        # Serialize enabled_models dictionary to JSON string and save it
        enabled_models_str = json.dumps(self.enabled_models)
        set_key(self.dotenv_path, "MUSICNN_ENABLED_MODELS", enabled_models_str)

        logger.debug("MusicnnSettings saved to .env (including enabled_models).")

    @staticmethod
    def default_enabled_models() -> Dict[str, bool]:
        """Returns the default enabled_models dictionary."""
        return {
            'MSD_musicnn_big': True,
            'MTT_musicnn': True,
            'MTT_vgg': True,
            'MSD_musicnn': True,
            'MSD_vgg': True
        }