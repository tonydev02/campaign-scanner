from datetime import UTC, datetime
from pathlib import Path

import pytest
from sqlalchemy import inspect, select, text
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateTable

from vpoint_scanner.db import (
    campaign_count,
    create_sqlite_engine,
    initialize_database,
    list_campaigns,
    open_existing_database,
    persist_campaigns,
)
from vpoint_scanner.models import CampaignRecord
from vpoint_scanner.schemas import Campaign


def make_campaign(
    *,
    title: str = "テストキャンペーン",
    url: str | None = "https://example.jp/campaign/1",
    period: str | None = "06/01~06/30",
    scraped_at: datetime = datetime(2026, 6, 14, tzinfo=UTC),
    raw_text: str | None = "最初の証拠",
) -> Campaign:
    return Campaign(
        source="https://cpn.tsite.jp/list/all",
        source_type="vpoint_public",
        title=title,
        campaign_url=url,
        visible_period_text=period,
        raw_text=raw_text,
        scraped_at=scraped_at,
    )


@pytest.fixture
def engine(tmp_path: Path):
    database_path = tmp_path / "nested" / "campaigns.sqlite3"
    engine = create_sqlite_engine(database_path)
    initialize_database(engine)
    assert database_path.exists()
    return engine


def test_url_repeat_preserves_first_seen_and_updates_latest_fields(engine) -> None:
    first_time = datetime(2026, 6, 1, tzinfo=UTC)
    second_time = datetime(2026, 6, 14, tzinfo=UTC)
    first = make_campaign(scraped_at=first_time)
    second = make_campaign(
        title="更新タイトル",
        url="https://EXAMPLE.jp/campaign/1/?utm_source=list",
        scraped_at=second_time,
        raw_text="最新の証拠",
    )

    assert persist_campaigns(engine, [first]).inserted == 1
    result = persist_campaigns(engine, [second])
    stored = list_campaigns(engine)

    assert result.updated == 1
    assert campaign_count(engine) == 1
    assert stored[0].title == "更新タイトル"
    assert stored[0].raw_text == "最新の証拠"
    assert stored[0].first_seen_at == first_time
    assert stored[0].last_seen_at == second_time


def test_fallback_repeat_and_url_upgrade_remain_one_row(engine) -> None:
    first = make_campaign(
        title=" キャンペーン　タイトル ",
        url=None,
        period="06/01~ 06/30",
    )
    repeated = make_campaign(
        title="キャンペーン タイトル",
        url=None,
        period=" 06/01~ 06/30 ",
    )
    upgraded = make_campaign(
        title="キャンペーン タイトル",
        url="https://example.jp/new-id",
        period="06/01~ 06/30",
    )

    persist_campaigns(engine, [first])
    persist_campaigns(engine, [repeated])
    persist_campaigns(engine, [upgraded])

    with Session(engine) as session:
        record = session.scalar(select(CampaignRecord))
        assert record is not None
        assert record.identity_key == "url:https://example.jp/new-id"
        assert record.canonical_url == "https://example.jp/new-id"
    assert campaign_count(engine) == 1


def test_different_urls_with_same_fallback_remain_distinct(engine) -> None:
    result = persist_campaigns(
        engine,
        [
            make_campaign(url="https://example.jp/one"),
            make_campaign(url="https://example.jp/two"),
        ],
    )

    assert result.inserted == 2
    assert campaign_count(engine) == 2


def test_missing_latest_evidence_does_not_erase_stored_evidence(engine) -> None:
    persist_campaigns(engine, [make_campaign(raw_text="保存する証拠")])
    persist_campaigns(engine, [make_campaign(raw_text=None)])

    assert list_campaigns(engine)[0].raw_text == "保存する証拠"


def test_legacy_rows_gain_review_facts_from_stored_evidence(engine) -> None:
    persist_campaigns(
        engine,
        [
            make_campaign(
                title="WINTICKET 最大10万ポイント抽選",
                url="https://example.jp/campaign",
            )
        ],
    )

    stored = list_campaigns(engine)[0]

    assert stored.max_reward_points == 100000
    assert stored.is_lottery is True
    assert stored.is_gambling_or_prediction is True
    assert stored.detail_scrape_status.value == "external_skipped"


def test_unobserved_campaigns_are_not_deleted(engine) -> None:
    persist_campaigns(
        engine,
        [
            make_campaign(url="https://example.jp/one"),
            make_campaign(url="https://example.jp/two"),
        ],
    )

    persist_campaigns(engine, [make_campaign(url="https://example.jp/one")])

    assert campaign_count(engine) == 2


def test_bulk_transaction_rolls_back_on_failure(engine, monkeypatch) -> None:
    from vpoint_scanner import db

    original = db._upsert_campaign
    call_count = 0

    def fail_second(session, campaign):
        nonlocal call_count
        call_count += 1
        if call_count == 2:
            raise RuntimeError("forced failure")
        return original(session, campaign)

    monkeypatch.setattr(db, "_upsert_campaign", fail_second)

    with pytest.raises(RuntimeError, match="forced failure"):
        persist_campaigns(
            engine,
            [
                make_campaign(url="https://example.jp/one"),
                make_campaign(url="https://example.jp/two"),
            ],
        )

    assert campaign_count(engine) == 0


def test_initialize_migrates_phase_06_database_without_losing_rows(
    tmp_path: Path,
) -> None:
    engine = create_sqlite_engine(tmp_path / "legacy.sqlite3")
    new_columns = {
        "detail_scrape_status",
        "requires_new_application",
        "is_lottery",
        "is_guaranteed",
        "is_financial_product",
        "is_gambling_or_prediction",
    }
    current_sql = str(CreateTable(CampaignRecord.__table__).compile(engine))
    legacy_sql = "\n".join(
        line
        for line in current_sql.splitlines()
        if not any(column in line for column in new_columns)
    )
    with engine.begin() as connection:
        connection.execute(text(legacy_sql))
        connection.execute(
            text(
                """
                INSERT INTO campaigns (
                    identity_key, canonical_url, fallback_key, source,
                    source_type, title, first_seen_at, last_seen_at,
                    scraped_at, status
                ) VALUES (
                    'fallback:legacy', NULL, 'fallback:legacy', 'manual',
                    'manual', '既存キャンペーン',
                    '2026-06-01T00:00:00+00:00',
                    '2026-06-14T00:00:00+00:00',
                    '2026-06-14T00:00:00+00:00', 'unknown'
                )
                """
            )
        )

    initialize_database(engine)

    columns = {column["name"] for column in inspect(engine).get_columns("campaigns")}
    stored = list_campaigns(engine)
    assert new_columns <= columns
    assert stored[0].title == "既存キャンペーン"
    assert stored[0].detail_scrape_status.value == "unsupported"


def test_open_existing_database_applies_additive_migrations(tmp_path: Path) -> None:
    database_path = tmp_path / "existing.sqlite3"
    engine = create_sqlite_engine(database_path)
    initialize_database(engine)
    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE campaigns RENAME TO campaigns_current"))
        current_sql = str(CreateTable(CampaignRecord.__table__).compile(engine))
        legacy_sql = "\n".join(
            line
            for line in current_sql.splitlines()
            if "detail_scrape_status" not in line
        )
        connection.execute(text(legacy_sql))
        connection.execute(text("DROP TABLE campaigns_current"))

    opened = open_existing_database(database_path)

    columns = {column["name"] for column in inspect(opened).get_columns("campaigns")}
    assert "detail_scrape_status" in columns
