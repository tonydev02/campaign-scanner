from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from vpoint_scanner.schemas import Campaign, DetailScrapeStatus
from vpoint_scanner.sources.vpoint_public import (
    enrich_campaign_details,
    is_eligible_detail_url,
)

DETAIL_HTML = """
<div class="contents">
  <div class="entry-image"><img data-dynbtn></div>
  <p class="warning-text">1,000円以上利用でポイントが当たる。
  エントリーください。</p>
</div>
<div class="info"><div class="info-one">
  <p class="info-one__title">■ご注意事項</p>
  <p class="info-one__text">返品は対象外です。</p>
</div></div>
"""


@dataclass
class FakeResponse:
    status: int


class FakePage:
    def __init__(self, responses: dict[str, tuple[int, str]]):
        self.responses = responses
        self.current_html = ""
        self.actions: list[tuple[object, ...]] = []

    def goto(self, url: str, *, wait_until: str, timeout: int) -> FakeResponse:
        self.actions.append(("goto", url, wait_until, timeout))
        status, self.current_html = self.responses[url]
        return FakeResponse(status)

    def wait_for_selector(self, selector: str, *, timeout: int) -> None:
        self.actions.append(("wait_for_selector", selector, timeout))

    def content(self) -> str:
        self.actions.append(("content",))
        return self.current_html

    def screenshot(self, *, path: str, full_page: bool) -> None:
        self.actions.append(("screenshot", path, full_page))
        Path(path).write_bytes(b"public screenshot")


def make_campaign(title: str, url: str | None) -> Campaign:
    return Campaign(
        source="https://cpn.tsite.jp/list/all",
        source_type="vpoint_public",
        title=title,
        campaign_url=url,
        raw_text=f"{title} card",
        scraped_at=datetime(2026, 6, 14, 6, tzinfo=UTC),
    )


def test_detail_eligibility_is_same_origin_https_path_only() -> None:
    assert is_eligible_detail_url("https://cpn.tsite.jp/detail/en001")
    assert not is_eligible_detail_url("http://cpn.tsite.jp/detail/en001")
    assert not is_eligible_detail_url("https://other.jp/detail/en001")
    assert not is_eligible_detail_url("https://lot.tsite.jp/#/detail2/lt001")
    assert not is_eligible_detail_url(None)


def test_enrichment_visits_only_eligible_urls_with_delay_and_no_clicks() -> None:
    first_url = "https://cpn.tsite.jp/detail/en001"
    second_url = "https://cpn.tsite.jp/detail/en002"
    campaigns = [
        make_campaign("first", first_url),
        make_campaign("external", "https://example.jp/campaign"),
        make_campaign("lottery", "https://lot.tsite.jp/#/detail2/lt001"),
        make_campaign("second", second_url),
    ]
    page = FakePage(
        {
            first_url: (200, DETAIL_HTML),
            second_url: (200, DETAIL_HTML),
        }
    )
    delays: list[float] = []

    result = enrich_campaign_details(
        page,
        campaigns,
        timeout_ms=1000,
        screenshots=False,
        screenshots_dir=None,
        delay_seconds=1.5,
        sleep=delays.append,
    )

    assert result.detail_enriched == 2
    assert result.detail_skipped == 2
    assert result.detail_failed == 0
    assert delays == [1.5]
    assert [action[0] for action in page.actions].count("goto") == 2
    assert not {"click", "fill", "submit"} & {action[0] for action in page.actions}
    assert result.campaigns[1].raw_text == "external card"
    assert result.campaigns[0].raw_html_hash is not None
    assert result.campaigns[0].detail_scrape_status is DetailScrapeStatus.EXTRACTED
    assert (
        result.campaigns[1].detail_scrape_status is DetailScrapeStatus.EXTERNAL_SKIPPED
    )
    assert (
        result.campaigns[2].detail_scrape_status is DetailScrapeStatus.EXTERNAL_SKIPPED
    )


def test_normal_failure_continues_and_block_stops_remaining_details() -> None:
    failed_url = "https://cpn.tsite.jp/detail/fail"
    blocked_url = "https://cpn.tsite.jp/detail/blocked"
    unvisited_url = "https://cpn.tsite.jp/detail/unvisited"
    campaigns = [
        make_campaign("failed", failed_url),
        make_campaign("blocked", blocked_url),
        make_campaign("unvisited", unvisited_url),
    ]
    page = FakePage(
        {
            failed_url: (500, ""),
            blocked_url: (429, ""),
            unvisited_url: (200, DETAIL_HTML),
        }
    )

    result = enrich_campaign_details(
        page,
        campaigns,
        timeout_ms=1000,
        screenshots=False,
        screenshots_dir=None,
        delay_seconds=1.0,
        sleep=lambda _: None,
    )

    assert result.detail_enriched == 0
    assert result.detail_failed == 3
    assert [action[1] for action in page.actions if action[0] == "goto"] == [
        failed_url,
        blocked_url,
    ]
    assert [item.raw_text for item in result.campaigns] == [
        "failed card",
        "blocked card",
        "unvisited card",
    ]
    assert all(
        item.detail_scrape_status is DetailScrapeStatus.FAILED
        for item in result.campaigns
    )


def test_missing_and_same_origin_unsupported_urls_are_explained() -> None:
    result = enrich_campaign_details(
        FakePage({}),
        [
            make_campaign("missing", None),
            make_campaign("list", "https://cpn.tsite.jp/list/all"),
        ],
        timeout_ms=1000,
        screenshots=False,
        screenshots_dir=None,
        delay_seconds=1.0,
    )

    assert [item.detail_scrape_status for item in result.campaigns] == [
        DetailScrapeStatus.UNSUPPORTED,
        DetailScrapeStatus.UNSUPPORTED,
    ]


def test_screenshots_are_optional_and_public(tmp_path: Path) -> None:
    url = "https://cpn.tsite.jp/detail/en001"
    campaign = make_campaign("screenshot", url)
    page = FakePage({url: (200, DETAIL_HTML)})

    disabled = enrich_campaign_details(
        page,
        [campaign],
        timeout_ms=1000,
        screenshots=False,
        screenshots_dir=tmp_path,
        delay_seconds=1.0,
    )
    assert disabled.screenshots_saved == 0
    assert not list(tmp_path.iterdir())

    enabled = enrich_campaign_details(
        page,
        [campaign],
        timeout_ms=1000,
        screenshots=True,
        screenshots_dir=tmp_path,
        delay_seconds=1.0,
    )

    assert enabled.screenshots_saved == 1
    screenshot_path = Path(enabled.campaigns[0].screenshot_path or "")
    assert screenshot_path.parent == tmp_path
    assert screenshot_path.name.startswith("en001-")
    assert screenshot_path.read_bytes() == b"public screenshot"
