from datetime import date

import pytest

from vpoint_scanner.normalize import (
    calculate_status,
    campaign_identity,
    canonicalize_url,
    normalize_text,
    parse_visible_period,
)
from vpoint_scanner.schemas import CampaignStatus


def test_normalize_text_preserves_japanese_characters() -> None:
    assert normalize_text("  はずれなし！　毎日\tあたる  くじ\n") == (
        "はずれなし！ 毎日 あたる くじ"
    )


@pytest.mark.parametrize(
    ("text", "reference_date", "expected_start", "expected_end"),
    [
        ("05/01〜06/30", date(2026, 6, 14), date(2026, 5, 1), date(2026, 6, 30)),
        (
            "2026/04/22〜2026/06/30",
            None,
            date(2026, 4, 22),
            date(2026, 6, 30),
        ),
        ("6月1日〜6月30日", date(2026, 1, 1), date(2026, 6, 1), date(2026, 6, 30)),
        ("2026年6月30日まで", None, None, date(2026, 6, 30)),
        (
            "12/15〜01/10",
            date(2026, 12, 1),
            date(2026, 12, 15),
            date(2027, 1, 10),
        ),
    ],
)
def test_parse_supported_periods(
    text: str,
    reference_date: date | None,
    expected_start: date | None,
    expected_end: date | None,
) -> None:
    parsed = parse_visible_period(text, reference_date=reference_date)

    assert parsed.start_date == expected_start
    assert parsed.end_date == expected_end


@pytest.mark.parametrize(
    "text",
    [
        "05/01〜06/30",
        "2026/04/22〜06/30",
        "2026/02/30〜2026/03/10",
        "6月1日から6月30日",
        "6月30日まで",
        "",
    ],
)
def test_uncertain_or_invalid_periods_remain_null(text: str) -> None:
    parsed = parse_visible_period(text)

    assert parsed.start_date is None
    assert parsed.end_date is None


def test_canonicalize_url_normalizes_equivalent_variants() -> None:
    expected = "https://example.jp/campaign?id=7&view=all"

    assert (
        canonicalize_url(
            "/campaign/?view=all&utm_source=test&id=7#entry",
            "HTTPS://EXAMPLE.JP/list/",
        )
        == expected
    )
    assert (
        canonicalize_url("https://example.jp:443/campaign?id=7&view=all&fbclid=ignored")
        == expected
    )


def test_canonicalize_url_preserves_semantic_hash_routes() -> None:
    first = canonicalize_url("https://lot.tsite.jp/#/detail2/lt001")
    second = canonicalize_url("https://lot.tsite.jp/#/detail2/lt002")

    assert first == "https://lot.tsite.jp/#/detail2/lt001"
    assert second == "https://lot.tsite.jp/#/detail2/lt002"
    assert first != second


@pytest.mark.parametrize("url", ["", "/relative", "javascript:void(0)", "ftp://x.jp/a"])
def test_canonicalize_url_rejects_non_http_urls(url: str) -> None:
    assert canonicalize_url(url) is None


def test_campaign_identity_prefers_canonical_url() -> None:
    first = campaign_identity(
        title="異なるタイトル",
        visible_period_text=None,
        campaign_url="/campaign/1/?utm_medium=email",
        base_url="https://example.jp/list",
    )
    second = campaign_identity(
        title="キャンペーン",
        visible_period_text="05/01〜06/30",
        campaign_url="https://EXAMPLE.jp/campaign/1#details",
    )

    assert first == second == "url:https://example.jp/campaign/1"


def test_campaign_identity_falls_back_to_normalized_title_and_period() -> None:
    first = campaign_identity(
        title=" キャンペーン　タイトル ",
        visible_period_text="05/01〜 06/30",
    )
    second = campaign_identity(
        title="キャンペーン タイトル",
        visible_period_text=" 05/01〜 06/30 ",
    )

    assert first == second
    assert first.startswith("title_period:")


def test_campaign_identity_requires_title_without_valid_url() -> None:
    with pytest.raises(ValueError):
        campaign_identity(title=" ", visible_period_text=None)


@pytest.mark.parametrize(
    ("end_date", "expected"),
    [
        (None, CampaignStatus.UNKNOWN),
        (date(2026, 6, 13), CampaignStatus.EXPIRED),
        (date(2026, 6, 14), CampaignStatus.ENDING_SOON),
        (date(2026, 6, 21), CampaignStatus.ENDING_SOON),
        (date(2026, 6, 22), CampaignStatus.ACTIVE),
    ],
)
def test_calculate_status(end_date: date | None, expected: CampaignStatus) -> None:
    assert calculate_status(end_date, today=date(2026, 6, 14)) is expected


def test_calculate_status_rejects_negative_window() -> None:
    with pytest.raises(ValueError):
        calculate_status(
            date(2026, 6, 14), today=date(2026, 6, 14), ending_within_days=-1
        )
