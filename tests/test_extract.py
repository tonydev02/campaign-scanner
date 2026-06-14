from datetime import UTC, datetime

import pytest

from vpoint_scanner.extract import enrich_campaign_from_visible_text
from vpoint_scanner.schemas import Campaign, RewardType


def campaign(title: str) -> Campaign:
    return Campaign(
        source="https://cpn.tsite.jp/list/all",
        source_type="vpoint_public",
        title=title,
        raw_text=title,
        scraped_at=datetime(2026, 6, 14, tzinfo=UTC),
    )


@pytest.mark.parametrize(
    ("title", "points"),
    [
        ("最大10万ポイント当たる", 100000),
        ("最大10,000ポイント", 10000),
        ("最大50pt", 50),
    ],
)
def test_extracts_explicit_maximum_points(title: str, points: int) -> None:
    result = enrich_campaign_from_visible_text(campaign(title))

    assert result.max_reward_points == points
    assert result.reward_text is not None


def test_extracts_conservative_review_flags() -> None:
    result = enrich_campaign_from_visible_text(
        campaign("WINTICKET 新規申込で最大10万ポイント抽選")
    )

    assert result.reward_type is RewardType.LOTTERY
    assert result.is_lottery is True
    assert result.requires_new_application is True
    assert result.is_gambling_or_prediction is True


def test_extracts_multiplier_guarantee_and_financial_product() -> None:
    multiplier = enrich_campaign_from_visible_text(campaign("ポイント3倍"))
    guaranteed = enrich_campaign_from_visible_text(campaign("もれなく500ポイント"))
    financial = enrich_campaign_from_visible_text(
        campaign("Oliveクレジットカード新規入会")
    )

    assert multiplier.reward_type is RewardType.MULTIPLIER
    assert guaranteed.reward_type is RewardType.GUARANTEED
    assert guaranteed.is_guaranteed is True
    assert financial.is_financial_product is True
    assert financial.requires_new_application is True


def test_absent_signals_remain_unknown() -> None:
    result = enrich_campaign_from_visible_text(campaign("通常のお知らせ"))

    assert result.reward_type is None
    assert result.is_lottery is None
    assert result.requires_new_application is None
