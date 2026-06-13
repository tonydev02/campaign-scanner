import re
from dataclasses import dataclass
from datetime import date
from urllib.parse import (
    parse_qsl,
    urlencode,
    urljoin,
    urlsplit,
    urlunsplit,
)

from vpoint_scanner.schemas import CampaignStatus

_WHITESPACE = re.compile(r"\s+")
_RANGE_SEPARATOR = r"\s*[〜～~\-]\s*"
_SLASH_RANGE = re.compile(
    rf"^(?:(?P<start_year>\d{{4}})/)?"
    rf"(?P<start_month>\d{{1,2}})/(?P<start_day>\d{{1,2}})"
    rf"{_RANGE_SEPARATOR}"
    rf"(?:(?P<end_year>\d{{4}})/)?"
    rf"(?P<end_month>\d{{1,2}})/(?P<end_day>\d{{1,2}})$"
)
_JAPANESE_RANGE = re.compile(
    rf"^(?:(?P<start_year>\d{{4}})年)?"
    rf"(?P<start_month>\d{{1,2}})月(?P<start_day>\d{{1,2}})日?"
    rf"{_RANGE_SEPARATOR}"
    rf"(?:(?P<end_year>\d{{4}})年)?"
    rf"(?P<end_month>\d{{1,2}})月(?P<end_day>\d{{1,2}})日$"
)
_JAPANESE_UNTIL = re.compile(
    r"^(?P<end_year>\d{4})年"
    r"(?P<end_month>\d{1,2})月(?P<end_day>\d{1,2})日まで$"
)
_TRACKING_PARAMETERS = {"fbclid", "gclid"}
_SEMANTIC_FRAGMENT = re.compile(r"^/?(?:detail2?|campaign)/[^/?#]+")


@dataclass(frozen=True)
class ParsedPeriod:
    start_date: date | None
    end_date: date | None


def normalize_text(value: str) -> str:
    """Normalize identity whitespace without translating or changing case."""

    return _WHITESPACE.sub(" ", value.replace("\u3000", " ")).strip()


def canonicalize_url(url: str, base_url: str | None = None) -> str | None:
    """Return a stable HTTP(S) URL suitable for campaign identity."""

    normalized_input = normalize_text(url)
    if not normalized_input:
        return None

    absolute = urljoin(base_url, normalized_input) if base_url else normalized_input
    parts = urlsplit(absolute)
    scheme = parts.scheme.lower()
    if scheme not in {"http", "https"} or not parts.hostname:
        return None

    hostname = parts.hostname.lower()
    port = parts.port
    if port is not None and not (
        (scheme == "http" and port == 80) or (scheme == "https" and port == 443)
    ):
        hostname = f"{hostname}:{port}"

    path = parts.path or "/"
    if path != "/":
        path = path.rstrip("/")

    query_items = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if not key.lower().startswith("utm_")
        and key.lower() not in _TRACKING_PARAMETERS
    ]
    query = urlencode(sorted(query_items))
    fragment = parts.fragment if _SEMANTIC_FRAGMENT.match(parts.fragment) else ""
    return urlunsplit((scheme, hostname, path, query, fragment))


def parse_visible_period(
    visible_period_text: str | None,
    *,
    reference_date: date | None = None,
) -> ParsedPeriod:
    """Parse documented period formats, returning nulls when uncertain."""

    if visible_period_text is None:
        return ParsedPeriod(None, None)
    text = normalize_text(visible_period_text)
    if not text:
        return ParsedPeriod(None, None)

    until_match = _JAPANESE_UNTIL.fullmatch(text)
    if until_match:
        end_date = _safe_date(
            int(until_match["end_year"]),
            int(until_match["end_month"]),
            int(until_match["end_day"]),
        )
        return ParsedPeriod(None, end_date)

    match = _SLASH_RANGE.fullmatch(text) or _JAPANESE_RANGE.fullmatch(text)
    if not match:
        return ParsedPeriod(None, None)

    start_year_text = match["start_year"]
    end_year_text = match["end_year"]
    if start_year_text is None and end_year_text is None:
        if reference_date is None:
            return ParsedPeriod(None, None)
        start_year = reference_date.year
        end_year = reference_date.year
    elif start_year_text is not None and end_year_text is not None:
        start_year = int(start_year_text)
        end_year = int(end_year_text)
    else:
        return ParsedPeriod(None, None)

    start_month = int(match["start_month"])
    start_day = int(match["start_day"])
    end_month = int(match["end_month"])
    end_day = int(match["end_day"])
    if (
        start_year_text is None
        and end_year_text is None
        and (end_month, end_day) < (start_month, start_day)
    ):
        end_year += 1

    start_date = _safe_date(start_year, start_month, start_day)
    end_date = _safe_date(end_year, end_month, end_day)
    if start_date is None or end_date is None or end_date < start_date:
        return ParsedPeriod(None, None)
    return ParsedPeriod(start_date, end_date)


def campaign_identity(
    *,
    title: str,
    visible_period_text: str | None,
    campaign_url: str | None = None,
    base_url: str | None = None,
) -> str:
    """Build the URL-first identity used by later persistence."""

    canonical_url = (
        canonicalize_url(campaign_url, base_url) if campaign_url is not None else None
    )
    if canonical_url:
        return f"url:{canonical_url}"

    normalized_title = normalize_text(title)
    if not normalized_title:
        raise ValueError("campaign title is required for fallback identity")
    normalized_period = normalize_text(visible_period_text or "")
    return f"title_period:{normalized_title}|{normalized_period}"


def calculate_status(
    end_date: date | None,
    *,
    today: date,
    ending_within_days: int = 7,
) -> CampaignStatus:
    """Calculate date status using an inclusive ending-soon window."""

    if ending_within_days < 0:
        raise ValueError("ending_within_days must be non-negative")
    if end_date is None:
        return CampaignStatus.UNKNOWN

    days_remaining = (end_date - today).days
    if days_remaining < 0:
        return CampaignStatus.EXPIRED
    if days_remaining <= ending_within_days:
        return CampaignStatus.ENDING_SOON
    return CampaignStatus.ACTIVE


def _safe_date(year: int, month: int, day: int) -> date | None:
    try:
        return date(year, month, day)
    except ValueError:
        return None
