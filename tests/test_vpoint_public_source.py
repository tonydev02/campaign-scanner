from dataclasses import dataclass
from datetime import UTC, datetime

import pytest

from vpoint_scanner.sources.base import SourceError
from vpoint_scanner.sources.vpoint_public import campaigns_from_html, load_listing_html


@dataclass
class FakeResponse:
    status: int


class FakePage:
    def __init__(self, *, status: int = 200, html: str = "<html>cards</html>"):
        self.response = FakeResponse(status)
        self.html = html
        self.actions: list[tuple[object, ...]] = []

    def goto(self, url: str, *, wait_until: str, timeout: int) -> FakeResponse:
        self.actions.append(("goto", url, wait_until, timeout))
        return self.response

    def wait_for_selector(self, selector: str, *, timeout: int) -> None:
        self.actions.append(("wait_for_selector", selector, timeout))

    def content(self) -> str:
        self.actions.append(("content",))
        return self.html


def test_listing_loader_uses_one_navigation_and_no_clicks() -> None:
    page = FakePage()

    html = load_listing_html(
        page,
        url="https://cpn.tsite.jp/list/all",
        timeout_ms=1234,
    )

    assert html == "<html>cards</html>"
    assert page.actions == [
        ("goto", "https://cpn.tsite.jp/list/all", "domcontentloaded", 1234),
        ("wait_for_selector", ".list-item", 1234),
        ("content",),
    ]


@pytest.mark.parametrize("status", [401, 403, 429])
def test_listing_loader_reports_blocked_status(status: int) -> None:
    with pytest.raises(SourceError, match=f"blocked access with HTTP {status}"):
        load_listing_html(
            FakePage(status=status),
            url="https://cpn.tsite.jp/list/all",
            timeout_ms=1234,
        )


def test_listing_loader_reports_other_http_errors() -> None:
    with pytest.raises(SourceError, match="returned HTTP 500"):
        load_listing_html(
            FakePage(status=500),
            url="https://cpn.tsite.jp/list/all",
            timeout_ms=1234,
        )


def test_empty_listing_reports_structure_change() -> None:
    with pytest.raises(SourceError, match="no campaign cards were found"):
        campaigns_from_html(
            "<html></html>",
            url="https://cpn.tsite.jp/list/all",
            scraped_at=datetime(2026, 6, 14, tzinfo=UTC),
        )


def test_malformed_card_is_reported_as_source_error() -> None:
    with pytest.raises(SourceError, match="card 1 has no title"):
        campaigns_from_html(
            '<div class="list-item"></div>',
            url="https://cpn.tsite.jp/list/all",
            scraped_at=datetime(2026, 6, 14, tzinfo=UTC),
        )
