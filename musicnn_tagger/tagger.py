#!filepath: musicnn_tagger/tagger.py
from .taggram import init_extractor, get_sorted_tag_weights
from typing import Dict, List
import concurrent.futures
import os
import time
import threading
import colorama
from colorama import Fore, Back, Style

colorama.init()

def loading_animation(stop_event: threading.Event):
    """
    Displays a more 3D-like and visually engaging loading animation.
    """
    animation_chars_3d = [
        "       .o       ",
        "      .oO.      ",
        "     .oOoO.     ",
        "    .oOo.oOo.    ",
        "   .oO.   .oO.   ",
        "  .oO.     .oO.  ",
        " .oO.       .oO. ",
        ".oO.         .oO.",
        ".o.           .o.",
        " o             o ",
        "               "
    ] # 3D sphere/orb-like expansion and contraction
    colors_3d = [
        Fore.CYAN,
        Fore.LIGHTBLUE_EX, # Replaced LIGHT_CYAN_EX with LIGHTBLUE_EX (common issue, intended color similar)
        Fore.BLUE,
        Fore.LIGHTBLUE_EX,
        Fore.CYAN,
        Fore.LIGHTBLUE_EX,
        Fore.BLUE,
        Fore.LIGHTBLUE_EX,
        Fore.CYAN,
        Fore.LIGHTBLUE_EX,
        Fore.RESET # Reset color for spacing
    ] # Shades of blue and cyan, plus reset
    bg_color = Back.BLACK
    idx = 0
    color_idx = 0
    animation_width = 35 # Wider to accommodate 3D shape

    base_text = f"{Fore.WHITE}{bg_color}  🔮 Neural Network Audio Analysis... {Style.RESET_ALL}{bg_color}{Fore.WHITE}  " # Even more immersive text


    while not stop_event.is_set():
        char_block = animation_chars_3d[idx % len(animation_chars_3d)]
        color = colors_3d[color_idx % len(colors_3d)]
        colored_animation = bg_color + color + char_block + Style.RESET_ALL
        padding_right = " " * (animation_width - len(char_block) - len(base_text.split(Style.RESET_ALL)[0])) # Adjust padding more dynamically

        animation_line = f"\r{base_text}{colored_animation}{padding_right}{Style.RESET_ALL}"
        print(animation_line, end="")

        idx += 1
        color_idx += 1 # Step through colors gently
        time.sleep(0.07) # Faster pace for pulsing 3D effect

    done_line = f"\r{base_text}{bg_color}{Fore.GREEN}  ✨ Audio Analysis Complete! █████  {Style.RESET_ALL}    " # Enhanced "Complete!"
    print(done_line, end="\r")
    print()


def get_topN(data: Dict[str, float], topN: int = 5, min_weight: float = 0.0) -> Dict[str, float]:
    """
    Sorts a dictionary by value in descending order and returns the top N items
    that have a value greater than or equal to min_weight.

    Performance optimized version.
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
    """
    print(f'ﮩ٨ـﮩﮩ٨ـ♡ﮩ٨ـﮩﮩ٨ـ {music_path.split("/")[-1]} ﮩ٨ـﮩﮩ٨ـ♡ﮩ٨ـﮩﮩ٨ـ')
    model_names: List[str] = {
        1: ['MSD_musicnn_big'],
        2: ['MSD_musicnn_big', 'MTT_musicnn'],
        3: ['MSD_musicnn_big', 'MTT_musicnn', 'MTT_vgg'],
        4: ['MSD_musicnn_big', 'MTT_musicnn', 'MTT_vgg', 'MSD_musicnn'],
        5: ['MSD_musicnn_big', 'MTT_musicnn', 'MTT_vgg', 'MSD_musicnn', 'MSD_vgg'],
    }.get(ai_model_count, ['MSD_musicnn_big'])

    tags_list: List[Dict[str, float]] = []
    stop_loading_event = threading.Event()
    loading_thread = threading.Thread(target=loading_animation, args=(stop_loading_event,))
    loading_thread.start()

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=ai_model_count) as executor: # Use ThreadPoolExecutor for parallel tasks
            futures = [executor.submit(_process_model, music_path, model_name, ai_genres_count, min_weight) for model_name in model_names]
            for future in concurrent.futures.as_completed(futures):
                tags_list.append(future.result()) # Collect results as they become available
    finally:
        stop_loading_event.set() # Signal loading animation to stop
        loading_thread.join() # Wait for loading animation thread to finish

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