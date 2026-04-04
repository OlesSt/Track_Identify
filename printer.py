"""
tools/inspect_db.py

Debug utility — inspect the contents of any fingerprint DB.
Run from the project root:

    python tools/inspect_db.py main      # inspects main.db path from config
    python tools/inspect_db.py query     # inspects query DB path from config
    python tools/inspect_db.py /path/to/any.db
"""

import sqlite3
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config


def inspect_db(db_path: str) -> None:
    print(f"\n=== Inspecting DB: {db_path} ===")

    if not os.path.exists(db_path):
        print(f"ERROR: File not found: '{db_path}'")
        return

    try:
        conn = sqlite3.connect(db_path)
    except Exception as e:
        print(f"ERROR: Could not open database: {e}")
        return

    c = conn.cursor()

    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in c.fetchall()]
    print(f"Tables: {tables}\n")

    for table in tables:
        c.execute(f"SELECT COUNT(*) FROM {table}")
        row_count = c.fetchone()[0]
        print(f"Table '{table}': {row_count} rows")

        try:
            c.execute(f"SELECT DISTINCT track_name FROM {table}")
            tracks = [t[0] for t in c.fetchall()]
            print(f"  Tracks ({len(tracks)}): {tracks}")
        except Exception as e:
            print(f"  WARNING: Could not read track names: {e}")
            tracks = []

        for track in tracks:
            print(f"\n  First 10 rows for '{track}':")
            c.execute(f"SELECT * FROM {table} WHERE track_name = ? LIMIT 10", (track,))
            for i, row in enumerate(c.fetchall()):
                print(f"    [{i}] {row}")

    conn.close()
    print("\n=== Done ===")


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "main"

    if arg == "main":
        inspect_db(config.DB_MAIN)
    elif arg == "query":
        inspect_db(config.DB_TO_COMPARE)
    else:
        inspect_db(arg)