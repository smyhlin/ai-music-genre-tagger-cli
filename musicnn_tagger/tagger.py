#!filepath: tagger.py
from .taggram import init_extractor, get_sorted_tag_weights
from typing import Dict, List
import concurrent.futures
import os


def get_topN(data: Dict[str, float], topN: int = 5, min_weight: float = 0.0) -> Dict[str, float]:
    """
    Sorts a dictionary by value in descending order and returns the top N items
    that have a value greater than or equal to min_weight.

    Performance optimized version.

    Args:
        data: The input dictionary to sort.
        topN: The maximum number of top items to return.
        min_weight: The minimum weight value for an item to be included.

    Returns:
        A dictionary containing the top N items from the input dictionary
        that have a value greater than or equal to min_weight,
        sorted by value in descending order.
    """
    sortd = {}
    for key, value in sorted(data.items(), key=lambda x: x[1], reverse=True):
        if value >= min_weight:
            if topN <= 0:
                break
            sortd[key] = value
            topN -= 1
        else:
            break
    return sortd


def process_topN_dict(*data: Dict[str, float]) -> Dict[str, float]:
    """
    Combine multiple dictionaries, retaining the highest value for common keys.

    Performance optimized version using dictionary updates.

    Args:
        *data: Variable number of dictionaries to combine.

    Returns:
        A dictionary with combined data, keeping the maximum value for each key.
    """
    processed_data: Dict[str, float] = {}
    for ddict in data:
        processed_data.update(
            (key, max(processed_data.get(key, 0), value)) for key, value in ddict.items()
        )
    return processed_data


def _process_model(music_path: str, model_name: str, ai_genres_count: int, min_weight: float) -> Dict[str, float]:
    """Helper function to process a single model."""
    taggram, model_tags = init_extractor(music_path, model=model_name)
    sorted_weights = get_sorted_tag_weights(taggram, model_tags)
    return get_topN(sorted_weights, ai_genres_count, min_weight)


def get_init_extractor(music_path: str = '', ai_model_count: int = 1, ai_genres_count: int = 5, max_genres_return_count: int = 5, min_weight: float = 0.2) -> Dict[str, float]:
    """
    Initializes and uses multiple AI models to extract and process music tags.

    Performance optimized version using list comprehension and efficient function calls.

    Args:
        music_path: Path to the music file.
        ai_model_count: Number of AI models to use (1-5).
        ai_genres_count: Number of genres to get from each AI model.
        max_genres_return_count: Maximum number of genres to return in total.
        min_weight: Minimum weight threshold for genre tags.

    Returns:
        A dictionary of top music genre tags with weights, filtered and combined from AI models.
    """
    model_names: List[str] = {
        1: ['MSD_musicnn_big'],
        2: ['MSD_musicnn_big', 'MTT_musicnn'],
        3: ['MSD_musicnn_big', 'MTT_musicnn', 'MTT_vgg'],
        4: ['MSD_musicnn_big', 'MTT_musicnn', 'MTT_vgg', 'MSD_musicnn'],
        5: ['MSD_musicnn_big', 'MTT_musicnn', 'MTT_vgg', 'MSD_musicnn', 'MSD_vgg'],
    }.get(ai_model_count, ['MSD_musicnn_big'])

    tags_list: List[Dict[str, float]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=ai_model_count) as executor: # Use ThreadPoolExecutor for parallel tasks
        futures = [executor.submit(_process_model, music_path, model_name, ai_genres_count, min_weight) for model_name in model_names]
        for future in concurrent.futures.as_completed(futures):
            tags_list.append(future.result()) # Collect results as they become available

    combined_tags: Dict[str, float] = process_topN_dict(*tags_list)  # Use * to unpack list as arguments
    return get_topN(combined_tags, max_genres_return_count, min_weight)


if __name__ == "__main__":
    song_path = r"D:\GITHB\FNAF2\test_fldr\Post punk\After Dark.mp3"
    ai_model_count = 5
    ai_genres_count = 10
    max_genres_return_count = 10
    min_weight = 0.2

    import time
    st = time.time()
    tags = get_init_extractor(song_path, ai_model_count, ai_genres_count, max_genres_return_count, min_weight)
    et = time.time()
    print(f"Elapsed time: {et - st:.4f} seconds")
    print(tags)