"""
test_app.py – Pytest suite for the AI Chatbot FastAPI backend.

Run with:
    pip install pytest pytest-asyncio httpx
    pytest test_app.py -v

All external dependencies (OpenAI, AWS Secrets Manager) are mocked so no
real credentials are required.
"""

import json
import sys
from contextlib import contextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# ─────────────────────────────────────────────────────────────────────────────
# Bootstrap: import backend with AWS / OpenAI fully mocked
# ─────────────────────────────────────────────────────────────────────────────

FAKE_API_KEY = "sk-test-fake-key-1234567890"

# Patch boto3 before the module loads so top-level credential resolution
# never hits real AWS.
with patch("boto3.session.Session") as _mock_session:
    _mock_client = MagicMock()
    _mock_client.get_secret_value.return_value = {
        "SecretString": json.dumps({"OPENAI_API_KEY": FAKE_API_KEY})
    }
    _mock_session.return_value.client.return_value = _mock_client

    import os
    os.environ.setdefault("OPENAI_API_KEY", FAKE_API_KEY)
    os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")

    sys.modules.pop("backend", None)
    import backend


# ─────────────────────────────────────────────────────────────────────────────
# LLM mock helpers
# ChatOpenAI inherits ainvoke from BaseChatModel. Because ChatOpenAI is a
# Pydantic v2 model, you cannot setattr on an *instance*. We must patch at
# the *class* level instead.
# ─────────────────────────────────────────────────────────────────────────────

_LLM_PATCH_PATH = "langchain_core.language_models.chat_models.BaseChatModel.ainvoke"


@contextmanager
def mock_llm(reply_text: str):
    """Context manager that makes llm.ainvoke return reply_text."""
    mock_response = MagicMock()
    mock_response.content = reply_text
    with patch(_LLM_PATCH_PATH, new=AsyncMock(return_value=mock_response)) as m:
        yield m


@contextmanager
def mock_llm_error(message: str):
    """Context manager that makes llm.ainvoke raise an Exception."""
    with patch(_LLM_PATCH_PATH, new=AsyncMock(side_effect=Exception(message))) as m:
        yield m


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture()
def client():
    return TestClient(backend.app)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Health check
# ─────────────────────────────────────────────────────────────────────────────

class TestHealthCheck:
    def test_health_returns_200(self, client):
        assert client.get("/health").status_code == 200

    def test_health_body(self, client):
        assert client.get("/health").json() == {"status": "ok"}


# ─────────────────────────────────────────────────────────────────────────────
# 2. Root endpoint
# ─────────────────────────────────────────────────────────────────────────────

class TestRoot:
    def test_root_returns_200(self, client):
        assert client.get("/").status_code == 200

    def test_root_contains_message_key(self, client):
        assert "message" in client.get("/").json()

    def test_root_message_mentions_running(self, client):
        assert "running" in client.get("/").json()["message"].lower()


# ─────────────────────────────────────────────────────────────────────────────
# 3. /chat – happy path
# ─────────────────────────────────────────────────────────────────────────────

class TestChatEndpoint:

    def test_chat_returns_200(self, client):
        with mock_llm("Hi there!"):
            assert client.post("/chat", json={"message": "Hi"}).status_code == 200

    def test_chat_returns_reply_key(self, client):
        with mock_llm("Sure thing!"):
            assert "reply" in client.post("/chat", json={"message": "Test"}).json()

    def test_chat_reply_content(self, client):
        expected = "The sky is blue."
        with mock_llm(expected):
            assert client.post("/chat", json={"message": "Sky?"}).json()["reply"] == expected

    def test_chat_default_system_prompt_injected(self, client):
        from langchain_core.messages import SystemMessage
        with mock_llm("OK") as m:
            client.post("/chat", json={"message": "Hello"})
        args = m.call_args[0][0]
        assert isinstance(args[0], SystemMessage)
        assert "helpful" in args[0].content.lower()

    def test_chat_custom_system_prompt(self, client):
        from langchain_core.messages import SystemMessage
        with mock_llm("Arr!") as m:
            client.post("/chat", json={"message": "Who?", "system_prompt": "You are a pirate."})
        args = m.call_args[0][0]
        assert isinstance(args[0], SystemMessage)
        assert "pirate" in args[0].content.lower()

    def test_chat_history_forwarded(self, client):
        from langchain_core.messages import HumanMessage, AIMessage
        with mock_llm("I remember!") as m:
            client.post("/chat", json={
                "message": "Do you remember?",
                "history": [
                    {"role": "user",      "content": "My name is Alice."},
                    {"role": "assistant", "content": "Nice to meet you, Alice!"},
                ],
            })
        types = [type(msg).__name__ for msg in m.call_args[0][0]]
        assert "HumanMessage" in types
        assert "AIMessage" in types

    def test_chat_with_history_returns_reply(self, client):
        with mock_llm("I remember!"):
            resp = client.post("/chat", json={
                "message": "Do you remember?",
                "history": [
                    {"role": "user",      "content": "My name is Alice."},
                    {"role": "assistant", "content": "Nice to meet you, Alice!"},
                ],
            })
        assert resp.status_code == 200
        assert "reply" in resp.json()

    def test_chat_empty_history(self, client):
        with mock_llm("Fresh!"):
            assert client.post("/chat", json={"message": "Start", "history": []}).status_code == 200

    def test_chat_history_empty_content_skipped(self, client):
        with mock_llm("Still works!") as m:
            resp = client.post("/chat", json={
                "message": "Test",
                "history": [
                    {"role": "user",      "content": ""},
                    {"role": "assistant", "content": ""},
                ],
            })
        assert resp.status_code == 200
        # Empty-content history entries must not appear as blank messages
        contents = [msg.content for msg in m.call_args[0][0]]
        assert "" not in contents

    def test_chat_history_unknown_role_ignored(self, client):
        with mock_llm("OK"):
            resp = client.post("/chat", json={
                "message": "Test",
                "history": [{"role": "system", "content": "ignore me"}],
            })
        assert resp.status_code == 200


