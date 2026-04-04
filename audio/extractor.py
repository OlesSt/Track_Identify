import numpy as np
import librosa
import config


def extract_peaks(y: np.ndarray, sr: int) -> list:
    """
    Compute STFT and extract the top spectral peaks per frame.
    No file I/O. No database. Pure signal processing.

    Args:
        y:  audio time series (numpy array)
        sr: sample rate

    Returns:
        List of (frame_index, peak_frequency_hz) tuples — one tuple per peak.
        A 3-minute track at default settings produces ~(frames * PEAKS_PER_FRAME) tuples.
    """
    S = np.abs(librosa.stft(
        y,
        n_fft=config.FFT_SIZE,
        hop_length=config.HOP_LENGTH,
        window=config.WINDOW
    ))

    n_bins = S.shape[0]
    peaks = []

    for frame_index in range(S.shape[1]):
        frame = S[:, frame_index]
        top_indices = frame.argsort()[-config.PEAKS_PER_FRAME:][::-1]
        for bin_index in top_indices:
            freq_hz = bin_index * sr / (n_bins * 2 - 2)  # convert bin → Hz (corrected formula)
            peaks.append((frame_index, freq_hz))

    return peaks


def pair_peaks(peaks: list, sr: int) -> list:
    """
    Generate hashes from peak pairs.
    For each anchor peak, pair it with nearby peaks within the time window.

    Args:
        peaks: list of (frame_index, freq_hz) from extract_peaks()
        sr:    sample rate

    Returns:
        List of (hash_int, anchor_frame) tuples — one per valid pair.
    """
    frames_per_sec = sr / config.HOP_LENGTH
    min_delta = int(config.PAIR_MIN_TIME_DELTA * frames_per_sec)
    max_delta = int(config.PAIR_MAX_TIME_DELTA * frames_per_sec)

    hashes = []

    for i, (anchor_frame, anchor_freq) in enumerate(peaks):
        pairs_found = 0

        for j in range(i + 1, len(peaks)):
            target_frame, target_freq = peaks[j]
            delta = target_frame - anchor_frame

            if delta < min_delta:
                continue
            if delta > max_delta:
                break

            freq1 = int(anchor_freq)
            freq2 = int(target_freq)
            hash_int = (freq1 & 0xFFF) << 20 | (freq2 & 0xFFF) << 8 | (delta & 0xFF)

            hashes.append((hash_int, anchor_frame))
            pairs_found += 1

            if pairs_found >= config.MAX_PAIRS_PER_PEAK:
                break

    return hashes