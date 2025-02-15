# 🎵🤖 Music Tagger: AI & Last.fm Genre Magic! ✨

This project is a Python-powered music tagger that automatically suggests and sets genres for your music files. 🎧 It's like having a super-smart music librarian! 🤓 It uses two awesome sources to figure out the genres:

1.  **🧠 AI Genre Prediction (musicnn):**  Uses the power of deep learning (the `musicnn` library) to *listen* to your music and predict the genres. It's got multiple AI "brains" (`MSD_musicnn_big`, `MTT_musicnn`, `MTT_vgg`, `MSD_musicnn`, and `MSD_vgg`) for extra accuracy! If the biggest brain (`MSD_musicnn_big`) isn't available, it'll use a slightly smaller one (`MTT_musicnn`) so you always get suggestions.  We've even included a handy script (`download_big_model.bat`) to get the big brain!
2.  **🧑‍🤝‍🧑 Last.fm API:**  Asks the Last.fm community for their genre opinions! It checks for tags based on the track and artist, so you get the wisdom of the crowds. If it can't find track-specific tags, it'll use artist tags.

This tagger works with tons of music file types: `.mp3`, `.m4a`, `.flac`, `.ogg`, `.opus`, `.oga`, `.spx`, `.wav`, `.aiff`, `.aif`, `.asf`, `.wma`, `.wmv`, `.ape`, and `.wv`.  It uses the `mutagen` library to handle all the metadata magic. 🧙‍♂️

## Features 🌟

*   **🤖🤝🧑‍🤝‍🧑 Automated Genre Suggestions:**  Combines AI smarts and Last.fm's community tags for the best genre suggestions.
*   **🧠 Multiple AI Models:** Uses several `musicnn` models (like having multiple experts!) with a backup plan for maximum accuracy and reliability.
*   **🎶 Last.fm Integration:** Gets the top tags from Last.fm based on your song's artist and title.
*   **🏷️ Metadata Extraction:**  Pulls out the artist and track info from your music files' metadata (ID3, MP4, etc.).
*   **📁 Filename Parsing:** If the metadata is missing, it can even try to figure out the artist and track from the filename!
*   **✍️ Interactive Genre Selection:** Shows you the AI and Last.fm suggestions. You can:
    *   ✅ Pick one or more of the suggestions.
    *   ✏️ Type in your own genres (separate them with commas!).
    *   ❌ Skip tagging a file if you want.
*   **🚀 Auto-Apply Tags:**  Want it to be super fast?  Turn on auto-apply, and it'll automatically add the suggestions!
*   **🗂️ Batch Processing:**  Tag entire folders of music at once!
*   **🎧 Extensive File Format Support:** Works with all those file types listed above!
*   **🛡️ Robust Error Handling:**  Deals with problems like API errors, file issues, and missing models gracefully.
*   **🖥️ Interactive Menu System:** Easy-to-use menu with keyboard controls (arrow keys, Enter, Backspace, Esc) to:
    *   📂 Pick your music folder.
    *   ▶️ Start the tagging!
    *   ⚙️ Change settings (auto-apply, AI model count, how sure the AI needs to be, turn AI and Last.fm on/off).
    *   💾 Save your settings.
*   **⚙️ Settings Management:** Uses a `.env` file (like a secret settings file) and some clever code to keep track of your API key, preferences, and more.

## Installation 🚀

### Prerequisites

*   **🐍 Python:** You'll need Python 3.7.16 (or a compatible version). Anaconda is a great way to get Python!
*   **pip:** Make sure you have `pip` installed (it usually comes with Python).

### Steps

1.  **Get the Code! 📦**
    *   Clone the repository (if you know Git):
        ```bash
        git clone <repository_url>
        cd <project_directory>
        ```
    *   Or, download the project as a ZIP file and extract it.

2.  **Install the Required Packages 🛠️:**

    ```bash
    pip install -r requirements.txt
    ```

    Or, install them one by one:

    ```bash
    pip install pydantic requests mutagen musicnn python-dotenv colorama keyboard
    ```

