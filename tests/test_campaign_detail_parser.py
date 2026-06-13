import hashlib
from datetime import UTC, datetime
from pathlib import Path

import pytest

from vpoint_scanner.parsers.campaign_detail import (
    CampaignDetailParseError,
    enrich_campaign_from_detail,
)
from vpoint_scanner.schemas import Campaign, RewardType

FIXTURE = Path(__file__).parent / "fixtures" / "vpoint_campaign_detail.html"


def card_campaign() -> Campaign:
    return Campaign(
        source="https://cpn.tsite.jp/list/all",
        source_type="vpoint_public",
        title="Vポイント祭",
        campaign_url="https://cpn.tsite.jp/detail/en001",
        raw_text="カードの証拠",
        scraped_at=datetime(2026, 6, 14, tzinfo=UTC),
    )


def test_detail_enrichment_preserves_evidence_and_extracts_explicit_facts() -> None:
    html = FIXTURE.read_text(encoding="utf-8")

    campaign = enrich_campaign_from_detail(
        card_campaign(),
        html,
        screenshot_path="/tmp/en001.png",
    )

    assert campaign.requires_entry is True
    assert "エントリー" in (campaign.entry_text or "")
    assert "最大50,000ポイント" in (campaign.reward_text or "")
    assert campaign.max_reward_points == 50000
    assert campaign.reward_type is RewardType.LOTTERY
    assert "VポイントPayアプリ" in (campaign.target_payment_text or "")
    assert "1,000円" in (campaign.minimum_spend_text or "")
    assert "返品・取消" in (campaign.exclusions_text or "")
    assert campaign.raw_text is not None
    assert "[CARD]\nカードの証拠" in campaign.raw_text
    assert "[DETAIL]" in campaign.raw_text
    assert campaign.raw_html_hash == hashlib.sha256(html.encode()).hexdigest()
    assert campaign.screenshot_path == "/tmp/en001.png"


def test_detail_without_supported_visible_content_fails() -> None:
    with pytest.raises(CampaignDetailParseError, match=r"no \.contents or \.info"):
        enrich_campaign_from_detail(card_campaign(), "<html><body></body></html>")


def test_reward_amount_is_not_mistaken_for_minimum_spend() -> None:
    html = """
    <div class="contents">
      <p class="warning-text">最大4,000円分クーポンをプレゼント</p>
    </div>
    """

    campaign = enrich_campaign_from_detail(card_campaign(), html)

    assert campaign.reward_type is RewardType.COUPON
    assert campaign.minimum_spend_text is None
