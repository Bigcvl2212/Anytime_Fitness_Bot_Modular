import base64
import json
from typing import List

import pytest
import requests

from src.services.api.v2_invoice_fetcher import V2InvoiceError, V2InvoiceFetcher


def _make_token(payload: dict) -> str:
    header = base64.urlsafe_b64encode(json.dumps({"alg": "HS256"}).encode()).rstrip(b"=")
    body = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=")
    return f"{header.decode()}.{body.decode()}.signature"


class DummyResponse:
    def __init__(self, status_code: int, json_data=None, text: str = ""):
        self.status_code = status_code
        self._json_data = json_data
        self.text = text

    def json(self):
        if self._json_data is None:
            raise json.JSONDecodeError("", "", 0)
        return self._json_data


class DummySession:
    def __init__(self, responses: List[DummyResponse]):
        self._responses = responses
        self.cookies = requests.cookies.RequestsCookieJar()
        self.request_log = []

    def get(self, url, headers=None, cookies=None, timeout=None):
        self.request_log.append({
            "url": url,
            "headers": headers,
            "cookies": cookies,
            "timeout": timeout,
        })
        if not self._responses:
            raise RuntimeError("No more responses configured")
        return self._responses.pop(0)


@pytest.fixture(autouse=True)
def fast_sleep(monkeypatch):
    monkeypatch.setattr("src.services.api.v2_invoice_fetcher.time.sleep", lambda *_: None)


def test_fetch_success_single_attempt():
    payload = {
        "delegatedUserId": 186188573,
        "loggedInUserId": 187032782,
        "sessionId": "SESSION123",
    }
    token = _make_token(payload)
    response = DummyResponse(200, json_data={"invoices": []})
    session = DummySession([response])
    session.cookies.set("JSESSIONID", "SESSION123")
    session.cookies.set("delegatedUserId", "186188573")
    session.cookies.set("loggedInUserId", "187032782")
    session.cookies.set("apiV3AccessToken", token)

    fetcher = V2InvoiceFetcher(session=session, base_url="https://example.com")
    data = fetcher.fetch("1651819", token)

    assert data == {"invoices": []}
    assert session.request_log[0]["cookies"]["JSESSIONID"] == "SESSION123"
    assert "Authorization" in session.request_log[0]["headers"]


def test_fetch_retry_then_success():
    payload = {
        "delegatedUserId": 1,
        "loggedInUserId": 2,
        "sessionId": "S",
    }
    token = _make_token(payload)
    session = DummySession([
        DummyResponse(500, text="boom"),
        DummyResponse(200, json_data={"invoices": [1]}),
    ])
    session.cookies.set("JSESSIONID", "S")
    session.cookies.set("delegatedUserId", "1")
    session.cookies.set("loggedInUserId", "2")
    session.cookies.set("apiV3AccessToken", token)

    fetcher = V2InvoiceFetcher(session=session, base_url="https://example.com")
    result = fetcher.fetch("1651819", token, retry_attempts=2, retry_backoff=0)

    assert result["invoices"] == [1]
    assert len(session.request_log) == 2
    assert session.request_log[0]["url"] != session.request_log[1]["url"]


def test_fetch_scope_mismatch_raises():
    payload = {
        "delegatedUserId": 1,
        "loggedInUserId": 2,
        "sessionId": "S",
    }
    token = _make_token(payload)
    session = DummySession([])
    session.cookies.set("JSESSIONID", "WRONG")
    session.cookies.set("delegatedUserId", "1")
    session.cookies.set("loggedInUserId", "2")
    session.cookies.set("apiV3AccessToken", token)

    fetcher = V2InvoiceFetcher(session=session, base_url="https://example.com")

    with pytest.raises(V2InvoiceError, match="Session mismatch"):
        fetcher.fetch("123", token)


def test_fetch_exhausts_retries_and_raises():
    payload = {
        "delegatedUserId": 1,
        "loggedInUserId": 2,
        "sessionId": "S",
    }
    token = _make_token(payload)
    session = DummySession([
        DummyResponse(500, text="boom"),
        DummyResponse(500, text="boom"),
    ])
    session.cookies.set("JSESSIONID", "S")
    session.cookies.set("delegatedUserId", "1")
    session.cookies.set("loggedInUserId", "2")
    session.cookies.set("apiV3AccessToken", token)

    fetcher = V2InvoiceFetcher(session=session, base_url="https://example.com")

    with pytest.raises(V2InvoiceError):
        fetcher.fetch("123", token, retry_attempts=2, retry_backoff=0)
