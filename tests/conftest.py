from datetime import timedelta
from typing import Iterator

import pytest
from freezegun.api import FrozenDateTimeFactory, freeze_time
from pytest_mock import MockerFixture
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import Session as SASession
from sqlalchemy.orm import scoped_session, sessionmaker

import factory.database
from factory.controller import RobotController, StateController
from factory.models import Bar, Foo, Foobar


@pytest.fixture
def mock_session(mocker: MockerFixture) -> Iterator[SASession]:
    engine = create_engine("sqlite:///:memory:")
    Session = scoped_session(sessionmaker(engine))

    mocker.patch("factory.database.engine", engine)
    mocker.patch("factory.database.Session", Session)

    with Session() as session:
        yield session


@pytest.fixture
def initialized_session(mock_session: SASession) -> SASession:
    """
    Same as mock_session, but ensures the database is initialized.
    """
    factory.database.init_database()

    return mock_session


@pytest.fixture
def test_controller(
    request: pytest.FixtureRequest, initialized_session: SASession
) -> StateController:
    """
    For each foobar created, this fixture will also create a used foo and bar.
    """
    creation_parameters = request.node.get_closest_marker("init_controller_with")
    controller = StateController()

    if not creation_parameters:
        # Short-circuit the initialization
        return controller

    foo_to_create = creation_parameters.kwargs.get("foo", 0)
    bar_to_create = creation_parameters.kwargs.get("bar", 0)
    foobar_to_create = creation_parameters.kwargs.get("foobar", 0)
    euros_to_create = creation_parameters.kwargs.get("euros", 0)

    for _ in range(foo_to_create):
        initialized_session.add(Foo())

    for _ in range(bar_to_create):
        initialized_session.add(Bar())

    for _ in range(foobar_to_create):
        foo = Foo()
        bar = Bar()
        initialized_session.add(
            Foobar(
                foo_used=foo,
                bar_used=bar,
            )
        )

    controller.add_euros(initialized_session, euros_to_create)

    return controller


@pytest.fixture
def test_robot(
    request: pytest.FixtureRequest,
    initialized_session: SASession,
    test_controller: StateController,
    frozen_time: FrozenDateTimeFactory,
) -> RobotController:
    creation_parameters = request.node.get_closest_marker("init_robot_with")
    robot = test_controller.new_robot(initialized_session)

    if not creation_parameters:
        return robot

    action = creation_parameters.kwargs.get("action")
    if action:
        robot.change_action(initialized_session, action)
        frozen_time.tick(timedelta(seconds=5))
        robot.update(initialized_session, frozen_time())

    return robot


@pytest.fixture
def frozen_time() -> Iterator[FrozenDateTimeFactory]:
    with freeze_time() as frozen_datetime:
        yield frozen_datetime
