# =========================
# Audio settings
# =========================
SAMPLE_RATE = 22050          # Hz
MONO = True

# =========================
# STFT settings
# =========================
FFT_SIZE = 4096              # Window size
HOP_LENGTH = 2048            # Hop between frames
WINDOW = "hann"

# =========================
# Peak detection
# =========================
PEAKS_PER_FRAME = 5          # Top spectral peaks extracted per frame

# =========================
# Supported audio formats
# =========================
SUPPORTED_EXTENSIONS = {".wav", ".mp3", ".aiff", ".aif", ".flac", ".ogg", ".mp4", ".mov"}


# =========================
# NOT YET IMPLEMENTED
# Kept here as a roadmap for the next algorithm version
# (pairing + hashing + dominance scoring, like real Shazam)
# =========================
# PEAK_MIN_DB = -30
# PAIR_MIN_TIME_DELTA = 0.5
# PAIR_MAX_TIME_DELTA = 3.0
# MAX_PAIRS_PER_PEAK = 5
# HASH_BITS = 32
# MIN_MATCHES = 20
# DOMINANCE_RATIO = 1.8