from typing import Optional

from PySide2.QtWidgets import QGroupBox, QLabel, QVBoxLayout, QWidget
from sqlalchemy.orm import Session as SASession

from factory.controller import StateController


class InventoryView(QGroupBox):
    """
    View the number of each resources available.
    """

    def update_from_controller(self, session: SASession) -> None:
        foo_count, bar_count, foobar_count, euros_count = self.controller.counts(
            session
        )

        self.foo_label.setText(f"Foos: {foo_count}")
        self.bar_label.setText(f"Bars: {bar_count}")
        self.foobar_label.setText(f"Foobars: {foobar_count}")
        self.euros_label.setText(f"Money: {euros_count}€")

    def __init__(self, controller: StateController, parent: Optional[QWidget]):
        super().__init__(parent)
        self.controller = controller
        self.setTitle("Inventory")

        self.inventory_layout = QVBoxLayout(self)
        self.foo_label = QLabel("Foos:")
        self.bar_label = QLabel("Bars:")
        self.foobar_label = QLabel("Foobars:")
        self.euros_label = QLabel("Euros:")

        self.inventory_layout.addWidget(self.foo_label)
        self.inventory_layout.addWidget(self.bar_label)
        self.inventory_layout.addWidget(self.foobar_label)
        self.inventory_layout.addWidget(self.euros_label)
        self.inventory_layout.addStretch(1)
