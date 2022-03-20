from datetime import timedelta
from unittest.mock import MagicMock

import pytest
from freezegun.api import FrozenDateTimeFactory
from PySide6.QtCore import Qt
from pytest_mock.plugin import MockerFixture
from pytestqt.qtbot import QtBot
from sqlalchemy.orm.session import Session

from factory.controller import RobotController, StateController
from factory.models import RobotAction
from factory.widgets import MainWindow
from factory.widgets.robots import RobotView


class MockedStateController(StateController):
    counts = MagicMock(return_value=(0, 0, 0, 0))
    update = MagicMock()


class TestMainWindow:
    def test_timer_is_setup(self, qtbot: QtBot, mocker: MockerFixture) -> None:
        mocker.patch.object(MainWindow, "update", mocker.MagicMock())
        window = MainWindow(MockedStateController())

        qtbot.addWidget(window)

        with qtbot.waitSignal(window.timer.timeout):
            window.timer.timeout.emit()

        window.update.assert_called()

    def test_updates_the_state(self, qtbot: QtBot) -> None:
        """
        Asserts the window updates the controller each time it tries to
        update itself.
        """
        controller = MockedStateController()
        window = MainWindow(controller)

        qtbot.addWidget(window)
        window.update()

        MockedStateController.update.assert_called()


class TestRobotView:
    def update(self, session: Session, test_robot: RobotController, widget: RobotView):
        """
        Helper function to update controller then fetch state.
        """
        state_controller = test_robot.parent_controller()
        assert (
            state_controller
        ), "State controller went out of scope, shouldn't be possible"

        state_controller.update(session)
        widget.update_from_controller()

    @pytest.mark.parametrize(
        "button_text,new_action",
        [
            ("mine foo", RobotAction.MINING_FOO),
            ("mine bar", RobotAction.MINING_BAR),
            ("make foobar", RobotAction.MAKING_FOOBAR),
            ("sell foobar", RobotAction.SELLING_FOOBAR),
            ("buy robot", RobotAction.BUYING_ROBOT),
        ],
    )
    def test_buttons_change_action(
        self,
        button_text: str,
        new_action: RobotAction,
        qtbot: QtBot,
        test_robot: RobotController,
        mocker: MockerFixture,
    ) -> None:
        change_action_mock = mocker.MagicMock()
        mocker.patch.object(RobotController, "change_action", change_action_mock)

        robot_view = RobotView(test_robot)
        qtbot.addWidget(robot_view)

        for button in robot_view.robot_actions:
            if button.text().lower() == button_text:
                qtbot.mouseClick(button, Qt.LeftButton)

        change_action_mock.assert_called_once()

        # We only care about the second argument (the first is the session)
        _, button_action = change_action_mock.call_args.args
        assert button_action == new_action

    @pytest.mark.parametrize(
        "time_to_wait,expected_text,expected_progress",
        [
            (0, "changing to: mining foo", 0),
            (2.5, "changing to: mining foo", 50),
            (5, "current action: mining foo", 0),
        ],
    )
    def test_text_is_accurate(
        self,
        time_to_wait: float,
        expected_text: str,
        expected_progress: int,
        qtbot: QtBot,
        initialized_session: Session,
        test_robot: RobotController,
        frozen_time: FrozenDateTimeFactory,
    ) -> None:
        widget = RobotView(test_robot)
        qtbot.addWidget(widget)

        test_robot.change_action(initialized_session, RobotAction.MINING_FOO)
        frozen_time.tick(timedelta(seconds=time_to_wait))

        self.update(initialized_session, test_robot, widget)
        assert widget.action_label.text().lower() == expected_text
        assert widget.progress_bar.value() == expected_progress

    def test_default_is_idle(
        self, test_robot: RobotController, initialized_session: Session, qtbot: QtBot
    ):
        widget = RobotView(test_robot)
        self.update(initialized_session, test_robot, widget)

        assert widget.action_label.text() == "Idle"
