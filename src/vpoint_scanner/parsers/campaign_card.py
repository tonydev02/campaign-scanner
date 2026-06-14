import json
import re
from datetime import UTC, date, datetime
from typing import Any
from urllib.parse import urljoin, urlsplit

from selectolax.parser import HTMLParser, Node

from vpoint_scanner.extract import enrich_campaign_from_visible_text
from vpoint_scanner.normalize import (
    calculate_status,
    normalize_text,
    parse_visible_period,
)
from vpoint_scanner.schemas import Campaign, SourceType

CARD_SELECTOR = ".list-item"
_CAMPAIGN_ID = re.compile(r"(?:^|/)(?:detail2?|content)/([^/?#]+)")


class CampaignCardParseError(ValueError):
    """Raised when rendered card evidence cannot be represented safely."""


def parse_campaign_cards(
    html: str,
    *,
    source_url: str,
    scraped_at: datetime,
) -> list[Campaign]:
    """Parse all rendered V Point list cards in document order."""

    tree = HTMLParser(html)
    metadata = _parse_next_metadata(tree)
    campaigns: list[Campaign] = []

    for index, card in enumerate(tree.css(CARD_SELECTOR), start=1):
        campaigns.append(
            _parse_card(
                card,
                index=index,
                source_url=source_url,
                scraped_at=scraped_at,
                metadata=metadata,
            )
        )
    return campaigns


def _parse_card(
    card: Node,
    *,
    index: int,
    source_url: str,
    scraped_at: datetime,
    metadata: dict[str, dict[str, Any]],
) -> Campaign:
    title_node = card.css_first(".list-item__contents__text")
    title = normalize_text(title_node.text()) if title_node else ""
    if not title:
        raise CampaignCardParseError(f"campaign card {index} has no title")

    period_node = card.css_first(".list-item__contents__date")
    visible_period = normalize_text(period_node.text()) if period_node else None
    link_node = card.css_first(".t-button[href]") or card.css_first(
        ".list-item__img a[href]"
    )
    image_node = card.css_first(".list-item__img img[src]")
    campaign_url = _resolve_attribute(link_node, "href", source_url)
    image_url = _resolve_attribute(image_node, "src", source_url)
    campaign_id = _extract_campaign_id(campaign_url, image_url)
    campaign_metadata = metadata.get(campaign_id or "", {})

    start_date = _metadata_date(campaign_metadata.get("start_date"))
    end_date = _metadata_date(campaign_metadata.get("end_date"))
    if start_date is None and end_date is None:
        parsed_period = parse_visible_period(
            visible_period,
            reference_date=scraped_at.date(),
        )
        start_date = parsed_period.start_date
        end_date = parsed_period.end_date

    requires_entry = True if str(campaign_metadata.get("entry_type")) == "1" else None
    raw_text = normalize_text(card.text(separator=" ", strip=True))
    campaign = Campaign(
        source=source_url,
        source_type=SourceType.VPOINT_PUBLIC,
        title=title,
        campaign_url=campaign_url,
        image_url=image_url,
        visible_period_text=visible_period,
        start_date=start_date,
        end_date=end_date,
        description=title,
        requires_entry=requires_entry,
        entry_text="エントリーが必要" if requires_entry else None,
        raw_text=raw_text,
        scraped_at=scraped_at,
        status=calculate_status(end_date, today=scraped_at.date()),
    )
    return enrich_campaign_from_visible_text(campaign)


def _parse_next_metadata(tree: HTMLParser) -> dict[str, dict[str, Any]]:
    node = tree.css_first("#__NEXT_DATA__")
    if node is None:
        return {}
    try:
        payload = json.loads(node.text())
        campaigns = payload["props"]["pageProps"]["data"]["campaigns"]
    except (json.JSONDecodeError, KeyError, TypeError):
        return {}
    if not isinstance(campaigns, list):
        return {}
    return {
        str(item["id"]): item
        for item in campaigns
        if isinstance(item, dict) and item.get("id")
    }


def _resolve_attribute(node: Node | None, name: str, base_url: str) -> str | None:
    if node is None:
        return None
    value = node.attributes.get(name)
    return urljoin(base_url, value) if value else None


def _extract_campaign_id(
    campaign_url: str | None,
    image_url: str | None,
) -> str | None:
    for candidate in (campaign_url, image_url):
        if not candidate:
            continue
        parts = urlsplit(candidate)
        for value in (parts.path, parts.fragment):
            match = _CAMPAIGN_ID.search(value)
            if match:
                return match.group(1)
    return None


def _metadata_date(value: object) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def utc_now() -> datetime:
    """Provide an injectable timezone-aware scrape timestamp."""

    return datetime.now(UTC)
