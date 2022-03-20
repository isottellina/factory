from typing import Optional

import sqlalchemy as sa
from PySide6.QtWidgets import QGroupBox, QListWidget, QVBoxLayout, QWidget
from sqlalchemy.orm import Session as SASession

from factory.controller import StateController
from factory.models import Foobar


class TraceabilityView(QGroupBox):
    """
    View the number of each resources available.
    """

    def update_from_controller(self, session: SASession) -> None:
        foobars = session.scalars(sa.select(Foobar).where(Foobar.used)).all()

        db_foobars = {foobar.serial for foobar in foobars}
        to_add = db_foobars - self.already_added

        for new_foobar in to_add:
            self.list.addItem(new_foobar)

        self.already_added.update(db_foobars)

    def __init__(self, controller: StateController, parent: Optional[QWidget]):
        super().__init__(parent)
        self.controller = controller
        self.setTitle("Sold foobars")

        # Foobars already added to this widget
        self.already_added: set[str] = set()

        self.list_layout = QVBoxLayout(self)
        self.list = QListWidget()

        self.list_layout.addWidget(self.list)
