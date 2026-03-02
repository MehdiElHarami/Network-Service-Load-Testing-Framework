import requests

BASE_URL = "http://127.0.0.1:8000"

def test_ping():
    response = requests.get(f"{BASE_URL}/ping")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_login_success():
    response = requests.post(
        f"{BASE_URL}/login",
        params={"username": "admin", "password": "password"}
    )
    assert response.status_code == 200

def test_login_fail():
    response = requests.post(
        f"{BASE_URL}/login",
        params={"username": "wrong", "password": "wrong"}
    )
    assert response.status_code == 401

def test_data():
    response = requests.get(f"{BASE_URL}/data")
    assert response.status_code == 200
    assert "data" in response.json()
