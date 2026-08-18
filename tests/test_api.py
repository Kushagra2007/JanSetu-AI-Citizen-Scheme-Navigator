def _authed_client(client, email="apitester@example.com", password="testpass123"):
    client.post("/api/auth/register", json={"name": "API Tester", "email": email, "password": password})
    login = client.post("/api/auth/login", json={"email": email, "password": password})
    token = login.cookies.get("csn_token")
    client.cookies.set("csn_token", token)
    return client


def test_list_schemes_public(client):
    res = client.get("/api/schemes")
    assert res.status_code == 200
    assert len(res.json()) >= 20


def test_list_services_public(client):
    res = client.get("/api/services")
    assert res.status_code == 200
    assert len(res.json()) >= 6


def test_get_profile_authenticated(client):
    client = _authed_client(client)
    res = client.get("/api/profile")
    assert res.status_code == 200


def test_update_profile(client):
    client = _authed_client(client, email="profiletest@example.com")
    res = client.put("/api/profile", json={"age": 28, "state": "Kerala", "occupation": "student"})
    assert res.status_code == 200
    profile = client.get("/api/profile").json()
    assert profile["age"] == 28
    assert profile["state"] == "Kerala"


def test_recommended_schemes(client):
    client = _authed_client(client, email="recotest@example.com")
    client.put("/api/profile", json={"age": 25, "income": 100000, "occupation": "farmer", "state": "Bihar"})
    res = client.get("/api/schemes/recommended")
    assert res.status_code == 200
    data = res.json()
    assert len(data) > 0
    assert "score" in data[0]


def test_chat_message_flow(client):
    client = _authed_client(client, email="chattest@example.com")
    res = client.post("/api/chat/message", json={"message": "I am 22 years old student from Delhi", "session_id": "s1"})
    assert res.status_code == 200
    data = res.json()
    assert data["entities"]["age"] == 22
    history = client.get("/api/chat/history?session_id=s1")
    assert len(history.json()) == 2


def test_chat_history_is_preserved_when_the_browser_session_id_changes(client):
    client = _authed_client(client, email="chatpersisttest@example.com")
    client.post("/api/chat/message", json={"message": "I am 22 years old student from Delhi", "session_id": "before-redirect"})

    # A return from another page must restore the account conversation even if
    # the browser no longer has its earlier local session value.
    history = client.get("/api/chat/history?session_id=after-redirect")
    assert len(history.json()) == 2
    assert history.json()[0]["message"] == "I am 22 years old student from Delhi"


def test_chat_page_renders_saved_history_before_javascript_loads(client):
    client = _authed_client(client, email="chatpagetest@example.com")
    message = "How can I get a passport?"
    client.post("/api/chat/message", json={"message": message})

    page = client.get("/chat")
    assert page.status_code == 200
    assert message in page.text


def test_chat_service_message_returns_service_path(client):
    client = _authed_client(client, email="servicechattest@example.com")
    res = client.post("/api/chat/message", json={"message": "I need a passport", "session_id": "s1"})
    assert res.status_code == 200
    assert res.json()["redirect_url"].startswith("/service/")


def test_chat_scholarship_message_returns_filtered_schemes(client):
    client = _authed_client(client, email="schemechattest@example.com")
    res = client.post("/api/chat/message", json={"message": "I need a student scholarship", "session_id": "s1"})
    assert res.status_code == 200
    assert res.json()["redirect_url"] is None
    assert "income" in res.json()["missing_profile_fields"]


def test_create_and_track_application(client):
    client = _authed_client(client, email="apptest@example.com")
    services = client.get("/api/services").json()
    service_id = services[0]["id"]
    res = client.post("/api/applications", json={"type": "service", "ref_id": service_id})
    assert res.status_code == 200
    app_id = res.json()["id"]

    step_res = client.put(f"/api/applications/{app_id}/step", json={"step_index": 0, "completed": True})
    assert step_res.status_code == 200

    status_res = client.put(f"/api/applications/{app_id}/status", json={"status": "submitted"})
    assert status_res.status_code == 200

    list_res = client.get("/api/applications")
    assert any(a["id"] == app_id for a in list_res.json())


def test_notifications_flow(client):
    client = _authed_client(client, email="notiftest@example.com")
    services = client.get("/api/services").json()
    app_res = client.post("/api/applications", json={"type": "service", "ref_id": services[0]["id"]})
    app_id = app_res.json()["id"]
    client.put(f"/api/applications/{app_id}/status", json={"status": "approved"})

    notifs = client.get("/api/notifications").json()
    assert len(notifs) > 0
    unread = client.get("/api/notifications/unread-count").json()
    assert unread["unread_count"] >= 1


def test_digilocker_mock_flow(client):
    client = _authed_client(client, email="digitest@example.com")
    connect_res = client.get("/api/digilocker/connect")
    assert connect_res.status_code == 200
    auth_url = connect_res.json()["auth_url"]
    callback_path = auth_url.replace("http://testserver", "")
    client.get(callback_path, follow_redirects=False)
    me = client.get("/api/auth/me").json()
    assert me["digilocker_connected"] is True
