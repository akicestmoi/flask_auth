from flask import Blueprint, request, make_response, jsonify
from .models import Account, db, flask_bcrypt
from . import services

authentication = Blueprint("authentication", __name__)

@authentication.route("/")
def home():
    return "The server is ready to be used"


@authentication.route("/db-content", methods=["GET"])
def show_db_content():
    try:
        all_accounts = db.session.query(Account).order_by(Account.id)
        return make_response(jsonify([account.convert_to_dict() for account in all_accounts]), 200)
    except Exception as e:
        print(e)
        return make_response(jsonify({"status": "failure", "message": "get request failed", "code": "500"}), 500)


@authentication.route("/accounts/<id>", methods=["GET"])
def get_account(id: int):
    try:
        account_info = db.session.query(Account).filter(Account.id == id).first()
        if not account_info:
            return make_response(jsonify({"status": "failure", "message": "the account does not exist", "code": "404"}), 404)
        
        return make_response(jsonify({"status": "success", "message": account_info.convert_to_dict(), "code": "200"}), 200)
    except Exception as e:
        print(e)
        return make_response(jsonify({"status": "failure", "message": "account request failed", "code": "500"}), 500)
    

@authentication.route("/signup", methods=["POST"])
def signup():
    try:
        data: any = request.get_json()
        missing_fields: list[str] = services.get_missing_field(data)
        optional_fields_dict: dict[str, str|None] = services.handle_optional_field_for_signup(data)

        if len(missing_fields) != 0:
            message = "missing field: " + ", ".join(missing_fields)
            return make_response(jsonify({"status": "failure", "message": message, "code": "400"}), 400)
    
        if not services.check_email_unicity(db.session, data["email"]):
            message = "an account is already registered with this email"
            return make_response(jsonify({"status": "failure", "message": message, "code": "400"}), 400)

        if not services.check_username_unicity(db.session, data["username"]):
            message = "the username is already taken"
            return make_response(jsonify({"status": "failure", "message": message, "code": "400"}), 400)

        password_validity_check = services.check_password_validity(data["password"])
        is_password_valid = password_validity_check["validity"]
        password_not_valid_message = password_validity_check["message"]
        
        if not is_password_valid:
            return make_response(jsonify({"status": "failure", "message": password_not_valid_message, "code": "400"}), 400)

        new_account = Account(email=data["email"], username=data["username"], 
                              password=flask_bcrypt.generate_password_hash(data["password"]).decode("utf-8"), 
                              gender=optional_fields_dict["gender"], phone_number=optional_fields_dict["phone_number"],
                              address=optional_fields_dict["address"], is_logged_in=True)
        db.session.add(new_account)
        db.session.commit()
        return make_response(jsonify({"status": "success", "message": "signup success", "code": "200"}), 200)
                    
    except Exception as e:
        print(e)
        return make_response(jsonify({"status": "failure", "message": "signup request failed", "code": "500"}), 500)


@authentication.route("/login", methods=["PATCH"])
def login():
    try:
        data = request.get_json()
        account = db.session.query(Account).filter(Account.username == data["username"]).first()

        if account is None:
            return make_response(jsonify({"status": "failure", "message": "wrong username", "code": "400"}), 400)
        
        if account.is_logged_in == True:
            return make_response(jsonify({"status": "failure", "message": "the account is already logged in", "code": "400"}), 400)
        
        real_password: str = account.password
        if not flask_bcrypt.check_password_hash(real_password, data["password"]):
            return make_response(jsonify({"status": "failure", "message": "wrong password", "code": "400"}), 400)
                    
        account.is_logged_in = True
        db.session.commit()
        return make_response(jsonify({"status": "success", "message": "login success", "code": "200"}), 200)
               
    except Exception as e:
        print(e)
        return make_response(jsonify({"status": "failure", "message": "login request failed", "code": "500"}), 500)
    


