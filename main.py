from PyQt6 import QtWidgets
import sys
from main_window import MainWindow  # your PyQt6 UI

if __name__ == "__main__":
    print("START APP")

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
