from __future__ import annotations

import random
import weakref
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Iterator, Optional, Tuple, Type

import sqlalchemy as sa
from faker import Faker
from sqlalchemy.orm import Session as SASession
from sqlalchemy.sql.elements import not_
from typing_extensions import TypeAlias

import factory.database
from factory.models import (
    Bar,
    Foo,
    Foobar,
    GlobalState,
    Robot,
    RobotAction,
    UsableObject,
)


class RobotController:
    SESSION: TypeAlias = SASession

    def __init__(self, parent: StateController, robot: Robot):
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
            with factory.database.Session() as session:
                yield session

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

    def start_action(self, session: SESSION, now: datetime) -> None:
        def action_will_take() -> timedelta:
            """
            How much time will the action take? Can't use a mapping for this
            one since one of the action is random.
            """
            if self.robot.action == RobotAction.MINING_FOO:
                return timedelta(seconds=2)

            elif self.robot.action == RobotAction.MINING_BAR:
                return timedelta(milliseconds=random.randint(500, 2000))

            elif self.robot.action == RobotAction.MAKING_FOOBAR:
                return timedelta(seconds=2)

            elif self.robot.action == RobotAction.SELLING_FOOBAR:
                return timedelta(seconds=10)

            raise AssertionError("The robot's action is in an incoherent state.")

        if self.robot.action == RobotAction.BUYING_ROBOT:
            # This one is instantly finished.
            self.action_done(session)
            self.robot.action = None
            return

        self.robot.time_started = now
        self.robot.time_when_done = now + action_will_take()

    def action_done(self, session: SESSION) -> bool:
        """
        Function to run when an action is done. Manages the weakref to
        the parent. Returns whether the action should start again.
        """
        assert self.robot.action

        parent = self.parent_controller()
        assert parent, "Parent controller was Garbage-Collected?"

        result = parent.robot_action_done(self.robot.action, session)
        if self.robot.action == RobotAction.BUYING_ROBOT:
            return False

        return result

    def update(self, session: SESSION, now: datetime) -> None:
        """
        Check if current action is done, and updates state accordingly.
        """
        self.robot = session.merge(self.robot)

        # Short-circuit if the robot is doing nothing.
        if self.robot.action is None:
            return

        # Is the robot changing actions?
        if self.robot.time_when_available:
            if self.robot.time_when_available <= now:
                self.robot.time_when_available = None
                self.start_action(session, now)

            return

        # Is the robot done with its action?
        assert self.robot.time_when_done
        if self.robot.time_when_done <= now:
            if self.action_done(session):
                self.start_action(session, now)
            else:
                self.robot.action = None

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
        self.robot_cache: dict[int, RobotController] = {}

    @contextmanager
    def model_session(self) -> Iterator[SASession]:
        """
        Instantiate a session to the Model. We avoid using this in our
        own functions because a session should be tied to a wider action,
        such as one instantiated by the User.
        """
        with factory.database.Session() as session:
            yield session

    def get_from_cache_or_create(self, robot: Robot) -> RobotController:
        _robot_controller = self.robot_cache.get(robot.id)
        if _robot_controller:
            return _robot_controller

        self.robot_cache[robot.id] = self.ROBOT_CONTROLLER_FACTORY(self, robot)
        return self.robot_cache[robot.id]

    def update(self, session: SESSION) -> None:
        """
        Updates the state.
        """
        now = datetime.now()

        for robot in self.list_robots(session):
            robot.update(session, now)

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

    def add_euros(self, session: SESSION, n: int) -> None:
        current_euros = session.scalar(sa.select(GlobalState.euros))

        session.execute(sa.update(GlobalState).values(euros=current_euros + n))

    def sub_euros(self, session: SESSION, n: int) -> None:
        current_euros = session.scalar(sa.select(GlobalState.euros))

        session.execute(sa.update(GlobalState).values(euros=current_euros - n))

    def list_robots(self, session: SESSION) -> list[RobotController]:
        return [
            self.get_from_cache_or_create(robot)
            for robot in session.scalars(sa.select(Robot)).all()
        ]

    def new_robot(self, session: SESSION) -> RobotController:
        """
        Generate a new robot with a unique name.
        """
        name = self.faker.unique.name()

        robot = Robot(
            name=name,
            action=None,
            time_when_available=None,
            time_when_done=None,
        )

        session.add(robot)
        return self.get_from_cache_or_create(robot)

    def use_product(
        self, session: SESSION, product: Type[UsableObject]
    ) -> Optional[UsableObject]:
        """
        Uses a product and returns the product
        """
        obj = session.scalar(sa.select(product).where(not_(product.used)))

        if obj:
            obj.used = True

        # Type of obj is either None or the queried type, but mypy can't check this.
        return obj  # type: ignore

    def use_n_products(
        self, session: SESSION, product_cls: Type[UsableObject], n: int
    ) -> int:
        """
        Uses at max n products, return the number that was used.
        """
        query = sa.select(product_cls).where(not_(product_cls.used)).limit(n)

        used_products = session.scalars(query).all()

        for product in used_products:
            product.used = True

        return len(used_products)

    def robot_action_done(self, action: RobotAction, session: SESSION) -> bool:
        """
        A Robot has finished its action. Returns whether the action
        can happen again.
        """
        foo_count, bar_count, foobar_count, euros_count = self.counts(session)

        if action == RobotAction.MINING_FOO:
            # Create a new Foo. This can't fail.
            session.add(Foo())

            return True

        elif action == RobotAction.MINING_BAR:
            # Same but for Bar.
            session.add(Bar())

            return True

        elif action == RobotAction.MAKING_FOOBAR:
            if foo_count >= 1 and bar_count >= 1:
                # We use the foo anyway, even if it fails.
                foo: Foo = self.use_product(session, Foo)  # type: ignore

                chance_of_success = random.randint(1, 100)
                if chance_of_success > 60:  # Making Foobar failed.
                    return True

                bar: Bar = self.use_product(session, Bar)  # type: ignore

                session.add(Foobar(foo_used=foo, bar_used=bar))

                return True
            return False

        elif action == RobotAction.SELLING_FOOBAR:
            if foobar_count == 0:
                return False

            nb_foobar_to_sell = random.randint(1, 5)

            # If we have less than the amount to sell but still not 0, we still sell the
            # max we can.
            nb_foobar_sold = self.use_n_products(session, Foobar, nb_foobar_to_sell)
            self.add_euros(session, nb_foobar_sold)

            return True

        elif action == RobotAction.BUYING_ROBOT:  # This one finished instantly
            if foo_count >= 6 and euros_count >= 3:
                self.use_n_products(session, Foo, 6)
                self.sub_euros(session, 3)
                self.new_robot(session)

            return False

        raise AssertionError("This point should be unreachable.")
