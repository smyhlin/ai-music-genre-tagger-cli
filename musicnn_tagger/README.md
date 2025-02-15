# Musicnn Tagger Module

This module integrates the `musicnn` library to provide AI-powered genre prediction for music files. It leverages deep learning models to analyze audio content and suggest relevant genres. This module is designed to be used as part of a larger music tagging application.

## Features

*   **AI-Based Genre Prediction:** Utilizes deep learning models from the `musicnn` library to analyze audio and predict genres.
*   **Multiple Model Support:** Supports several `musicnn` models for genre prediction, including `MSD_musicnn_big`, `MTT_musicnn`, `MTT_vgg`, `MSD_musicnn`, and `MSD_vgg`.
*   **Model Fallback:** Implements a fallback mechanism to ensure robustness. If the `MSD_musicnn_big` model is unavailable, it defaults to using `MTT_musicnn`.
*   **Configurable Settings:** Allows users to configure:
    *   Enabling/disabling the musicnn tagger.
    *   The number of AI models to use for prediction (1-5).
    *   A threshold weight for filtering suggested genres.
    *   The number of genres to be considered by the AI.
*   **Concurrent Processing:** Uses `concurrent.futures.ThreadPoolExecutor` to process multiple AI models in parallel, improving performance when using more than one model.
*   **Taggram Visualization (Optional):** Provides functions to visualize the taggram (temporal evolution of tags) and tags likelihood mean, useful for debugging and understanding model outputs.
*   **Settings Management:** Uses the `MusicnnSettings` class and `.env` file for easy configuration and persistence of settings.
*   **Logging:** Integrates with Python's `logging` module for informative messages and error reporting.

## Files

*   **`__init__.py`**:
    *   Makes the `musicnn_tagger` directory a Python package.
    *   Exports key functions for external use: `get_musicnn_tags`, `init_extractor`, `show_taggram`, `show_tags_likelihood_mean`.
*   **`config.py`**:
    *   Defines the `MusicnnSettings` class to manage configuration settings for the musicnn tagger.
    *   Loads and saves settings from/to a `.env` file located in the parent directory.
    *   Includes validation for settings values to ensure they are within acceptable ranges.
*   **`tagger.py`**:
    *   Contains the core logic for AI-based genre tagging.
    *   `get_musicnn_tags(music_path, ai_model_count, ai_genres_count, max_genres_return_count, min_weight)`: The main function to get genre suggestions for a music file. It handles model loading, parallel processing, tag combination, and filtering.
    *   Helper functions: `get_top_n_genres`, `combine_genre_dicts`, `_process_model`.
*   **`taggram.py`**:
    *   Provides functions related to processing and visualizing the taggram output from `musicnn`.
    *   `init_extractor(music_path, model)`: Initializes the `musicnn` extractor for a given music file and model.
    *   `show_taggram(taggram, tags)`: Displays a visualization of the taggram.
    *   `show_tags_likelihood_mean(taggram, tags)`: Displays a bar chart of the mean likelihood of each tag.
    *   `get_sorted_tag_weights(taggram, tags)`: Calculates and returns sorted tag weights from the taggram.

## Usage

The primary function to use is `get_musicnn_tags` from `tagger.py`:

```python
from musicnn_tagger import get_musicnn_tags

music_file_path = 'path/to/your/music_file.mp3' # Replace with your music file path

# Get genre suggestions using default settings (1 model, threshold 0.2, 5 genres count)
suggested_genres = get_musicnn_tags(music_path=music_file_path)
print("Suggested Genres (default settings):", suggested_genres)

# Get genre suggestions using custom settings (5 models, threshold 0.3, 10 genres count)
custom_genres = get_musicnn_tags(music_path=music_file_path, ai_model_count=5, min_weight=0.3, ai_genres_count=10)
print("Suggested Genres (custom settings):", custom_genres)
```

**Explanation:**

1.  **Import:** Import the `get_musicnn_tags` function.
2.  **Call `get_musicnn_tags`:**
    *   `music_path`: (Required) Path to the music file you want to analyze.
    *   `ai_model_count`: (Optional) Number of AI models to use (integer between 1 and 5, default is 1). More models may improve accuracy but increase processing time.
    *   `ai_genres_count`: (Optional) Number of genres the AI should consider for each model (integer between 1 and 10, default is 5).
    *   `max_genres_return_count`: (Optional) Maximum number of genres to return in the final output (integer, default is 5).
    *   `min_weight`: (Optional) Minimum confidence threshold for a genre to be included in the suggestions (float between 0.0 and 1.0, default is 0.2).
3.  **Process Results:** The function returns a dictionary where keys are genre names and values are their corresponding weights (confidence scores).

