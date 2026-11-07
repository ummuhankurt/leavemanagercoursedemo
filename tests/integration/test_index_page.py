"""Spec 0001 AC-3…AC-6 — the served status page. The rendered states are proven by VERIFY's
screenshots (spec Constraints, G-4); these tests prove what the browser receives."""

from __future__ import annotations

from html.parser import HTMLParser

from fastapi.testclient import TestClient


class _PageParser(HTMLParser):
    """Collects the html lang, the live region's attributes and its initial text."""

    def __init__(self) -> None:
        super().__init__()
        self.lang: str | None = None
        self.scripts: list[dict[str, str | None]] = []
        self.live_region: dict[str, str | None] | None = None
        self.live_text = ""
        self._depth_in_region = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "html":
            self.lang = attributes.get("lang")
        if tag == "script":
            self.scripts.append(attributes)
        if self._depth_in_region:
            self._depth_in_region += 1
        elif attributes.get("aria-live") is not None:
            self.live_region = attributes
            self._depth_in_region = 1

    def handle_endtag(self, tag: str) -> None:
        if self._depth_in_region:
            self._depth_in_region -= 1

    def handle_data(self, data: str) -> None:
        if self._depth_in_region:
            self.live_text += data


def _parse_index(client: TestClient) -> _PageParser:
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    parser = _PageParser()
    parser.feed(response.text)
    return parser


def test_index_shows_loading_text_in_live_region(client: TestClient) -> None:
    page = _parse_index(client)

    assert page.live_region is not None
    assert page.live_text.strip() == "Sistem durumu kontrol ediliyor…"


def test_index_serves_page_and_script(client: TestClient) -> None:
    page = _parse_index(client)
    assert {"type": "module", "src": "/app.js"} in page.scripts

    script = client.get("/app.js")

    assert script.status_code == 200
    assert "javascript" in script.headers["content-type"]
    # The script asks the status query and carries the success and error texts (AC-4, AC-5).
    for expected in (
        "/api/v1/health",
        "Sistem çalışıyor",
        "Veritabanı: erişilebilir",
        "Sistem şu anda kullanılamıyor",
        "textContent",
    ):
        assert expected in script.text
    assert "innerHTML" not in script.text


def test_index_declares_lang_tr_and_live_region(client: TestClient) -> None:
    page = _parse_index(client)

    assert page.lang == "tr"
    assert page.live_region is not None
    assert page.live_region.get("role") == "status"
    assert page.live_region.get("aria-live") == "polite"
