from unittest.mock import MagicMock, patch
from ai_assistant import _catalogue_context, generate_citizen_reply
from types import SimpleNamespace


def test_catalogue_context_generation():
    schemes = [
        SimpleNamespace(
            name="PM Kisan", description="Income support for farmers",
            benefits="Rs 6000/year", min_age=18, max_age=None,
            max_income=None, caste_categories="[]", occupations="['farmer']",
            states="['All']",
        )
    ]
    services = [
        SimpleNamespace(
            name="PAN Card", description="Permanent Account Number",
            fee="Rs 107", duration_estimate="15 days",
        )
    ]
    context = _catalogue_context(schemes, services)
    assert "PM Kisan" in context
    assert "PAN Card" in context


def test_generate_citizen_reply_none_when_no_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    reply = generate_citizen_reply("Hello", "en", {}, [], [], [])
    assert reply is None


def test_generate_citizen_reply_mocked(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-mock-key")
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

    fake_response = MagicMock()
    fake_response.read.return_value = b'{"candidates": [{"content": {"parts": [{"text": "Hello citizen, you may be eligible."}]}}]}'
    fake_response.__enter__.return_value = fake_response
    fake_response.__exit__.return_value = None

    with patch("ai_assistant.urlopen", return_value=fake_response):
        reply = generate_citizen_reply("What scheme for farmers?", "en", {"age": 30}, [], [], [])
        assert reply == "Hello citizen, you may be eligible."


def test_vercel_entrypoint_imports_app():
    from api.index import app
    assert app.title == "Citizen Service Navigator"
