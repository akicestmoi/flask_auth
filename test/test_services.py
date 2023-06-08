from sqlalchemy.orm.session import Session
from api.services import *
from .test_helper import create_test_db_session, close_test_db_session


def test_optional_fields_returns_correct_dict() -> None:
    params: dict = {}
    assert get_missing_field(params) == ["email", "username", "password"]

    params: dict[str, str] = {"random_field": "random_value"}
    assert get_missing_field(params) == ["email", "username", "password"]

    params: dict[str, str] = {"username": "test"}
    assert get_missing_field(params) == ["email", "password"]

    params: dict[str, str] = {"random_field": "random_value", "password": "test_password", "email": "test_email"}
    assert get_missing_field(params) == ["username"]



def test_email_unicity_checker_works() -> None:
    test_email: str = "test_email@email.test"

    session: Session = create_test_db_session()
    assert check_email_unicity(session, "test_email@email.test")
    
    session.add(Account(test_email, "test_user", "test_pw", True, None, None, None))
    assert not check_email_unicity(session, "test_email@email.test")
    close_test_db_session(session, rollback=True)



def test_username_unicity_checker_works() -> None:
    test_username: str = "test_user"

    session: Session = create_test_db_session()
    assert check_username_unicity(session, test_username)
    
    session.add(Account("test_email@email.test", test_username, "test_pw", True, None, None, None))
    assert not check_username_unicity(session, test_username)
    close_test_db_session(session, rollback=True)



def test_password_checker_works() -> None:
    password: str = "test"
    assert not check_password_validity(password)["validity"]
    assert len(check_password_validity(password)["message"]) == 4

    password: str = "TEST"
    assert not check_password_validity(password)["validity"]
    assert len(check_password_validity(password)["message"]) == 4

    password: str = "testpw"
    assert not check_password_validity(password)["validity"]
    assert len(check_password_validity(password)["message"]) == 3

    password: str = "Testpw"
    assert not check_password_validity(password)["validity"]
    assert len(check_password_validity(password)["message"]) == 2

    password: str = "testpw*"
    assert not check_password_validity(password)["validity"]
    assert len(check_password_validity(password)["message"]) == 2

    password: str = "Testpw*"
    assert not check_password_validity(password)["validity"]
    assert len(check_password_validity(password)["message"]) == 1

    password: str = "Testpw0*"
    assert check_password_validity(password)["validity"]
    assert len(check_password_validity(password)["message"]) == 0



def test_optional_field_has_value() -> None:
    params: dict = {}
    valid_result: dict[str, None] = {"gender": None, "phone_number": None, "address": None}
    assert handle_optional_field_for_signup(params) == valid_result

    params: dict[str, str] = {"random_param": "random_value"}
    valid_result: dict[str, None]  = {"gender": None, "phone_number": None, "address": None}
    assert handle_optional_field_for_signup(params) == valid_result

    params: dict[str, str] = {"random_param": "random_value", "gender": "M"}
    valid_result: dict[str, str | None] = {"gender": "M", "phone_number": None, "address": None}
    assert handle_optional_field_for_signup(params) == valid_result

    params: dict[str, str] = {"gender": "F", "phone_number": "0101010101", "address": "random_address"}
    assert handle_optional_field_for_signup(params) == params