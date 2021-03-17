import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base


def get_default_session(filename=None):
    if filename is None:
        filename = os.path.join(
            os.path.dirname(__file__),
            'static',
            'ruwordnet.db'
        )
    if not os.path.exists(filename):
        raise FileNotFoundError(
            f'The file {filename} was not found. '
            f'Please make sure you have provided a correct database filename.'
        )

    engine = create_engine(f'sqlite:///{filename}', echo=False)
    Base.metadata.create_all(engine)

    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    return session
