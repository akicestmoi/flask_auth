import requests
from flask import Response
from .test_helper import get_account_data, get_account_specifics
from api.models import Account, flask_bcrypt


base_endpoint: str = "http://127.0.0.1:5555"

request_body: dict[str, str] = {
    "email": "test_email@test.com",
    "username": "test_name",
    "password": "Testpw0-"
}


def test_endpoint_is_accessible() -> None:
    endpoint: str = base_endpoint + "/"
    response: Response = requests.get(endpoint)
    assert response.status_code == 200



def test_database_is_accessible() -> None:
    endpoint: str = base_endpoint + "/db-content"
    response: Response = requests.get(endpoint)
    assert response.status_code == 200 and response.json()



def test_signup_works() -> None:
    endpoint: str = base_endpoint + "/signup"

    body_missing_required_fields: dict[str, str] = {
        "email": "test_email@test.com"
    }
    response: Response = requests.post(endpoint, json=body_missing_required_fields)
    assert response.status_code == 400

    wrong_password_body: dict[str, str] = {
        "email": "test_email@test.com",
        "username": "test_name",
        "password": "wrong_password"
    }
    response: Response = requests.post(endpoint, json=wrong_password_body)
    assert response.status_code == 400

    valid_body: dict[str, str] = request_body
    response: Response = requests.post(endpoint, json=valid_body)
    assert response.status_code == 200

    not_unique_email_body: dict[str, str] = {
        "email": "test_email@test.com",
        "username": "new_user",
        "password": "Testpw0-"
    }
    response: Response = requests.post(endpoint, json=not_unique_email_body)
    assert response.status_code == 400

    not_unique_username_body: dict[str, str] = {
        "email": "new_test_email@test.com",
        "username": "test_name",
        "password": "Testpw0-"
    }
    response: Response = requests.post(endpoint, json=not_unique_username_body)
    assert response.status_code == 400

    posted_data: dict[str, str] = get_account_data(request_body["email"])
    additionnal_body: dict[str, None | bool | int] = {
        "address": None,
        "gender": None,
        "phone_number": None,
        "is_logged_in": True,
        "id": posted_data["id"]
    }
    request_body.update(additionnal_body)
    assert flask_bcrypt.check_password_hash(posted_data["password"], request_body["password"])

    posted_data_without_password: dict[str, str] = {k:v for k,v in posted_data.items() if k not in ("password")}
    request_body_witout_password: dict[str, str] = {k:v for k,v in request_body.items() if k not in ("password")}
    assert posted_data_without_password == request_body_witout_password



def test_can_get_single_account() -> None:
    id_to_get: int = get_account_specifics(request_body["email"], "id")
    endpoint: str = base_endpoint + "/accounts/" + str(id_to_get)
    response: Response = requests.get(endpoint)
    assert response.status_code == 200 and response.json()

    non_existent_id: str = "10000"
    endpoint: str = base_endpoint + "/accounts/" + non_existent_id
    response: Response = requests.get(endpoint)
    assert response.status_code == 404



def test_logout_works() -> None:   
    id_to_logout: int = get_account_specifics(request_body["email"], "id")
    endpoint: str = base_endpoint + "/logout/" + str(id_to_logout)
    response: Response = requests.post(endpoint)
    assert response.status_code == 200

    account_status: bool = get_account_specifics(request_body["email"], "is_logged_in")
    assert account_status == False

    already_logged_out_endpoint: str = endpoint
    response: Response = requests.post(already_logged_out_endpoint)
    assert response.status_code == 400

    non_existent_id: str = "10000"
    endpoint: str = base_endpoint + "/accounts/" + non_existent_id
    response: Response = requests.get(endpoint)
    assert response.status_code == 404



