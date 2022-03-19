from typing import Iterator

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import Session as SASession
from sqlalchemy.orm import scoped_session, sessionmaker

import factory.database
from factory.controller import StateController
from factory.models import Bar, Foo


@pytest.fixture
def mock_session(mocker: MockerFixture) -> Iterator[SASession]:
    engine = create_engine("sqlite:///:memory:")
    Session = scoped_session(sessionmaker(engine))

    mocker.patch("factory.database.engine", engine)
    mocker.patch("factory.database.Session", Session)

    with Session() as session:
        yield session


@pytest.fixture
def test_controller(
    request: pytest.FixtureRequest, mock_session: SASession
) -> StateController:
    """
    For now the init phase only supports creating foos and bars.
    """
    creation_parameters = request.node.get_closest_marker("init_controller_with")
    controller = StateController()

    if not creation_parameters:
        # Short-circuit the initialization
        return controller

    for _ in range(creation_parameters.kwargs.get("foo", 0)):
        mock_session.add(Foo())

    for _ in range(creation_parameters.kwargs.get("bar", 0)):
        mock_session.add(Bar())

    return controller


@pytest.fixture
def initialized_session(mock_session: scoped_session) -> scoped_session:
    """
    Same as mock_session, but ensures the database is initialized.
    """
    factory.database.init_database()

    return mock_session
