1.  **Install Python**:
    -   Ensure you have Python 3.9 or later installed. You can check your Python version by running `python --version` or `python3 --version` in your terminal or command prompt.
    -   If you don't have Python installed or have an older version, download and install it from the official Python website: [https://www.python.org/downloads/](https://www.python.org/downloads/)

2.  **Install `pydantic` and `requests` libraries**:
    -   Open your terminal or command prompt.
    -   Use `pip` (Python package installer) to install the required libraries. Run the following command:
        ```bash
        pip install pydantic requests
        ```
        or if you are using `pip3`:
        ```bash
        pip3 install pydantic requests
        ```

3.  **Create project files**:
    -   Create a new directory for your project (e.g., `lastfm_tag_parser`).
    -   Navigate into this directory using your terminal (`cd lastfm_tag_parser`).
    -   Create the following files in this directory, and copy-paste the code blocks into the respective files:
        -   `config.py`
        -   `api_client.py`
        -   `parser.py`
        -   `main.py`
        -   `models.py`
        -   `.env` (create an empty file named `.env`)

4.  **Set up Last.fm API Key**:
    -   You need a Last.fm API key to use their API. If you don't have one, you can get it by:
        -   Going to [https://www.last.fm/api/account/create](https://www.last.fm/api/account/create) and follow the instructions to create an API account.
    -   Once you have your API key, open the `.env` file you created.
    -   Add the following line to the `.env` file, replacing `YOUR_LASTFM_API_KEY` with your actual API key:
        ```
        LASTFM_API_KEY=YOUR_LASTFM_API_KEY
        ```
    -   **Important**:  Do not commit your `.env` file with your API key to version control if you are using Git or similar, as it contains sensitive information. `.env` is usually added to `.gitignore`.

5.  **Run the `main.py` script**:
    -   In your terminal, make sure you are still in the project directory (`lastfm_tag_parser`).
    -   Run the `main.py` script using Python:
        ```bash
        python main.py
        ```
        or if you are using `python3` as your default Python 3 command:
        ```bash
        python3 main.py
        ```

6.  **Interact with the script**:
    -   The script will prompt you to enter the artist name and track name.
    -   Enter the artist name when prompted (e.g., `Radiohead`) and press Enter.
    -   Enter the track name when prompted (e.g., `Paranoid Android`) and press Enter.
    -   The script will then query the Last.fm API and display the tags for the track if found. If tags are found, they will be printed in the terminal. If no tags are found, or if there is an error, a corresponding message will be displayed.

**Example Interaction in the terminal:**

```text
Enter artist name: Radiohead
Enter track name: Paranoid Android

Tags for 'Paranoid Android' by 'Radiohead':
- alternative
- rock
- british
- classic rock
- indie