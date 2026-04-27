from src.database.config import settings


def test_registration_success(client):
    response = client.post(
        "/api/auth/registration",
        json={"email": "user@example.com", "username": "my_user", "password": "pass1234"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user"]["username"] == "my_user"
    assert data["user"]["email"] == "user@example.com"
    assert "password" not in data["user"]
    assert settings.SESSION_COOKIE_NAME in response.cookies


def test_registration_duplicate_email(client):
    payload = {"email": "dup@example.com", "username": "user1", "password": "pass1234"}
    client.post("/api/auth/registration", json=payload)

    response = client.post(
        "/api/auth/registration",
        json={"email": "dup@example.com", "username": "user2", "password": "pass5678"}
    )

    assert response.status_code == 409


def test_registration_invalid_data(client):
    response = client.post(
        "/api/auth/registration",
        json={"email": "bad@example.com", "username": "ab", "password": "123"}
    )

    assert response.status_code == 422


def test_login_success(client):
    client.post(
        "/api/auth/registration",
        json={"email": "login@example.com", "username": "loginuser", "password": "pass1234"}
    )

    response = client.post(
        "/api/auth/login",
        json={"email": "login@example.com", "password": "pass1234"}
    )

    assert response.status_code == 200
    assert response.json()["user"]["email"] == "login@example.com"
    assert settings.SESSION_COOKIE_NAME in response.cookies


def test_login_wrong_password(client):
    client.post(
        "/api/auth/registration",
        json={"email": "wp@example.com", "username": "wpuser", "password": "pass1234"}
    )

    response = client.post(
        "/api/auth/login",
        json={"email": "wp@example.com", "password": "wrongpass"}
    )

    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post(
        "/api/auth/login",
        json={"email": "ghost@example.com", "password": "pass1234"}
    )

    assert response.status_code == 401


def test_logout_success(client):
    client.post(
        "/api/auth/registration",
        json={"email": "logout@example.com", "username": "logoutuser", "password": "pass1234"}
    )

    response = client.post("/api/auth/logout")

    assert response.status_code == 200
    assert response.json() == {"detail": "Logged out"}
