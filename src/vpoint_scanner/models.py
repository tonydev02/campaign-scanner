from datetime import date, datetime

from sqlalchemy import Boolean, Date, Integer, String, Text
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import TypeDecorator


class Base(DeclarativeBase):
    pass


class UTCDateTime(TypeDecorator[datetime]):
    """Store aware datetimes as ISO strings because SQLite loses timezones."""

    impl = String(40)
    cache_ok = True

    def process_bind_param(
        self,
        value: datetime | None,
        dialect: Dialect,
    ) -> str | None:
        del dialect
        if value is None:
            return None
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("datetime must include timezone information")
        return value.isoformat()

    def process_result_value(
        self,
        value: str | None,
        dialect: Dialect,
    ) -> datetime | None:
        del dialect
        return datetime.fromisoformat(value) if value is not None else None


class CampaignRecord(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    identity_key: Mapped[str] = mapped_column(String(2048), unique=True, index=True)
    canonical_url: Mapped[str | None] = mapped_column(
        String(2048),
        unique=True,
        nullable=True,
    )
    fallback_key: Mapped[str] = mapped_column(String(2048), index=True)
    source: Mapped[str] = mapped_column(String(2048))
    source_type: Mapped[str] = mapped_column(String(32))
    title: Mapped[str] = mapped_column(Text)
    campaign_url: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(Text)
    visible_period_text: Mapped[str | None] = mapped_column(Text)
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(Text)
    requires_entry: Mapped[bool | None] = mapped_column(Boolean)
    entry_text: Mapped[str | None] = mapped_column(Text)
    reward_text: Mapped[str | None] = mapped_column(Text)
    max_reward_points: Mapped[int | None] = mapped_column(Integer)
    reward_type: Mapped[str | None] = mapped_column(String(32))
    target_payment_text: Mapped[str | None] = mapped_column(Text)
    target_store_text: Mapped[str | None] = mapped_column(Text)
    minimum_spend_text: Mapped[str | None] = mapped_column(Text)
    exclusions_text: Mapped[str | None] = mapped_column(Text)
    detail_scrape_status: Mapped[str] = mapped_column(
        String(32),
        default="not_attempted",
    )
    requires_new_application: Mapped[bool | None] = mapped_column(Boolean)
    is_lottery: Mapped[bool | None] = mapped_column(Boolean)
    is_guaranteed: Mapped[bool | None] = mapped_column(Boolean)
    is_financial_product: Mapped[bool | None] = mapped_column(Boolean)
    is_gambling_or_prediction: Mapped[bool | None] = mapped_column(Boolean)
    raw_text: Mapped[str | None] = mapped_column(Text)
    raw_html_hash: Mapped[str | None] = mapped_column(String(128))
    screenshot_path: Mapped[str | None] = mapped_column(Text)
    first_seen_at: Mapped[datetime] = mapped_column(UTCDateTime())
    last_seen_at: Mapped[datetime] = mapped_column(UTCDateTime())
    scraped_at: Mapped[datetime] = mapped_column(UTCDateTime())
    status: Mapped[str] = mapped_column(String(32))
