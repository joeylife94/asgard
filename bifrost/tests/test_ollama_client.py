"""OllamaClient 단위 테스트 (네트워크 없음)"""

import json

import pytest
import requests

from bifrost import ollama as ollama_mod
from bifrost.ollama import OllamaClient


def _resp(status, body):
    r = requests.Response()
    r.status_code = status
    r._content = body if isinstance(body, bytes) else body.encode("utf-8")
    r.url = "http://ollama.test/api/generate"
    r.encoding = "utf-8"
    return r


def _json_resp(status, obj):
    return _resp(status, json.dumps(obj))


@pytest.fixture
def fake(monkeypatch):
    monkeypatch.delenv("BIFROST_OLLAMA_NUM_PREDICT", raising=False)
    monkeypatch.delenv("BIFROST_OLLAMA_ALLOW_FALLBACK", raising=False)

    class Fake:
        def __init__(self):
            self.responses = []
            self.payloads = []
            self.sleeps = []

        def queue(self, *responses):
            self.responses.extend(responses)

    f = Fake()

    def fake_post(url, json=None, **kwargs):
        f.payloads.append(json)
        return f.responses.pop(0)

    monkeypatch.setattr(ollama_mod.requests, "post", fake_post)
    monkeypatch.setattr(ollama_mod.time, "sleep", lambda s: f.sleeps.append(s))
    return f


def _client():
    return OllamaClient(url="http://ollama.test", model="smollm:135m")


def test_5xx_then_200_retries_once(fake):
    fake.queue(
        _json_resp(500, {"error": "boom"}),
        _json_resp(200, {"response": "hello", "done": True}),
    )
    result = _client().analyze("p")
    assert len(fake.payloads) == 2
    assert fake.sleeps == [1]
    assert result["response"] == "hello"
    assert result["metadata"]["model"] == "smollm:135m"
    assert result["metadata"]["done"] is True


def test_5xx_exhausted_raises_with_body(fake):
    fake.queue(*[_json_resp(500, {"error": "boom"}) for _ in range(3)])
    with pytest.raises(Exception) as exc:
        _client().analyze("p")
    msg = str(exc.value)
    assert len(fake.payloads) == 3
    assert fake.sleeps == [1, 2]
    assert "Ollama API 요청 실패" in msg
    assert "500" in msg
    assert "ollama_error: boom" in msg


def test_error_body_truncated(fake):
    fake.queue(*[_json_resp(500, {"error": "x\n" * 5000}) for _ in range(3)])
    with pytest.raises(Exception) as exc:
        _client().analyze("p")
    msg = str(exc.value)
    detail = msg.split("ollama_error: ", 1)[1].rstrip(")")
    assert 0 < len(detail) <= 300
    assert "\n" not in detail
    assert "\n" not in msg


def test_non_json_body_captured(fake):
    fake.queue(*[_resp(502, "upstream exploded") for _ in range(3)])
    with pytest.raises(Exception) as exc:
        _client().analyze("p")
    assert "upstream exploded" in str(exc.value)


def test_404_without_fallback_not_retried(fake):
    fake.queue(_json_resp(404, {"error": "model not found"}))
    with pytest.raises(Exception):
        _client().analyze("p")
    assert len(fake.payloads) == 1
    assert fake.sleeps == []


def test_404_with_fallback_returns_fallback(fake, monkeypatch):
    monkeypatch.setenv("BIFROST_OLLAMA_ALLOW_FALLBACK", "true")
    fake.queue(_json_resp(404, {"error": "model not found"}))
    result = _client().analyze("p")
    assert len(fake.payloads) == 1
    assert fake.sleeps == []
    assert result["response"]
    assert result["metadata"]["model"] == "fallback"
    assert result["metadata"]["fallback_reason"] == "ollama_model_not_available"


def test_400_not_retried(fake):
    fake.queue(_json_resp(400, {"error": "bad request body"}))
    with pytest.raises(Exception) as exc:
        _client().analyze("p")
    assert len(fake.payloads) == 1
    assert fake.sleeps == []
    assert "ollama_error: bad request body" in str(exc.value)


def test_healthy_payload_unchanged(fake, monkeypatch):
    fake.queue(_json_resp(200, {"response": "ok", "done": True}))
    _client().analyze("p")
    assert len(fake.payloads) == 1
    assert fake.sleeps == []
    payload = fake.payloads[0]
    assert payload["model"] == "smollm:135m"
    assert payload["prompt"] == "p"
    assert payload["stream"] is False
    assert "options" not in payload

    monkeypatch.setenv("BIFROST_OLLAMA_NUM_PREDICT", "256")
    fake.queue(_json_resp(200, {"response": "ok", "done": True}))
    _client().analyze("p")
    assert fake.payloads[1]["options"] == {"num_predict": 256}


def test_error_detail_never_raises():
    client = _client()
    assert client._error_detail(Exception("no response attr")) == ""

    class BadResponse:
        def json(self):
            raise ValueError("not json")

        @property
        def text(self):
            raise RuntimeError("text unavailable")

    err = requests.exceptions.HTTPError("x")
    err.response = BadResponse()
    assert client._error_detail(err) == ""
