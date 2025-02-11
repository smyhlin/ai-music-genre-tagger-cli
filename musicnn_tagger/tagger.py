#!filepath: musicnn_tagger/tagger.py
from .taggram import init_extractor, get_sorted_tag_weights
from typing import Dict, List
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
        logger.warning(f"Error loading model {model_name}: {e}. Falling back to empty tags.")
        return {} # Return empty dict if model fails to load

    sorted_weights = get_sorted_tag_weights(taggram, model_tags)
    return get_top_n_genres(sorted_weights, genres_count, min_weight)


def get_musicnn_tags(music_path: str = '', ai_model_count: int = 1, ai_genres_count: int = 5, max_genres_return_count: int = 5, min_weight: float = 0.2) -> Dict[str, float]:
    """
    Initializes and uses multiple AI models to extract and process music tags.
    No print statements or animation. Pure background processing.
    """
    logger.debug(f'Processing AI genres for: {music_path.split(os.sep)[-1]}') # Debug log - less intrusive

    model_names: List[str] = {
        1: ['MSD_musicnn_big', 'MTT_musicnn'],
        2: ['MSD_musicnn_big', 'MTT_musicnn', 'MTT_vgg'],
        3: ['MSD_musicnn_big', 'MTT_musicnn', 'MTT_vgg'],
        4: ['MSD_musicnn_big', 'MTT_musicnn', 'MTT_vgg', 'MSD_musicnn'],
        5: ['MSD_musicnn_big', 'MTT_musicnn', 'MTT_vgg', 'MSD_musicnn', 'MSD_vgg'],
    }.get(ai_model_count, ['MSD_musicnn_big', 'MTT_musicnn'])

    tags_list: List[Dict[str, float]] = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=ai_model_count) as executor:
        futures = [executor.submit(_process_model, music_path, model_name, ai_genres_count, min_weight) for model_name in model_names[:ai_model_count]]
        for future in concurrent.futures.as_completed(futures):
            tags_list.append(future.result())

    combined_tags: Dict[str, float] = combine_genre_dicts(*tags_list)
    logger.debug(f'AI genre processing complete for: {music_path.split(os.sep)[-1]}') # Debug log - less intrusive
    return get_top_n_genres(combined_tags, max_genres_return_count, min_weight)


if __name__ == "__main__":
    song_path = r"D:\GITHB\FNAF2\test_fldr\Post punk\After Dark.mp3"
    ai_model_count = 5
    ai_genres_count = 10
    max_genres_return_count = 10
    min_weight = 0.2

    import time
    st = time.time()
    tags = get_musicnn_tags(song_path, ai_model_count, ai_genres_count, max_genres_return_count, min_weight)
    et = time.time()
    print(f"Elapsed time: {et - st:.4f} seconds")
    print(tags)