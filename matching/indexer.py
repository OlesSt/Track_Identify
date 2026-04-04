import os
import config
from audio.loader import load_audio
from audio.extractor import extract_peaks
from storage.db import create_table, insert_peaks


def index_folder(audio_folder: str, db_path: str) -> list:
    """
    Index all supported audio files in audio_folder into db_path.
    Works for both the main library (→ main.db) and query tracks (→ query.db).

    Args:
        audio_folder: path to folder containing audio files
        db_path:      path to the target SQLite DB

    Returns:
        List of log message strings (no print statements — caller decides what to do with them).
    """
    logs = []

    files = [
        f for f in os.listdir(audio_folder)
        if os.path.splitext(f)[1].lower() in config.SUPPORTED_EXTENSIONS
    ]

    if not files:
        return [f"ERROR: No supported audio files found in '{audio_folder}'"]

    logs.append(f"Found {len(files)} file(s) to index → '{db_path}'")
    create_table(db_path)

    for filename in files:
        path = os.path.join(audio_folder, filename)
        try:
            y, sr = load_audio(path)
            peaks = extract_peaks(y, sr)
            insert_peaks(db_path, filename, peaks)
            logs.append(f"  Indexed '{filename}' ({len(peaks)} peaks)")

        except Exception as e:
            logs.append(f"  ERROR indexing '{filename}': {e}")

    logs.append(f"Done.")
    return logs