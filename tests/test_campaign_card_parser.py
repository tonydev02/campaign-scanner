from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from vpoint_scanner.parsers.campaign_card import (
    CampaignCardParseError,
    parse_campaign_cards,
)

FIXTURES = Path(__file__).parent / "fixtures"
SOURCE_URL = "https://cpn.tsite.jp/list/all"
SCRAPED_AT = datetime(2026, 6, 14, 6, tzinfo=UTC)


def test_parse_every_fixture_card_in_document_order() -> None:
    html = (FIXTURES / "vpoint_campaign_list.html").read_text(encoding="utf-8")

    campaigns = parse_campaign_cards(
        html,
        source_url=SOURCE_URL,
        scraped_at=SCRAPED_AT,
    )

    assert [campaign.title for campaign in campaigns] == [
        "はずれなし！毎日あたるくじ",
        "Vポイント祭 For VポイントPayアプリ",
    ]
    assert campaigns[0].campaign_url == "https://lot.tsite.jp/#/detail2/lt001"
    assert campaigns[1].campaign_url == "https://cpn.tsite.jp/detail/en002"
    assert campaigns[1].image_url == (
        "https://cpn.tsite.jp/resources/lot/content/en002/img/thumbnail.png"
    )
    assert campaigns[0].visible_period_text == "05/01~06/30"
    assert "詳細を見る" in (campaigns[0].raw_text or "")


def test_embedded_metadata_provides_dates_and_entry_flag() -> None:
    html = (FIXTURES / "vpoint_campaign_list.html").read_text(encoding="utf-8")

    campaigns = parse_campaign_cards(
        html,
        source_url=SOURCE_URL,
        scraped_at=SCRAPED_AT,
    )

    assert campaigns[0].start_date == date(2026, 5, 1)
    assert campaigns[0].end_date == date(2026, 6, 30)
    assert campaigns[0].requires_entry is None
    assert campaigns[1].requires_entry is True
    assert campaigns[1].entry_text == "エントリーが必要"


def test_malformed_metadata_retains_card_with_period_fallback() -> None:
    html = (FIXTURES / "vpoint_campaign_list_bad_metadata.html").read_text(
        encoding="utf-8"
    )

    campaigns = parse_campaign_cards(
        html,
        source_url=SOURCE_URL,
        scraped_at=SCRAPED_AT,
    )

    assert len(campaigns) == 1
    assert campaigns[0].start_date == date(2026, 6, 1)
    assert campaigns[0].end_date == date(2026, 6, 30)
    assert campaigns[0].requires_entry is None


def test_card_without_title_fails_loudly() -> None:
    with pytest.raises(CampaignCardParseError, match="card 1 has no title"):
        parse_campaign_cards(
            '<div class="list-item"><a class="t-button" href="/x">detail</a></div>',
            source_url=SOURCE_URL,
            scraped_at=SCRAPED_AT,
        )
