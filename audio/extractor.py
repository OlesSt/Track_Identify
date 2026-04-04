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