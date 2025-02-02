#!filepath: parser.py
from typing import List, Dict, Any

import logging
from .models import TrackGetTopTagsResponse, TagModel, ArtistGetTopTagsResponse

logger = logging.getLogger(__name__)

def parse_track_tags(api_response: Dict[str, Any]) -> List[TagModel]:
    """
    Parses the Last.fm API response (for track.getTopTags) to extract track tags using Pydantic models.

    Args:
        api_response: A dictionary representing the JSON response from the Last.fm API (track.getTopTags).

    Returns:
        A list of TagModel objects.
        Returns an empty list if no tags are found or if the response format is invalid.
    """
    tags: List[TagModel] = []
    try:
        track_top_tags_response = TrackGetTopTagsResponse.parse_obj(api_response)
        if track_top_tags_response.toptags and track_top_tags_response.toptags.tag:
            tags = track_top_tags_response.toptags.tag
        else:
            logger.info("No track tags found in the API response or tags list is empty.")
    except Exception as e:
        logger.error(f"Error parsing track tags API response with Pydantic model: {e}")
        logger.debug(f"API Response causing error: {api_response}")
    return tags


def parse_artist_tags(api_response: Dict[str, Any]) -> List[TagModel]:
    """
    Parses the Last.fm API response (for artist.getTopTags) to extract artist tags using Pydantic models.

    Args:
        api_response: A dictionary representing the JSON response from the Last.fm API (artist.getTopTags).

    Returns:
        A list of TagModel objects.
        Returns an empty list if no tags are found or if the response format is invalid.
    """
    tags: List[TagModel] = []
    try:
        artist_top_tags_response = ArtistGetTopTagsResponse.parse_obj(api_response)
        if artist_top_tags_response.toptags and artist_top_tags_response.toptags.tag:
            tags = artist_top_tags_response.toptags.tag
        else:
            logger.info("No artist tags found in the API response or tags list is empty.")
    except Exception as e:
        logger.error(f"Error parsing artist tags API response with Pydantic model: {e}")
        logger.debug(f"API Response causing error: {api_response}")
    return tags