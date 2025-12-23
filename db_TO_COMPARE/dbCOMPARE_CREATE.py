import sqlite3
import numpy as np
import librosa
import os
import config  # Your config.py with SAMPLE_RATE, MONO, FFT_SIZE, etc.

COMPARE_DB_PATH = config.DB_TO_COMPARE  # separate DB for comparison tracks
TRACKS_FOLDER = "/Users/oles/Documents/progLOCAL_SHAZAM/musicTEST"  # folder with tracks
TOP_PEAKS = 5  # number of peaks per frame, same as main DB

def extract_peaks(S, sr, top_n=TOP_PEAKS):
    """
    Extract top_n peaks per frame from spectrogram S (magnitude)
    Returns: List of tuples: [(frame_index, [freq1, freq2, ...]), ...]
    """
    peaks_per_frame = []
    for i in range(S.shape[1]):  # iterate over frames
        frame = S[:, i]
        top_indices = frame.argsort()[-top_n:][::-1]  # indices of top_n peaks
        freqs_hz = top_indices * sr / S.shape[0]  # convert bin to Hz
        peaks_per_frame.append((i, freqs_hz.tolist()))
    return peaks_per_frame


def add_tracks_for_comparison(folder_path=None, db_folder=None):
    if folder_path is None:
        folder_path = "/Users/oles/Documents/progLOCAL_SHAZAM/musicTEST"

    if db_folder is None:
        db_path = COMPARE_DB_PATH
    else:
        os.makedirs(db_folder, exist_ok=True)
        db_path = os.path.join(db_folder, "compare.db")

    print("\n=== ADD TRACK TO COMPARE DB ===")

    # Remove old DB if exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"DEBUG: Removed old DB '{db_path}'")

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Drop table if exists
    c.execute("DROP TABLE IF EXISTS compare_fingerprints")
    print("DEBUG: Dropped existing table 'compare_fingerprints' (if any)")

    # Create table
    c.execute('''
        CREATE TABLE compare_fingerprints (
            track_name TEXT,
            frame_index INTEGER,
            peak_frequency REAL
        )
    ''')
    print("DEBUG: Created table 'compare_fingerprints'")

    # --- iterate files ---
    files = [f for f in os.listdir(folder_path)
             if os.path.splitext(f)[1].lower() in config.SUPPORTED_EXTENSIONS]

    if not files:
        print(f"ERROR: No supported audio files found in {folder_path}")
        conn.close()
        return

    print(f"DEBUG: Found {len(files)} files to process")

    for file_name in files:
        track_path = os.path.join(folder_path, file_name)
        print(f"\nDEBUG: Processing track: {track_path}")
        y, sr = librosa.load(track_path, sr=None, mono=False)

        if config.MONO and y.ndim > 1:
            y = librosa.to_mono(y)

        if sr != config.SAMPLE_RATE:
            y = librosa.resample(y, orig_sr=sr, target_sr=config.SAMPLE_RATE)
            sr = config.SAMPLE_RATE

        y = y / np.max(np.abs(y))
        S = np.abs(librosa.stft(y, n_fft=config.FFT_SIZE,
                                hop_length=config.HOP_LENGTH,
                                window=config.WINDOW))

        peaks_per_frame = extract_peaks(S, sr, top_n=TOP_PEAKS)

        for frame_index, freqs in peaks_per_frame:
            for peak_hz in freqs:
                c.execute(
                    "INSERT INTO compare_fingerprints (track_name, frame_index, peak_frequency) VALUES (?, ?, ?)",
                    (file_name, frame_index, peak_hz)
                )

        print(f"DEBUG: Indexed '{file_name}' ({len(peaks_per_frame)} frames, {TOP_PEAKS} peaks per frame)")

    conn.commit()
    print(f"DEBUG: Committed all fingerprints to DB: {db_path}")
    conn.close()
    print("=== Finished processing all tracks for comparison ===\n\n")



if __name__ == "__main__":
    add_tracks_for_comparison()
