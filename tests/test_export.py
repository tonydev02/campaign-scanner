import json
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest
from typer.testing import CliRunner

from vpoint_scanner.cli import app
from vpoint_scanner.db import (
    create_sqlite_engine,
    initialize_database,
    persist_campaigns,
    summarize_campaigns,
)
from vpoint_scanner.export import ExportError, ExportProfile, write_campaign_export
from vpoint_scanner.schemas import Campaign, CampaignStatus

TODAY = date(2026, 6, 14)
EXPORTED_AT = datetime(2026, 6, 14, 6, tzinfo=UTC)
runner = CliRunner()


def campaign(
    *,
    title: str,
    end_date: date | None,
    source: str = "https://cpn.tsite.jp/list/all",
    campaign_id: int | None = None,
) -> Campaign:
    return Campaign(
        id=campaign_id,
        source=source,
        source_type="vpoint_public",
        title=title,
        end_date=end_date,
        raw_text="日本語の証拠",
        scraped_at=EXPORTED_AT,
        status=CampaignStatus.UNKNOWN,
    )


def sample_campaigns() -> list[Campaign]:
    return [
        campaign(title="期限不明", end_date=None, campaign_id=4),
        campaign(title="通常", end_date=TODAY + timedelta(days=8), campaign_id=3),
        campaign(title="本日期限", end_date=TODAY, campaign_id=2),
        campaign(title="期限切れ", end_date=TODAY - timedelta(days=1), campaign_id=1),
    ]


def test_default_export_shape_utf8_and_order(tmp_path: Path) -> None:
    output_path = tmp_path / "campaigns.json"

    envelope = write_campaign_export(
        sample_campaigns(),
        output_path=output_path,
        today=TODAY,
        exported_at=EXPORTED_AT,
    )
    text = output_path.read_text(encoding="utf-8")
    parsed = json.loads(text)

    assert envelope["campaign_count"] == 3
    assert parsed["exported_at"] == "2026-06-14T06:00:00+00:00"
    assert parsed["source_count"] == 1
    assert [item["title"] for item in parsed["campaigns"]] == [
        "本日期限",
        "通常",
        "期限不明",
    ]
    assert "end_date" not in parsed["campaigns"][-1]
    assert parsed["campaigns"][-1]["status"] == "unknown"
    assert parsed["profile"] == "compact"
    assert parsed["campaigns"][-1]["raw_text_preview"] == "日本語の証拠"
    assert parsed["campaigns"][-1]["raw_text_length"] == 6
    assert parsed["campaigns"][-1]["has_detail_text"] is False
    assert "日本語の証拠" in text
    assert "\\u65e5" not in text


def test_full_export_preserves_nulls_and_complete_raw_text(tmp_path: Path) -> None:
    item = campaign(title="完全版", end_date=None)
    item.raw_text = "証拠" * 1000

    envelope = write_campaign_export(
        [item],
        output_path=tmp_path / "campaigns_full.json",
        today=TODAY,
        exported_at=EXPORTED_AT,
        profile=ExportProfile.FULL,
    )
    exported = envelope["campaigns"][0]

    assert envelope["profile"] == "full"
    assert exported["end_date"] is None
    assert exported["raw_text"] == "証拠" * 1000
    assert "raw_text_preview" not in exported


def test_compact_export_bounds_preview_and_reports_detail_length(
    tmp_path: Path,
) -> None:
    item = campaign(title="詳細あり", end_date=TODAY)
    detail = "詳" * 900
    item.raw_text = f"[CARD]\nカード\n\n[DETAIL]\n{detail}"

    envelope = write_campaign_export(
        [item],
        output_path=tmp_path / "campaigns_compact.json",
        today=TODAY,
        exported_at=EXPORTED_AT,
    )
    exported = envelope["campaigns"][0]

    assert len(exported["raw_text_preview"]) == 803
    assert exported["raw_text_preview"].endswith("...")
    assert exported["has_detail_text"] is True
    assert exported["detail_text_length"] == 900


@pytest.mark.parametrize(
    ("days", "expected_titles"),
    [
        (0, ["本日期限"]),
        (7, ["本日期限"]),
        (8, ["本日期限", "通常"]),
    ],
)
def test_ending_window_is_inclusive(
    tmp_path: Path,
    days: int,
    expected_titles: list[str],
) -> None:
    envelope = write_campaign_export(
        sample_campaigns(),
        output_path=tmp_path / f"ending-{days}.json",
        today=TODAY,
        exported_at=EXPORTED_AT,
        ending_within_days=days,
    )

    assert [item["title"] for item in envelope["campaigns"]] == expected_titles


def test_atomic_failure_preserves_existing_output(tmp_path: Path, monkeypatch) -> None:
    output_path = tmp_path / "campaigns.json"
    output_path.write_text('{"old": true}\n', encoding="utf-8")

    def fail_replace(source: Path, destination: Path) -> None:
        del source, destination
        raise OSError("forced replacement failure")

    monkeypatch.setattr("vpoint_scanner.export.os.replace", fail_replace)

    with pytest.raises(ExportError, match="forced replacement failure"):
        write_campaign_export(
            sample_campaigns(),
            output_path=output_path,
            today=TODAY,
            exported_at=EXPORTED_AT,
        )

    assert output_path.read_text(encoding="utf-8") == '{"old": true}\n'
    assert list(tmp_path.glob("*.tmp")) == []


def test_summary_recalculates_current_status(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "campaigns.sqlite3")
    initialize_database(engine)
    persist_campaigns(engine, sample_campaigns())

    result = summarize_campaigns(engine, today=TODAY)

    assert result.total == 4
    assert result.source_count == 1
    assert result.active == 1
    assert result.ending_soon == 1
    assert result.expired == 1
    assert result.unknown == 1


def test_export_and_summary_cli_with_seeded_database(
    tmp_path: Path,
    monkeypatch,
) -> None:
    database_path = tmp_path / "campaigns.sqlite3"
    exports_dir = tmp_path / "exports"
    engine = create_sqlite_engine(database_path)
    initialize_database(engine)
    today = datetime.now().astimezone().date()
    persist_campaigns(
        engine,
        [
            campaign(title="有効", end_date=today + timedelta(days=10)),
            campaign(title="不明", end_date=None),
        ],
    )
    monkeypatch.setattr(
        "vpoint_scanner.cli.get_settings",
        lambda: SimpleNamespace(
            database_path=database_path,
            exports_dir=exports_dir,
        ),
    )

    export_result = runner.invoke(app, ["export"])
    summary_result = runner.invoke(app, ["summary"])

    assert export_result.exit_code == 0
    assert "Exported 2 campaigns" in export_result.stdout
    assert (exports_dir / "campaigns_compact.json").is_file()
    full_result = runner.invoke(app, ["export", "--profile", "full"])
    assert full_result.exit_code == 0
    assert (exports_dir / "campaigns_full.json").is_file()
    assert summary_result.exit_code == 0
    assert "Campaigns: 2" in summary_result.stdout
    assert "Active: 1" in summary_result.stdout
    assert "Unknown: 1" in summary_result.stdout