@authentication.route("/logout/<id>", methods=["PATCH"])
def logout(id: int):
    try:
        account_to_logout = db.session.query(Account).filter(Account.id == id).first()
        if account_to_logout is None:
            return make_response(jsonify({"status": "failure", "message": "the account does not exist", "code": "404"}), 404)
        
        if account_to_logout.is_logged_in == False:
            return make_response(jsonify({"status": "failure", "message": "the account is already logged out", "code": "400"}), 400)
        
        account_to_logout.is_logged_in = False
        db.session.commit()
        return make_response(jsonify({"status": "success", "message": "the account has been logged out", "code": "200"}), 200)
            
    except:
        return make_response(jsonify({"status": "failure", "message": "logout request failed", "code": "500"}), 500)



@authentication.route("/accounts/<id>", methods=["PATCH"])
def modify_content(id: int):
    try:
        request_params = request.get_json()
        account_to_update = db.session.query(Account).filter(Account.id == id).first()

        if account_to_update is None:
            return make_response(jsonify({"status": "failure", "message": "the account does not exist", "code": "400"}), 400)
        
        for column_name in request_params.keys():
            if column_name != "password" and column_name in Account.get_model_fields():
                setattr(account_to_update, column_name, request_params[column_name])
            elif column_name == "password":
                if "password_validation" not in request_params.keys():
                    message = "'password_validation' field missing (should contain original password as value)"
                    return make_response(jsonify({"status": "failure", "message": message, "code": "400"}), 400)
                    
                is_original_password_validated = flask_bcrypt.check_password_hash(account_to_update.password, 
                                                                                  request_params["password_validation"])
                            
                if not is_original_password_validated:
                    message = "wrong original password"
                    return make_response(jsonify({"status": "failure", "message": message, "code": "400"}), 400)  
                
                password_validity_check = services.check_password_validity(request_params[column_name])
                is_password_valid = password_validity_check["validity"]
                password_not_valid_message = password_validity_check["message"]

                if not is_password_valid:
                    return make_response(jsonify({"status": "failure", "message": password_not_valid_message, "code": "400"}), 400)
                
                new_password = flask_bcrypt.generate_password_hash(request_params[column_name]).decode("utf-8")
                setattr(account_to_update, column_name, new_password)  
                        
        db.session.commit()
        return make_response(jsonify({"status": "success", "message": "the account has been updated", "code": "200"}), 200)
            
    except Exception as e:
        print(e)
        return make_response(jsonify({"status": "failure", "message": "updated request failed", "code": "500"}), 500)



@authentication.route("/accounts/<id>", methods=["PUT"])
def reset_optional_field(id: int):
    try:
        account_to_update = db.session.query(Account).filter(Account.id == id).first()
        if account_to_update is None:
            return make_response(jsonify({"status": "failure", "message": "the account does not exist", "code": "404"}), 404)
        
        required_fields: list[str] = Account.get_model_fields("required") + Account.get_model_fields("auto")
        new_body = {param: (getattr(account_to_update, param) if param in required_fields else None) 
                    for param in Account.__table__.columns.keys()}
        for column_name, new_value in new_body.items():
            setattr(account_to_update, column_name, new_value)
        db.session.commit()
        return make_response(jsonify({"status": "success", "message": "the account has been updated", "code": "200"}), 200)
            
    except Exception as e:
        print(e)
        return make_response(jsonify({"status": "failure", "message": "updated request failed", "code": "500"}), 500)
    


@authentication.route("/accounts/<id>", methods=["DELETE"])
def delete_account(id: int):
    try:
        account_to_delete = db.session.query(Account).filter(Account.id == id).first()
        if account_to_delete is None:
            return make_response(jsonify({"status": "failure", "message": "the account does not exist", "code": "404"}), 404)
        
        db.session.delete(account_to_delete)
        db.session.commit()
        return make_response(jsonify({"status": "success", "message": "the account has been deleted", "code": "200"}), 200)
            
    except Exception as e:
        print(e)
        return make_response(jsonify({"status": "failure", "message": "delete request failed", "code": "500"}), 500)