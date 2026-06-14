import json
import os
import tempfile
from datetime import date, datetime, timedelta
from enum import StrEnum
from pathlib import Path

from vpoint_scanner.normalize import calculate_status, normalize_text
from vpoint_scanner.schemas import Campaign


class ExportError(RuntimeError):
    """A user-facing campaign export failure."""


class ExportProfile(StrEnum):
    COMPACT = "compact"
    FULL = "full"


def write_campaign_export(
    campaigns: list[Campaign],
    *,
    output_path: Path,
    today: date,
    exported_at: datetime,
    ending_within_days: int | None = None,
    profile: ExportProfile = ExportProfile.COMPACT,
) -> dict[str, object]:
    """Filter, serialize, and atomically write a campaign export."""

    if exported_at.tzinfo is None or exported_at.utcoffset() is None:
        raise ExportError("exported_at must include timezone information")
    selected = _select_campaigns(
        campaigns,
        today=today,
        ending_within_days=ending_within_days,
    )
    envelope: dict[str, object] = {
        "exported_at": exported_at.isoformat(),
        "source_count": len({campaign.source for campaign in selected}),
        "campaign_count": len(selected),
        "profile": profile.value,
        "campaigns": [
            _serialize_campaign(campaign, profile=profile)
            for campaign in _ordered_campaigns(selected)
        ],
    }
    _atomic_write_json(output_path, envelope)
    return envelope


def _serialize_campaign(
    campaign: Campaign,
    *,
    profile: ExportProfile,
) -> dict[str, object]:
    if profile is ExportProfile.FULL:
        return campaign.model_dump(mode="json")

    raw_text = campaign.raw_text or ""
    detail_text = _detail_text(raw_text)
    values: dict[str, object | None] = {
        "id": campaign.id,
        "source": campaign.source_type.value,
        "title": campaign.title,
        "url": campaign.campaign_url,
        "image_url": campaign.image_url,
        "period": _period(campaign),
        "visible_period_text": campaign.visible_period_text,
        "start_date": campaign.start_date.isoformat() if campaign.start_date else None,
        "end_date": campaign.end_date.isoformat() if campaign.end_date else None,
        "status": campaign.status.value,
        "description": campaign.description,
        "category": campaign.category,
        "requires_entry": campaign.requires_entry,
        "entry_text": campaign.entry_text,
        "reward_text": campaign.reward_text,
        "max_reward_points": campaign.max_reward_points,
        "reward_type": (
            campaign.reward_type.value if campaign.reward_type is not None else None
        ),
        "requires_new_application": campaign.requires_new_application,
        "is_lottery": campaign.is_lottery,
        "is_guaranteed": campaign.is_guaranteed,
        "is_financial_product": campaign.is_financial_product,
        "is_gambling_or_prediction": campaign.is_gambling_or_prediction,
        "target_payment_text": campaign.target_payment_text,
        "target_store_text": campaign.target_store_text,
        "minimum_spend_text": campaign.minimum_spend_text,
        "exclusions_text": campaign.exclusions_text,
        "detail_scrape_status": campaign.detail_scrape_status.value,
        "raw_text_preview": _preview(raw_text) if raw_text else None,
        "raw_text_length": len(raw_text) if raw_text else None,
        "has_detail_text": bool(detail_text),
        "detail_text_length": len(detail_text) if detail_text else None,
    }
    return {key: value for key, value in values.items() if value is not None}


def _period(campaign: Campaign) -> str | None:
    if campaign.start_date and campaign.end_date:
        return f"{campaign.start_date.isoformat()} to {campaign.end_date.isoformat()}"
    if campaign.end_date:
        return f"through {campaign.end_date.isoformat()}"
    return campaign.visible_period_text


def _detail_text(raw_text: str) -> str:
    marker = "[DETAIL]\n"
    return raw_text.split(marker, 1)[1] if marker in raw_text else ""


def _preview(text: str, *, limit: int = 800) -> str:
    if len(text) <= limit:
        return text
    return f"{text[:limit].rstrip()}..."


def _select_campaigns(
    campaigns: list[Campaign],
    *,
    today: date,
    ending_within_days: int | None,
) -> list[Campaign]:
    if ending_within_days is not None and ending_within_days < 0:
        raise ExportError("ending_within_days must be non-negative")

    selected: list[Campaign] = []
    window_end = (
        today + timedelta(days=ending_within_days)
        if ending_within_days is not None
        else None
    )
    for campaign in campaigns:
        if window_end is None:
            if campaign.end_date is not None and campaign.end_date < today:
                continue
        elif (
            campaign.end_date is None
            or campaign.end_date < today
            or campaign.end_date > window_end
        ):
            continue
        selected.append(
            campaign.model_copy(
                update={
                    "status": calculate_status(campaign.end_date, today=today),
                }
            )
        )
    return selected


def _ordered_campaigns(campaigns: list[Campaign]) -> list[Campaign]:
    return sorted(
        campaigns,
        key=lambda campaign: (
            campaign.end_date is None,
            campaign.end_date or date.max,
            normalize_text(campaign.title),
            campaign.id or 0,
        ),
    )


def _atomic_write_json(output_path: Path, payload: dict[str, object]) -> None:
    temporary_path: Path | None = None
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=output_path.parent,
            prefix=f".{output_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            json.dump(payload, temporary, ensure_ascii=False, indent=2)
            temporary.write("\n")
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_path, output_path)
    except (OSError, TypeError, ValueError) as exc:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise ExportError(f"Could not write JSON export {output_path}: {exc}") from exc
