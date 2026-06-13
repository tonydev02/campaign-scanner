import json
import os
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path

from vpoint_scanner.normalize import calculate_status, normalize_text
from vpoint_scanner.schemas import Campaign


class ExportError(RuntimeError):
    """A user-facing campaign export failure."""


def write_campaign_export(
    campaigns: list[Campaign],
    *,
    output_path: Path,
    today: date,
    exported_at: datetime,
    ending_within_days: int | None = None,
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
        "campaigns": [
            campaign.model_dump(mode="json")
            for campaign in _ordered_campaigns(selected)
        ],
    }
    _atomic_write_json(output_path, envelope)
    return envelope


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
