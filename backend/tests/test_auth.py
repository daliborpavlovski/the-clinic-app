import pytest


def test_register_success(client):
    res = client.post("/api/v1/auth/register", json={
        "email": "new@example.com",
        "password": "Password1",
        "full_name": "New User",
    })
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "new@example.com"
    assert data["role"] == "patient"


def test_register_duplicate_email(client):
    payload = {"email": "dup@example.com", "password": "Password1", "full_name": "User"}
    client.post("/api/v1/auth/register", json=payload)
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 409


def test_register_weak_password(client):
    res = client.post("/api/v1/auth/register", json={
        "email": "weak@example.com",
        "password": "short",
        "full_name": "Weak",
    })
    assert res.status_code == 422


def test_register_no_digit_password(client):
    res = client.post("/api/v1/auth/register", json={
        "email": "nodigit@example.com",
        "password": "NoDigitPass",
        "full_name": "No Digit",
    })
    assert res.status_code == 422


def test_login_success(client):
    client.post("/api/v1/auth/register", json={
        "email": "login@example.com",
        "password": "Password1",
        "full_name": "Login User",
    })
    res = client.post("/api/v1/auth/login", json={
        "email": "login@example.com",
        "password": "Password1",
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post("/api/v1/auth/register", json={
        "email": "wrongpwd@example.com",
        "password": "Password1",
        "full_name": "Test",
    })
    res = client.post("/api/v1/auth/login", json={
        "email": "wrongpwd@example.com",
        "password": "WrongPass1",
    })
    assert res.status_code == 401


def test_login_nonexistent_email(client):
    res = client.post("/api/v1/auth/login", json={
        "email": "nobody@example.com",
        "password": "Password1",
    })
    assert res.status_code == 401


def test_get_me(client):
    client.post("/api/v1/auth/register", json={
        "email": "me@example.com",
        "password": "Password1",
        "full_name": "Me User",
    })
    tokens = client.post("/api/v1/auth/login", json={
        "email": "me@example.com",
        "password": "Password1",
    }).json()

    res = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert res.status_code == 200
    assert res.json()["email"] == "me@example.com"
