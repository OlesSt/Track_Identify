from config import MIN_RATIO
from PySide6 import QtWidgets, QtCore, QtGui
import os
from datetime import datetime

from matching import index_folder, find_matches
from storage import get_avg_hashes_per_track

from storage import get_library_info


class DropZone(QtWidgets.QLabel):
    files_dropped = QtCore.Signal(list)

    def __init__(self):
        super().__init__()
        self.setText("Drop audio file here to identify")
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.setAcceptDrops(True)
        self.setMinimumHeight(100)
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaaaaa;
                border-radius: 8px;
                font-size: 14px;
                color: #888888;
                background-color: #f9f9f9;
            }
        """)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QLabel {
                    border: 2px dashed #4444ff;
                    border-radius: 8px;
                    font-size: 14px;
                    color: #4444ff;
                    background-color: #f0f0ff;
                }
            """)

    def dragLeaveEvent(self, event):
        self._reset_style()

    def dropEvent(self, event):
        self._reset_style()
        paths = [url.toLocalFile() for url in event.mimeData().urls()]
        self.files_dropped.emit(paths)

    def _reset_style(self):
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaaaaa;
                border-radius: 8px;
                font-size: 14px;
                color: #888888;
                background-color: #f9f9f9;
            }
        """)


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Local Music Matcher")
        self.setGeometry(300, 200, 600, 1000)
        self.console_log = []
        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout()

        # ---------------------------
        # Library buttons
        # ---------------------------
        library_btn_layout = QtWidgets.QHBoxLayout()

        self.create_update_btn = QtWidgets.QPushButton("▶  Create / Update Library")
        self.create_update_btn.setCheckable(True)
        self.create_update_btn.setChecked(False)
        self.create_update_btn.clicked.connect(self.toggle_create_update)
        library_btn_layout.addWidget(self.create_update_btn)

        self.open_db_btn = QtWidgets.QPushButton("Open Library")
        self.open_db_btn.clicked.connect(self.open_existing_db)
        library_btn_layout.addWidget(self.open_db_btn)

        layout.addLayout(library_btn_layout)

        # ---------------------------
        # Create / Update panel (collapsible)
        # ---------------------------
        self.create_update_panel = QtWidgets.QWidget()
        create_layout = QtWidgets.QVBoxLayout()
        create_layout.setContentsMargins(0, 0, 0, 0)

        create_layout.addWidget(QtWidgets.QLabel("Path to Database Folder"))
        db_folder_layout = QtWidgets.QHBoxLayout()
        self.db_folder_input = QtWidgets.QLineEdit()
        self.db_folder_input.setReadOnly(True)
        db_folder_layout.addWidget(self.db_folder_input)
        browse_db_folder_btn = QtWidgets.QPushButton("Browse")
        browse_db_folder_btn.clicked.connect(self.select_db_folder)
        db_folder_layout.addWidget(browse_db_folder_btn)
        create_layout.addLayout(db_folder_layout)

        create_layout.addWidget(QtWidgets.QLabel("Path to your Music Library"))
        folder_layout = QtWidgets.QHBoxLayout()
        self.music_folder_input = QtWidgets.QLineEdit()
        self.music_folder_input.setReadOnly(True)
        folder_layout.addWidget(self.music_folder_input)
        browse_folder_btn = QtWidgets.QPushButton("Browse")
        browse_folder_btn.clicked.connect(self.select_music_folder)
        folder_layout.addWidget(browse_folder_btn)
        create_layout.addLayout(folder_layout)

        self.build_btn = QtWidgets.QPushButton("Build Library")
        self.build_btn.clicked.connect(self.run_index)
        create_layout.addWidget(self.build_btn)

        self.create_update_panel.setLayout(create_layout)
        self.create_update_panel.setVisible(False)
        layout.addWidget(self.create_update_panel)

        # ---------------------------
        # Drag & Drop Zone
        # ---------------------------
        self.drop_zone = DropZone()
        self.drop_zone.files_dropped.connect(self.on_files_dropped)
        layout.addWidget(self.drop_zone)

        # ---------------------------
        # Advanced Search (collapsible)
        # ---------------------------
        self.advanced_btn = QtWidgets.QPushButton("▶  Advanced Search")
        self.advanced_btn.setCheckable(True)
        self.advanced_btn.setChecked(False)
        self.advanced_btn.clicked.connect(self.toggle_advanced)
        layout.addWidget(self.advanced_btn)

        self.advanced_panel = QtWidgets.QWidget()
        advanced_layout = QtWidgets.QVBoxLayout()
        advanced_layout.setContentsMargins(0, 0, 0, 0)

        advanced_layout.addWidget(QtWidgets.QLabel("Path to music you want to identify"))
        test_folder_layout = QtWidgets.QHBoxLayout()
        self.test_music_input = QtWidgets.QLineEdit()
        self.test_music_input.setReadOnly(True)
        test_folder_layout.addWidget(self.test_music_input)
        browse_test_folder_btn = QtWidgets.QPushButton("Browse")
        browse_test_folder_btn.clicked.connect(self.select_test_folder)
        test_folder_layout.addWidget(browse_test_folder_btn)
        advanced_layout.addLayout(test_folder_layout)

        self.identify_btn = QtWidgets.QPushButton("IDENTIFY")
        self.identify_btn.clicked.connect(self.run_identify)
        advanced_layout.addWidget(self.identify_btn)

        self.print_library_btn = QtWidgets.QPushButton("Print Library")
        self.print_library_btn.clicked.connect(self.print_library)
        advanced_layout.addWidget(self.print_library_btn)

        self.advanced_panel.setLayout(advanced_layout)
        self.advanced_panel.setVisible(False)
        layout.addWidget(self.advanced_panel)

        # ---------------------------
        # Output Field
        # ---------------------------
        self.output_field = QtWidgets.QTextEdit()
        self.output_field.setReadOnly(True)
        self.output_field.setAcceptRichText(True)
        layout.addWidget(self.output_field)

        # ---------------------------
        # Save Logs Button
        # ---------------------------
        logs_btn_layout = QtWidgets.QHBoxLayout()

        self.save_logs_btn = QtWidgets.QPushButton("Save Logs")
        self.save_logs_btn.clicked.connect(self.save_logs)
        logs_btn_layout.addWidget(self.save_logs_btn)

        self.clear_logs_btn = QtWidgets.QPushButton("Clear Logs")
        self.clear_logs_btn.clicked.connect(self.clear_logs)
        logs_btn_layout.addWidget(self.clear_logs_btn)

        layout.addLayout(logs_btn_layout)

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

    def toggle_create_update(self, checked):
        self.create_update_panel.setVisible(checked)
        self.create_update_btn.setText(
            "▼  Create / Update Library" if checked else "▶  Create / Update Library"
        )

    def open_existing_db(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open Library Database", "", "Database Files (*.db)"
        )
        if file_path:
            folder = os.path.dirname(file_path)
            self.db_folder_input.setText(folder)
            self.log(f"Library opened: '{file_path}'")

    # ---------------------------
    # Advanced Search Toggle
    # ---------------------------
    def toggle_advanced(self, checked):
        self.advanced_panel.setVisible(checked)
        self.advanced_btn.setText(
            "▼  Advanced Search" if checked else "▶  Advanced Search"
        )

    # ---------------------------
    # Drag & Drop Handler
    # ---------------------------
    def on_files_dropped(self, paths):
        db_folder = self.db_folder_input.text().strip()
        if not db_folder:
            self.log("Please select a database folder first!")
            return

        supported = {".wav", ".mp3", ".aiff", ".aif", ".flac",
                     ".ogg", ".mp4", ".mov"}
        audio_files = [p for p in paths
                       if os.path.splitext(p)[1].lower() in supported]

        if not audio_files:
            self.log("No supported audio files in dropped items.")
            return

        import tempfile, shutil
        tmp_folder = tempfile.mkdtemp()
        try:
            for f in audio_files:
                shutil.copy(f, tmp_folder)

            query_db_path = os.path.join(db_folder, "query.db")
            main_db_path = os.path.join(db_folder, "main.db")

            logs = index_folder(audio_folder=tmp_folder, db_path=query_db_path, force_rebuild=True)

            for line in logs:
                self.console(line)

            avg_hashes = get_avg_hashes_per_track(query_db_path)
            auto_votes = max(50, int(avg_hashes * MIN_RATIO))
            self.console(f"MIN_VOTES = {auto_votes}  |  MIN_RATIO = {MIN_RATIO:.2f}")

            if avg_hashes < 975:
                self.log_warning(
                    "Short clip detected (under 4 seconds). Results may be inaccurate — "
                    "please verify any matches against the source track."
                )

            results = find_matches(
                main_db_path=main_db_path,
                query_db_path=query_db_path,
                min_ratio=MIN_RATIO
            )

            for line in results:
                self.console(line)
                if line.startswith("MATCH:"):
                    parts = line.split("→")
                    query_name = parts[0].replace("MATCH:", "").strip().strip("'")
                    lib_name = parts[1].split("(")[0].strip().strip("'")
                    self.log_match(query_name, lib_name)
                else:
                    query_name = line.replace("NOT FOUND:", "").split("(")[0].strip().strip("'")
                    self.log_not_found(query_name)

        except Exception as e:
            import traceback
            self.log(traceback.format_exc())
        finally:
            shutil.rmtree(tmp_folder)

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

        try:
            logs = index_folder(audio_folder=test_folder, db_path=query_db_path, force_rebuild=True)

            for line in logs:
                self.console(line)

            avg_hashes = get_avg_hashes_per_track(query_db_path)
            auto_votes = max(50, int(avg_hashes * MIN_RATIO))
            self.console(f"MIN_VOTES = {auto_votes}  |  MIN_RATIO = {MIN_RATIO:.2f}")

            if avg_hashes < 975:
                self.log_warning(
                    "Short clip detected (under 4 seconds). Results may be inaccurate — "
                    "please verify any matches against the source track."
                )

            results = find_matches(
                main_db_path=main_db_path,
                query_db_path=query_db_path,
                min_ratio=MIN_RATIO
            )

            for line in results:
                self.console(line)
                if line.startswith("MATCH:"):
                    parts = line.split("→")
                    query_name = parts[0].replace("MATCH:", "").strip().strip("'")
                    lib_name = parts[1].split("(")[0].strip().strip("'")
                    self.log_match(query_name, lib_name)
                else:
                    query_name = line.replace("NOT FOUND:", "").split("(")[0].strip().strip("'")
                    self.log_not_found(query_name)

        except Exception as e:
            self.log(f"IDENTIFY failed: {e}")

    # ---------------------------
    # Helpers
    # ---------------------------
    def log(self, text):
        """Plain text log — goes to UI."""
        self.output_field.append(text)
        self.output_field.verticalScrollBar().setValue(
            self.output_field.verticalScrollBar().maximum()
        )

    def console(self, text):
        print(text)
        self.console_log.append(text)

    def print_library(self):
        db_folder = self.db_folder_input.text().strip()
        if not db_folder:
            self.log("Please select a database folder first!")
            return

        db_path = os.path.join(db_folder, "main.db")
        if not os.path.exists(db_path):
            self.log("No library found at selected folder.")
            return

        try:
            info = get_library_info(db_path)
            self.log(f"Database created: {info['created']}")
            self.log(f"Last update:      {info['updated']}")
            self.log(f"Tracks: {len(info['tracks'])}")
            self.log("─" * 40)
            for i, (track_name, hash_count) in enumerate(info['tracks'], 1):
                self.log(f"  {i}. {track_name}")
            self.log("─" * 40)
        except Exception as e:
            self.log(f"Failed to read library: {e}")

    def log_match(self, query_name, lib_name):
        self.output_field.append(
            f'<span style="color: #2e7d32; font-weight: bold;">&#10003; FOUND: </span>'
            f'<span>{query_name} </span>'
            f'<span style="color: #2e7d32; font-weight: bold;">→ {lib_name}</span>'
        )
        self.output_field.append(
            '<span style="color: #aaaaaa;">────────────────────────────────────────</span>'
        )
        self.output_field.verticalScrollBar().setValue(
            self.output_field.verticalScrollBar().maximum()
        )

    def log_not_found(self, query_name):
        self.output_field.append(
            f'<span style="color: #c62828; font-weight: bold;">&#10007; NOT FOUND: </span>'
            f'<span>{query_name}</span>'
        )
        self.output_field.append(
            '<span style="color: #aaaaaa;">────────────────────────────────────────</span>'
        )
        self.output_field.verticalScrollBar().setValue(
            self.output_field.verticalScrollBar().maximum()
        )

    def log_warning(self, text):
        self.output_field.append(
            f'<span style="color: #f9a825; font-weight: bold;">&#9888; </span>'
            f'<span style="color: #f9a825;">{text}</span>'
        )
        self.output_field.verticalScrollBar().setValue(
            self.output_field.verticalScrollBar().maximum()
        )

    def save_logs(self):
        if not self.console_log:
            self.log("No logs to save!")
            return

        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Folder to Save Logs")
        if not folder:
            self.log("Save cancelled.")
            return

        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(folder, f"local_shazam_logs_{now}.txt")
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write("\n".join(self.console_log))
            self.log(f"Logs saved to '{filename}'")
        except Exception as e:
            self.log(f"Failed to save logs: {e}")

    def clear_logs(self):
        self.output_field.clear()
        self.console_log = []