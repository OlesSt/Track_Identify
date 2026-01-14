import sqlite3
from collections import defaultdict, Counter
import config

# =========================
# MATCH SETTINGS
# =========================
MIN_VOTES_ABSOLUTE = 400       # works for 5–10 sec clips
MIN_VOTES_RATIO = 0.5         # % of clip hashes


# =========================
# LOAD PEAKS FROM DB
# =========================
def load_peaks(db_path, table):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(f"""
        SELECT track_name, peak_frequency, frame_index
        FROM {table}
        ORDER BY frame_index
    """)
    tracks = defaultdict(list)
    for track, freq, frame in c.fetchall():
        h = round(freq)
        tracks[track].append((h, frame))
    conn.close()
    return tracks


# =========================
# COMPARE TRACKS
# =========================
def compare_tracks(main_db_path=None, compare_db_path=None, min_votes_absolute=400):
    """
    Compare tracks between main DB and compare DB.
    If paths are None, fallback to config defaults.
    """

    # ----------------------
    # Use UI-selected DB paths
    # ----------------------
    import config
    if main_db_path is None:
        main_db_path = config.DB_MAIN
    if compare_db_path is None:
        compare_db_path = config.DB_TO_COMPARE

    compare_tracks_data = load_peaks(compare_db_path, "compare_fingerprints")
    main_tracks_data = load_peaks(main_db_path, "fingerprints")

    for cmp_name, cmp_hashes in compare_tracks_data.items():
        found = False

        cmp_len = len(cmp_hashes)
        min_votes = max(
            MIN_VOTES_ABSOLUTE,
            int(cmp_len * MIN_VOTES_RATIO)
        )

        for main_name, main_hashes in main_tracks_data.items():
            main_lookup = defaultdict(list)
            for h, f in main_hashes:
                main_lookup[h].append(f)

            offset_votes = Counter()
            for h, cmp_frame in cmp_hashes:
                for main_frame in main_lookup.get(h, []):
                    offset = main_frame - cmp_frame
                    weight = 1 + max(0, 50 - abs(offset)) / 50
                    offset_votes[offset] += weight

            if not offset_votes:
                continue

            best_offset, votes = offset_votes.most_common(1)[0]

            if votes >= min_votes:
                print(
                    f"FOUND MATCH: '{cmp_name}' → '{main_name}' "
                    f"({votes:.1f} votes, offset {best_offset})"
                )
                found = True
                break

        if not found:
            print(f"TRACK '{cmp_name}' NOT FOUND in main DB")


# =========================
# RUN
# =========================
if __name__ == "__main__":
    # Example: pass custom DB paths
    compare_tracks(
        main_db_path="/Users/oles/Documents/progLOCAL_SHAZAM/DB/main.db",
        compare_db_path="/Users/oles/Documents/progLOCAL_SHAZAM/DB/compare.db"
    )
