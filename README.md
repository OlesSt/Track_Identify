# 🎵 Local Shazam

> Identify audio tracks from your local music library using acoustic fingerprinting — offline, private, no API keys.

Built as a portfolio project and practical tool for sound design and music production workflows.

---

## Table of Contents

- [Overview](#overview)
- [Demo](#demo)
- [Features](#features)
- [How It Works](#how-it-works)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Performance](#performance)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Building a Standalone App](#building-a-standalone-app)
- [Tech Stack](#tech-stack)
- [License](#license)

---

## Overview

Local Shazam lets you build a fingerprint database from your music library and then identify any audio clip — a recording, a sample, a fragment — by matching it against that database. Everything runs locally on your machine. No internet connection required, no data sent anywhere.

**Who is this for:**
- Sound designers who work with large sample libraries
- Music producers who need to trace the source of a recording
- Game audio teams managing licensed music assets
- Anyone who wants to identify tracks from their own collection

---

## Demo

```
✓ FOUND: mystery_clip.wav  →  MUSIC_03.wav
────────────────────────────────────────
✗ NOT FOUND: unknown_sample.wav
────────────────────────────────────────
⚠ Short clip detected (under 4 seconds). Results may be inaccurate —
  please verify any matches against the source track.
```

---

## Features

- **Drag & drop identification** — drop a file, get an instant result
- **Incremental library building** — add new tracks without rebuilding the whole database
- **Batch identification** — identify a whole folder of clips at once via Advanced Search
- **Library inspection** — view all indexed tracks with creation and update timestamps
- **Clean result display** — color-coded UI with detailed logs saved separately
- **Fully offline** — no network calls, no telemetry, no accounts

---

## How It Works

The algorithm is inspired by the acoustic fingerprinting approach described by Wang (2003):

1. Audio is loaded and normalized to mono at 22050 Hz
2. STFT (Short-Time Fourier Transform) extracts the frequency spectrum over time
3. The top spectral peaks per frame are identified
4. Peaks are **paired** within a time window — each pair of frequencies plus the time delta between them forms a hash
5. Hashes are stored in a SQLite database with an index for fast lookup
6. To identify a clip, its hashes are looked up in the library and time offsets are voted on — a strong concentration of votes at one offset means a match

The pairing step is what makes this work reliably. Raw frequency matching produces too many coincidental hits. Hash pairs are far more unique, which eliminates false positives even on short clips.

---

## Getting Started

### Prerequisites

- Python 3.10+
- macOS (tested on macOS 14 — Windows/Linux not tested but likely works)
- `ffmpeg` (optional) — required only for `.mp4` and `.mov` files.
  Install via `brew install ffmpeg` on Mac or `winget install ffmpeg` on Windows.
  All other supported formats work without it.

### Installation

```bash
git clone https://github.com/OlesSt/Track_Identify
cd local-shazam
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

---

## Usage

### Step 1 — Build your library

Click **Create / Update Library** to expand the panel. Select a folder for the database and a folder with your music files. Click **Build Library**.

The database builds incrementally — running it again only indexes tracks not already in the database. Safe to run on libraries of hundreds of tracks.

**Supported formats:** `.wav` `.mp3` `.aiff` `.aif` `.flac` `.ogg` `.mp4` `.mov`

### Step 2 — Identify a track

Drag and drop any audio file onto the drop zone. Results appear immediately.

For batch identification, open **Advanced Search**, select a folder of clips, and click **IDENTIFY**.

### Step 3 — Inspect your library

Inside **Advanced Search**, click **Print Library** to list all indexed tracks with database creation and last update timestamps.

### Logs

**Save Logs** exports the full technical log (hash counts, vote scores, thresholds) to a `.txt` file. **Clear Logs** resets the output panel.

---

## Performance

Tested on a library of 20 tracks across 6 genres (BEAT, CINEMA, FUNK, POP, ROCK, TECHNO) against 240 query clips — correct matches and deliberately wrong tracks at every clip length.

| Clip length | Detection rate | False positives | Notes |
|---|---|---|---|
| 1 sec | 60% | 0 / 80 | Unreliable — not recommended |
| 2 sec | 100% | 0 / 80 | Minimum reliable length |
| 4 sec | 85% | 0 / 80 | |
| 8 sec | 100% | 0 / 80 | |
| 16 sec | 75% | 0 / 80 | |
| 30 sec | 100% | 0 / 80 | |
| 60 sec | 70% | 0 / 80 | |
| 120 sec | 85% | 0 / 80 | |

**Overall: 135 / 160 correct matches (84%), 0 / 80 false positives across all lengths.**

Missed detections are caused by tracks with less distinctive spectral content at the specific timestamp tested — not algorithm failures. The same tracks often match correctly at other clip lengths. Clips under 4 seconds display a warning in the UI.

---

## Project Structure

```
local_shazam/
├── main.py                  # entry point
├── config.py                # all audio and algorithm settings
├── requirements.txt
│
├── ui/
│   ├── __init__.py
│   └── main_window.py       # UI only — no business logic
│
├── audio/
│   ├── __init__.py
│   ├── loader.py            # audio loading, resampling, normalization
│   └── extractor.py         # STFT peak extraction + hash pair generation
│
├── storage/
│   ├── __init__.py
│   └── db.py                # all SQLite operations in one place
│
└── matching/
    ├── __init__.py
    ├── indexer.py            # orchestrates audio → storage pipeline
    └── matcher.py            # hash lookup and offset voting
```

The dependency flow is strictly one direction — `ui` → `matching` → `audio` / `storage`. No layer imports upward.

---

## Configuration

All settings live in `config.py`:

```python
SAMPLE_RATE = 22050       # Hz
FFT_SIZE = 4096           # STFT window size
HOP_LENGTH = 2048         # 50% overlap (standard for Hann window)
PEAKS_PER_FRAME = 5       # spectral peaks per frame (~55 peaks/sec)
PAIR_MAX_TIME_DELTA = 3.0 # seconds — hash pairing window
MAX_PAIRS_PER_PEAK = 5    # hashes generated per anchor peak
```

> ⚠️ Changing `PEAKS_PER_FRAME`, `FFT_SIZE`, or `HOP_LENGTH` requires deleting and rebuilding the database. The query and library databases must always use the same settings.

---

## Building a Standalone App

```bash
pip install pyinstaller
pyinstaller --windowed --name LocalShazam main.py
```

Output: `dist/LocalShazam.app` on macOS.

---

## Tech Stack

| Library | Purpose | License |
|---|---|---|
| [PySide6](https://pypi.org/project/PySide6/) | Desktop UI | LGPL |
| [librosa](https://librosa.org/) | Audio analysis, STFT | ISC |
| [numpy](https://numpy.org/) | Numerical computing | BSD |
| [scipy](https://scipy.org/) | Signal processing | BSD |
| [numba](https://numba.pydata.org/) | JIT compilation for librosa | BSD |
| [soundfile](https://python-soundfile.readthedocs.io/) | Audio file I/O | BSD |
| SQLite | Fingerprint storage | Public domain |

---

## License

MIT — use it however you want, including commercially.

---

## References

Inspired by the acoustic fingerprinting approach described in:

> Wang, A. (2003). *An Industrial-Strength Audio Search Algorithm*. Proceedings of the 4th International Society for Music Information Retrieval Conference (ISMIR).
