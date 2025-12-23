from PyQt6 import QtWidgets
import sys

from db_MAIN.dbMAIN_CREATE import create_db_and_index
from db_MAIN.dbMAIN_PRINT import print_db_contents

from db_TO_COMPARE.dbCOMPARE_CREATE import add_tracks_for_comparison
from db_TO_COMPARE.dbCOMPARE_PRINT import print_compare_db_contents

from MATCHER import compare_tracks
from main_window import MainWindow  # your PyQt6 UI

if __name__ == "__main__":
    print("START APP")

    # ---------------------------
    # Step 1: Index main DB
    # ---------------------------
    # print("\n=== ADD TRACK TO MAIN DB ===")
    # create_db_and_index()
    # Optional: print DB contents
    # print_db_contents()

    # ---------------------------
    # Step 2: Add tracks to compare DB
    # ---------------------------
    # print("\n=== ADD TRACK TO COMPARE DB ===")
    # add_tracks_for_comparison()
    # Optional: print compare DB contents
    # print_compare_db_contents()

    # ---------------------------
    # Step 3: Compare tracks
    # ---------------------------
    # print("\n=== COMPARE TRACKS ===")
    # compare_tracks()

    # ---------------------------
    # Step 4: Run PyQt6 UI
    # ---------------------------
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
