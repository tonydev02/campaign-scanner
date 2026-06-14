import logging
import re
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page, sync_playwright

from vpoint_scanner.extract import inferred_detail_scrape_status
from vpoint_scanner.parsers.campaign_card import (
    CARD_SELECTOR,
    CampaignCardParseError,
    parse_campaign_cards,
    utc_now,
)
from vpoint_scanner.parsers.campaign_detail import (
    CampaignDetailParseError,
    enrich_campaign_from_detail,
)
from vpoint_scanner.schemas import Campaign, DetailScrapeStatus
from vpoint_scanner.sources.base import SourceError

DETAIL_SELECTOR = ".contents, .info"
_SAFE_FILENAME = re.compile(r"[^A-Za-z0-9_-]+")
logger = logging.getLogger("vpoint_scanner")


class DetailBlockedError(SourceError):
    """A detail response that requires stopping further traversal."""


@dataclass(frozen=True)
class CollectionResult:
    campaigns: list[Campaign]
    detail_enriched: int
    detail_skipped: int
    detail_failed: int
    screenshots_saved: int


def collect_vpoint_public(
    *,
    url: str,
    timeout_ms: int,
    screenshots: bool = False,
    screenshots_dir: Path | None = None,
    detail_delay_seconds: float = 1.5,
    now: Callable[[], datetime] = utc_now,
) -> CollectionResult:
    """Collect the approved list and sequential same-origin details."""

    if not 1.0 <= detail_delay_seconds <= 3.0:
        raise SourceError("detail delay must be between 1 and 3 seconds")
    scraped_at = now()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                context = browser.new_context()
                try:
                    page = context.new_page()
                    html = load_listing_html(page, url=url, timeout_ms=timeout_ms)
                    campaigns = campaigns_from_html(
                        html,
                        url=url,
                        scraped_at=scraped_at,
                    )
                    result = enrich_campaign_details(
                        page,
                        campaigns,
                        timeout_ms=timeout_ms,
                        screenshots=screenshots,
                        screenshots_dir=screenshots_dir,
                        delay_seconds=detail_delay_seconds,
                    )
                finally:
                    context.close()
            finally:
                browser.close()
    except PlaywrightError as exc:
        raise SourceError(f"V Point public page could not be loaded: {exc}") from exc
    return result


def campaigns_from_html(
    html: str,
    *,
    url: str,
    scraped_at: datetime,
) -> list[Campaign]:
    """Convert rendered listing HTML into campaigns with source-safe errors."""

    try:
        campaigns = parse_campaign_cards(
            html,
            source_url=url,
            scraped_at=scraped_at,
        )
    except CampaignCardParseError as exc:
        raise SourceError(f"V Point campaign card could not be parsed: {exc}") from exc
    if not campaigns:
        raise SourceError(
            "V Point public page loaded but no campaign cards were found; "
            "the page structure may have changed."
        )
    return campaigns


def enrich_campaign_details(
    page: Page | Any,
    campaigns: list[Campaign],
    *,
    timeout_ms: int,
    screenshots: bool,
    screenshots_dir: Path | None,
    delay_seconds: float,
    sleep: Callable[[float], None] = time.sleep,
) -> CollectionResult:
    """Visit eligible details one at a time without interacting with controls."""

    enriched_campaigns = [
        campaign.model_copy(
            update={"detail_scrape_status": inferred_detail_scrape_status(campaign)}
        )
        for campaign in campaigns
    ]
    detail_enriched = 0
    detail_failed = 0
    screenshots_saved = 0
    detail_skipped = sum(
        not is_eligible_detail_url(campaign.campaign_url) for campaign in campaigns
    )
    attempted = 0

    for index, campaign in enumerate(campaigns):
        if not is_eligible_detail_url(campaign.campaign_url):
            continue
        if attempted:
            sleep(delay_seconds)
        attempted += 1
        try:
            html = load_detail_html(
                page,
                url=campaign.campaign_url or "",
                timeout_ms=timeout_ms,
            )
            enriched = enrich_campaign_from_detail(campaign, html)
        except DetailBlockedError as exc:
            remaining = sum(
                is_eligible_detail_url(item.campaign_url) for item in campaigns[index:]
            )
            detail_failed += remaining
            for remaining_index in range(index, len(campaigns)):
                if is_eligible_detail_url(campaigns[remaining_index].campaign_url):
                    enriched_campaigns[remaining_index] = enriched_campaigns[
                        remaining_index
                    ].model_copy(
                        update={
                            "detail_scrape_status": DetailScrapeStatus.FAILED,
                        }
                    )
            logger.warning("%s Further detail traversal stopped.", exc)
            break
        except (SourceError, CampaignDetailParseError, PlaywrightError) as exc:
            detail_failed += 1
            enriched_campaigns[index] = enriched_campaigns[index].model_copy(
                update={"detail_scrape_status": DetailScrapeStatus.FAILED}
            )
            logger.warning("Detail enrichment failed for %s: %s", campaign.title, exc)
            continue

        if screenshots:
            try:
                screenshot_path = _save_screenshot(
                    page,
                    campaign,
                    screenshots_dir=screenshots_dir,
                )
                enriched = enriched.model_copy(
                    update={"screenshot_path": str(screenshot_path)}
                )
                screenshots_saved += 1
            except (OSError, PlaywrightError, SourceError) as exc:
                detail_failed += 1
                logger.warning("Screenshot failed for %s: %s", campaign.title, exc)

        enriched_campaigns[index] = enriched
        detail_enriched += 1

    return CollectionResult(
        campaigns=enriched_campaigns,
        detail_enriched=detail_enriched,
        detail_skipped=detail_skipped,
        detail_failed=detail_failed,
        screenshots_saved=screenshots_saved,
    )


def is_eligible_detail_url(url: str | None) -> bool:
    if not url:
        return False
    parts = urlsplit(url)
    return (
        parts.scheme.lower() == "https"
        and (parts.hostname or "").lower() == "cpn.tsite.jp"
        and parts.path.startswith("/detail/")
    )


def load_listing_html(page: Page | Any, *, url: str, timeout_ms: int) -> str:
    """Load one list page without following or clicking campaign controls."""

    response = page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
    status = response.status if response is not None else None
    if status in {401, 403, 429}:
        raise SourceError(f"V Point public page blocked access with HTTP {status}.")
    if status is not None and status >= 400:
        raise SourceError(f"V Point public page returned HTTP {status}.")
    page.wait_for_selector(CARD_SELECTOR, timeout=timeout_ms)
    return page.content()


def load_detail_html(page: Page | Any, *, url: str, timeout_ms: int) -> str:
    response = page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
    status = response.status if response is not None else None
    if status in {401, 403, 429}:
        raise DetailBlockedError(f"Detail page blocked access with HTTP {status}.")
    if status is not None and status >= 400:
        raise SourceError(f"Detail page returned HTTP {status}.")
    page.wait_for_selector(DETAIL_SELECTOR, timeout=timeout_ms)
    return page.content()


def _save_screenshot(
    page: Page | Any,
    campaign: Campaign,
    *,
    screenshots_dir: Path | None,
) -> Path:
    if screenshots_dir is None:
        raise SourceError("public screenshot directory is not configured")
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    detail_id = urlsplit(campaign.campaign_url or "").path.rsplit("/", 1)[-1]
    safe_id = _SAFE_FILENAME.sub("-", detail_id).strip("-") or "campaign"
    timestamp = campaign.scraped_at.strftime("%Y%m%dT%H%M%S%z")
    path = screenshots_dir / f"{safe_id}-{timestamp}.png"
    page.screenshot(path=str(path), full_page=True)
    return path
