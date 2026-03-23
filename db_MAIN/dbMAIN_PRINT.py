import sqlite3
import config


def print_db_contents():
    print("DEBUG: Starting 'print_db_contents' function")
    print(f"DEBUG: Database path: {config.DB_MAIN}")

    # Open database
    try:
        conn = sqlite3.connect(config.DB_MAIN)
        print("DEBUG: Database opened successfully")
    except Exception as e:
        print(f"ERROR: Could not open database: {e}")
        return

    c = conn.cursor()

    # Get list of tables
    print("DEBUG: Retrieving list of tables")
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()
    table_names = [t[0] for t in tables]
    print(f"DEBUG: Tables found: {table_names}")

    for table_name in table_names:
        print(f"\nDEBUG: Inspecting table '{table_name}'")

        # Count rows in table
        c.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = c.fetchone()[0]
        print(f"DEBUG: Table '{table_name}' has {row_count} rows")

        # Extract distinct track titles
        try:
            c.execute(f"SELECT DISTINCT track_name FROM {table_name}")
            tracks = [t[0] for t in c.fetchall()]
            if tracks:
                print(f"DEBUG: Tracks in table '{table_name}': {tracks}")
            else:
                print(f"DEBUG: No track names found in table '{table_name}'")
        except Exception as e:
            print(f"WARNING: Could not extract track names: {e}")
            tracks = []

        # Print first 10 rows per track (optional, helps inspect)
        for track in tracks:
            print(f"\nDEBUG: First 10 rows for track '{track}':")
            try:
                c.execute(f"SELECT * FROM {table_name} WHERE track_name = ? LIMIT 10", (track,))
                rows = c.fetchall()
                for i, row in enumerate(rows):
                    print(f"  Row {i}: {row}")
            except Exception as e:
                print(f"WARNING: Could not fetch rows for track '{track}': {e}")

    conn.close()
    print("DEBUG: Database connection closed")
    print("DEBUG: Finished printing DB contents")


if __name__ == "__main__":
    print_db_contents()
