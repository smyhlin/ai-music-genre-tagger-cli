#!filepath: musicnn_tagger/tagger.py
from .taggram import init_extractor, get_sorted_tag_weights
from typing import Dict, List, Tuple
import concurrent.futures
import os
import logging

logger = logging.getLogger(__name__)


def get_top_n_genres(data: Dict[str, float], top_n: int = 5, min_weight: float = 0.0) -> Dict[str, float]:
    """
    Sorts a dictionary by value in descending order and returns the top N items
    that have a value greater than or equal to min_weight.
    """
    sorted_genres = {}
    for key, value in sorted(data.items(), key=lambda x: x[1], reverse=True):
        if value >= min_weight:
            if top_n <= 0:
                break
            sorted_genres[key] = value
            top_n -= 1
        else:
            break
    return sorted_genres


def combine_genre_dicts(*genre_dicts: Dict[str, float]) -> Dict[str, float]:
    """
    Combine multiple dictionaries, retaining the highest value for common keys.
    """
    combined_genres: Dict[str, float] = {}
    for genre_dict in genre_dicts:
        combined_genres.update(
            (key, max(combined_genres.get(key, 0), value)) for key, value in genre_dict.items()
        )
    return combined_genres

def _process_model(music_path: str, model_name: str, genres_count: int, min_weight: float) -> Dict[str, float]:
    """Helper function to process a single model."""
    try:
        taggram, model_tags = init_extractor(music_path, model=model_name)
    except Exception as e:
        logger.warning(f"Error loading model {model_name}: {e}")
        if model_name == 'MSD_musicnn_big': # Fallback logic for MSD_musicnn_big
            fallback_model = 'MTT_musicnn'
            logger.warning(f"Falling back from {model_name} to {fallback_model}...")
            try:
                taggram, model_tags = init_extractor(music_path, model=fallback_model) # Try fallback model
                logger.info(f"Successfully loaded fallback model {fallback_model}.")
            except Exception as fallback_e:
                logger.error(f"Error loading fallback model {fallback_model}: {fallback_e}. Returning empty tags.")
                return {} # Return empty dict if fallback also fails
        else:
            logger.warning(f"Falling back to empty tags for {model_name} due to loading error.")
            return {} # Return empty dict if model fails to load

    sorted_weights = get_sorted_tag_weights(taggram, model_tags)
    return get_top_n_genres(sorted_weights, genres_count, min_weight)

def _remove_duplicate_gender_tags(genre_dict: Dict[str, float]) -> Dict[str, float]:
    """
    Removes duplicate gender-specific tags, keeping only the shortest tag.

    Args:
        genre_dict (Dict[str, float]): Dictionary of genres and their weights.

    Returns:
        Dict[str, float]: Modified dictionary with duplicate gender tags removed.
    """
    modified_genre_dict = genre_dict.copy()
    female_keywords = ['woman', 'female', 'female vocal', 'female voice', 'female vocalists', 'female singer', 'female vocals']
    male_keywords = ['man', 'male', 'male vocal', 'male voice', 'male vocalists', 'male singer', 'male vocals']

    female_tags = []
    male_tags = []

    # Identify all gender-related tags
    for tag in genre_dict:
        tag_lower = tag.lower()
        for keyword in female_keywords:
            if keyword in tag_lower:
                female_tags.append(tag)
                break  # Avoid double-counting
        for keyword in male_keywords:
            if keyword in tag_lower:
                male_tags.append(tag)
                break

    # Remove duplicates for female tags, keeping the shortest
    if female_tags:
        shortest_female_tag = min(female_tags, key=len) # Find the shortest tag
        for tag in female_tags:
            if tag != shortest_female_tag:
                if tag in modified_genre_dict: # Check for exist
                    del modified_genre_dict[tag]

    # Remove duplicates for male tags, keeping the shortest
    if male_tags:
        shortest_male_tag = min(male_tags, key=len)
        for tag in male_tags:
            if tag != shortest_male_tag:
                if tag in modified_genre_dict: # Check for exist
                    del modified_genre_dict[tag]

    return modified_genre_dict

def get_musicnn_tags(music_path: str = '', ai_genres_count: int = 5, max_genres_return_count: int = 5, min_weight: float = 0.2, enabled_models_config: Dict[str, bool] = None) -> Dict[str, float]:
    """
    Initializes and uses multiple AI models to extract and process music tags.
    Removes duplicate gender tags.
    Uses enabled_models_config to determine which models to use.
    """
    logger.debug(f'Processing AI genres for: {music_path.split(os.sep)[-1]}')

    # Use enabled_models_config to get the list of enabled models
    if enabled_models_config is None:
        model_names: List[str] = ['MSD_musicnn_big', 'MTT_musicnn'] # Default models if config is not provided (should not happen in normal use)
    else:
        model_names: List[str] = [model_name for model_name, is_enabled in enabled_models_config.items() if is_enabled]

    tags_list: List[Dict[str, float]] = []
    num_enabled_models = len(model_names)

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_enabled_models if num_enabled_models > 0 else 1) as executor: # Use number of enabled models as max_workers
        futures = [executor.submit(_process_model, music_path, model_name, ai_genres_count, min_weight) for model_name in model_names]
        for future in concurrent.futures.as_completed(futures):
            tags_list.append(future.result())

    combined_tags: Dict[str, float] = combine_genre_dicts(*tags_list)

    # Remove duplicate gender tags
    deduplicated_tags = _remove_duplicate_gender_tags(combined_tags)

    logger.debug(f'AI genre processing complete for: {music_path.split(os.sep)[-1]}')
    return get_top_n_genres(deduplicated_tags, max_genres_return_count, min_weight)


if __name__ == "__main__":
    song_path = r"D:\GITHB\FNAF2\test_fldr\Post punk\After Dark.mp3"  # Replace with your music file path
    # Or use a path with known duplicate gender tags for testing:
    # song_path = r"path/to/your/music_file_with_duplicates.mp3"
    ai_genres_count = 10
    max_genres_return_count = 10
    min_weight = 0.2
    enabled_models_test_config = { # Example config for testing
        'MSD_musicnn_big': True,
        'MTT_musicnn': False,
        'MTT_vgg': True,
        'MSD_musicnn': False,
        'MSD_vgg': False
    }

    import time
    st = time.time()
    tags = get_musicnn_tags(song_path, ai_genres_count, max_genres_return_count, min_weight, enabled_models_test_config)
    et = time.time()
    print(f"Elapsed time: {et - st:.4f} seconds")
    print(tags)