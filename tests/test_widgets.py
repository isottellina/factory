from unittest.mock import MagicMock

from pytest_mock.plugin import MockerFixture
from pytestqt.qtbot import QtBot

from factory.controller import StateController
from factory.widgets import MainWindow


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