3.  **Set up Your Last.fm API Key 🔑:**

    *   Get a free API key from Last.fm: [https://www.last.fm/api/account/create](https://www.last.fm/api/account/create)
    *   Create a file named `.env` in the main project folder.
    *   Put your API key and other settings in the `.env` file like this and activate LASTFM_ENABLED=TRUE:

        ```
        LASTFM_API_KEY=YOUR_LASTFM_API_KEY
        AUTO_APPLY_TAGS=FALSE
        DEFAULT_MUSIC_DIR=
        MUSICNN_ENABLED=TRUE
        MUSICNN_MODEL_COUNT=5
        MUSICNN_THRESHOLD_WEIGHT=0.2
        MUSICNN_GENRES_COUNT=5
        LASTFM_ENABLED=FALSE
        LASTFM_THRESHOLD_WEIGHT=0.6
        ```
        **Important:** Replace `YOUR_LASTFM_API_KEY` with your *actual* key!  The other settings have good defaults, but you can change them.  **Keep your `.env` file secret! Don't share it or put it in version control.**

4.  **(Optional, but HIGHLY Recommended) Get the Big AI Brain! 🧠💪:**

    *   **Make sure you installed `musicnn`** (from step 2).
    *   **Run the download script:**
        ```bash
        download_big_model.bat
        ```
        This will download the `MSD_musicnn_big` model files (it's a big one!).
    *   **Manual Installation (Super Important!):** After the script finishes, you need to *manually* copy the downloaded `MSD_musicnn_big` folder.
        *   **Find the downloaded folder:** It'll be in `musicnn_tagger/MSD_musicnn_big`.
        *   **Find your Python's `site-packages` folder:** This is where Python keeps its libraries. It's usually:
            *   Inside your Anaconda environment's `Lib\site-packages` folder (if you're using Anaconda).
            *   Or, in your main Python installation's `Lib\site-packages` folder.
        *   **Go into the `musicnn` folder inside `site-packages`.**
        *   **Copy the `MSD_musicnn_big` folder** into the `musicnn` folder.  The final path should look like: `[your_site-packages_path]/musicnn/MSD_musicnn_big`.

        **Why this manual step?**  It puts the big model files where the `musicnn` library can find them.  It's a bit of a hassle, but it's worth it for much better AI accuracy!

    If you skip this step, the tagger will still work, but it'll use the `MTT_musicnn` model, which is a bit less powerful.

## Usage 🎶

1.  **Open your terminal and go to the project directory.**

2.  **Run the `main.py` script:**

    ```bash
    python main.py
    ```

3.  **The Interactive Menu 🪄:**

    *   You'll see a menu on your screen.
    *   Use the **up** and **down** arrow keys to move around.
    *   Use the **left** and **right** arrow keys to change settings. Hold **Shift** with the arrow keys to change them faster!
    *   Press **Enter** to select something.
    *   Press **Backspace** to go back.
    *   Press **Esc** to go back to the main menu.

4.  **Menu Options 🎛️:**

    *   **Select Music Root Folder 📂:** Pick the folder where your music lives. On Windows, a file selection box will pop up. On other systems, you'll type in the path.
    *   **Process Directory ▶️:**  Start tagging the music in the folder you selected!
    *   **Settings ⚙️:**
        *   **Processing Engine:**
            *   **Musicnn AI Tagger:**
                *   **Enable/Disable:** Turn the AI on or off.
                *   **Models Count:** Choose how many AI models to use (1-5). More models = more accuracy, but it takes longer.
                *   **Threshold Weight:**  How sure the AI needs to be before suggesting a genre (0.0 - 1.0).
                *   **Genres Count:** How many genres should the AI consider (1-10)
            *   **LastFM Grabber:**
                *   **Enable/Disable:** Turn Last.fm on or off.
                *   **Threshold Weight:** How sure Last.fm needs to be about a tag (0.0 - 1.0).
        *   **Auto-apply Tags:** Turn on automatic tagging (no need to confirm each suggestion).

    *   **Exit 🚪:**  Quit the program.

5.  **The Tagging Process (when you click "Process Directory") 🏷️:**

    *   The script goes through each music file in your folder.
    *   For each file:
        *   It shows AI suggestions (if enabled) in cyan.
        *   It shows Last.fm suggestions (if enabled) in magenta.
        *   It asks you to enter genres.
        *   You can:
            *   Type a genre name.
            *   Type one of the suggestions (exactly as it's shown).
            *   Type multiple genres, separated by commas (like `Rock, Indie, Alternative`).
            *   Type `skip` to skip the file.
            *   Just press Enter to try again.
    *   If you turned on "Auto-apply Tags," it'll automatically add the suggestions without asking you.

6.  **Settings are Saved! 💾:**  Any changes you make in the menu are saved to the `.env` file, so you don't have to set them up every time.

## Project Structure 📁
```
. ├── .env # Secret settings file (API key, etc.) - DON'T SHARE THIS! 
  ├── main.py # The main script you run 
  ├── music_tagger.py # The core tagging logic 
  ├── README.md # This file! 
  ├── requirements.txt # List of Python packages you need 
  ├── download_big_model.bat # Script to download the big AI model 
  ├── lastfm_tagger/ # Code for getting tags from Last.fm 
  │   ├── api_client.py # Talks to the Last.fm API 
  │   ├── config.py # Last.fm settings 
  │   ├── lastfm_tagger.py # Gets and processes Last.fm tags 
  │   ├── models.py # (Currently unused) 
  │   ├── parser.py # (Currently unused) 
  │   └── init.py 
  ├── musicnn_tagger/ # Code for AI genre prediction 
  │   ├── tagger.py # Uses the musicnn models 
  │   ├── taggram.py # Works with musicnn's output 
  │   ├── config.py # Musicnn settings 
  │   ├── extractor.py # Lower-level musicnn functions 
  │   ├── MSD_musicnn_big/ # (Optional) The big AI model (if you downloaded it) 
  │   └── init.py
```
## Requirements 📝

*   Python 3.7.16
*   The packages listed in `requirements.txt`

## Troubleshooting ❓

*   **`MSD_musicnn_big` not found:** If you see an error about this model, either run `download_big_model.bat` to get it, or the program will use the `MTT_musicnn` model (which is still pretty good!).
*   **Last.fm API errors:** Double-check your `LASTFM_API_KEY` in the `.env` file.  You might also have internet connection problems.
*   **File format errors:** Make sure your music files are valid and that `mutagen` supports them.
*   **Tkinter errors (Windows):** If you have problems with the folder selection box, make sure Tkinter is installed with your Python.  The program will fall back to asking you to type the path if Tkinter isn't working.
*   **PowerShell errors (Windows):** If `download_big_model.bat` gives you an error, make sure you can run PowerShell scripts.

## License 📜

`MIT License`