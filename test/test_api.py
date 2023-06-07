import requests
from .helper import get_account_data, get_account_specifics
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
    response = requests.post(endpoint, json=request_body)
    assert response.status_code == 200

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



def test_logout_works():   
    id_to_logout = get_account_specifics(request_body["email"], "id")
    endpoint = base_endpoint + "/logout/" + str(id_to_logout)
    response = requests.patch(endpoint)
    assert response.status_code == 200

    account_status = get_account_specifics(request_body["email"], "is_logged_in")
    assert account_status == False



def test_login_works():
    endpoint = base_endpoint + "/login"

    login_body = {
        "username": "",
        "password": "",
    }
    response = requests.patch(endpoint, json=login_body)
    assert response.status_code == 400

    login_body = {
        "username": "",
        "password": request_body["password"],
    }
    response = requests.patch(endpoint, json=login_body)
    assert response.status_code == 400

    login_body = {
        "username": request_body["username"],
        "password": "wrong_password"
    }
    response = requests.patch(endpoint, json=login_body)
    assert response.status_code == 400

    login_body = {
        "username": request_body["username"],
        "password": request_body["password"],
    }
    response = requests.patch(endpoint, json=login_body)
    assert response.status_code == 200

    account_status = get_account_specifics(request_body["email"], "is_logged_in")
    assert account_status == True



def test_content_modification():
    id_to_patch = get_account_specifics(request_body["email"], "id")
    endpoint = base_endpoint + "/accounts/" + str(id_to_patch)

    patch_body = {
        "gender": "F",
        "phone_number": "0143058596"
    }
    response = requests.patch(endpoint, json=patch_body)
    assert response.status_code == 200

    patched_data = get_account_data(request_body["email"])
    gender = patched_data["gender"]
    phone_number = patched_data["phone_number"]
    assert gender == patch_body["gender"] and phone_number == patch_body["phone_number"]



def test_reset_optional_field():
    id_to_put = get_account_specifics(request_body["email"], "id")
    endpoint = base_endpoint + "/accounts/" + str(id_to_put)
    response = requests.put(endpoint)
    assert response.status_code == 200

    put_data = get_account_data(request_body["email"])
    optional_fields = Account.get_optional_fields()
    validity_check_list = ["X" for field in optional_fields if put_data[field] is not None]
    assert len(validity_check_list) == 0



def test_delete_works():
    id_to_delete = get_account_specifics(request_body["email"], "id")
    endpoint = base_endpoint + "/accounts/" + str(id_to_delete)

    response = requests.delete(endpoint)
    assert response.status_code == 200

    response = requests.get(endpoint)
    assert response.status_code == 400