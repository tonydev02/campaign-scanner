from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from vpoint_scanner.schemas import (
    Campaign,
    CampaignStatus,
    RewardType,
    SourceType,
)


def test_complete_campaign_preserves_japanese_source_text() -> None:
    campaign = Campaign(
        id=7,
        source="Vポイント",
        source_type=SourceType.VPOINT_PUBLIC,
        title="  はずれなし！毎日あたるくじ  ",
        campaign_url="https://example.jp/campaign/7",
        image_url="https://example.jp/images/7.png",
        visible_period_text="05/01〜06/30",
        description="説明",
        category="おすすめ",
        requires_entry=True,
        entry_text="エントリーが必要",
        reward_text="最大10,000pt",
        max_reward_points=10000,
        reward_type=RewardType.LOTTERY,
        target_payment_text="VポイントPayアプリ",
        target_store_text="対象店舗",
        minimum_spend_text="3,000円ごと",
        exclusions_text="取消・返品は対象外",
        raw_text="  元の日本語テキスト\n",
        raw_html_hash="abc123",
        screenshot_path="data/screenshots/7.png",
        first_seen_at=datetime(2026, 6, 1, tzinfo=UTC),
        last_seen_at=datetime(2026, 6, 14, tzinfo=UTC),
        scraped_at=datetime(2026, 6, 14, tzinfo=UTC),
        status=CampaignStatus.ACTIVE,
    )

    assert campaign.title == "  はずれなし！毎日あたるくじ  "
    assert campaign.raw_text == "  元の日本語テキスト\n"
    assert campaign.model_dump(mode="json")["source_type"] == "vpoint_public"


def test_sparse_campaign_is_valid() -> None:
    campaign = Campaign(
        source="manual",
        source_type="manual",
        title="確認待ち",
        scraped_at=datetime(2026, 6, 14, tzinfo=UTC),
    )

    assert campaign.campaign_url is None
    assert campaign.status is CampaignStatus.UNKNOWN


@pytest.mark.parametrize(
    "overrides",
    [
        {"source_type": "unsupported"},
        {"scraped_at": datetime(2026, 6, 14)},
        {"title": " \t "},
        {"source": ""},
    ],
)
def test_campaign_rejects_invalid_core_fields(overrides: dict[str, object]) -> None:
    values = {
        "source": "Vポイント",
        "source_type": "vpoint_public",
        "title": "キャンペーン",
        "scraped_at": datetime(2026, 6, 14, tzinfo=UTC),
    }
    values.update(overrides)

    with pytest.raises(ValidationError):
        Campaign(**values)
