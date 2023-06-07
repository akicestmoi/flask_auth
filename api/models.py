from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
flask_bcrypt = Bcrypt()


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
                 phone_number: int | None, address: str | None) -> None:
        self.email = email
        self.username = username
        self.password = password
        self.is_logged_in = is_logged_in
        self.gender = gender
        self.phone_number = phone_number
        self.address = address


    def convert_to_dict(self):
        account_dict = self.__dict__
        del account_dict["_sa_instance_state"]
        return account_dict

    @staticmethod
    def get_auto_completed_required_fields() -> list[str]:
        return ["id", "is_logged_in"]


    @staticmethod
    def get_required_fields() -> list[str]:
        return ["email", "username", "password"]
    

    @staticmethod
    def get_optional_fields() -> list[str]:
        return ["gender", "phone_number", "address"]