# ─────────────────────────────────────────────────────────────────────────────
# 4. /chat – error handling
# ─────────────────────────────────────────────────────────────────────────────

class TestChatErrorHandling:

    def test_llm_exception_returns_500(self, client):
        with mock_llm_error("LLM unavailable"):
            assert client.post("/chat", json={"message": "crash"}).status_code == 500

    def test_llm_exception_detail_in_response(self, client):
        with mock_llm_error("LLM unavailable"):
            detail = client.post("/chat", json={"message": "crash"}).json()["detail"]
        assert "LLM unavailable" in detail

    def test_missing_message_field_returns_422(self, client):
        assert client.post("/chat", json={}).status_code == 422

    def test_malformed_json_returns_422(self, client):
        resp = client.post("/chat", content=b"not json",
                           headers={"Content-Type": "application/json"})
        assert resp.status_code == 422


# ─────────────────────────────────────────────────────────────────────────────
# 5. Pydantic ChatRequest model
# ─────────────────────────────────────────────────────────────────────────────

class TestChatRequestModel:

    def test_defaults(self):
        req = backend.ChatRequest(message="hello")
        assert req.history == []
        assert req.system_prompt == "You are a helpful AI assistant."

    def test_custom_fields(self):
        req = backend.ChatRequest(
            message="yo",
            history=[{"role": "user", "content": "prev"}],
            system_prompt="Custom prompt.",
        )
        assert req.message == "yo"
        assert len(req.history) == 1
        assert req.system_prompt == "Custom prompt."

    def test_message_required(self):
        with pytest.raises(Exception):
            backend.ChatRequest()  # message is required


# ─────────────────────────────────────────────────────────────────────────────
# 6. CORS headers
# ─────────────────────────────────────────────────────────────────────────────

class TestCORS:

    def test_cors_allow_origin_present(self, client):
        resp = client.get("/health", headers={"Origin": "http://example.com"})
        assert "access-control-allow-origin" in resp.headers

    def test_cors_preflight(self, client):
        resp = client.options(
            "/chat",
            headers={
                "Origin": "http://example.com",
                "Access-Control-Request-Method": "POST",
            },
        )
        assert resp.status_code in (200, 204)


# ─────────────────────────────────────────────────────────────────────────────
# 7. get_secret helper
# ─────────────────────────────────────────────────────────────────────────────

class TestGetSecret:

    def test_get_secret_success(self):
        mock_client = MagicMock()
        mock_client.get_secret_value.return_value = {
            "SecretString": json.dumps({"OPENAI_API_KEY": "sk-xyz"})
        }
        with patch("boto3.session.Session") as mock_session:
            mock_session.return_value.client.return_value = mock_client
            result = backend.get_secret("my-secret", "us-east-1")
        assert result == {"OPENAI_API_KEY": "sk-xyz"}

    def test_get_secret_client_error_raises(self):
        from botocore.exceptions import ClientError
        mock_client = MagicMock()
        mock_client.get_secret_value.side_effect = ClientError(
            {"Error": {"Code": "ResourceNotFoundException", "Message": "Not found"}},
            "GetSecretValue",
        )
        with patch("boto3.session.Session") as mock_session:
            mock_session.return_value.client.return_value = mock_client
            with pytest.raises(RuntimeError, match="Failed to retrieve secret"):
                backend.get_secret("missing-secret", "us-east-1")

    def test_get_secret_returns_dict(self):
        mock_client = MagicMock()
        mock_client.get_secret_value.return_value = {
            "SecretString": json.dumps({"KEY": "VALUE"})
        }
        with patch("boto3.session.Session") as mock_session:
            mock_session.return_value.client.return_value = mock_client
            result = backend.get_secret("test", "eu-west-1")
        assert isinstance(result, dict)