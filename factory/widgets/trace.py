from typing import Optional, cast

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGroupBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from sqlalchemy.orm import Session as SASession

from factory.controller import StateController
from factory.models import Foobar


class TraceabilityView(QGroupBox):
    """
    View the number of each resources available.
    """

    def insertFoobar(self, foobar: Foobar) -> None:
        current_rowcount = self.table.rowCount()

        assert foobar.foo_used.serial
        assert foobar.bar_used.serial
        foo_item = QTableWidgetItem(foobar.foo_used.serial)
        bar_item = QTableWidgetItem(foobar.bar_used.serial)

        # all type checkers are very annoying with the types ItemFlag and ItemFlags,
        # I guess the binding generator are not very good for enum flags.
        flags = cast(Qt.ItemFlags, Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # type: ignore
        foo_item.setFlags(flags)
        bar_item.setFlags(flags)

        self.table.setRowCount(current_rowcount + 1)
        self.table.setItem(current_rowcount, 0, foo_item)
        self.table.setItem(current_rowcount, 1, bar_item)
        self.table.resizeColumnsToContents()

    def update_from_controller(self, session: SASession) -> None:
        foobars = self.controller.list_sold_foobars(session)

        db_foobars = {foobar.id: foobar for foobar in foobars}
        to_add = set(db_foobars) - self.already_added

        for new_foobar in to_add:
            self.insertFoobar(db_foobars[new_foobar])

        self.already_added.update(set(db_foobars))

    def __init__(self, controller: StateController, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.controller = controller
        self.setTitle("Sold foobars")

        # Foobars already added to this widget
        self.already_added: set[int] = set()

        self.internal_layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Foo used", "Bar used"])

        self.internal_layout.addWidget(self.table)
