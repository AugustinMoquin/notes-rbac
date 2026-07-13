from tests.conftest import auth_headers


def test_create_and_list_notes(client):
    h = auth_headers(client, "Acme", "admin@acme.io")

    res = client.post("/notes", json={"title": "First", "content": "hello"}, headers=h)
    assert res.status_code == 201
    note = res.json()
    assert note["title"] == "First"

    res = client.get("/notes", headers=h)
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_get_missing_note(client):
    h = auth_headers(client, "Acme", "admin@acme.io")
    assert client.get("/notes/999", headers=h).status_code == 404


def test_update_and_delete_own_note(client):
    h = auth_headers(client, "Acme", "admin@acme.io")
    note_id = client.post("/notes", json={"title": "T", "content": ""}, headers=h).json()["id"]

    res = client.put(f"/notes/{note_id}", json={"title": "Updated", "content": "x"}, headers=h)
    assert res.status_code == 200
    assert res.json()["title"] == "Updated"

    assert client.delete(f"/notes/{note_id}", headers=h).status_code == 204
    assert client.get(f"/notes/{note_id}", headers=h).status_code == 404
