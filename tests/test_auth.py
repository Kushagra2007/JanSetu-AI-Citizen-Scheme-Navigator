def test_register_new_user(client):
    res = client.post("/api/auth/register", json={
        "name": "Alice", "email": "alice@example.com", "phone": "8888888888",
        "password": "MyPassword1", "language_pref": "en",
    })
    assert res.status_code == 200
    assert res.json()["user"]["email"] == "alice@example.com"


def test_register_duplicate_email(client):
    payload = {"name": "Bob", "email": "bob@example.com", "phone": "7777777777", "password": "pass123"}
    r1 = client.post("/api/auth/register", json=payload)
    assert r1.status_code == 200
    r2 = client.post("/api/auth/register", json=payload)
    assert r2.status_code == 400


def test_register_duplicate_phone(client):
    client.post("/api/auth/register", json={
        "name": "First", "email": "first-phone@example.com", "phone": "7777777777", "password": "pass123",
    })
    res = client.post("/api/auth/register", json={
        "name": "Second", "email": "second-phone@example.com", "phone": "7777777777", "password": "pass123",
    })
    assert res.status_code == 400
    assert res.json()["detail"] == "Phone number already registered"


def test_login_success(client):
    client.post("/api/auth/register", json={"name": "Carol", "email": "carol@example.com", "password": "pw12345"})
    res = client.post("/api/auth/login", json={"email": "carol@example.com", "password": "pw12345"})
    assert res.status_code == 200
    assert "csn_token" in res.cookies


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={"name": "Dave", "email": "dave@example.com", "password": "correctpw"})
    res = client.post("/api/auth/login", json={"email": "dave@example.com", "password": "wrongpw"})
    assert res.status_code == 401


def test_me_requires_auth(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401


def test_me_with_auth(client):
    client.post("/api/auth/register", json={"name": "Eve", "email": "eve@example.com", "password": "pw999999"})
    login = client.post("/api/auth/login", json={"email": "eve@example.com", "password": "pw999999"})
    token = login.cookies.get("csn_token")
    res = client.get("/api/auth/me", cookies={"csn_token": token})
    assert res.status_code == 200
    assert res.json()["email"] == "eve@example.com"
