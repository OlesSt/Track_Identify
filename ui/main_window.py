from PyQt6 import QtWidgets, QtCore
import os
from datetime import datetime

from matching import index_folder, find_matches


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Local Music Matcher")
        self.setGeometry(300, 200, 800, 1000)
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
        # Query Music Folder Selection
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

        # ---------------------------
        # Min Votes Slider
        # ---------------------------
        layout.addWidget(QtWidgets.QLabel("MINIMUM VOTES FOR MATCH"))
        self.votes_label = QtWidgets.QLabel("Current: 400")
        layout.addWidget(self.votes_label)

        votes_layout = QtWidgets.QHBoxLayout()
        self.votes_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.votes_slider.setMinimum(10)
        self.votes_slider.setMaximum(10000)
        self.votes_slider.setValue(400)
        self.votes_slider.setTickInterval(500)
        self.votes_slider.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)
        self.votes_slider.valueChanged.connect(self.update_votes_label)
        votes_layout.addWidget(QtWidgets.QLabel("10"))
        votes_layout.addWidget(self.votes_slider)
        votes_layout.addWidget(QtWidgets.QLabel("10000"))
        layout.addLayout(votes_layout)

        # ---------------------------
        # Min Votes Ratio Slider
        # ---------------------------
        layout.addWidget(QtWidgets.QLabel("MINIMUM VOTES RATIO"))
        self.ratio_label = QtWidgets.QLabel("Current: 0.50")
        layout.addWidget(self.ratio_label)

        ratio_layout = QtWidgets.QHBoxLayout()
        self.ratio_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.ratio_slider.setMinimum(10)
        self.ratio_slider.setMaximum(100)
        self.ratio_slider.setValue(50)
        self.ratio_slider.setTickInterval(5)
        self.ratio_slider.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)
        self.ratio_slider.valueChanged.connect(self.update_ratio_label)
        ratio_layout.addWidget(QtWidgets.QLabel("0.10"))
        ratio_layout.addWidget(self.ratio_slider)
        ratio_layout.addWidget(QtWidgets.QLabel("1.00"))
        layout.addLayout(ratio_layout)

        # ---------------------------
        # Identify Button
        # ---------------------------
        self.identify_btn = QtWidgets.QPushButton("IDENTIFY")
        self.identify_btn.clicked.connect(self.run_identify)
        layout.addWidget(self.identify_btn)

        # ---------------------------
        # Output Field
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
    # Folder Dialogs
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
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Query Music Folder")
        if folder:
            self.test_music_input.setText(folder)

    # ---------------------------
    # Slider Labels
    # ---------------------------
    def update_votes_label(self):
        self.votes_label.setText(f"Current: {self.votes_slider.value()}")

    def update_ratio_label(self):
        self.ratio_label.setText(f"Current: {self.ratio_slider.value() / 100:.2f}")

    # ---------------------------
    # Button Handlers
    # ---------------------------
    def run_index(self):
        folder = self.music_folder_input.text().strip()
        db_folder = self.db_folder_input.text().strip()

        if not db_folder:
            self.log("Please select a database folder first!")
            return
        if not folder:
            self.log("Please select your music library folder first!")
            return

        db_path = os.path.join(db_folder, "main.db")
        try:
            logs = index_folder(audio_folder=folder, db_path=db_path)
            for line in logs:
                self.log(line)
        except Exception as e:
            import traceback
            self.log(traceback.format_exc())
        # except Exception as e:
        #     self.log(f"INDEX failed: {e}")

    def run_identify(self):
        test_folder = self.test_music_input.text().strip()
        db_folder = self.db_folder_input.text().strip()

        if not db_folder:
            self.log("Please select a database folder first!")
            return
        if not test_folder:
            self.log("Please select a query music folder first!")
            return

        main_db_path = os.path.join(db_folder, "main.db")
        query_db_path = os.path.join(db_folder, "query.db")
        min_votes = self.votes_slider.value()
        min_ratio = self.ratio_slider.value() / 100

        try:
            # Step 1: index query tracks
            self.log("Indexing query tracks...")
            logs = index_folder(audio_folder=test_folder, db_path=query_db_path)
            for line in logs:
                self.log(line)

            # Step 2: run matching
            self.log(
                f"\n--- MATCH SETTINGS ---\n"
                f"MIN_VOTES = {min_votes}  |  MIN_RATIO = {min_ratio:.2f}\n"
                f"----------------------"
            )
            results = find_matches(
                main_db_path=main_db_path,
                query_db_path=query_db_path,
                min_votes=min_votes,
                min_ratio=min_ratio
            )
            for line in results:
                self.log(line)

        except Exception as e:
            self.log(f"IDENTIFY failed: {e}")

    # ---------------------------
    # Helpers
    # ---------------------------
    def log(self, text):
        self.output_field.append(text)
        self.output_field.verticalScrollBar().setValue(
            self.output_field.verticalScrollBar().maximum()
        )

    def save_logs(self):
        log_text = self.output_field.toPlainText()
        if not log_text.strip():
            self.log("No logs to save!")
            return

        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder to Save Logs")
        if not folder:
            self.log("Save cancelled.")
            return

        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(folder, f"local_shazam_logs_{now}.txt")
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(log_text)
            self.log(f"Logs saved to '{filename}'")
        except Exception as e:
            self.log(f"Failed to save logs: {e}")