def test_login_works() -> None:
    endpoint: str = base_endpoint + "/login"

    all_wrong_login_body: dict[str, str] = {
        "username": "",
        "password": "",
    }
    response: Response = requests.post(endpoint, json=all_wrong_login_body)
    assert response.status_code == 400

    wrong_username_login_body: dict[str, str] = {
        "username": "",
        "password": request_body["password"],
    }
    response: Response = requests.post(endpoint, json=wrong_username_login_body)
    assert response.status_code == 400

    wrong_password_login_body: dict[str, str] = {
        "username": request_body["username"],
        "password": "wrong_password"
    }
    response: Response = requests.post(endpoint, json=wrong_password_login_body)
    assert response.status_code == 400

    login_body: dict[str, str] = {
        "username": request_body["username"],
        "password": request_body["password"],
    }
    response: Response = requests.post(endpoint, json=login_body)
    assert response.status_code == 200

    account_status: bool = get_account_specifics(request_body["email"], "is_logged_in")
    assert account_status == True

    already_logged_in_body: dict[str, str] = {
        "username": request_body["username"],
        "password": request_body["password"],
    }
    response: Response = requests.post(endpoint, json=already_logged_in_body)
    assert response.status_code == 400



def test_content_modification() -> None:
    id_to_patch: int = get_account_specifics(request_body["email"], "id")
    endpoint: str = base_endpoint + "/accounts/" + str(id_to_patch)

    patch_body: dict[str, str] = {
        "gender": "F",
        "random_field": "random_value", 
        "phone_number": "0143058596"
    }
    response: Response = requests.patch(endpoint, json=patch_body)
    assert response.status_code == 200

    patched_data = get_account_data(request_body["email"])
    gender = patched_data["gender"]
    phone_number = patched_data["phone_number"]
    assert gender == patch_body["gender"] and phone_number == patch_body["phone_number"]

    wrong_password_patch_body = {
        "gender": "M",
        "password": "wrong_password"
    }
    response: Response = requests.patch(endpoint, json=wrong_password_patch_body)
    assert response.status_code == 400
    
    gender: str | None = get_account_specifics(request_body["email"], "gender")
    assert not gender == "M"

    valid_password: str = "Test-pw1"
    valid_password_change_body_no_original_validation: dict[str, str] = {
        "password": valid_password
    }
    response: Response = requests.patch(endpoint, json=valid_password_change_body_no_original_validation)
    assert response.status_code == 400

    valid_password_change_body_but_unvalidated: dict[str, str] = {
        "password_validation": "wrong original password",
        "password": valid_password
    }
    response: Response = requests.patch(endpoint, json=valid_password_change_body_but_unvalidated)
    assert response.status_code == 400

    valid_password_change_body_with_original_validation: dict[str, str] = {
        "password_validation": request_body["password"],
        "password": valid_password
    }
    response: Response = requests.patch(endpoint, json=valid_password_change_body_with_original_validation)
    assert response.status_code == 200
    
    modified_hash_password_in_db: str = get_account_specifics(request_body["email"], "password")
    assert not flask_bcrypt.check_password_hash(modified_hash_password_in_db, request_body["password"])
    assert flask_bcrypt.check_password_hash(modified_hash_password_in_db, valid_password)

    non_existent_id: str = "10000"
    endpoint: str = base_endpoint + "/accounts/" + non_existent_id
    response: Response = requests.get(endpoint)
    assert response.status_code == 404



def test_reset_optional_field() -> None:
    id_to_put: int = get_account_specifics(request_body["email"], "id")
    endpoint: str = base_endpoint + "/accounts/" + str(id_to_put)
    response: Response = requests.put(endpoint)
    assert response.status_code == 200

    put_data: str = get_account_data(request_body["email"])
    optional_fields: list[str] = Account.get_model_fields("optional")
    validity_check_list: list[str] = ["X" for field in optional_fields if put_data[field] is not None]
    assert len(validity_check_list) == 0

    non_existent_id: str = "10000"
    endpoint: str = base_endpoint + "/accounts/" + non_existent_id
    response: Response = requests.get(endpoint)
    assert response.status_code == 404



def test_delete_works() -> None:
    id_to_delete: int = get_account_specifics(request_body["email"], "id")
    endpoint: str = base_endpoint + "/accounts/" + str(id_to_delete)

    response: Response = requests.delete(endpoint)
    assert response.status_code == 200

    already_deleted_endpoint: str = endpoint
    response: Response = requests.get(already_deleted_endpoint)
    assert response.status_code == 404