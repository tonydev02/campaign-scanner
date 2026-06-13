from collections.abc import Callable
from datetime import datetime
from typing import Any

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page, sync_playwright

from vpoint_scanner.parsers.campaign_card import (
    CARD_SELECTOR,
    CampaignCardParseError,
    parse_campaign_cards,
    utc_now,
)
from vpoint_scanner.schemas import Campaign
from vpoint_scanner.sources.base import SourceError


def collect_vpoint_public(
    *,
    url: str,
    timeout_ms: int,
    now: Callable[[], datetime] = utc_now,
) -> list[Campaign]:
    """Collect the approved public listing with one browser page."""

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                context = browser.new_context()
                try:
                    page = context.new_page()
                    html = load_listing_html(page, url=url, timeout_ms=timeout_ms)
                finally:
                    context.close()
            finally:
                browser.close()
    except PlaywrightError as exc:
        raise SourceError(f"V Point public page could not be loaded: {exc}") from exc

    return campaigns_from_html(html, url=url, scraped_at=now())


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
