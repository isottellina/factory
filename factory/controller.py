import enum
import random
import weakref
from contextlib import contextmanager
from typing import Iterator

import sqlalchemy as sa
from PySide6.QtCore import QObject, Signal, Slot
from sqlalchemy.orm import Session as SASession
from typing_extensions import TypeAlias

from factory.database import Session
from factory.models import Robot, RobotAction


class InventoryChange(enum.Enum):
    """
    Represents a change in the player's inventory.
    """

    NEW_FOO = enum.auto()
    NEW_BAR = enum.auto()
    NEW_FOOBAR = enum.auto()
    FOOBAR_SOLD = enum.auto()


class RobotController(QObject):
    changing = Signal()  # Emitted when the robot changes action.
    finished = Signal()  # Emitted when the robot finished its current action

    def __init__(self, parent: "StateController", robot: Robot):
        self.parent_controller = weakref.ref(parent)
        self.robot = robot

    @Slot(RobotAction)
    def change_action(self, new_action: RobotAction) -> None:
        print("Changing action to", new_action)


class StateController(QObject):
    """
    Controls the state of the game. It is the parent of every
    other controller.
    """

    # The factory used to make a Robot controller, useful when subclassing
    ROBOT_CONTROLLER_FACTORY = RobotController

    # The Session type used for queries
    SESSION: TypeAlias = SASession

    # Emitted when any robot changes state. It is emitted with
    # the name of the robot who changed state.
    robot = Signal()

    # Emitted when the inventory changes.
    inventory = Signal()

    @contextmanager
    def model_session(self) -> Iterator[SASession]:
        """
        Instantiate a session to the Model. We avoid using this in our
        own functions because a session should be tied to a wider action,
        such as one instantiated by the User.
        """
        with Session() as session:
            yield session

    def list_robots(self, session: SESSION) -> list[RobotController]:
        return session.scalars(sa.select(Robot)).all()

    def get_robot_by_id(self, session: SESSION, id: int) -> RobotController:
        robot = session.scalar(sa.select(Robot).where(Robot.id == id))

        return RobotController(self, robot)

    def get_robot_by_name(self, session: SESSION, name: str) -> RobotController:
        robot = session.scalar(sa.select(Robot).where(Robot.name == name))

        return RobotController(self, robot)

    def new_robot(self, session: SESSION) -> RobotController:
        robot = Robot(
            name="Test name %f" % random.random(),
            action=None,
            time_when_available=None,
            time_when_done=None,
        )

        session.add(robot)
        return RobotController(self, robot)
