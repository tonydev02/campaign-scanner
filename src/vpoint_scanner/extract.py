import re
from urllib.parse import urlsplit

from vpoint_scanner.schemas import (
    Campaign,
    DetailScrapeStatus,
    RewardType,
)

_MAX_POINTS = re.compile(
    r"最大\s*([\d,]+(?:\.\d+)?)\s*(万)?\s*(?:ポイント|pt)",
    re.IGNORECASE,
)
_LOTTERY_TERMS = ("抽選", "当たる", "当選", "くじ", "ハズレなし", "はずれなし")
_GUARANTEED_TERMS = ("必ずもらえる", "必ず進呈", "もれなく", "全員にもらえる")
_MULTIPLIER = re.compile(r"(?:\d+(?:\.\d+)?\s*倍|倍率アップ|ポイント倍)")
_NEW_APPLICATION_TERMS = (
    "新規入会",
    "新規申込",
    "新規申し込み",
    "新規お申し込み",
    "カード発行",
)
_FINANCIAL_TERMS = (
    "クレジットカード",
    "カード入会",
    "Olive",
    "リボ",
    "キャッシング",
    "カードローン",
)
_GAMBLING_TERMS = (
    "WINTICKET",
    "競輪",
    "競馬",
    "競艇",
    "ボートレース",
    "オートレース",
    "スポーツくじ",
    "投票",
)


def enrich_campaign_from_visible_text(campaign: Campaign) -> Campaign:
    """Derive only facts explicitly signaled by visible card text."""

    text = "\n".join(part for part in (campaign.title, campaign.raw_text) if part)
    lottery = _contains_any(text, _LOTTERY_TERMS)
    guaranteed = _contains_any(text, _GUARANTEED_TERMS)
    reward_type = campaign.reward_type
    if reward_type is None:
        if lottery:
            reward_type = RewardType.LOTTERY
        elif guaranteed:
            reward_type = RewardType.GUARANTEED
        elif _MULTIPLIER.search(text):
            reward_type = RewardType.MULTIPLIER
        elif "クーポン" in text:
            reward_type = RewardType.COUPON

    points_match = _MAX_POINTS.search(text)
    max_reward_points = campaign.max_reward_points or _points_from_match(points_match)
    reward_text = campaign.reward_text
    if reward_text is None and points_match is not None:
        reward_text = points_match.group(0)

    return campaign.model_copy(
        update={
            "reward_text": reward_text,
            "max_reward_points": max_reward_points,
            "reward_type": reward_type,
            "requires_new_application": _true_or_existing(
                _contains_any(text, _NEW_APPLICATION_TERMS),
                campaign.requires_new_application,
            ),
            "is_lottery": _true_or_existing(lottery, campaign.is_lottery),
            "is_guaranteed": _true_or_existing(
                guaranteed,
                campaign.is_guaranteed,
            ),
            "is_financial_product": _true_or_existing(
                _contains_any(text, _FINANCIAL_TERMS),
                campaign.is_financial_product,
            ),
            "is_gambling_or_prediction": _true_or_existing(
                _contains_any(text, _GAMBLING_TERMS),
                campaign.is_gambling_or_prediction,
            ),
        }
    )


def inferred_detail_scrape_status(campaign: Campaign) -> DetailScrapeStatus:
    """Explain legacy detail evidence without claiming an unrecorded attempt."""

    if "[DETAIL]\n" in (campaign.raw_text or ""):
        return DetailScrapeStatus.EXTRACTED
    url = campaign.campaign_url
    if not url:
        return DetailScrapeStatus.UNSUPPORTED
    parts = urlsplit(url)
    if (
        parts.scheme.lower() == "https"
        and (parts.hostname or "").lower() == "cpn.tsite.jp"
        and parts.path.startswith("/detail/")
    ):
        return DetailScrapeStatus.NOT_ATTEMPTED
    if (parts.hostname or "").lower() != "cpn.tsite.jp":
        return DetailScrapeStatus.EXTERNAL_SKIPPED
    return DetailScrapeStatus.UNSUPPORTED


def _max_reward_points(text: str) -> int | None:
    return _points_from_match(_MAX_POINTS.search(text))


def _points_from_match(match: re.Match[str] | None) -> int | None:
    if match is None:
        return None
    value = float(match.group(1).replace(",", ""))
    if match.group(2):
        value *= 10_000
    return int(value)


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    folded = text.casefold()
    return any(term.casefold() in folded for term in terms)


def _true_or_existing(found: bool, existing: bool | None) -> bool | None:
    return True if found else existing