## Configuration

The module's behavior is configured using settings loaded from a `.env` file (located in the parent directory) and managed by the `MusicnnSettings` class in `config.py`.

**`.env` settings:**

```dotenv
MUSICNN_ENABLED=TRUE       # Enable or disable the Musicnn tagger (TRUE/FALSE)
MUSICNN_MODEL_COUNT=1     # Number of AI models to use (1-5)
MUSICNN_THRESHOLD_WEIGHT=0.2 # Minimum confidence threshold (0.0-1.0)
MUSICNN_GENRES_COUNT=5      # Number of genres considered by AI (1-10)
```

*   **`MUSICNN_ENABLED`**:  Boolean value to enable or disable the AI genre prediction.
*   **`MUSICNN_MODEL_COUNT`**: Integer value between 1 and 5, controlling the number of AI models used.
*   **`MUSICNN_THRESHOLD_WEIGHT`**: Float value between 0.0 and 1.0, representing the minimum confidence score for a genre to be suggested. Increase to get more confident suggestions, decrease to get more suggestions (potentially less accurate).
*   **`MUSICNN_GENRES_COUNT`**: Integer value between 1 and 10, defining how many top genres each AI model should consider internally.

You can modify these values in the `.env` file to customize the behavior of the musicnn tagger. The `MusicnnSettings` class will automatically load these settings when initialized.

## Dependencies

*   `musicnn`: The core musicnn library for deep learning based audio tagging.
* `tensorflow`:  TensorFlow is a dependency of `musicnn`.
*   `librosa`:  Librosa is used for audio analysis and feature extraction by `musicnn`.
*   `python-dotenv`: For loading settings from the `.env` file.
*   `colorama`: For colored console output and the loading animation.
*   `concurrent.futures`: For parallel processing of AI models.
*   `threading`: For managing the loading animation in a separate thread.
*   `time`: For controlling the animation speed.
*   `logging`: For logging messages and errors.
*   `numpy`: For numerical operations, especially with `musicnn` and audio data.
*   `matplotlib.pyplot`: (Optional) For visualizing taggrams using `show_taggram` and `show_tags_likelihood_mean` functions.

These dependencies are typically listed in the main project's `requirements.txt` file. Ensure they are installed before using the `musicnn_tagger` module.

## Notes

*   The `MSD_musicnn_big` model is the largest and generally most accurate model, but it may require more resources. If you encounter performance issues, try reducing `MUSICNN_MODEL_COUNT` or using fewer models in your configuration.
*   The loading animation is designed to provide user feedback during the potentially time-consuming AI analysis.
*   Error handling is included to gracefully manage potential issues like model loading failures or invalid settings.
*   The `taggram.py` module provides visualization tools that can be helpful for understanding the output of the `musicnn` models and for debugging purposes, but they are not essential for basic genre tagging functionality.

## Model Installation Note for `MSD_musicnn_big`

To utilize the `MSD_musicnn_big` model, which generally provides the most accurate genre predictions, you need to perform a manual installation step after running the `download_big_model.bat` script from the main project directory.

**Steps:**

1.  **Install the base `musicnn` library:** Ensure you have installed the `musicnn` Python package using `pip` (this is typically done as part of the main project's installation: `pip install -r requirements.txt`).
2.  **Run `download_big_model.bat` (from the main project directory):** Execute the `download_big_model.bat` script located in the root of the main music tagger project. This script downloads the `MSD_musicnn_big` model files.
3.  **Manually Copy `MSD_musicnn_big` to `site-packages`:**
    *   **Locate the downloaded folder:** Find the `MSD_musicnn_big` folder within the `musicnn_tagger/MSD_musicnn_big` directory in your project.
    *   **Find your Python `site-packages` directory:** Determine the location of your Python environment's `site-packages` directory (where `pip` installs packages). This is often within your default Python or Anaconda environment's `Lib\site-packages` or in your system's Python installation under `Lib\site-packages`.
    *   **Navigate to the `musicnn` directory:** Inside `site-packages`, locate the `musicnn` folder (created when you installed the `musicnn` package).
    *   **Copy the `MSD_musicnn_big` folder:** Copy the *entire* `MSD_musicnn_big` folder into the `musicnn` directory in `site-packages`.  The final path should resemble: `[your_site-packages_path]/musicnn/MSD_musicnn_big`.

**Importance:** This manual copying step is crucial. The `musicnn` library expects the `MSD_musicnn_big` model files to be located within its own directory in `site-packages`.

If you do not perform this manual installation, the `musicnn_tagger` module will still function, but it will fall back to using the `MTT_musicnn` model instead of `MSD_musicnn_big`.
