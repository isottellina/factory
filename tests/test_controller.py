import pytest
import sqlalchemy as sa
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session

from factory.controller import StateController
from factory.models import Bar, Foo, Foobar, Robot, RobotAction


class TestStateController:
    def test_new_robot(
        self, initialized_session: Session, test_controller: StateController
    ) -> None:
        test_controller.new_robot(initialized_session)
        # There should be only one robot.
        assert initialized_session.scalar(sa.select(sa.func.count(Robot.id))) == 1

        test_controller.new_robot(initialized_session)
        # Now there should be two
        assert initialized_session.scalar(sa.select(sa.func.count(Robot.id))) == 2

    def test_mining_foo_done(
        self, initialized_session: Session, test_controller: StateController
    ) -> None:
        # There should be zero foo
        assert Foo.count_not_used(initialized_session) == 0
        test_controller.robot_action_done(RobotAction.MINING_FOO, initialized_session)

        # Now there's one
        assert Foo.count_not_used(initialized_session) == 1

    def test_mining_bar_done(
        self, initialized_session: Session, test_controller: StateController
    ) -> None:
        # There should be zero bar
        assert Bar.count_not_used(initialized_session) == 0
        test_controller.robot_action_done(RobotAction.MINING_BAR, initialized_session)

        # Now there's one
        assert Bar.count_not_used(initialized_session) == 1

    @pytest.mark.init_controller_with(foo=1, bar=1)
    def test_making_foobar_failing(
        self,
        initialized_session: Session,
        test_controller: StateController,
        mocker: MockerFixture,
    ) -> None:
        # Always get critical failure
        mocker.patch("random.randint", mocker.MagicMock(return_value=100))

        # There should be zero foobar
        assert Foobar.count_not_used(initialized_session) == 0

        test_controller.robot_action_done(
            RobotAction.MAKING_FOOBAR, initialized_session
        )

        # Now there's zero foo, one bar, and still zero foobar
        assert Foo.count_not_used(initialized_session) == 0
        assert Bar.count_not_used(initialized_session) == 1
        assert Foobar.count_not_used(initialized_session) == 0

    @pytest.mark.init_controller_with(foo=1, bar=1)
    def test_making_foobar_succeeding(
        self,
        initialized_session: Session,
        test_controller: StateController,
        mocker: MockerFixture,
    ) -> None:
        # Always get critical success
        mocker.patch("random.randint", mocker.MagicMock(return_value=0))

        # There should be zero foobar
        assert Foobar.count_not_used(initialized_session) == 0

        test_controller.robot_action_done(
            RobotAction.MAKING_FOOBAR, initialized_session
        )

        # Now there's zero foo, zero bar, and one foobar
        assert Foo.count_not_used(initialized_session) == 0
        assert Bar.count_not_used(initialized_session) == 0
        assert Foobar.count_not_used(initialized_session) == 1

    def test_making_foobar_not_enough_materials(
        self, initialized_session: Session, test_controller: StateController
    ) -> None:
        # There should be zero foobar
        assert Foobar.count_not_used(initialized_session) == 0
        test_controller.robot_action_done(
            RobotAction.MAKING_FOOBAR, initialized_session
        )

        # There should still be zero foobars
        assert Foobar.count_not_used(initialized_session) == 0
