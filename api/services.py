from flask_sqlalchemy.query import Query
from sqlalchemy.orm.scoping import scoped_session
from .models import Account


def get_missing_field(request_data: dict[str, str]) -> list[str]:
    return [field for field in Account.get_model_fields("required") if field not in request_data.keys()]


def check_email_unicity(session: scoped_session, email: str) -> bool:
    query: Query = session.query(Account).filter(Account.email == email)
    if query.count() < 1:
        return True
    else:
        return False


def check_username_unicity(session: scoped_session, username: str) -> bool:
    query: Query = session.query(Account).filter(Account.username == username)
    if query.count() < 1:
        return True
    else:
        return False


def check_password_validity(password: str) -> dict[str, bool | list[str]]:
    
    is_longer_than_6_words: bool = (len(password) >= 6)
    has_special_character: bool = any(not c.isalnum() for c in password)
    has_capital_letter: bool = any(ele.isupper() for ele in password)
    has_lower_letter: bool = any(ele.islower() for ele in password)
    has_numerical_character: bool = any(char.isdigit() for char in password)
    
    message: list[str] = [(not is_longer_than_6_words) * "password must contain at least 6 characters", 
                          (not has_special_character) * "password must contain at least 1 special character",
                          (not has_capital_letter) * "password must contain at least 1 upper case letter",
                          (not has_lower_letter) * "password must contain at least 1 lower case letter",
                          (not has_numerical_character) * "password must contain at least 1 numerical character"]
    cleaned_message: list[str] = [x for x in message if x != ""]

    validity_dict: dict[str, bool | list[str]] = {"validity": (len(cleaned_message)==0), "message": cleaned_message}
    
    return validity_dict
    

def handle_optional_field_for_signup(request_data: dict[str, str]) -> dict[str, str | None]:
    optional_fields: list[str] = Account.get_model_fields("optional")
    return {field: (request_data[field] if field in request_data.keys() else None) for field in optional_fields}