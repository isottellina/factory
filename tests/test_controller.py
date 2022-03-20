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

    @pytest.mark.init_controller_with(foo=2)
    def test_using_product(
        self, initialized_session: Session, test_controller: StateController
    ):
        """
        Tests the use_product function uses only one object, and marks it as used.
        """
        assert Foo.count_not_used(initialized_session) == 2
        foo = test_controller.use_product(initialized_session, Foo)

        assert isinstance(foo, Foo)
        assert foo

        assert Foo.count_not_used(initialized_session) == 1
        assert foo.used

    @pytest.mark.init_controller_with(foobar=5)
    def test_selling_max_foobar(
        self,
        initialized_session: Session,
        test_controller: StateController,
        mocker: MockerFixture,
    ):
        mocker.patch("random.randint", mocker.MagicMock(return_value=5))

        _, _, foobar_count, euros_count = test_controller.counts(initialized_session)
        assert foobar_count == 5
        assert euros_count == 0

        test_controller.robot_action_done(
            RobotAction.SELLING_FOOBAR, initialized_session
        )

        _, _, new_foobar_count, new_euros_count = test_controller.counts(
            initialized_session
        )
        assert new_foobar_count == 0
        assert new_euros_count == 5

    @pytest.mark.init_controller_with(foobar=3)
    def test_selling_more_foobar(
        self,
        initialized_session: Session,
        test_controller: StateController,
        mocker: MockerFixture,
    ):
        """
        Tests what happens when we have less foobar than what we could sell.
        We should only sell what we have.
        """
        mocker.patch("random.randint", mocker.MagicMock(return_value=5))

        _, _, foobar_count, euros_count = test_controller.counts(initialized_session)
        assert foobar_count == 3
        assert euros_count == 0

        test_controller.robot_action_done(
            RobotAction.SELLING_FOOBAR, initialized_session
        )

        _, _, new_foobar_count, new_euros_count = test_controller.counts(
            initialized_session
        )
        assert new_foobar_count == 0
        assert new_euros_count == 3

    @pytest.mark.init_controller_with(foo=6, euros=3)
    def test_buying_robot(
        self, initialized_session: Session, test_controller: StateController
    ):
        robot_list = test_controller.list_robots(initialized_session)
        foo_count, _, _, euros_count = test_controller.counts(initialized_session)
        assert len(robot_list) == 0
        assert foo_count == 6
        assert euros_count == 3

        test_controller.robot_action_done(RobotAction.BUYING_ROBOT, initialized_session)
        new_robot_list = test_controller.list_robots(initialized_session)
        new_foo_count, _, _, new_euros_count = test_controller.counts(
            initialized_session
        )
        assert len(new_robot_list) == 1
        assert new_foo_count == 0
        assert new_euros_count == 0
