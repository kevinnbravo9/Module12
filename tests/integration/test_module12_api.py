import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from main import app
from app.database import get_db
from app.models import Calculation, User


@pytest.fixture
def client(db_session, monkeypatch):
    from app.auth import get_current_user
    from app.database import get_db as database_get_db
    from app.calculation_routes import get_db as routes_get_db
    from app.auth import get_db as auth_get_db

    monkeypatch.setenv(
        "JWT_SECRET_KEY",
        "module12-test-only-secret-key-not-for-production",
    )

    def override_get_db():
        yield db_session

    app.dependency_overrides.clear()

    # Override the database dependency everywhere it is referenced.
    for dependency in (get_db, database_get_db, routes_get_db, auth_get_db):
        app.dependency_overrides[dependency] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


def register(client, username=None):
    username = username or f"user_{uuid.uuid4().hex[:12]}"
    password = "SecurePassword123!"

    response = client.post(
        "/users/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": password,
        },
    )
    return response, username, password


def authenticated_client(client):
    response, username, password = register(client)
    assert response.status_code == 201

    login = client.post(
        "/users/login",
        json={"username": username, "password": password},
    )
    assert login.status_code == 200

    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_register_user(client):
    response, username, _ = register(client)

    assert response.status_code == 201
    assert response.json()["username"] == username
    assert "password" not in response.json()
    assert "password_hash" not in response.json()


def test_duplicate_registration(client):
    response, username, password = register(client)
    assert response.status_code == 201

    duplicate = client.post(
        "/users/register",
        json={
            "username": username,
            "email": f"other_{uuid.uuid4().hex[:8]}@example.com",
            "password": password,
        },
    )

    assert duplicate.status_code == 400


def test_login_success(client):
    response, username, password = register(client)
    assert response.status_code == 201

    login = client.post(
        "/users/login",
        json={"username": username, "password": password},
    )

    assert login.status_code == 200
    assert login.json()["access_token"]
    assert login.json()["token_type"] == "bearer"


def test_login_wrong_password(client):
    response, username, _ = register(client)
    assert response.status_code == 201

    login = client.post(
        "/users/login",
        json={"username": username, "password": "WrongPassword123!"},
    )

    assert login.status_code == 401


def test_invalid_registration(client):
    response = client.post(
        "/users/register",
        json={
            "username": "ab",
            "email": "not-an-email",
            "password": "short",
        },
    )

    assert response.status_code == 422


def test_calculations_require_authentication(client):
    response = client.get("/calculations")
    assert response.status_code == 401

    response = client.post(
        "/calculations",
        json={"type": "addition", "inputs": [10, 20]},
    )
    assert response.status_code == 401


def test_invalid_token(client):
    response = client.get(
        "/calculations",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401


def test_calculation_bread(client):
    headers = authenticated_client(client)

    created = client.post(
        "/calculations",
        json={"type": "addition", "inputs": [10, 20]},
        headers=headers,
    )

    assert created.status_code == 201
    assert created.json()["result"] == 30

    calculation_id = created.json()["id"]

    listed = client.get("/calculations", headers=headers)
    assert listed.status_code == 200
    assert any(
        item["id"] == calculation_id
        for item in listed.json()
    )

    read = client.get(
        f"/calculations/{calculation_id}",
        headers=headers,
    )
    assert read.status_code == 200

    updated = client.put(
        f"/calculations/{calculation_id}",
        json={"inputs": [50, 25]},
        headers=headers,
    )

    assert updated.status_code == 200
    assert updated.json()["result"] == 75

    deleted = client.delete(
        f"/calculations/{calculation_id}",
        headers=headers,
    )

    assert deleted.status_code == 204

    missing = client.get(
        f"/calculations/{calculation_id}",
        headers=headers,
    )

    assert missing.status_code == 404


@pytest.mark.parametrize(
    "operation,inputs,expected",
    [
        ("addition", [10, 20], 30),
        ("subtraction", [10, 20], -10),
        ("multiplication", [10, 20], 200),
        ("division", [20, 10], 2),
    ],
)
def test_calculation_operations(client, operation, inputs, expected):
    headers = authenticated_client(client)

    response = client.post(
        "/calculations",
        json={"type": operation, "inputs": inputs},
        headers=headers,
    )

    assert response.status_code == 201
    assert response.json()["result"] == expected


def test_division_by_zero(client):
    headers = authenticated_client(client)

    response = client.post(
        "/calculations",
        json={"type": "division", "inputs": [10, 0]},
        headers=headers,
    )

    assert response.status_code == 422


def test_invalid_calculation_type(client):
    headers = authenticated_client(client)

    response = client.post(
        "/calculations",
        json={"type": "invalid", "inputs": [10, 20]},
        headers=headers,
    )

    assert response.status_code == 422


def test_user_cannot_access_another_users_calculation(client):
    first_user = authenticated_client(client)

    created = client.post(
        "/calculations",
        json={"type": "addition", "inputs": [5, 5]},
        headers=first_user,
    )
    assert created.status_code == 201

    calculation_id = created.json()["id"]
    second_user = authenticated_client(client)

    for method in ("get", "put", "delete"):
        request = getattr(client, method)

        kwargs = {"headers": second_user}
        if method == "put":
            kwargs["json"] = {"inputs": [100, 100]}

        response = request(
            f"/calculations/{calculation_id}",
            **kwargs,
        )
        assert response.status_code == 404

    listed = client.get("/calculations", headers=second_user)
    assert listed.status_code == 200
    assert all(
        item["id"] != calculation_id
        for item in listed.json()
    )


def test_update_division_by_zero(client):
    headers = authenticated_client(client)

    created = client.post(
        "/calculations",
        json={"type": "division", "inputs": [20, 5]},
        headers=headers,
    )
    assert created.status_code == 201

    calculation_id = created.json()["id"]

    response = client.put(
        f"/calculations/{calculation_id}",
        json={"inputs": [20, 0]},
        headers=headers,
    )

    assert response.status_code == 422

    unchanged = client.get(
        f"/calculations/{calculation_id}",
        headers=headers,
    )

    assert unchanged.status_code == 200
    assert unchanged.json()["result"] == 4
