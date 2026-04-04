import sqlite3
import os
from collections import defaultdict


def create_table(db_path: str) -> None:
    """
    Create the fingerprints table in db_path.
    Wipes any existing data — call once before indexing a folder.
    Creates parent directories if they don't exist.
    """
    parent = os.path.dirname(db_path)
    if parent:
        os.makedirs(parent, exist_ok=True)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS fingerprints")
    c.execute("""
        CREATE TABLE fingerprints (
            track_name      TEXT,
            frame_index     INTEGER,
            peak_frequency  REAL
        )
    """)
    conn.commit()
    conn.close()


def insert_peaks(db_path: str, track_name: str, peaks: list) -> None:
    """
    Insert peaks for one track into db_path.

    Args:
        db_path:    path to the SQLite DB (must already have table created)
        track_name: filename of the track
        peaks:      list of (frame_index, peak_frequency_hz) tuples
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.executemany(
        "INSERT INTO fingerprints (track_name, frame_index, peak_frequency) VALUES (?, ?, ?)",
        [(track_name, frame, freq) for frame, freq in peaks]
    )
    conn.commit()
    conn.close()


def load_peaks(db_path: str) -> dict:
    """
    Load all peaks from a DB.

    Returns:
        { track_name: [(freq_hash, frame_index), ...] }
        Frequencies are rounded to integers for fast hash lookup.
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        SELECT track_name, peak_frequency, frame_index
        FROM fingerprints
        ORDER BY frame_index
    """)
    tracks = defaultdict(list)
    for track_name, freq, frame_index in c.fetchall():
        tracks[track_name].append((round(freq), frame_index))
    conn.close()
    return tracks