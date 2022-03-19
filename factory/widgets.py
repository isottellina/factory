from typing import Optional

from PySide6.QtCore import QSize, Slot
from PySide6.QtWidgets import (
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenuBar,
    QProgressBar,
    QPushButton,
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
        main_layout = QVBoxLayout(self)

        top_layout = QHBoxLayout()
        name_label = QLabel(name)
        action_label = QLabel("Current action:")
        progress_bar = QProgressBar()
        top_layout.addWidget(name_label)
        top_layout.addStretch(1)
        top_layout.addWidget(action_label)
        top_layout.addWidget(progress_bar, 1)

        bottom_layout = QHBoxLayout()
        mine_foo_button = QPushButton("Mine Foo", None)
        mine_bar_button = QPushButton("Mine Bar", None)
        make_foobar_button = QPushButton("Make Foobar", None)
        sell_foobar_button = QPushButton("Sell foobar", None)
        buy_robot_button = QPushButton("Buy robot", None)
        bottom_layout.addWidget(mine_foo_button)
        bottom_layout.addWidget(mine_bar_button)
        bottom_layout.addWidget(make_foobar_button)
        bottom_layout.addWidget(sell_foobar_button)
        bottom_layout.addWidget(buy_robot_button)

        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom_layout)


class RobotsView(QGroupBox):
    """
    Presents all robots in a list-like fashion.
    """

    def __init__(self, parent: QWidget):
        super().__init__("Robots", parent)
        layout = QVBoxLayout()

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

        robots_view = RobotsView(self)
        label2 = QLabel("Test2")

        central_layout.addWidget(robots_view, 75)
        central_layout.addWidget(label2, 25)

        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

    @Slot()
    def save(self) -> None:
        raise NotImplementedError()

    def sizeHint(self) -> QSize:
        return QSize(1366, 768)
