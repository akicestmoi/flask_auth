from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db: SQLAlchemy = SQLAlchemy()
flask_bcrypt: Bcrypt = Bcrypt()


class Account(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=True)
    username = db.Column(db.String, nullable=True)
    password = db.Column(db.String, nullable=True)
    gender = db.Column(db.String, nullable=True)
    phone_number = db.Column(db.String, nullable=True)
    address = db.Column(db.String, nullable=True)
    is_logged_in = db.Column(db.Boolean, nullable=True, default=False)


    def __init__(self, email: str, username: str, password: str, is_logged_in: bool, gender: str | None, 
                 phone_number: str | None, address: str | None) -> None:
        self.email: str = email
        self.username: str = username
        self.password: str = password
        self.is_logged_in: bool = is_logged_in
        self.gender: str | None = gender
        self.phone_number: str | None = phone_number
        self.address: str | None = address


    def convert_to_dict(self) -> dict[str, str]:
        account_dict: dict[str, str] = self.__dict__
        del account_dict["_sa_instance_state"]
        return account_dict


    @staticmethod
    def get_model_fields(method: str="all") -> list[str]:
        auto: list[str] = ["id", "is_logged_in"]
        required: list[str] = ["email", "username", "password"]
        optional: list[str] = ["gender", "phone_number", "address"]

        if method == "auto":
            return auto
        elif method == "required":
            return required
        elif method == "optional":
            return optional
        else:
            return auto + required + optional
    
    

