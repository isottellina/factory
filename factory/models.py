import enum

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class RobotAction(enum.Enum):
    MINING_FOO = enum.auto()
    MINING_BAR = enum.auto()
    MAKING_FOOBAR = enum.auto()
    SELLING_FOOBAR = enum.auto()
    BUYING_ROBOT = enum.auto()


class Robot(Base):
    __tablename__ = "robot"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(
        sa.String(64),
        unique=True,
        nullable=False,
        doc="The name of the robot. It should be unique, for the player's sake.",
    )

    action = sa.Column(
        sa.Enum(RobotAction),
        nullable=True,
    )

    time_when_available = sa.Column(
        sa.DateTime,
        nullable=True,
        doc="When this robot will be available to do its scheduled task.",
    )
    time_when_done = sa.Column(
        sa.DateTime,
        nullable=True,
        doc="When this robot will be done with its current task.",
    )
