import os
import config
from audio.loader import load_audio
from audio.extractor import extract_peaks, pair_peaks
from storage.db import create_hash_table, insert_hashes, get_indexed_tracks
from storage.db import create_metadata_table, update_metadata_last_update

def index_folder(audio_folder: str, db_path: str) -> list:
    """
    Index all supported audio files in audio_folder into db_path.
    Skips tracks already indexed by filename.
    Works for both the main library (→ main.db) and query tracks (→ query.db).

    Args:
        audio_folder: path to folder containing audio files
        db_path:      path to the target SQLite DB

    Returns:
        List of log message strings.
    """
    logs = []

    files = [
        f for f in os.listdir(audio_folder)
        if os.path.splitext(f)[1].lower() in config.SUPPORTED_EXTENSIONS
    ]

    if not files:
        return [f"ERROR: No supported audio files found in '{audio_folder}'"]

    create_hash_table(db_path)
    create_metadata_table(db_path)
    already_indexed = get_indexed_tracks(db_path)

    new_files = [f for f in files if f not in already_indexed]
    skipped = len(files) - len(new_files)

    logs.append(f"Found {len(files)} file(s) in folder — {len(new_files)} new, {skipped} already indexed")

    if not new_files:
        logs.append("Library is up to date. Nothing to add.")
        return logs

    for filename in new_files:
        path = os.path.join(audio_folder, filename)
        try:
            y, sr = load_audio(path)
            peaks = extract_peaks(y, sr)
            hashes = pair_peaks(peaks, sr)
            insert_hashes(db_path, filename, hashes)
            logs.append(f"  Added '{filename}' ({len(peaks)} peaks → {len(hashes)} hashes)")
        except Exception as e:
            logs.append(f"  ERROR indexing '{filename}': {e}")

    update_metadata_last_update(db_path)
    logs.append("Done.")
    return logs