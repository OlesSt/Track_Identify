import sqlite3
import os
from collections import defaultdict
from datetime import datetime


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


def create_hash_table(db_path: str) -> None:
    """
    Create the hashes table if it doesn't exist.
    Never wipes existing data.
    Creates parent directories if they don't exist.
    """
    parent = os.path.dirname(db_path)
    if parent:
        os.makedirs(parent, exist_ok=True)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS hashes (
            hash_int     INTEGER,
            track_name   TEXT,
            anchor_frame INTEGER
        )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_hash ON hashes (hash_int)")
    conn.commit()
    conn.close()


def get_indexed_tracks(db_path: str) -> set:
    """
    Returns a set of track names already in the DB.
    Returns empty set if DB doesn't exist yet.
    """
    if not os.path.exists(db_path):
        return set()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT DISTINCT track_name FROM hashes")
    tracks = {row[0] for row in c.fetchall()}
    conn.close()
    return tracks


def insert_hashes(db_path: str, track_name: str, hashes: list) -> None:
    """
    Insert hashes for one track into db_path.

    Args:
        db_path:    path to the SQLite DB
        track_name: filename of the track
        hashes:     list of (hash_int, anchor_frame) tuples from pair_peaks()
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.executemany(
        "INSERT INTO hashes (hash_int, track_name, anchor_frame) VALUES (?, ?, ?)",
        [(h, track_name, frame) for h, frame in hashes]
    )
    conn.commit()
    conn.close()


def load_hashes(db_path: str) -> dict:
    """
    Load all hashes from a DB.

    Returns:
        { hash_int: [(track_name, anchor_frame), ...] }
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT hash_int, track_name, anchor_frame FROM hashes")
    lookup = {}
    for hash_int, track_name, anchor_frame in c.fetchall():
        if hash_int not in lookup:
            lookup[hash_int] = []
        lookup[hash_int].append((track_name, anchor_frame))
    conn.close()
    return lookup


def get_avg_hashes_per_track(db_path: str) -> int:
    """Returns average hash count per track in the DB."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT COUNT(*), COUNT(DISTINCT track_name) FROM hashes")
    total, tracks = c.fetchone()
    conn.close()
    if not tracks:
        return 0
    return total // tracks


def create_metadata_table(db_path: str) -> None:
    """
    Create metadata table if it doesn't exist.
    Stores creation date, last update date.
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS metadata (
            key   TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    now = datetime.now().strftime("%d.%m.%Y  %H:%M")
    c.execute("""
        INSERT OR IGNORE INTO metadata (key, value) VALUES ('created', ?)
    """, (now,))
    conn.commit()
    conn.close()


def update_metadata_last_update(db_path: str) -> None:
    """Update last update timestamp."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    now = datetime.now().strftime("%d.%m.%Y  %H:%M")
    c.execute("""
        INSERT OR REPLACE INTO metadata (key, value) VALUES ('updated', ?)
    """, (now,))
    conn.commit()
    conn.close()


def get_library_info(db_path: str) -> dict:
    """
    Returns library metadata and track list with hash counts.
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("SELECT key, value FROM metadata")
    meta = dict(c.fetchall())

    c.execute("""
        SELECT track_name, COUNT(*) as hash_count
        FROM hashes
        GROUP BY track_name
        ORDER BY track_name
    """)
    tracks = c.fetchall()
    conn.close()

    return {
        "created": meta.get("created", "unknown"),
        "updated": meta.get("updated", "never"),
        "tracks": tracks
    }