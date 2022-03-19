from typing import Optional

from PySide6.QtCore import QSize, QTimer, Slot
from PySide6.QtWidgets import (
    QButtonGroup,
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
from factory.models import Robot, RobotAction


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

    def update_from_controller(self) -> None:
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
            self.progress_bar.setValue(0)

    @Slot(QPushButton)
    def button_pressed(self, button: QPushButton) -> None:
        with self.controller.model_session() as session:
            new_action = self.robot_actions[button]
            self.controller.change_action(session, new_action)

            session.commit()

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
        self.button_group = QButtonGroup()
        mine_foo_button = QPushButton("Mine Foo", None)
        mine_bar_button = QPushButton("Mine Bar", None)
        make_foobar_button = QPushButton("Make Foobar", None)
        sell_foobar_button = QPushButton("Sell foobar", None)
        buy_robot_button = QPushButton("Buy robot", None)

        # Mapping buttons to actions
        self.robot_actions = {
            mine_foo_button: RobotAction.MINING_FOO,
            mine_bar_button: RobotAction.MINING_BAR,
            make_foobar_button: RobotAction.MAKING_FOOBAR,
            sell_foobar_button: RobotAction.SELLING_FOOBAR,
            buy_robot_button: RobotAction.BUYING_ROBOT,
        }

        for button in self.robot_actions:
            self.button_group.addButton(button)
        self.button_group.buttonClicked.connect(self.button_pressed)

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
    def update_from_controller(self, session: SASession) -> None:
        """
        Update the widget from the data given by the controller.
        """
        # Update present widgets. We don't need to check them out
        # from the database, since the controller is supposed to have
        # been updated just before.
        for robot_view in self.present_robots.values():
            robot_view.update_from_controller()

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

        self.setLayout(self.robot_layout)


class InventoryView(QGroupBox):
    """
    View the number of each resources available.
    """

    def update_from_controller(self, session: SASession) -> None:
        foo_count, bar_count, foobar_count, euros_count = self.controller.counts(
            session
        )

        self.foo_label.setText(f"Foos: {foo_count}")
        self.bar_label.setText(f"Bars: {bar_count}")
        self.foobar_label.setText(f"Foobars: {foobar_count}")
        self.euros_label.setText(f"Money: {euros_count}€")

    def __init__(self, controller: StateController, parent: Optional[QWidget]):
        super().__init__(parent)
        self.controller = controller
        self.setTitle("Inventory")

        self.inventory_layout = QVBoxLayout(self)
        self.foo_label = QLabel("Foos:")
        self.bar_label = QLabel("Bars:")
        self.foobar_label = QLabel("Foobars:")
        self.euros_label = QLabel("Euros:")

        self.inventory_layout.addWidget(self.foo_label)
        self.inventory_layout.addWidget(self.bar_label)
        self.inventory_layout.addWidget(self.foobar_label)
        self.inventory_layout.addWidget(self.euros_label)
        self.inventory_layout.addStretch(1)


class MainWindow(QMainWindow):
    """
    Just the main window of the game. It presents
    a simple layout with robots and the inventory.
    """

    UPDATE_INTERVAL = 16  # Number of milliseconds between each update.

    def __init__(self, controller: StateController, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.controller = controller

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(self.UPDATE_INTERVAL)

        # Init menu
        menu = QMenuBar(self)
        file_menu = menu.addMenu("File")
        save_action = file_menu.addAction("Save")
        save_action.triggered.connect(self.save)

        self.setMenuBar(menu)

        central_widget = QWidget(self)
        central_layout = QHBoxLayout()

        self.robots_view = RobotsView(controller, self)
        self.inventory_view = InventoryView(controller, self)

        central_layout.addWidget(self.robots_view, 75)
        central_layout.addWidget(self.inventory_view, 25)

        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

    @Slot()
    def save(self) -> None:
        raise NotImplementedError()

    @Slot()
    def update(self) -> None:
        """
        Updates the state, then updates the view from the controller.
        """
        with self.controller.model_session() as session:
            self.controller.update(session)
            self.update_from_controller(session)

            session.commit()

    def update_from_controller(self, session: SASession) -> None:
        self.robots_view.update_from_controller(session)
        self.inventory_view.update_from_controller(session)

    def sizeHint(self) -> QSize:
        return QSize(1366, 768)
