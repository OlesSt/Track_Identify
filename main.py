from PySide6 import QtWidgets
import sys
import os
from ui import MainWindow

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

    # Clean up query DB on exit
    db_folder = window.db_folder_input.text().strip()

    if db_folder:
        query_db = os.path.join(db_folder, "query.db")
        if os.path.exists(query_db):
            os.remove(query_db)