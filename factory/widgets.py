from typing import Optional

from PySide6.QtCore import QSize, Slot
from PySide6.QtWidgets import (
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenuBar,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class RobotView(QFrame):
    """
    Presents a single Robot. Hi!
    """

    def sizePolicy(self) -> QSizePolicy:
        return QSizePolicy(
            QSizePolicy.Fixed,
            QSizePolicy.Ignored,
        )

    def sizeHint(self) -> QSize:
        return QSize(0, 100)

    def __init__(self, name: str, parent: QWidget):
        super().__init__(parent)

        self.setFrameShape(QFrame.WinPanel)
        self.setFrameShadow(QFrame.Raised)
        layout = QHBoxLayout(self)
        label = QLabel(name)

        layout.addWidget(label)


class RobotsView(QGroupBox):
    """
    Presents all robots in a list-like fashion.
    """

    def __init__(self, parent: QWidget):
        super().__init__("Robots", parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(RobotView("Mariette", self))
        layout.addWidget(RobotView("François", self))
        layout.addStretch()  # Remaining space should be taken by nothing.

        self.setLayout(layout)


class MainWindow(QMainWindow):
    """
    Just the main window of the game. It presents
    a simple layout with robots and the inventory.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Init menu
        menu = QMenuBar(self)
        file_menu = menu.addMenu("File")
        save_action = file_menu.addAction("Save")
        save_action.triggered.connect(self.save)

        self.setMenuBar(menu)

        central_widget = QWidget(self)
        central_layout = QHBoxLayout()
        central_layout.setContentsMargins(0, 0, 0, 0)

        robots_view = RobotsView(self)
        label2 = QLabel("Test2")

        central_layout.addWidget(robots_view)
        central_layout.addWidget(label2)
        central_layout.setStretch(0, 75)
        central_layout.setStretch(1, 25)

        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

    @Slot()
    def save(self) -> None:
        raise NotImplementedError()

    def sizeHint(self) -> QSize:
        return QSize(1366, 768)
