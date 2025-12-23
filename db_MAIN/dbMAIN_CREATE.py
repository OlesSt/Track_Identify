import sqlite3
import numpy as np
import librosa
import os
import config  # Import your config.py

TOP_PEAKS = 5  # number of peaks per frame

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


def create_db_and_index(folder_path=None, db_folder=None):
    """
    Index all audio files in the folder_path into the main database.
    If folder_path is None, use default path.
    If db_folder is None, use default config.DB_MAIN folder.
    """

    # --- set folder paths ---
    if folder_path is None:
        folder_path = "/Users/oles/Documents/progLOCAL_SHAZAM/musicMAIN"

    if db_folder is None:
        db_path = config.DB_MAIN
    else:
        os.makedirs(db_folder, exist_ok=True)
        db_path = os.path.join(db_folder, "main.db")

    # --- list audio files ---
    files = [f for f in os.listdir(folder_path)
             if os.path.splitext(f)[1].lower() in config.SUPPORTED_EXTENSIONS]

    if not files:
        print(f"ERROR: No supported audio files found in {folder_path}")
        return

    print(f"DEBUG: Found {len(files)} files to index")
    print(f"DEBUG: Creating database at {db_path}")

    # --- connect to DB ---
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # drop table if exists
    c.execute("DROP TABLE IF EXISTS fingerprints")

    # create table
    c.execute('''
        CREATE TABLE fingerprints (
            track_name TEXT,
            frame_index INTEGER,
            peak_frequency REAL
        )
    ''')

    # --- process each file ---
    for track_file in files:
        track_path = os.path.join(folder_path, track_file)
        print(f"\nDEBUG: Loading track: {track_path}")
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

        # extract peaks
        peaks_per_frame = extract_peaks(S, sr, top_n=TOP_PEAKS)

        # insert into DB
        for frame_index, freqs in peaks_per_frame:
            for peak_hz in freqs:
                c.execute(
                    "INSERT INTO fingerprints (track_name, frame_index, peak_frequency) VALUES (?, ?, ?)",
                    (track_file, frame_index, peak_hz)
                )

        print(f"DEBUG: Indexed '{track_file}' ({len(peaks_per_frame)} frames, {TOP_PEAKS} peaks per frame)")

    conn.commit()
    conn.close()
    print("\nDEBUG: Finished processing all tracks")



if __name__ == "__main__":
    create_db_and_index()
