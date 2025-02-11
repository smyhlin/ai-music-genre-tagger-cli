# Last.fm Tagger Module

This module provides functionality to retrieve genre tags from the Last.fm API for music tracks and artists. It's designed as part of a larger music tagging application.

## Features

*   **Track Tag Retrieval:** Fetches top tags for a specific track using the `track.getTopTags` Last.fm API method.
*   **Artist Tag Retrieval:** Fetches top tags for an artist using the `artist.getTopTags` Last.fm API method.
*   **Fallback Mechanism:** If no track-specific tags are found, the module automatically falls back to retrieving artist tags.
*   **Tag Filtering:** Filters tags based on a configurable minimum weight (count) threshold.
*   **Tag Limiting:** Returns a configurable maximum number of top tags.
*   **Error Handling:** Includes robust error handling for API requests and response parsing.
*   **Configuration:** Uses a `config.py` file and the `LastFMSettings` class to manage API keys, base URLs, and other settings.  Settings are loaded from and saved to a `.env` file in the parent directory.
*   **Pydantic Models:**  Uses Pydantic models (`models.py`) for structured data representation and validation of API responses (though the main `get_lastfm_tags` function returns a simple list of tuples).
*   **Logging:** Uses Python's `logging` module for informative messages and error reporting.

## Files

*   **`__init__.py`**:  Makes the `lastfm_tagger` directory a Python package and exports the main `get_lastfm_tags` function.
*   **`api_client.py`**:  Contains the `LastFMClient` class, responsible for making requests to the Last.fm API.  It handles URL construction, API key inclusion, and error handling for various request issues (HTTP errors, connection errors, timeouts, JSON decoding errors).
*   **`config.py`**:  Defines the `LastFMSettings` class, which manages configuration settings.  It loads settings from a `.env` file (located in the parent directory) and provides methods to save changes back to the `.env` file.
*   **`lastfm_tagger.py`**:  Contains the core logic:
    *   `get_lastfm_tags(artist_name, track_name, top_n=5, min_weight=60)`:  This is the main function.  It retrieves tags, handles the track/artist fallback, filters tags by weight, and limits the number of returned tags.
    *   `main(artist_name, track_name)`:  A simple example function demonstrating how to use `get_lastfm_tags`.
*   **`models.py`**:  Defines Pydantic models for representing Last.fm API responses in a structured way:
    *   `TagModel`: Represents a single tag (name, URL, count).
    *   `TopTagsListModel`: Represents a list of tags.
    *   `TrackGetTopTagsResponse`: Represents the full response from the `track.getTopTags` API method.
    *   `ArtistGetTopTagsResponse`: Represents the full response from the `artist.getTopTags` API method.
*   **`parser.py`**: Contains functions to parse the raw JSON responses from the Last.fm API into Pydantic models:
    *   `parse_track_tags(api_response)`: Parses the response from `track.getTopTags`.
    *   `parse_artist_tags(api_response)`: Parses the response from `artist.getTopTags`.

## Usage

The primary function to use is `get_lastfm_tags` from `lastfm_tagger.py`:

```python
from lastfm_tagger import get_lastfm_tags

# Example: Get top 3 tags for a track, with a minimum weight of 70.
artist = "Radiohead"
track = "Paranoid Android"
top_tags = get_lastfm_tags(artist, track, top_n=3, min_weight=70)

if top_tags:
    for tag, weight in top_tags:
        print(f"{tag}: {weight}")
else:
    print("No tags found.")

```

**Explanation:**

1.  **Import:** Import the `get_lastfm_tags` function.
2.  **Call `get_lastfm_tags`:**
    *   `artist_name`:  The artist's name (string).
    *   `track_name`: The track's name (string).
    *   `top_n`:  (Optional) The maximum number of tags to return (default is 5).
    *   `min_weight`: (Optional) The minimum tag weight (count) for a tag to be included (default is 60).  This is *not* a percentage; it's the raw count from the Last.fm API.
3.  **Process Results:** The function returns a list of tuples.  Each tuple contains the tag name (string) and its weight (integer).  If no tags are found (or no tags meet the criteria), it returns an empty list.

## Configuration

The module uses a `.env` file (located in the project's root directory, *not* within the `lastfm_tagger` directory itself) to store settings.  You need to create this file and add your Last.fm API key:

```
LASTFM_API_KEY=your_lastfm_api_key
LASTFM_ENABLED=True
LASTFM_THRESHOLD_WEIGHT=0.6
```
* **`LASTFM_API_KEY`**:  Your Last.fm API key (required). Obtain one from [https://www.last.fm/api/account/create](https://www.last.fm/api/account/create).
*   **`LASTFM_ENABLED`**:  A boolean (True/False) to enable or disable the Last.fm tagger.
*   **`LASTFM_THRESHOLD_WEIGHT`**: A float representing minimum tag weight. This value is used in `music_tagger.py` to filter Last.fm tags.

The `LastFMSettings` class in `config.py` handles loading and saving these settings.

## Dependencies
*   `python 3.7.16`: You can use anaconda environment (work only with this version of python)
*   `requests`: For making HTTP requests to the Last.fm API.
*   `python-dotenv`: For loading settings from the `.env` file.
*   `pydantic`: For data validation and structuring using Pydantic models.

These dependencies should be installed as part of the main project's `requirements.txt`.

## Notes

*   The `models.py` and `parser.py` files are present and provide a more structured way to handle API responses using Pydantic. While the current implementation of `get_lastfm_tags` doesn't directly use the parsed objects for its return value (it returns a list of tuples), the parsing logic is in place and could be used for more advanced features or stricter type checking in the future.
*   The logging level is set to INFO in `lastfm_tagger.py`.  You can adjust this if needed.
* The `main` function in `lastfm_tagger.py` is for standalone testing and demonstration purposes.