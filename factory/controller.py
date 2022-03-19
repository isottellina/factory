import weakref
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Iterator, Tuple

import sqlalchemy as sa
from faker import Faker
from sqlalchemy.orm import Session as SASession
from typing_extensions import TypeAlias

from factory.database import Session
from factory.models import Bar, Foo, Foobar, GlobalState, Robot, RobotAction


class RobotController:
    SESSION: TypeAlias = SASession

    def __init__(self, parent: "StateController", robot: Robot):
        self.parent_controller = weakref.ref(parent)
        self.robot = robot

    @property
    def id(self) -> int:
        return self.robot.id

    @property
    def name(self) -> str:
        return self.robot.name

    @contextmanager
    def model_session(self) -> Iterator[SESSION]:
        ref = self.parent_controller()
        if ref:
            with ref.model_session() as session:
                yield session

        else:
            # If parent is not available anymore, yield our own
            with Session() as session:
                yield session

    def update(self, session: SASession) -> None:
        """
        Reloads the object from database to ensure it isn't stale.
        """
        self.robot = session.merge(self.robot)

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
            time_now = datetime.now() - self.robot.time_started
            return (time_now / time_total) * 100
        else:
            time_total = self.robot.time_when_available - self.robot.time_started
            time_now = datetime.now() - self.robot.time_started

            return (time_now / time_total) * 100

    def change_action(self, session: SESSION, new_action: RobotAction) -> None:
        self.robot = session.merge(self.robot)

        now = datetime.now()
        self.robot.action = new_action
        self.robot.time_started = now
        self.robot.time_when_available = now + timedelta(seconds=5)


class StateController:
    """
    Controls the state of the game. It is the parent of every
    other controller.
    """

    # The factory used to make a Robot controller, useful when subclassing
    ROBOT_CONTROLLER_FACTORY = RobotController

    # The Session type used for queries
    SESSION: TypeAlias = SASession

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

    def counts(self, session: SESSION) -> Tuple[int, int, int, int]:
        """
        Returns number of foo, bar, foobars and euros.
        """
        return (
            Foo.count_not_used(session),
            Bar.count_not_used(session),
            Foobar.count_not_used(session),
            session.scalar(sa.select(GlobalState.euros)),
        )

    def list_robots(self, session: SESSION) -> list[RobotController]:
        return [
            self.ROBOT_CONTROLLER_FACTORY(self, robot)
            for robot in session.scalars(sa.select(Robot)).all()
        ]

    def get_robot_by_id(self, session: SESSION, id: int) -> RobotController:
        robot = session.scalar(sa.select(Robot).where(Robot.id == id))

        return self.ROBOT_CONTROLLER_FACTORY(self, robot)

    def get_robot_by_name(self, session: SESSION, name: str) -> RobotController:
        robot = session.scalar(sa.select(Robot).where(Robot.name == name))

        return self.ROBOT_CONTROLLER_FACTORY(self, robot)

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
        return self.ROBOT_CONTROLLER_FACTORY(self, robot)
