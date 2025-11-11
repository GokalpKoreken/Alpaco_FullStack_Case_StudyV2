from datetime import datetime, timedelta, timezone


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def _signup(client, email: str, password: str, is_admin: bool = False):
    payload = {"email": email, "password": password, "is_admin": is_admin}
    response = client.post("/auth/signup", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def _login(client, email: str, password: str) -> str:
    response = client.post("/auth/login", data={"username": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_waitlist_claim_idempotency(client):
    admin_email = "admin@example.com"
    user_email = "user@example.com"
    password = "S3curePass!"

    _signup(client, admin_email, password, is_admin=True)
    admin_token = _login(client, admin_email, password)

    now = datetime.now(timezone.utc)
    payload = {
        "title": "Limited Sneaker Drop",
        "description": "Test drop",
        "stock": 1,
        "waitlist_open_at": _iso(now - timedelta(hours=1)),
        "claim_open_at": _iso(now - timedelta(minutes=5)),
        "claim_close_at": _iso(now + timedelta(hours=1)),
        "base_priority": 5,
    }
    create_resp = client.post("/admin/drops", json=payload, headers=_auth_headers(admin_token))
    assert create_resp.status_code == 201, create_resp.text
    drop_id = create_resp.json()["id"]

    _signup(client, user_email, password)
    user_token = _login(client, user_email, password)

    join_resp = client.post(f"/drops/{drop_id}/join", headers=_auth_headers(user_token))
    assert join_resp.status_code == 200, join_resp.text
    assert join_resp.json()["status"] == "joined"

    second_join = client.post(f"/drops/{drop_id}/join", headers=_auth_headers(user_token))
    assert second_join.status_code == 200
    assert second_join.json()["already_joined"] is True

    claim_resp = client.post(f"/drops/{drop_id}/claim", headers=_auth_headers(user_token))
    assert claim_resp.status_code == 200, claim_resp.text
    claim_code = claim_resp.json()["claim_code"]

    repeat_claim = client.post(f"/drops/{drop_id}/claim", headers=_auth_headers(user_token))
    assert repeat_claim.status_code == 200
    assert repeat_claim.json()["claim_code"] == claim_code

    other_signup = _signup(client, "other@example.com", password)
    other_token = _login(client, other_signup["email"], password)

    join_other = client.post(f"/drops/{drop_id}/join", headers=_auth_headers(other_token))
    assert join_other.status_code == 200

    denied_claim = client.post(f"/drops/{drop_id}/claim", headers=_auth_headers(other_token))
    assert denied_claim.status_code == 409
    assert "No remaining" in denied_claim.text
