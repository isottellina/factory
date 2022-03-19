import sys

from PySide6.QtWidgets import QApplication

from factory.database import init_database
from factory.widgets import MainWindow


def main() -> None:
    app = QApplication(sys.argv)

    init_database()
    window = MainWindow()
    window.show()

    sys.exit(app.exec())
