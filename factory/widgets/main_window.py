#!/usr/bin/env python3
from typing import Optional

from PySide6.QtCore import QSize, QTimer, Slot
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QMenuBar, QWidget
from sqlalchemy.orm import Session as SASession

from factory.controller import StateController

from .inventory import InventoryView
from .robots import RobotsView


class MainWindow(QMainWindow):
    """
    Just the main window of the game. It presents
    a simple layout with robots and the inventory.
    """

    UPDATE_INTERVAL = 16  # Number of milliseconds between each update.

    def __init__(self, controller: StateController, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.controller = controller

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(self.UPDATE_INTERVAL)

        # Init menu
        menu = QMenuBar(self)
        file_menu = menu.addMenu("File")
        save_action = file_menu.addAction("Save")
        save_action.triggered.connect(self.save)

        self.setMenuBar(menu)

        central_widget = QWidget(self)
        central_layout = QHBoxLayout()

        self.robots_view = RobotsView(controller, self)
        self.inventory_view = InventoryView(controller, self)

        central_layout.addWidget(self.robots_view, 75)
        central_layout.addWidget(self.inventory_view, 25)

        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

    @Slot()
    def save(self) -> None:
        raise NotImplementedError()

    @Slot()
    def update(self) -> None:
        """
        Updates the state, then updates the view from the controller.
        """
        with self.controller.model_session() as session:
            self.controller.update(session)
            self.update_from_controller(session)

            session.commit()

    def update_from_controller(self, session: SASession) -> None:
        self.robots_view.update_from_controller(session)
        self.inventory_view.update_from_controller(session)

    def sizeHint(self) -> QSize:
        return QSize(1366, 768)
