import numpy as np
import librosa
import config


def load_audio(path: str):
    """
    Load an audio file from disk.
    - Converts to mono if config.MONO is True
    - Resamples to config.SAMPLE_RATE if needed
    - Normalizes amplitude to [-1, 1]

    Returns:
        y  (np.ndarray): audio time series
        sr (int):        sample rate
    """
    y, sr = librosa.load(path, sr=None, mono=False)

    if config.MONO and y.ndim > 1:
        y = librosa.to_mono(y)

    if sr != config.SAMPLE_RATE:
        y = librosa.resample(y, orig_sr=sr, target_sr=config.SAMPLE_RATE)
        sr = config.SAMPLE_RATE

    y = y / np.max(np.abs(y))
    return y, sr