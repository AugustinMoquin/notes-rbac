from tests.conftest import auth_headers


def test_signup_returns_token(client):
    res = client.post(
        "/auth/signup",
        json={"org_name": "Acme", "email": "admin@acme.io", "password": "pw-secret-123"},
    )
    assert res.status_code == 201
    assert res.json()["access_token"]


def test_duplicate_email_rejected(client):
    auth_headers(client, "Acme", "admin@acme.io")
    res = client.post(
        "/auth/signup",
        json={"org_name": "Other", "email": "admin@acme.io", "password": "pw-secret-123"},
    )
    assert res.status_code == 409


def test_login_and_me(client):
    auth_headers(client, "Acme", "admin@acme.io")

    res = client.post(
        "/auth/login",
        json={"email": "admin@acme.io", "password": "pw-secret-123"},
    )
    assert res.status_code == 200
    headers = {"Authorization": f"Bearer {res.json()['access_token']}"}

    me = client.get("/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["email"] == "admin@acme.io"
    assert me.json()["role"] == "admin"


def test_login_wrong_password(client):
    auth_headers(client, "Acme", "admin@acme.io")
    res = client.post(
        "/auth/login",
        json={"email": "admin@acme.io", "password": "wrong"},
    )
    assert res.status_code == 401


def test_no_token_is_rejected(client):
    assert client.get("/notes").status_code == 403  # HTTPBearer -> 403 without creds
