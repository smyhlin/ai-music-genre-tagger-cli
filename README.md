      
# Music Tagger with AI and Last.fm Genre Suggestions

This project is a Python-based music tagger that automatically suggests and sets genres for your music files. It leverages two primary sources for genre suggestions:

1.  **AI-based Genre Prediction (musicnn):** Uses deep learning models from the `musicnn` library to analyze audio content and predict relevant genres.
2.  **Last.fm API:** Queries the Last.fm API to fetch genre tags based on track and artist metadata, providing community-driven genre classifications.

The tagger supports setting genre tags for `.mp3` and `.m4a` files and is designed to be easily used for tagging entire music directories.

## Features

*   **Automated Genre Suggestion:** Combines AI-powered genre prediction and Last.fm's community tags for comprehensive genre suggestions.
*   **Multiple AI Models:** Utilizes several `musicnn` models for more robust genre predictions.
*   **Last.fm Integration:** Fetches top tags from Last.fm based on artist and track information.
*   **Metadata Extraction:** Extracts artist and track information from music file metadata (ID3 and MP4 tags).
*   **Filename Parsing:** Fallback mechanism to extract artist and track from filenames if metadata is not available.
*   **Interactive Genre Selection:** Prompts users to review and select genres from suggestions or input custom genres.
*   **Batch Processing:** Processes entire directories of music files.
*   **Supports `.mp3` and `.m4a` files:** Compatible with common audio file formats.
*   **Robust Error Handling:** Includes error logging and handling for API requests, file operations, and metadata extraction.

## Installation

### Prerequisites

*   **Python:** Python 3.7.16. You can install it from Anaconda conda extention.
*   **pip:**  Ensure `pip` is installed with your Python installation.

### Steps

1.  **Clone the repository (or download and extract the zip file):**

    ```bash
    git clone <repository_url>
    cd <project_directory>
    ```

2.  **Install required Python packages:**

    ```bash
    pip install -r requirements.txt
    ```

    Alternatively, you can install the dependencies individually:

    ```bash
    pip install pydantic requests mutagen musicnn
    ```

3.  **Set up Last.fm API Key:**

    *   Obtain a Last.fm API key by creating an API account at [https://www.last.fm/api/account/create](https://www.last.fm/api/account/create).
    *   Create a `.env` file in the project's root directory.
    *   Add your Last.fm API key to the `.env` file as follows:

        ```
        LASTFM_API_KEY=YOUR_LASTFM_API_KEY
        ```

        Replace `YOUR_LASTFM_API_KEY` with your actual API key. **Ensure you keep your `.env` file secure and do not commit it to version control.**

## Usage

1.  **Navigate to the project directory in your terminal.**

2.  **Run the `main.py` script, providing the path to your music directory as a command-line argument.**

    ```bash
    python main.py <path_to_your_music_directory>
    ```

    Replace `<path_to_your_music_directory>` with the actual path to the directory containing your music files. For example:

    ```bash
    python main.py D:\Music\MyLibrary
    ```

3.  **Interactive Genre Tagging:**

    *   The script will process each music file in the specified directory.
    *   For each file, it will display AI and Last.fm suggested genres.
    *   You will be prompted to enter genres for the current music file. You have the following options:
        *   Type a genre name to use it.
        *   Choose from the suggested genres (type the exact suggestion).
        *   Enter multiple genres separated by commas (e.g., `Rock, Indie, Alternative`).
        *   Type `skip` to skip tagging the current file.
        *   Leave input empty and press Enter to re-prompt.

4.  **Genre Tags are Set:** Once you enter a genre (or genres), the script will set the genre tag(s) in the music file's metadata.

## Project Structure

    

```
.
├── .env # Environment file for API key (keep secret)
├── main.py # Main script to run the music tagger
├── music_tagger.py # Main MusicTagger class and logic
├── README.md # Project documentation (this file)
├── requirements.txt # List of Python package dependencies
│
├── lastfm_tagger/ # Last.fm API integration components
│ ├── api_client.py # Client to interact with Last.fm API
│ ├── config.py # Configuration settings (API key, URLs)
│ ├── lastfm_tagger.py # Logic to fetch and process Last.fm tags
│ ├── models.py # Pydantic models for Last.fm API responses
│ ├── parser.py # Parsing API responses into Pydantic models
│ ├── README.md # README for lastfm_tagger module (original, can be removed or updated)
│ ├── init.py # Initializes lastfm_tagger package
│
└── musicnn_tagger/ # musicnn integration for AI genre prediction
├── tagger.py # Logic to use musicnn models for genre prediction
├── taggram.py # Functions related to taggram processing and visualization (musicnn output)
├── init.py # Initializes musicnn_tagger package
```
      
*   **`.env`**: Stores your Last.fm API key. **Do not commit this file to version control.**
*   **`main.py`**: The entry point to execute the music tagging process.
*   **`music_tagger.py`**: Contains the `MusicTagger` class that orchestrates the entire tagging process, integrating AI and Last.fm suggestions.
*   **`lastfm_tagger/`**:  A Python package dedicated to handling interactions with the Last.fm API, including configuration, API client, data parsing, and models.
*   **`musicnn_tagger/`**: A Python package that integrates the `musicnn` library for AI-based music genre tagging.

## Requirements

*   Python 3.7.16
*   Packages listed in `requirements.txt` (install using `pip install -r requirements.txt`)

## License

[Specify License, e.g., MIT License, or remove this section if you don't want to specify a license]

---

This `README.md` provides a comprehensive guide to understanding, installing, and using the Music Tagger project. If you encounter issues or have suggestions, please refer to the project's issue tracker or contact the maintainers.

    