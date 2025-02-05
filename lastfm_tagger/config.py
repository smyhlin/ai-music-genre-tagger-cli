#!filepath: lastfm_tagger/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os

class Settings(BaseSettings):
    """
    Settings class for managing application configurations.
    It inherits from Pydantic BaseSettings and automatically loads
    settings from environment variables.
    """
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    lastfm_api_key: str = Field(..., env='LASTFM_API_KEY', description='API key for Last.fm API')
    lastfm_api_base_url: str = "http://ws.audioscrobbler.com/2.0"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.lastfm_api_key:
            raise Exception("LASTFM_API_KEY environment variable is not set or is empty.")