#!filepath: lastfm_tagger.py
import logging
import os
from typing import List, Tuple, Optional, Dict

from .config import Settings
from .api_client import LastFMClient
from .parser import parse_track_tags, parse_artist_tags
from .models import TagModel

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

def get_tags_and_weights(artist_name: str, track_name: str, topN: int = 5, min_weight: float = 60) -> List[Tuple[str, int]]:
    """
    Retrieves top tags and their weights for a given music track from Last.fm.
    If track tags are not found, falls back to artist tags.
    Filters tags by min_weight and returns top N tags.

    Args:
        artist_name: The name of the artist.
        track_name: The name of the track.
        topN: Maximum number of top tags to return.
        min_weight: Minimum weight threshold for tags (as a fraction, e.g., 60 for 60%).

    Returns:
        A list of tuples, where each tuple contains (tag name: str, tag weight: int),
        filtered and sorted. Returns an empty list if no tags are found or if API key is missing.
    """
    try:
        settings = Settings()
        last_fm_client = LastFMClient(settings)
    except Exception as e:
        logger.error(str(e)) # Log settings error
        print("LASTFM_API_KEY empty")
        return []

    tags_and_weights: List[Tuple[str, int]] = []

    track_api_response = last_fm_client.get_track_top_tags(artist_name, track_name)
    track_tags: List[TagModel] = parse_track_tags(track_api_response)

    if track_tags:
        logger.info(f"Track tags found for '{track_name}' by '{artist_name}'.")
    else:
        logger.info(f"No track tags found for '{track_name}' by '{artist_name}'. Falling back to artist tags.")
        artist_tags: List[TagModel] = parse_artist_tags(last_fm_client.get_artist_top_tags(artist_name)) # Corrected line: assign to artist_tags
        if artist_tags:
            logger.info(f"Artist tags found for '{artist_name}'.")
            track_tags = artist_tags # Use artist tags as fallback
        else:
            logger.info(f"No tags found for '{track_name}' by '{artist_name}', and no artist tags found either.")
            return []

    # Filtering and sorting logic (moved outside if/else to apply to both track and artist tags)
    all_tags_weights = [(tag.name, tag.count) for tag in track_tags if tag.count is not None]
    total_weight = sum(weight for _, weight in all_tags_weights)
    if total_weight > 0:
        filtered_tags = [(tag, weight) for tag, weight in all_tags_weights if weight >= min_weight]
    else:
        filtered_tags = all_tags_weights
    sorted_tags = sorted(filtered_tags, key=lambda item: item[1], reverse=True)
    top_n_tags = sorted_tags[:topN]
    tags_and_weights = top_n_tags

    return tags_and_weights


def main(artist_name, track_name):
    """
    Main function to run when the script is executed directly.
    Demonstrates get_tags_and_weights function with topN and min_weight parameters.
    """
    if not artist_name or not track_name:
        logger.error("Artist name and track name are required.")
        return

    top_n = 5 # Example top N value
    min_weight_threshold = 70 # Example min_weight value
    tags_and_weights = get_tags_and_weights(artist_name, track_name, topN=top_n, min_weight=min_weight_threshold)

    if tags_and_weights:
        print(f"\nTop {top_n} tags (>= {min_weight_threshold:.0f}% weight) for '{track_name}' by '{artist_name}':")
        for tag_name, tag_weight in tags_and_weights:
            print(f"- {tag_name} (Weight: {tag_weight})")
    else:
        if os.getenv('LASTFM_API_KEY'):
            print(f"No tags found for '{track_name}' by '{artist_name}' with specified criteria.")


if __name__ == "__main__":
    artist_name = "Vexare"
    track_name = "The Clockmaker"
    main(artist_name, track_name)