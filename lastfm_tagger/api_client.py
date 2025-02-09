#!filepath: lastfm_tagger/api_client.py
import requests
import logging
from typing import Dict, Any
import urllib.parse

from lastfm_tagger.config import LastFMSettings

logger = logging.getLogger(__name__)

class LastFMClient:
    """
    Client for interacting with the Last.fm API.
    """

    def __init__(self, settings: LastFMSettings):
        """
        Initializes the LastFMClient with settings.

        Args:
            settings: An instance of Settings containing API configurations.
        """
        self.settings = settings

    def _build_api_url(self, method: str, params: Dict[str, Any]) -> str:
        """
        Constructs the full API URL for a given method and parameters.
        Function name unified to _build_api_url for consistency.
        """
        base_url = self.settings.lastfm_api_base_url
        api_key = self.settings.lastfm_api_key
        full_params = {
            'method': method,
            'api_key': api_key,
            'format': 'json',
            'autocorrect': '1',
            **{k: urllib.parse.quote(v) if isinstance(v, str) else v for k, v in params.items()} # URL encode params
        }
        param_string = '&'.join([f"{key}={value}" for key, value in full_params.items()])
        return f"{base_url}?{param_string}"

    def get_track_top_tags(self, artist_name: str, track_name: str) -> Dict:
        """
        Retrieves top tags for a track from Last.fm API (using track.getTopTags) and returns the raw JSON response.
        Function name unified to get_track_top_tags for consistency.
        """
        api_method = 'track.getTopTags'
        params = {
            'artist': artist_name,
            'track': track_name
        }
        url = self._build_api_url(api_method, params)
        logger.info(f"Fetching track top tags from: {url}")
        return self._fetch_api_data(url)


    def get_artist_top_tags(self, artist_name: str) -> Dict:
        """
        Retrieves top tags for an artist from Last.fm API (using artist.getTopTags) and returns the raw JSON response.
        Function name unified to get_artist_top_tags for consistency.
        """
        api_method = 'artist.getTopTags'
        params = {
            'artist': artist_name,
        }
        url = self._build_api_url(api_method, params)
        logger.info(f"Fetching artist top tags from: {url}")
        return self._fetch_api_data(url)

    def _fetch_api_data(self, url: str) -> Dict:
        """
        Fetches data from the Last.fm API at the given URL and handles errors.
        Function name unified to _fetch_api_data for consistency.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            json_response = response.json()
            logger.debug(f"API Response JSON: {json_response}")
            return json_response
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
            return {}
        except requests.exceptions.ConnectionError as conn_err:
            logger.error(f"Connection error occurred: {conn_err}")
            return {}
        except requests.exceptions.Timeout as timeout_err:
            logger.error(f"Timeout error occurred: {timeout_err}")
            return {}
        except requests.exceptions.RequestException as req_err:
            logger.error(f"Unexpected error occurred: {req_err}")
            return {}
        except ValueError as json_err:
            logger.error(f"JSON decoding error: {json_err}")
            return {}