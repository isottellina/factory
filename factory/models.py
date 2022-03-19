import enum
import uuid

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, declarative_base, declared_attr, relationship
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.elements import not_

Base = declarative_base()


class PKMixin:
    """
    This adds a primary key to models. Even though most of the models
    have a column that is unique to a single object, we still have an
    auto-incrementing PK because most of the others are strings, and
    possibly subject to change in subsequent versions.
    """

    id: Mapped[int] = sa.Column(sa.Integer, primary_key=True, autoincrement=True)


class UsableMixin:
    """
    Mixin for objects that can be used for something.
    """

    used = sa.Column(
        sa.Boolean,
        default=False,
        nullable=False,
        doc="Has this object been used?",
    )

    @classmethod
    def count_not_used(cls, session: Session) -> int:
        """
        Returns the number of instances that weren't used.
        """
        return session.scalar(  # type: ignore
            sa.select(sa.func.count(cls.used)).where(not_(cls.used))
        )


class RobotAction(enum.Enum):
    MINING_FOO = enum.auto()
    MINING_BAR = enum.auto()
    MAKING_FOOBAR = enum.auto()
    SELLING_FOOBAR = enum.auto()
    BUYING_ROBOT = enum.auto()

    def to_string(self) -> str:
        """
        Returns the name of an action, as it should be printed to the user.
        """
        return {
            RobotAction.MINING_BAR: "Mining bar",
            RobotAction.MINING_FOO: "Mining foo",
            RobotAction.MAKING_FOOBAR: "Making foobar",
            RobotAction.SELLING_FOOBAR: "Selling foobar",
            RobotAction.BUYING_ROBOT: "Buying a robot",
        }[self]


class Robot(Base, PKMixin):
    __tablename__ = "robot"

    name: Mapped[str] = sa.Column(
        sa.String(64),
        unique=True,
        nullable=False,
        doc="The name of the robot. It should be unique, for the player's sake.",
    )

    action = sa.Column(
        sa.Enum(RobotAction),
        nullable=True,
    )

    time_started = sa.Column(
        sa.DateTime,
        nullable=True,
        doc="When this robot started its current action or started changing its state.",
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


def gen_uuid() -> str:
    """
    We have to generate a string UUID, since SQLite doesn't support the UUID type.
    """
    return uuid.uuid4().hex


class MiningProductMixin:
    """
    This is a mixin for Foo and Bar, seeing as they share most of their columns.
    We don't make them into a single table, however, to ensure consistency.
    """

    serial = sa.Column(
        sa.String(32), default=gen_uuid, doc="For traceability purposes."
    )

    @declared_attr
    def miner_id(cls) -> sa.Column[sa.Integer]:
        return sa.Column(sa.Integer, sa.ForeignKey(Robot.id))

    @declared_attr
    def mined_by(cls) -> Mapped[Robot]:
        return relationship(Robot)


class Foo(Base, PKMixin, MiningProductMixin, UsableMixin):
    __tablename__ = "foo"


class Bar(Base, PKMixin, MiningProductMixin, UsableMixin):
    __tablename__ = "bar"


class Foobar(Base, PKMixin, UsableMixin):
    __tablename__ = "foobar"

    foo_used_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Foo.id),
        doc="The Foo used to make this Foobar",
    )
    bar_used_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Bar.id),
        doc="The Bar used to make this Foobar",
    )

    foo_used: Foo = relationship(Foo)
    bar_used: Bar = relationship(Bar)


class GlobalState(Base, PKMixin):
    """
    Singleton for the information that we can't put elsewhere.
    """

    __tablename__ = "global_state"

    euros = sa.Column(sa.Integer, default=0, nullable=False)
