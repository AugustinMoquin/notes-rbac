from tests.conftest import auth_headers


def _member_headers(client, admin_headers, email):
    """Admin creates a member, then we log in as that member."""
    res = client.post(
        "/users",
        json={"email": email, "password": "pw-secret-123", "role": "member"},
        headers=admin_headers,
    )
    assert res.status_code == 201, res.text
    token = client.post(
        "/auth/login", json={"email": email, "password": "pw-secret-123"}
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_member_cannot_create_users(client):
    admin = auth_headers(client, "Acme", "admin@acme.io")
    member = _member_headers(client, admin, "member@acme.io")

    res = client.post(
        "/users",
        json={"email": "another@acme.io", "password": "pw-secret-123"},
        headers=member,
    )
    assert res.status_code == 403


def test_member_cannot_modify_others_note(client):
    admin = auth_headers(client, "Acme", "admin@acme.io")
    member = _member_headers(client, admin, "member@acme.io")

    admin_note = client.post(
        "/notes", json={"title": "admin note", "content": ""}, headers=admin
    ).json()["id"]

    # Member can see it (same tenant) but cannot edit or delete it.
    assert client.get(f"/notes/{admin_note}", headers=member).status_code == 200
    assert client.put(
        f"/notes/{admin_note}", json={"title": "hax", "content": ""}, headers=member
    ).status_code == 403
    assert client.delete(f"/notes/{admin_note}", headers=member).status_code == 403


def test_admin_can_modify_members_note(client):
    admin = auth_headers(client, "Acme", "admin@acme.io")
    member = _member_headers(client, admin, "member@acme.io")

    member_note = client.post(
        "/notes", json={"title": "member note", "content": ""}, headers=member
    ).json()["id"]

    res = client.put(
        f"/notes/{member_note}", json={"title": "edited by admin", "content": ""}, headers=admin
    )
    assert res.status_code == 200


def test_tenant_isolation(client):
    acme = auth_headers(client, "Acme", "admin@acme.io")
    globex = auth_headers(client, "Globex", "admin@globex.io")

    acme_note = client.post(
        "/notes", json={"title": "acme secret", "content": ""}, headers=acme
    ).json()["id"]

    # Globex must not see Acme's note in listings...
    globex_list = client.get("/notes", headers=globex).json()
    assert globex_list == []

    # ...and direct access is 404, not 403, to avoid leaking existence.
    assert client.get(f"/notes/{acme_note}", headers=globex).status_code == 404
    assert client.put(
        f"/notes/{acme_note}", json={"title": "x", "content": ""}, headers=globex
    ).status_code == 404
