# =========================
# Audio settings
# =========================
SAMPLE_RATE = 22050          # Hz
MONO = True


# =========================
# STFT settings
# =========================
FFT_SIZE = 4096              # Window size
HOP_LENGTH = 2048             # Hop between frames
WINDOW = "hann"


# =========================
# Peak detection
# =========================
# Max number of spectral peaks per frame
PEAKS_PER_FRAME = 4

# Minimum magnitude (relative, in dB) to consider a peak
PEAK_MIN_DB = -30


# =========================
# Fingerprint pairing
# =========================
# Time window for pairing peaks (seconds)
PAIR_MIN_TIME_DELTA = 0.5
PAIR_MAX_TIME_DELTA = 3.0

# Max number of pairs generated per peak
MAX_PAIRS_PER_PEAK = 5


# =========================
# Hashing
# =========================
# Hash size (bits)
HASH_BITS = 32


# =========================
# Matching thresholds
# =========================

# Absolute minimum number of aligned matches
MIN_MATCHES = 20
# Best score must be X times larger than second best
DOMINANCE_RATIO = 1.8


# =========================
# Database
# =========================
DB_MAIN = "db_MAIN/db_MAIN.db"
DB_TO_COMPARE = "db_TO_COMPARE/db_TO_COMPARE.db"

# =========================
# Indexing
# =========================
# Supported audio formats
SUPPORTED_EXTENSIONS = {".wav", ".mp3", ".aiff", ".aif", ".flac", ".ogg"}
