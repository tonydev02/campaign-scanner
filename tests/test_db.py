from datetime import UTC, datetime
from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from vpoint_scanner.db import (
    campaign_count,
    create_sqlite_engine,
    initialize_database,
    list_campaigns,
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
