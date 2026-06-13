from datetime import UTC, datetime
from types import SimpleNamespace

from typer.testing import CliRunner

from vpoint_scanner.cli import app
from vpoint_scanner.db import (
    PersistenceError,
    UpsertResult,
    campaign_count,
    create_sqlite_engine,
)
from vpoint_scanner.schemas import Campaign
from vpoint_scanner.sources import SourceError

runner = CliRunner()


def test_root_help_lists_commands() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "scrape" in result.stdout
    assert "export" in result.stdout
    assert "summary" in result.stdout


def test_scrape_help_lists_future_options() -> None:
    result = runner.invoke(app, ["scrape", "--help"])

    assert result.exit_code == 0
    assert "--source" in result.stdout
    assert "--screenshots" in result.stdout


def test_export_help_lists_future_options() -> None:
    result = runner.invoke(app, ["export", "--help"])

    assert result.exit_code == 0
    assert "--format" in result.stdout
    assert "--output" in result.stdout
    assert "--ending-within-days" in result.stdout


def test_export_and_summary_do_not_create_missing_database(
    monkeypatch,
    tmp_path,
) -> None:
    database_path = tmp_path / "missing.sqlite3"
    output_path = tmp_path / "campaigns.json"
    monkeypatch.setattr(
        "vpoint_scanner.cli.get_settings",
        lambda: SimpleNamespace(
            database_path=database_path,
            exports_dir=tmp_path / "exports",
        ),
    )

    export_result = runner.invoke(app, ["export", "--output", str(output_path)])
    summary_result = runner.invoke(app, ["summary"])

    assert export_result.exit_code == 1
    assert "Database does not exist" in export_result.output
    assert summary_result.exit_code == 1
    assert "Database does not exist" in summary_result.output
    assert not database_path.exists()
    assert not output_path.exists()


def test_scrape_reports_collected_and_persisted_campaigns(monkeypatch) -> None:
    campaign = Campaign(
        source="https://cpn.tsite.jp/list/all",
        source_type="vpoint_public",
        title="テストキャンペーン",
        scraped_at=datetime(2026, 6, 14, tzinfo=UTC),
    )
    monkeypatch.setattr(
        "vpoint_scanner.cli.collect_vpoint_public",
        lambda **_: [campaign],
    )
    monkeypatch.setattr("vpoint_scanner.cli.create_sqlite_engine", lambda _: object())
    monkeypatch.setattr("vpoint_scanner.cli.initialize_database", lambda _: None)
    monkeypatch.setattr(
        "vpoint_scanner.cli.persist_campaigns",
        lambda *_: UpsertResult(inserted=1, updated=0),
    )

    result = runner.invoke(app, ["scrape", "--source", "vpoint_public"])

    assert result.exit_code == 0
    assert "Collected 1 campaign cards" in result.stdout
    assert "Persisted 1 inserted and 0 updated" in result.stdout


def test_scrape_rejects_unsupported_source() -> None:
    result = runner.invoke(app, ["scrape", "--source", "unknown"])

    assert result.exit_code != 0
    assert "unsupported source" in result.output


def test_scrape_reports_source_failure_without_traceback(monkeypatch) -> None:
    def fail(**_: object) -> list[Campaign]:
        raise SourceError("blocked by source")

    monkeypatch.setattr("vpoint_scanner.cli.collect_vpoint_public", fail)

    result = runner.invoke(app, ["scrape"])

    assert result.exit_code == 1
    assert "Scrape failed: blocked by source" in result.output
    assert "Traceback" not in result.output


def test_scrape_explains_screenshot_phase(monkeypatch) -> None:
    monkeypatch.setattr(
        "vpoint_scanner.cli.collect_vpoint_public",
        lambda **_: [
            Campaign(
                source="https://cpn.tsite.jp/list/all",
                source_type="vpoint_public",
                title="テスト",
                scraped_at=datetime(2026, 6, 14, tzinfo=UTC),
            )
        ],
    )
    monkeypatch.setattr("vpoint_scanner.cli.create_sqlite_engine", lambda _: object())
    monkeypatch.setattr("vpoint_scanner.cli.initialize_database", lambda _: None)
    monkeypatch.setattr(
        "vpoint_scanner.cli.persist_campaigns",
        lambda *_: UpsertResult(inserted=1, updated=0),
    )

    result = runner.invoke(app, ["scrape", "--screenshots"])

    assert result.exit_code == 0
    assert "introduced in Phase 06" in result.output


def test_scrape_persists_without_duplicates_across_runs(monkeypatch, tmp_path) -> None:
    database_path = tmp_path / "campaigns.sqlite3"
    campaign = Campaign(
        source="https://cpn.tsite.jp/list/all",
        source_type="vpoint_public",
        title="保存テスト",
        campaign_url="https://example.jp/campaign/1",
        scraped_at=datetime(2026, 6, 14, tzinfo=UTC),
    )
    monkeypatch.setattr(
        "vpoint_scanner.cli.get_settings",
        lambda: SimpleNamespace(
            vpoint_public_url="https://cpn.tsite.jp/list/all",
            browser_timeout_ms=1000,
            database_path=database_path,
        ),
    )
    monkeypatch.setattr(
        "vpoint_scanner.cli.collect_vpoint_public",
        lambda **_: [campaign],
    )

    first = runner.invoke(app, ["scrape"])
    second = runner.invoke(app, ["scrape"])

    assert first.exit_code == second.exit_code == 0
    assert "1 inserted and 0 updated" in first.stdout
    assert "0 inserted and 1 updated" in second.stdout
    assert campaign_count(create_sqlite_engine(database_path)) == 1


def test_scrape_reports_persistence_failure(monkeypatch) -> None:
    monkeypatch.setattr(
        "vpoint_scanner.cli.collect_vpoint_public",
        lambda **_: [
            Campaign(
                source="source",
                source_type="vpoint_public",
                title="テスト",
                scraped_at=datetime(2026, 6, 14, tzinfo=UTC),
            )
        ],
    )

    def fail(_):
        raise PersistenceError("disk unavailable")

    monkeypatch.setattr("vpoint_scanner.cli.create_sqlite_engine", fail)

    result = runner.invoke(app, ["scrape"])

    assert result.exit_code == 1
    assert "Scrape failed: disk unavailable" in result.output


def test_negative_ending_window_is_rejected() -> None:
    result = runner.invoke(app, ["export", "--ending-within-days", "-1"])

    assert result.exit_code != 0
