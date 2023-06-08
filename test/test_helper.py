from config import Config
from api.models import Account
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.session import Session


def create_test_db_session() -> Session:
    db_url: str | None = Config.SQLALCHEMY_DATABASE_URI
    engine: Engine = create_engine(db_url, echo=True)
    session: sessionmaker[Session] = sessionmaker(bind=engine)
    db_session: Session = session()

    return db_session


def close_test_db_session(session, rollback=False) -> None:
    if rollback == True:
        session.rollback()
    session.close()


def get_account_data(account_email: str) -> dict[str, str]:
    session = create_test_db_session()
    data: Account | None = session.query(Account).filter(Account.email == account_email).first()
    data: dict[str, str] = data.convert_to_dict()
    close_test_db_session(session)
    return data


def get_account_specifics(account_email: str, key: str) -> str | int | bool:
    data: dict[str, str] = get_account_data(account_email)
    account_specifics: str | int | bool = data[key]
    return account_specifics