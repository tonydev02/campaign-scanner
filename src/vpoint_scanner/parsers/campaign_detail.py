import hashlib
import re
from dataclasses import dataclass

from selectolax.parser import HTMLParser

from vpoint_scanner.normalize import normalize_text
from vpoint_scanner.schemas import Campaign, RewardType

_MAX_POINTS = re.compile(r"最大\s*([\d,]+)\s*(?:ポイント|pt)", re.IGNORECASE)
_MONEY = re.compile(r"[\d,]+\s*円")


class CampaignDetailParseError(ValueError):
    """Raised when an approved detail page has no usable visible evidence."""


@dataclass(frozen=True)
class DetailSection:
    heading: str
    body: str


def enrich_campaign_from_detail(
    campaign: Campaign,
    html: str,
    *,
    screenshot_path: str | None = None,
) -> Campaign:
    """Add explicit visible detail facts while preserving card evidence."""

    tree = HTMLParser(html)
    detail_blocks = [
        _node_text(node)
        for selector in (".contents", ".info")
        for node in tree.css(selector)
    ]
    detail_blocks = [block for block in detail_blocks if block]
    if not detail_blocks:
        raise CampaignDetailParseError("detail page has no .contents or .info text")

    detail_text = "\n".join(detail_blocks)
    sections = _extract_sections(tree)
    warning = _first_text(tree, ".warning-text")
    entry_body = _section_text(sections, "エントリー")
    entry_text = f"エントリー: {entry_body}" if entry_body else None
    if entry_text is None:
        entry_text = _matching_line(detail_text, ("エントリー",))
    explicit_entry = bool(
        tree.css_first("[data-dynbtn]")
        and (
            entry_text
            or "エントリーください" in detail_text
            or "エントリーが必要" in detail_text
        )
    )

    reward_text = _section_text(sections, "条件と特典", "特典内容", "特典")
    if not reward_text and warning and _contains_reward_term(warning):
        reward_text = warning

    minimum_spend_text = _matching_line(
        detail_text,
        ("以上", "ごと", "につき", "購入", "利用"),
        required_pattern=_MONEY,
    )
    target_payment_text = _matching_line(
        detail_text,
        ("VポイントPayアプリ", "クレジットカード", "決済"),
    )
    target_store_text = _section_text(sections, "対象店舗", "対象店")
    exclusions_text = _section_text(sections, "ご注意事項", "注意事項", "対象外")
    reward_type = _reward_type(reward_text or detail_text)
    max_reward_points = _max_reward_points(reward_text or detail_text)

    card_text = campaign.raw_text or ""
    combined_text = (
        f"[CARD]\n{card_text}\n\n[DETAIL]\n{detail_text}"
        if card_text
        else f"[DETAIL]\n{detail_text}"
    )
    return campaign.model_copy(
        update={
            "description": warning or campaign.description,
            "requires_entry": True if explicit_entry else campaign.requires_entry,
            "entry_text": entry_text or campaign.entry_text,
            "reward_text": reward_text or campaign.reward_text,
            "max_reward_points": max_reward_points or campaign.max_reward_points,
            "reward_type": reward_type or campaign.reward_type,
            "target_payment_text": (
                target_payment_text or campaign.target_payment_text
            ),
            "target_store_text": target_store_text or campaign.target_store_text,
            "minimum_spend_text": (minimum_spend_text or campaign.minimum_spend_text),
            "exclusions_text": exclusions_text or campaign.exclusions_text,
            "raw_text": combined_text,
            "raw_html_hash": hashlib.sha256(html.encode("utf-8")).hexdigest(),
            "screenshot_path": screenshot_path or campaign.screenshot_path,
        }
    )


def _extract_sections(tree: HTMLParser) -> list[DetailSection]:
    sections: list[DetailSection] = []
    for node in tree.css(".info-one"):
        heading_node = node.css_first(".info-one__title")
        if heading_node is None:
            continue
        heading = _node_text(heading_node).lstrip("■").strip()
        full_text = _node_text(node)
        body = full_text.removeprefix(_node_text(heading_node)).strip()
        sections.append(DetailSection(heading=heading, body=body))
    return sections


def _section_text(sections: list[DetailSection], *headings: str) -> str | None:
    for section in sections:
        if any(heading in section.heading for heading in headings) and section.body:
            return section.body
    return None


def _matching_line(
    text: str,
    terms: tuple[str, ...],
    *,
    required_pattern: re.Pattern[str] | None = None,
) -> str | None:
    for line in _lines(text):
        if any(term in line for term in terms) and (
            required_pattern is None or required_pattern.search(line)
        ):
            return line
    return None


def _lines(text: str) -> list[str]:
    return [
        normalized
        for part in re.split(r"[\n。]+", text)
        if (normalized := normalize_text(part))
    ]


def _reward_type(text: str) -> RewardType | None:
    if any(term in text for term in ("抽選", "当たる", "当選")):
        return RewardType.LOTTERY
    if any(term in text for term in ("ポイント倍", "倍キャンペーン", "倍率")):
        return RewardType.MULTIPLIER
    if "クーポン" in text:
        return RewardType.COUPON
    if any(term in text for term in ("もれなく", "必ずもらえる")):
        return RewardType.GUARANTEED
    return None


def _max_reward_points(text: str) -> int | None:
    match = _MAX_POINTS.search(text)
    return int(match.group(1).replace(",", "")) if match else None


def _contains_reward_term(text: str) -> bool:
    return any(
        term in text
        for term in ("ポイント", "特典", "当たる", "もらえる", "キャッシュバック")
    )


def _first_text(tree: HTMLParser, selector: str) -> str | None:
    node = tree.css_first(selector)
    return _node_text(node) if node is not None else None


def _node_text(node) -> str:
    return "\n".join(
        line
        for raw_line in node.text(separator="\n", strip=True).splitlines()
        if (line := normalize_text(raw_line))
    )
