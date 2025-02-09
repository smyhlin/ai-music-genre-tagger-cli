#!filepath: lastfm_tagger/lastfm_tagger.py
import logging
import os
from typing import List, Tuple

from .config import LastFMSettings
from .api_client import LastFMClient
from .parser import parse_track_tags, parse_artist_tags
from .models import TagModel

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

def get_lastfm_tags(artist_name: str, track_name: str, top_n: int = 5, min_weight: float = 60) -> List[Tuple[str, int]]:
    """
    Retrieves top tags and their weights for a given music track from Last.fm.
    If track tags are not found, falls back to artist tags.
    Filters tags by min_weight and returns top N tags.

    Args:
        artist_name: The name of the artist.
        track_name: The name of the track.
        top_n: Maximum number of top tags to return.
        min_weight: Minimum weight threshold for tags (as a fraction, e.g., 60 for 60%).

    Returns:
        A list of tuples, where each tuple contains (tag name: str, tag weight: int),
        filtered and sorted. Returns an empty list if no tags are found.
    """

    settings = LastFMSettings()
    last_fm_client = LastFMClient(settings)

    track_api_response = last_fm_client.get_track_top_tags(artist_name, track_name)
    track_tags: List[TagModel] = parse_track_tags(track_api_response)

    if not track_tags:
        logger.info(f"No track tags found for '{track_name}' by '{artist_name}'. Falling back to artist tags.")
        artist_tags: List[TagModel] = parse_artist_tags(last_fm_client.get_artist_top_tags(artist_name))
        if artist_tags:
            logger.info(f"Artist tags found for '{artist_name}'.")
            track_tags = artist_tags  # Use artist tags as fallback
        else:
            logger.info(f"No tags found for '{track_name}' by '{artist_name}', and no artist tags found either.")
            return []

    # Filtering and sorting logic
    all_tags_weights = [(tag.name, tag.count) for tag in track_tags if tag.count is not None]
    total_weight = sum(weight for _, weight in all_tags_weights)
    if total_weight > 0:
        filtered_tags = [(tag, weight) for tag, weight in all_tags_weights if weight >= min_weight]
    else:
        filtered_tags = all_tags_weights # Keep all if total weight is zero to avoid division by zero errors
    sorted_tags = sorted(filtered_tags, key=lambda item: item[1], reverse=True)
    return sorted_tags[:top_n]


def main(artist_name: str, track_name: str) -> None:
    """
    Main function to run when the script is executed directly.
    Demonstrates get_lastfm_tags function with top_n and min_weight parameters.
    """
    if not artist_name or not track_name:
        logger.error("Artist name and track name are required.")
        return

    top_n = 5  # Example top N value
    min_weight_threshold = 70  # Example min_weight value

    try:
        tags_and_weights = get_lastfm_tags(artist_name, track_name, top_n=top_n, min_weight=min_weight_threshold)

        if tags_and_weights:
            print(f"\nTop {top_n} tags (>= {min_weight_threshold:.0f}% weight) for '{track_name}' by '{artist_name}':")
            for tag_name, tag_weight in tags_and_weights:
                print(f"- {tag_name} (Weight: {tag_weight})")
        else:
            if os.getenv('LASTFM_API_KEY'):
                print(f"No tags found for '{track_name}' by '{artist_name}' with specified criteria.")

    except Exception as e:
        logger.error(f"Error retrieving tags: {e}")
        print(f"An error occurred: {e}") # User-friendly error message


if __name__ == "__main__":
    artist_name = "Vexare"
    track_name = "The Clockmaker"
    main(artist_name, track_name)