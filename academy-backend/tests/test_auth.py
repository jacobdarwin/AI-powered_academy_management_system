def test_login_returns_tokens_and_me(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"role": "superadmin", "userId": "admin@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    body = response.get_json()["data"]
    assert body["user"]["role"] == "superadmin"
    assert body["access_token"]

    me = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {body['access_token']}"}
    )
    assert me.status_code == 200
    assert me.get_json()["data"]["login_id"] == "admin@example.com"


def test_login_rejects_wrong_role_without_disclosure(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"role": "student", "userId": "admin@example.com", "password": "password123"},
    )
    assert response.status_code == 401
    assert response.get_json()["message"] == "Invalid credentials"


def test_role_guard_and_logout_revoke_token(client):
    login = client.post(
        "/api/v1/auth/login",
        json={"role": "superadmin", "userId": "admin@example.com", "password": "password123"},
    )
    token = login.get_json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    assert client.get("/api/v1/protected/superadmin-check", headers=headers).status_code == 200
    assert client.get("/api/v1/protected/staff-check", headers=headers).status_code == 403
    assert client.post("/api/v1/auth/logout", headers=headers).status_code == 200
    assert client.get("/api/v1/auth/me", headers=headers).status_code == 401


def test_login_locks_account_after_five_failures(client):
    payload = {"role": "superadmin", "userId": "admin@example.com", "password": "wrong"}
    for _ in range(5):
        assert client.post("/api/v1/auth/login", json=payload).status_code == 401

    assert (
        client.post(
            "/api/v1/auth/login",
            json={
                "role": "superadmin",
                "userId": "admin@example.com",
                "password": "password123",
            },
        ).status_code
        == 401
    )
