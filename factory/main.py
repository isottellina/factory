import sys
from typing import NoReturn

from PySide6.QtWidgets import QApplication

import factory.database
from factory.controller import StateController
from factory.widgets import MainWindow


def main() -> NoReturn:
    app = QApplication(sys.argv)

    factory.database.init_database()

    state = StateController()
    with factory.database.Session() as session:
        state.new_robot(session)
        state.new_robot(session)
        session.commit()

    window = MainWindow(state)
    window.show()

    sys.exit(app.exec())
