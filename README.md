# Music Tagger with AI and Last.fm Genre Suggestions

This project is a Python-based music tagger that automatically suggests and sets genres for your music files. It leverages two primary sources for genre suggestions:

1.  **AI-based Genre Prediction (musicnn):** Uses deep learning models from the `musicnn` library to analyze audio content and predict relevant genres.  It supports multiple models for robust predictions, including `MSD_musicnn_big`, `MTT_musicnn`, `MTT_vgg`, `MSD_musicnn`, and `MSD_vgg`.  A fallback mechanism ensures that if `MSD_musicnn_big` is unavailable, `MTT_musicnn` is used.  A batch script (`download_big_model.bat`) is provided to download the larger `MSD_musicnn_big` model.
2.  **Last.fm API:** Queries the Last.fm API to fetch genre tags based on track and artist metadata, providing community-driven genre classifications.  It attempts to retrieve track-specific tags first, and if none are found, it falls back to artist-level tags.

The tagger supports setting genre tags for a wide variety of audio file formats: `.mp3`, `.m4a`, `.flac`, `.ogg`, `.opus`, `.oga`, `.spx`, `.wav`, `.aiff`, `.aif`, `.asf`, `.wma`, `.wmv`, `.ape`, and `.wv`. It uses `mutagen` for robust metadata handling across these formats.

## Features

*   **Automated Genre Suggestion:** Combines AI-powered genre prediction and Last.fm's community tags for comprehensive genre suggestions.
*   **Multiple AI Models:** Utilizes several `musicnn` models (`MSD_musicnn_big`, `MTT_musicnn`, `MTT_vgg`, `MSD_musicnn`, `MSD_vgg`) with a fallback system for increased accuracy and reliability.
*   **Last.fm Integration:** Fetches top tags from Last.fm based on artist and track information, with a fallback to artist tags if track tags are unavailable.
*   **Metadata Extraction:** Extracts artist and track information from music file metadata (ID3, MP4, and other format-specific tags).
*   **Filename Parsing:** Fallback mechanism to extract artist and track from filenames if metadata is not available.
*   **Interactive Genre Selection:**  Presents AI and Last.fm suggestions to the user.  The user can:
    *   Select one or more of the suggested genres.
    *   Enter custom genres (comma-separated).
    *   Skip tagging the current file.
*   **Auto-Apply Tags:** An option to automatically apply the suggested genres without user interaction.
*   **Batch Processing:** Processes entire directories of music files.
*   **Extensive File Format Support:**  Handles `.mp3`, `.m4a`, `.flac`, `.ogg`, `.opus`, `.oga`, `.spx`, `.wav`, `.aiff`, `.aif`, `.asf`, `.wma`, `.wmv`, `.ape`, and `.wv` files.
*   **Robust Error Handling:** Includes error logging and handling for API requests, file operations, metadata extraction, and model loading.
*   **Interactive Menu System:** A console-based menu with keyboard navigation (arrow keys, Enter, Backspace, Esc) allows users to:
    *   Select the music root directory.
    *   Start the tagging process.
    *   Adjust settings (auto-apply, AI model count, thresholds, enable/disable AI and Last.fm).
    *   Save settings to a `.env` file.
*   **Loading Animation:**  A visual loading animation is displayed during AI processing.
* **Settings Management:** Uses a `.env` file and dedicated settings classes (`AppSettings`, `MusicnnSettings`, `LastFMSettings`) to manage configuration, including API keys, thresholds, and enabled features.  Settings are saved and loaded automatically.

## Installation

### Prerequisites

*   **Python:** Python 3.7.16 (or a compatible version).  Anaconda is recommended.
*   **pip:** Ensure `pip` is installed.

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

    Alternatively, install individually:

    ```bash
    pip install pydantic requests mutagen musicnn python-dotenv colorama
    ```

