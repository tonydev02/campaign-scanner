from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, field_validator


class SourceType(StrEnum):
    VPOINT_PUBLIC = "vpoint_public"
    SMBC_PUBLIC = "smbc_public"
    VPASS_PRIVATE = "vpass_private"
    EMAIL = "email"
    MANUAL = "manual"


class RewardType(StrEnum):
    GUARANTEED = "guaranteed"
    LOTTERY = "lottery"
    MULTIPLIER = "multiplier"
    COUPON = "coupon"
    UNKNOWN = "unknown"


class CampaignStatus(StrEnum):
    ACTIVE = "active"
    ENDING_SOON = "ending_soon"
    EXPIRED = "expired"
    UNKNOWN = "unknown"


class Campaign(BaseModel):
    """Canonical campaign data preserved from source evidence."""

    model_config = ConfigDict(str_strip_whitespace=False)

    id: int | None = None
    source: str
    source_type: SourceType
    title: str
    campaign_url: str | None = None
    image_url: str | None = None
    visible_period_text: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    description: str | None = None
    category: str | None = None
    requires_entry: bool | None = None
    entry_text: str | None = None
    reward_text: str | None = None
    max_reward_points: int | None = None
    reward_type: RewardType | None = None
    target_payment_text: str | None = None
    target_store_text: str | None = None
    minimum_spend_text: str | None = None
    exclusions_text: str | None = None
    raw_text: str | None = None
    raw_html_hash: str | None = None
    screenshot_path: str | None = None
    first_seen_at: datetime | None = None
    last_seen_at: datetime | None = None
    scraped_at: datetime
    status: CampaignStatus = CampaignStatus.UNKNOWN

    @field_validator("source", "title")
    @classmethod
    def require_nonempty_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must contain non-whitespace characters")
        return value

    @field_validator("scraped_at", "first_seen_at", "last_seen_at")
    @classmethod
    def require_timezone(cls, value: datetime | None) -> datetime | None:
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("must include timezone information")
        return value
