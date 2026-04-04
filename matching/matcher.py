from collections import defaultdict, Counter
from storage.db import load_peaks


def find_matches(
    main_db_path: str,
    query_db_path: str,
    min_votes: int = 400,
    min_ratio: float = 0.5
) -> list:
    """
    Compare every query track against the main library using offset voting.

    Args:
        main_db_path:  path to the indexed library DB
        query_db_path: path to the indexed query DB
        min_votes:     absolute minimum vote count to declare a match
        min_ratio:     minimum votes as a fraction of query track length
                       (whichever of min_votes / min_ratio is higher wins)

    Returns:
        List of result strings — one per query track.
        Caller decides how to display them.
    """
    results = []

    query_tracks = load_peaks(query_db_path)
    library_tracks = load_peaks(main_db_path)

    for query_name, query_hashes in query_tracks.items():
        query_len = len(query_hashes)
        threshold = max(min_votes, int(query_len * min_ratio))
        best_match = None
        best_votes = 0

        for lib_name, lib_hashes in library_tracks.items():
            # Build fast lookup: freq_hash → [frame_indices]
            lib_lookup = defaultdict(list)
            for h, f in lib_hashes:
                lib_lookup[h].append(f)

            # Vote on time offsets
            offset_votes = Counter()
            for h, query_frame in query_hashes:
                for lib_frame in lib_lookup.get(h, []):
                    offset = lib_frame - query_frame
                    weight = 1 + max(0, 50 - abs(offset)) / 50
                    offset_votes[offset] += weight

            if not offset_votes:
                continue

            best_offset, votes = offset_votes.most_common(1)[0]

            if votes >= threshold and votes > best_votes:
                best_votes = votes
                best_match = (lib_name, best_offset, votes)

        if best_match:
            lib_name, offset, votes = best_match
            results.append(
                f"MATCH:     '{query_name}'  →  '{lib_name}'  "
                f"({votes:.1f} votes, offset {offset})"
            )
        else:
            results.append(f"NOT FOUND: '{query_name}'")

    return results