import enum
import weakref
from contextlib import contextmanager
from datetime import datetime
from typing import Iterator

import sqlalchemy as sa
from faker import Faker
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

    @property
    def id(self) -> int:
        return self.robot.id

    @property
    def name(self) -> str:
        return self.robot.name

    def update(self, session: SASession) -> None:
        """
        Reloads the object from database to ensure it isn't stale.
        """
        self.robot = session.scalar(sa.select(Robot).where(Robot.id == self.robot.id))

    def progress(self) -> float:
        """
        Returns a float between 0 and 100 to indicate the progress
        with the current task, whether it's changing or not.

        To call this the robot must be doing something.
        """
        assert self.robot.action
        assert self.robot.time_started

        if self.robot.time_when_available is None:
            assert self.robot.time_when_done

            time_total = self.robot.time_when_done - self.robot.time_started
            time_now = self.robot.time_when_done - datetime.now()
            return (time_now / time_total) * 100
        else:
            time_total = self.robot.time_when_available - self.robot.time_started
            time_now = self.robot.time_when_available - datetime.now()
            return (time_now / time_total) * 100

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

    def __init__(self) -> None:
        self.faker = Faker()

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
        return [
            RobotController(self, robot)
            for robot in session.scalars(sa.select(Robot)).all()
        ]

    def get_robot_by_id(self, session: SESSION, id: int) -> RobotController:
        robot = session.scalar(sa.select(Robot).where(Robot.id == id))

        return RobotController(self, robot)

    def get_robot_by_name(self, session: SESSION, name: str) -> RobotController:
        robot = session.scalar(sa.select(Robot).where(Robot.name == name))

        return RobotController(self, robot)

    def new_robot(self, session: SESSION) -> RobotController:
        """
        Generate a new robot with a unique name.
        """
        name = self.faker.name()
        while session.execute(sa.select(Robot).filter_by(name=name)).first():
            name = self.faker.name()

        robot = Robot(
            name=name,
            action=None,
            time_when_available=None,
            time_when_done=None,
        )

        session.add(robot)
        return RobotController(self, robot)
