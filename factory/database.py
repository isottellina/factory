import sqlalchemy as sa
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from factory.models import Base, GlobalState

# For now, we initialize the database in a file to be able to
# query it with sqlite3 for debugging purposes. Ultimately it
# should be in memory.
engine = create_engine("sqlite:///test.sqlite3")
Session = scoped_session(sessionmaker(engine))


def init_database() -> None:
    """
    This initializes the database with every table it needs.
    """
    Base.metadata.create_all(engine)

    # If there is no global state, we need to create it.
    with engine.begin() as conn:
        global_state = conn.execute(sa.select(GlobalState)).first()

        if not global_state:
            conn.execute(sa.insert(GlobalState))
