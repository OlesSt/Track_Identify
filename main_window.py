from PyQt6 import QtWidgets, QtCore
import sys
import os
import io, contextlib
from datetime import datetime

from db_MAIN.dbMAIN_CREATE import create_db_and_index
from db_TO_COMPARE.dbCOMPARE_CREATE import add_tracks_for_comparison
from MATCHER import compare_tracks


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Local Music Matcher")
        self.setGeometry(300, 200, 800, 550)
        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout()

        # ---------------------------
        # Database Folder Selection
        # ---------------------------
        layout.addWidget(QtWidgets.QLabel("Path to Database Folder"))
        db_folder_layout = QtWidgets.QHBoxLayout()
        self.db_folder_input = QtWidgets.QLineEdit()
        self.db_folder_input.setReadOnly(True)
        db_folder_layout.addWidget(self.db_folder_input)
        browse_db_folder_btn = QtWidgets.QPushButton("Browse")
        browse_db_folder_btn.clicked.connect(self.select_db_folder)
        db_folder_layout.addWidget(browse_db_folder_btn)
        layout.addLayout(db_folder_layout)

        # ---------------------------
        # Music Library Selection
        # ---------------------------
        layout.addWidget(QtWidgets.QLabel("Path to your Music Library"))
        folder_layout = QtWidgets.QHBoxLayout()
        self.music_folder_input = QtWidgets.QLineEdit()
        self.music_folder_input.setReadOnly(True)
        folder_layout.addWidget(self.music_folder_input)
        browse_folder_btn = QtWidgets.QPushButton("Browse")
        browse_folder_btn.clicked.connect(self.select_music_folder)
        folder_layout.addWidget(browse_folder_btn)
        layout.addLayout(folder_layout)

        self.index_btn = QtWidgets.QPushButton("INDEX")
        self.index_btn.clicked.connect(self.run_index)
        layout.addWidget(self.index_btn)




        # ---------------------------
        # Test Music Folder Selection
        # ---------------------------
        layout.addWidget(QtWidgets.QLabel("Path to music you want to identify"))
        test_folder_layout = QtWidgets.QHBoxLayout()
        self.test_music_input = QtWidgets.QLineEdit()
        self.test_music_input.setReadOnly(True)
        test_folder_layout.addWidget(self.test_music_input)
        browse_test_folder_btn = QtWidgets.QPushButton("Browse")
        browse_test_folder_btn.clicked.connect(self.select_test_folder)
        test_folder_layout.addWidget(browse_test_folder_btn)
        layout.addLayout(test_folder_layout)

        self.identify_btn = QtWidgets.QPushButton("IDENTIFY")
        self.identify_btn.clicked.connect(self.run_identify)
        layout.addWidget(self.identify_btn)

        # ---------------------------
        # Min Votes Slider
        # ---------------------------
        layout.addWidget(QtWidgets.QLabel("Minimum Votes for Match"))

        votes_layout = QtWidgets.QHBoxLayout()

        self.votes_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.votes_slider.setMinimum(10)
        self.votes_slider.setMaximum(1000)
        self.votes_slider.setValue(400)  # default
        self.votes_slider.setTickInterval(50)
        self.votes_slider.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)
        self.votes_slider.valueChanged.connect(self.update_votes_label)

        votes_layout.addWidget(QtWidgets.QLabel("10"))
        votes_layout.addWidget(self.votes_slider)
        votes_layout.addWidget(QtWidgets.QLabel("1000"))
        layout.addLayout(votes_layout)

        self.votes_label = QtWidgets.QLabel("Current Min Votes: 400")
        layout.addWidget(self.votes_label)

        # ---------------------------
        # Output Debug Field
        # ---------------------------
        self.output_field = QtWidgets.QTextEdit()
        self.output_field.setReadOnly(True)
        layout.addWidget(self.output_field)

        # ---------------------------
        # Save Logs Button
        # ---------------------------
        self.save_logs_btn = QtWidgets.QPushButton("Save Logs")
        self.save_logs_btn.clicked.connect(self.save_logs)
        layout.addWidget(self.save_logs_btn)

        self.setLayout(layout)

    # ---------------------------
    # File Dialogs
    # ---------------------------
    def select_db_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Database Folder")
        if folder:
            self.db_folder_input.setText(folder)

    def select_music_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Music Library Folder")
        if folder:
            self.music_folder_input.setText(folder)

    def select_test_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Test Music Folder")
        if folder:
            self.test_music_input.setText(folder)


    def update_votes_label(self):
        self.votes_label.setText(f"Current Min Votes: {self.votes_slider.value()}")

    # ---------------------------
    # Button Handlers
    # ---------------------------
    def run_index(self):
        folder = self.music_folder_input.text().strip()
        db_folder = self.db_folder_input.text().strip()
        if not db_folder:
            self.output("Please select a database folder first!")
            return
        if not folder:
            self.output("Please select your music library folder first!")
            return
        if not os.path.exists(db_folder):
            os.makedirs(db_folder, exist_ok=True)
        self.output(f"Indexing folder: {folder} into DB folder: {db_folder}")
        try:
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                create_db_and_index(folder_path=folder, db_folder=db_folder)
            self.output(buffer.getvalue())
        except Exception as e:
            self.output(f"INDEX failed: {e}")

    def run_identify(self):
        test_folder = self.test_music_input.text().strip()
        db_folder = self.db_folder_input.text().strip()

        if not db_folder:
            self.output("Please select a database folder first!")
            return
        if not test_folder:
            self.output("Please select a test music folder first!")
            return
        if not os.path.exists(db_folder):
            os.makedirs(db_folder, exist_ok=True)

        self.output(f"Identifying tracks in folder: {test_folder} using DB folder: {db_folder}")
        try:
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                add_tracks_for_comparison(folder_path=test_folder, db_folder=db_folder)

                main_db_path = os.path.join(db_folder, "main.db")
                compare_db_path = os.path.join(db_folder, "compare.db")

                # Get current slider value
                min_votes_absolute = self.votes_slider.value()

                # Print & log MIN_VOTES header
                header = f"\n---------- MIN_VOTES_ABSOLUTE = {min_votes_absolute} ----------\n"
                print(header)

                # Run matcher
                compare_tracks(
                    main_db_path=main_db_path,
                    compare_db_path=compare_db_path,
                    min_votes_absolute=min_votes_absolute
                )

            self.output(buffer.getvalue())
        except Exception as e:
            self.output(f"IDENTIFY failed: {e}")

    # ---------------------------
    # Output Helper
    # ---------------------------
    def output(self, text):
        self.output_field.append(text)
        self.output_field.verticalScrollBar().setValue(
            self.output_field.verticalScrollBar().maximum()
        )

    # ---------------------------
    # Save Logs Helper
    # ---------------------------
    def save_logs(self):
        log_text = self.output_field.toPlainText()
        if not log_text.strip():
            self.output("No logs to save!")
            return

        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder to Save Logs")
        if not folder:
            self.output("Save cancelled.")
            return

        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(folder, f"local_music_logs_{now}.txt")
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(log_text)
            self.output(f"Logs saved to '{filename}'")
        except Exception as e:
            self.output(f"Failed to save logs: {e}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
