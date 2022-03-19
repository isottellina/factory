import sys

from PySide6.QtWidgets import QApplication

from factory.controller import StateController
from factory.database import Session, init_database
from factory.widgets import MainWindow


def main() -> None:
    # Debug code to remove the test data at each start.
    # TODO: Remove that
    import pathlib

    db_path = pathlib.Path("./test.sqlite3")
    if db_path.exists():
        db_path.unlink()

    app = QApplication(sys.argv)

    init_database()

    state = StateController()
    with Session() as session:
        state.new_robot(session)
        state.new_robot(session)
        session.commit()

    window = MainWindow(state)
    window.show()

    sys.exit(app.exec())