3.  **Set up Last.fm API Key:**

    *   Obtain a Last.fm API key at [https://www.last.fm/api/account/create](https://www.last.fm/api/account/create).
    *   Create a `.env` file in the project's root directory.
    *   Add your Last.fm API key and other settings to the `.env` file:

        ```
        LASTFM_API_KEY=YOUR_LASTFM_API_KEY
        AUTO_APPLY_TAGS=FALSE
        DEFAULT_MUSIC_DIR=
        MUSICNN_ENABLED=TRUE
        MUSICNN_MODEL_COUNT=5
        MUSICNN_THRESHOLD_WEIGHT=0.2
        MUSICNN_GENRES_COUNT=5
        LASTFM_ENABLED=TRUE
        LASTFM_THRESHOLD_WEIGHT=0.6
        ```
        Replace `YOUR_LASTFM_API_KEY` with your actual key.  The other settings have default values but can be customized. **Keep your `.env` file secure and do not commit it to version control.**

4. **(Optional but Recommended) Download and Install the `MSD_musicnn_big` model for Enhanced AI Accuracy:**

    *   **Install the base `musicnn` library:** Ensure you have installed `musicnn` as described in step 2 (`pip install -r requirements.txt` or `pip install musicnn`).
    *   **Run the download script:** Execute the `download_big_model.bat` script:
        ```bash
        download_big_model.bat
        ```
        This script will download the `MSD_musicnn_big` model files.
    *   **Manual Installation (Important):**  After the script completes, you need to manually copy the downloaded `MSD_musicnn_big` folder.  Locate the downloaded folder at `musicnn_tagger/MSD_musicnn_big`.
        *   **Find your Python `site-packages` directory:**  This is where Python libraries installed by `pip` are stored. The location varies depending on your Python installation.  Common locations include:
            *   Within your Anaconda environment's `Lib\site-packages` folder (if using Anaconda).
            *   In your system's Python installation directory under `Lib\site-packages`.
        *   **Navigate to the `musicnn` directory within `site-packages`:**  Inside `site-packages`, find the `musicnn` folder (this folder was created when you installed `musicnn` using `pip`).
        *   **Copy `MSD_musicnn_big`:** Copy the *entire* `MSD_musicnn_big` folder that was downloaded by the batch script into the `musicnn` folder inside `site-packages`. The path should look something like: `[your_site-packages_path]/musicnn/MSD_musicnn_big`.

        **Note:** This manual step is necessary to place the larger `MSD_musicnn_big` model files in the correct location for the `musicnn` library to find them.

   This step is optional but highly recommended for significantly improved AI genre prediction accuracy. If you skip this step, the tagger will automatically fall back to the `MTT_musicnn` model.

## Usage

1.  **Navigate to the project directory in your terminal.**

2.  **Run the `main.py` script:**

    ```bash
    python main.py
    ```

3.  **Interactive Menu:**

    *   The script will launch an interactive menu.
    *   Use the **up** and **down** arrow keys to navigate.
    *   Use the **left** and **right** arrow keys to change values (e.g., increase/decrease thresholds).  Hold **Shift** with the arrow keys to change values by larger increments.
    *   Press **Enter** to select an option.
    *   Press **Backspace** to go back to the parent menu.
    *   Press **Esc** to return to the root menu.

4.  **Menu Options:**

    *   **Select Music Root Folder:**  Choose the directory containing your music files.  On Windows, a file dialog will open.  On other systems, you'll be prompted to enter the path in the console.
    *   **Process Directory:**  Starts the tagging process for the selected directory.
    *   **Settings:**
        *   **Processing Engine:**
            *   **Musicnn AI Tagger:**
                *   **Enable/Disable:** Turn the AI tagger on or off.
                *   **Models Count:**  Select the number of AI models to use (1-5). More models generally improve accuracy but increase processing time.
                *   **Threshold Weight:** Set the minimum confidence threshold for AI-suggested genres (0.0 - 1.0).
                *   **Genres Count:** Set the number of genres the AI should consider (1-10).
            *   **LastFM Grabber:**
                *   **Enable/Disable:** Turn the Last.fm tagger on or off.
                *   **Threshold Weight:** Set the minimum weight threshold for Last.fm tags (0.0 - 1.0).
        *   **Auto-apply Tags:** Toggle whether to automatically apply suggested tags without user confirmation.

    *   **Exit:**  Exits the program.

5.  **Genre Tagging Process (when "Process Directory" is selected):**

    *   The script will process each music file in the selected directory.
    *   For each file, it will:
        *   Display AI-suggested genres (if enabled) in cyan.
        *   Display Last.fm-suggested genres (if enabled) in magenta.
        *   Prompt you to enter genres.
        *   You can:
            *   Type a genre name.
            *   Choose from the suggested genres (type the exact suggestion).
            *   Enter multiple genres separated by commas (e.g., `Rock, Indie, Alternative`).
            *   Type `skip` to skip tagging the current file.
            *   Leave the input empty and press Enter to re-prompt.
    *   If "Auto-apply Tags" is enabled, the script will automatically set the genre tags based on the suggestions (if any) without prompting. If there are no suggestions, and auto-apply is on, the file will be skipped.

6.  **Settings are Saved:**  Changes you make in the menu are automatically saved to the `.env` file.

## Project Structure

```
.
├── .env                          # Environment file for API key and settings (keep secret)
├── main.py                       # Main script to run the music tagger and interactive menu
├── music_tagger.py              # MusicTagger class: core logic for tagging, metadata handling
├── README.md                     # Project documentation (this file)
├── requirements.txt              # List of Python package dependencies
├── download_big_model.bat        # Batch script to download the MSD_musicnn_big model
│
├── lastfm_tagger/                # Last.fm API integration
│   ├── api_client.py             # Client to interact with Last.fm API
│   ├── config.py                 # Configuration settings for LastFM (API key, URLs, thresholds)
│   ├── lastfm_tagger.py          # Logic to fetch and process Last.fm tags, including fallback to artist tags
│   ├── models.py                 # Pydantic models for Last.fm API responses (currently unused, but could be used for stricter typing)
│   ├── parser.py                 # Parsing API responses into Pydantic models (currently unused)
│   ├── README.md                 # Original README for lastfm_tagger (can be removed)
│   └── __init__.py               # Initializes lastfm_tagger package
│
└── musicnn_tagger/               # musicnn integration for AI genre prediction
    ├── tagger.py                 # Logic to use musicnn models, including model selection and fallback
    ├── taggram.py                # Functions for taggram processing and visualization (musicnn output)
    ├── config.py                 # Configuration settings for Musicnn (enabled, model count, thresholds)
    ├── extractor.py              # Lower-level musicnn extractor functions (used by tagger.py)
    ├── MSD_musicnn_big/          # (Optional) Directory containing the MSD_musicnn_big model (downloaded by download_big_model.bat)
    ├── README.md                 # Original README for musicnn_tagger (can be removed)
    └── __init__.py               # Initializes musicnn_tagger package
```

*   **`.env`**: Stores your Last.fm API key and application settings.  **Do not commit this file.**
*   **`main.py`**:  The entry point.  Handles the interactive menu, loads settings, and calls `MusicTagger`.
*   **`music_tagger.py`**:  The `MusicTagger` class orchestrates the tagging process.  It finds music files, extracts metadata, calls the AI and Last.fm taggers, and sets the genre tags.
*   **`lastfm_tagger/`**:  Handles Last.fm API interactions.
    *   `api_client.py`:  Makes requests to the Last.fm API.
    *   `config.py`:  Manages Last.fm-specific settings.
    *   `lastfm_tagger.py`:  Fetches tags, handles track/artist fallback, and filters by weight.
*   **`musicnn_tagger/`**:  Handles AI-based genre prediction.
    *   `tagger.py`:  Manages the `musicnn` models, including selection, fallback, and combining results.
    *   `taggram.py`:  Provides functions for working with `musicnn`'s taggram output.
    *   `config.py`: Manages Musicnn-specific settings.
    *   `extractor.py`: Lower level functions to use the `musicnn` extractor.
    *   `MSD_musicnn_big/`: Contains the (optional) larger `MSD_musicnn_big` model.
*   **`download_big_model.bat`**: Downloads the `MSD_musicnn_big` model.

## Requirements

*   Python 3.7.16
*   Packages listed in `requirements.txt`

## Troubleshooting

*   **`MSD_musicnn_big` not found:** If you get an error about the `MSD_musicnn_big` model, either run `download_big_model.bat` to download it, or the program will automatically use the `MTT_musicnn` model instead.
*   **Last.fm API errors:** Make sure your `LASTFM_API_KEY` in the `.env` file is correct.  Network connectivity issues can also cause API errors.
*   **File format errors:** If you encounter errors with specific files, ensure they are valid audio files and that `mutagen` supports them.  The `music_tagger.py` file includes extensive error handling for various file formats.
*   **Tkinter errors on Windows:** The folder selection dialog uses Tkinter.  If you encounter errors, ensure Tkinter is properly installed with your Python distribution.  The code includes a fallback to console input if Tkinter is unavailable.
* **PowerShell errors on Windows:** The `download_big_model.bat` script uses powershell. If you encounter errors, ensure that you have permissions to run scripts.

## License
`MIT License`
---