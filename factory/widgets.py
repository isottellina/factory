from typing import Optional

from PySide6.QtCore import QSize, QTimer, Slot
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
from sqlalchemy.orm import Session as SASession

from factory.controller import RobotController, StateController
from factory.models import Robot


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

    @property
    def id(self) -> int:
        return self.controller.id

    @property
    def robot(self) -> Robot:
        return self.controller.robot

    def update_from_controller(self, session: SASession) -> None:
        # Ensure object is fresh from the database
        self.controller.update(session)

        if self.robot.action and self.robot.time_when_available is None:
            # Case when a robot is actively doing something
            self.action_label.setText(
                f"Current action: {self.robot.action.to_string()}"
            )
            self.progress_bar.setValue(int(self.controller.progress()))
        elif self.robot.action and self.robot.time_when_available:
            # Case when a robot is currently changing action
            self.action_label.setText(f"Changing to: {self.robot.action.to_string()}")
            self.progress_bar.setValue(int(self.controller.progress()))
        else:
            # Case when a robot is doing nothing (probably lazy)
            self.action_label.setText("Idle")

    def __init__(self, controller: RobotController, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.controller: RobotController = controller

        self.setFrameShape(QFrame.WinPanel)
        self.setFrameShadow(QFrame.Raised)
        main_layout = QVBoxLayout(self)

        top_layout = QHBoxLayout()
        name_label = QLabel(controller.name)
        self.action_label = QLabel("Current action:")
        self.progress_bar = QProgressBar()

        top_layout.addWidget(name_label)
        top_layout.addStretch(1)
        top_layout.addWidget(self.action_label)
        top_layout.addWidget(self.progress_bar, 1)

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

    @Slot()
    def update_from_controller(self) -> None:
        """
        Update the widget from the data given by the controller.
        """

        with self.controller.model_session() as session:
            # Update present widgets
            for robot in self.present_robots.values():
                robot.update_from_controller(session)

            # Check for added robots. We don't need to check for removed robots
            # since there is no way to lose a robot.
            robots = self.controller.list_robots(session)

            for robot in robots:
                if robot.id not in self.present_robots:
                    self.add_robot(robot)

    def add_robot(self, robot: RobotController) -> None:
        """
        Add a RobotView given a RobotController
        """
        new_place = self.robot_layout.count() - 1
        view = RobotView(robot)
        self.robot_layout.insertWidget(new_place, view)
        self.present_robots[robot.id] = view

    def __init__(self, controller: StateController, parent: QWidget):
        super().__init__("Robots", parent)

        self.controller = controller
        # Robots already inserted. We keep them with a mapping from robot id to widget.
        self.present_robots: dict[int, RobotView] = {}

        self.robot_layout = QVBoxLayout()
        self.robot_layout.addStretch()  # Remaining space should be taken by nothing.

        self.update_from_controller()

        self.setLayout(self.robot_layout)


class MainWindow(QMainWindow):
    """
    Just the main window of the game. It presents
    a simple layout with robots and the inventory.
    """

    def __init__(self, controller: StateController, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_from_controller)
        self.timer.start(16)

        # Init menu
        menu = QMenuBar(self)
        file_menu = menu.addMenu("File")
        save_action = file_menu.addAction("Save")
        save_action.triggered.connect(self.save)

        self.setMenuBar(menu)

        central_widget = QWidget(self)
        central_layout = QHBoxLayout()

        self.robots_view = RobotsView(controller, self)
        label2 = QLabel("Test2")

        central_layout.addWidget(self.robots_view, 75)
        central_layout.addWidget(label2, 25)

        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

    @Slot()
    def save(self) -> None:
        raise NotImplementedError()

    @Slot()
    def update_from_controller(self) -> None:
        self.robots_view.update_from_controller()

    def sizeHint(self) -> QSize:
        return QSize(1366, 768)
