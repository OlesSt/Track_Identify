from collections import defaultdict
from storage.db import load_hashes


def find_matches(
    main_db_path: str,
    query_db_path: str,
    min_ratio: float = 0.65
) -> list:
    """
    Match query tracks against the main library using hash lookup + offset voting.

    Args:
        main_db_path:  path to the indexed library DB
        query_db_path: path to the indexed query DB
        min_ratio:     minimum hits as a fraction of query hashes

    Returns:
        List of result strings — one per query track.
    """
    results = []

    library = load_hashes(main_db_path)
    query_tracks = load_hashes(query_db_path)

    query_by_track = defaultdict(list)
    for hash_int, entries in query_tracks.items():
        for track_name, anchor_frame in entries:
            query_by_track[track_name].append((hash_int, anchor_frame))

    for query_name, query_hashes in query_by_track.items():
        query_len = len(query_hashes)
        threshold = max(50, int(query_len * min_ratio))

        offset_votes = defaultdict(lambda: defaultdict(int))

        for hash_int, query_frame in query_hashes:
            for lib_track, lib_frame in library.get(hash_int, []):
                offset = lib_frame - query_frame
                offset_votes[lib_track][offset] += 1

        best_match = None
        best_votes = 0

        for lib_track, offsets in offset_votes.items():
            top_votes = max(offsets.values())
            if top_votes >= threshold and top_votes > best_votes:
                best_votes = top_votes
                best_offset = max(offsets, key=offsets.get)
                best_match = (lib_track, best_offset, top_votes)

        if best_match:
            lib_name, offset, votes = best_match
            results.append(
                f"MATCH:     '{query_name}'  →  '{lib_name}'  "
                f"({votes} votes, offset {offset}, threshold {threshold})"
            )
        else:
            results.append(f"NOT FOUND: '{query_name}'  (threshold {threshold})")

    return results