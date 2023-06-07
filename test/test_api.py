import requests
from .test_helper import get_account_data, get_account_specifics
from api.models import Account, flask_bcrypt


base_endpoint = "http://127.0.0.1:5555"

request_body = {
    "email": "test_email@test.com",
    "username": "test_name",
    "password": "Testpw0-"
}


def test_endpoint_is_accessible():
    endpoint = base_endpoint + "/"
    response = requests.get(endpoint)
    assert response.status_code == 200



def test_database_is_accessible():
    endpoint = base_endpoint + "/db-content"
    response = requests.get(endpoint)
    assert response.status_code == 200 and response.json()



def test_signup_works():
    endpoint = base_endpoint + "/signup"

    body_missing_required_fields = {
        "email": "test_email@test.com"
    }
    response = requests.post(endpoint, json=body_missing_required_fields)
    assert response.status_code == 400

    wrong_password_body = {
        "email": "test_email@test.com",
        "username": "test_name",
        "password": "wrong_password"
    }
    response = requests.post(endpoint, json=wrong_password_body)
    assert response.status_code == 400

    valid_body = request_body
    response = requests.post(endpoint, json=valid_body)
    assert response.status_code == 200

    not_unique_email_body = {
        "email": "test_email@test.com",
        "username": "new_user",
        "password": "Testpw0-"
    }
    response = requests.post(endpoint, json=not_unique_email_body)
    assert response.status_code == 400

    not_unique_username_body = {
        "email": "new_test_email@test.com",
        "username": "test_name",
        "password": "Testpw0-"
    }
    response = requests.post(endpoint, json=not_unique_username_body)
    assert response.status_code == 400

    posted_data = get_account_data(request_body["email"])
    additionnal_body = {
        "address": None,
        "gender": None,
        "phone_number": None,
        "is_logged_in": True,
        "id": posted_data["id"]
    }
    request_body.update(additionnal_body)
    assert flask_bcrypt.check_password_hash(posted_data["password"], request_body["password"])

    posted_data_without_password = {k:v for k,v in posted_data.items() if k not in ("password")}
    request_body_witout_password = {k:v for k,v in request_body.items() if k not in ("password")}
    assert posted_data_without_password == request_body_witout_password



def test_can_get_single_account():
    id_to_get = get_account_specifics(request_body["email"], "id")
    endpoint = base_endpoint + "/accounts/" + str(id_to_get)
    response = requests.get(endpoint)
    assert response.status_code == 200 and response.json()

    non_existent_id = "10000"
    endpoint = base_endpoint + "/accounts/" + non_existent_id
    response = requests.get(endpoint)
    assert response.status_code == 404



def test_logout_works():   
    id_to_logout = get_account_specifics(request_body["email"], "id")
    endpoint = base_endpoint + "/logout/" + str(id_to_logout)
    response = requests.patch(endpoint)
    assert response.status_code == 200

    account_status = get_account_specifics(request_body["email"], "is_logged_in")
    assert account_status == False

    already_logged_out_endpoint = endpoint
    response = requests.patch(already_logged_out_endpoint)
    assert response.status_code == 400

    non_existent_id = "10000"
    endpoint = base_endpoint + "/accounts/" + non_existent_id
    response = requests.get(endpoint)
    assert response.status_code == 404



def test_login_works():
    endpoint = base_endpoint + "/login"

    all_wrong_login_body = {
        "username": "",
        "password": "",
    }
    response = requests.patch(endpoint, json=all_wrong_login_body)
    assert response.status_code == 400

    wrong_username_login_body = {
        "username": "",
        "password": request_body["password"],
    }
    response = requests.patch(endpoint, json=wrong_username_login_body)
    assert response.status_code == 400

    wrong_password_login_body = {
        "username": request_body["username"],
        "password": "wrong_password"
    }
    response = requests.patch(endpoint, json=wrong_password_login_body)
    assert response.status_code == 400

    login_body = {
        "username": request_body["username"],
        "password": request_body["password"],
    }
    response = requests.patch(endpoint, json=login_body)
    assert response.status_code == 200

    account_status = get_account_specifics(request_body["email"], "is_logged_in")
    assert account_status == True

    already_logged_in_body = {
        "username": request_body["username"],
        "password": request_body["password"],
    }
    response = requests.patch(endpoint, json=already_logged_in_body)
    assert response.status_code == 400



def test_content_modification():
    id_to_patch = get_account_specifics(request_body["email"], "id")
    endpoint = base_endpoint + "/accounts/" + str(id_to_patch)

    patch_body = {
        "gender": "F",
        "random_field": "random_value", 
        "phone_number": "0143058596"
    }
    response = requests.patch(endpoint, json=patch_body)
    assert response.status_code == 200

    patched_data = get_account_data(request_body["email"])
    gender = patched_data["gender"]
    phone_number = patched_data["phone_number"]
    assert gender == patch_body["gender"] and phone_number == patch_body["phone_number"]

    wrong_password_patch_body = {
        "gender": "M",
        "password": "wrong_password"
    }
    response = requests.patch(endpoint, json=wrong_password_patch_body)
    assert response.status_code == 400
    
    gender = get_account_specifics(request_body["email"], "gender")
    assert not gender == "M"

    valid_password = "Test-pw1"
    valid_password_change_body_no_original_validation = {
        "password": valid_password
    }
    response = requests.patch(endpoint, json=valid_password_change_body_no_original_validation)
    assert response.status_code == 400

    valid_password_change_body_but_unvalidated = {
        "password_validation": "wrong original password",
        "password": valid_password
    }
    response = requests.patch(endpoint, json=valid_password_change_body_but_unvalidated)
    assert response.status_code == 400

    valid_password_change_body_with_original_validation = {
        "password_validation": request_body["password"],
        "password": valid_password
    }
    response = requests.patch(endpoint, json=valid_password_change_body_with_original_validation)
    assert response.status_code == 200
    
    modified_hash_password_in_db = get_account_specifics(request_body["email"], "password")
    assert not flask_bcrypt.check_password_hash(modified_hash_password_in_db, request_body["password"])
    assert flask_bcrypt.check_password_hash(modified_hash_password_in_db, valid_password)

    non_existent_id = "10000"
    endpoint = base_endpoint + "/accounts/" + non_existent_id
    response = requests.get(endpoint)
    assert response.status_code == 404



def test_reset_optional_field():
    id_to_put = get_account_specifics(request_body["email"], "id")
    endpoint = base_endpoint + "/accounts/" + str(id_to_put)
    response = requests.put(endpoint)
    assert response.status_code == 200

    put_data = get_account_data(request_body["email"])
    optional_fields = Account.get_model_fields("optional")
    validity_check_list = ["X" for field in optional_fields if put_data[field] is not None]
    assert len(validity_check_list) == 0

    non_existent_id = "10000"
    endpoint = base_endpoint + "/accounts/" + non_existent_id
    response = requests.get(endpoint)
    assert response.status_code == 404



def test_delete_works():
    id_to_delete = get_account_specifics(request_body["email"], "id")
    endpoint = base_endpoint + "/accounts/" + str(id_to_delete)

    response = requests.delete(endpoint)
    assert response.status_code == 200

    already_deleted_endpoint = endpoint
    response = requests.get(already_deleted_endpoint)
    assert response.status_code == 404