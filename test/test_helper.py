from config import Config
from api.models import Account
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def create_test_db_session():
    db_url = Config.SQLALCHEMY_DATABASE_URI
    engine = create_engine(db_url, echo=True)
    Session = sessionmaker(bind=engine)
    db_session = Session()

    return db_session


def close_test_db_session(session, rollback=False):
    if rollback == True:
        session.rollback()
    session.close()


def get_account_data(account_email: str) -> dict[str, str]:
    session = create_test_db_session()
    data = session.query(Account).filter(Account.email == account_email).first()
    data = data.convert_to_dict()
    close_test_db_session(session)
    return data


def get_account_specifics(account_email: str, key: str) -> str|int|bool:
    data = get_account_data(account_email)
    account_specifics: str|int|bool = data[key]
    return account_specifics