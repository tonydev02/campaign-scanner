from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import Engine, create_engine, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from vpoint_scanner.models import Base, CampaignRecord
from vpoint_scanner.normalize import campaign_identity, canonicalize_url
from vpoint_scanner.schemas import Campaign


class PersistenceError(RuntimeError):
    """A user-facing local database failure."""


@dataclass(frozen=True)
class UpsertResult:
    inserted: int
    updated: int


_MERGE_FIELDS = (
    "source",
    "source_type",
    "title",
    "campaign_url",
    "image_url",
    "visible_period_text",
    "start_date",
    "end_date",
    "description",
    "category",
    "requires_entry",
    "entry_text",
    "reward_text",
    "max_reward_points",
    "reward_type",
    "target_payment_text",
    "target_store_text",
    "minimum_spend_text",
    "exclusions_text",
    "raw_text",
    "raw_html_hash",
    "screenshot_path",
    "status",
)


def create_sqlite_engine(database_path: Path) -> Engine:
    """Create a SQLite engine and parent directory on explicit invocation."""

    try:
        database_path.parent.mkdir(parents=True, exist_ok=True)
        return create_engine(f"sqlite:///{database_path}", future=True)
    except OSError as exc:
        raise PersistenceError(
            f"Could not prepare database path {database_path}: {exc}"
        ) from exc


def initialize_database(engine: Engine) -> None:
    try:
        Base.metadata.create_all(engine)
    except SQLAlchemyError as exc:
        raise PersistenceError(f"Could not initialize SQLite database: {exc}") from exc


def persist_campaigns(engine: Engine, campaigns: list[Campaign]) -> UpsertResult:
    """Atomically insert or update a batch of campaign observations."""

    inserted = 0
    updated = 0
    try:
        with Session(engine) as session, session.begin():
            for campaign in campaigns:
                created = _upsert_campaign(session, campaign)
                inserted += int(created)
                updated += int(not created)
    except SQLAlchemyError as exc:
        raise PersistenceError(f"Could not persist campaigns: {exc}") from exc
    return UpsertResult(inserted=inserted, updated=updated)


def campaign_count(engine: Engine) -> int:
    with Session(engine) as session:
        return session.scalar(select(func.count()).select_from(CampaignRecord)) or 0


def list_campaigns(engine: Engine) -> list[Campaign]:
    with Session(engine) as session:
        records = session.scalars(
            select(CampaignRecord).order_by(CampaignRecord.id)
        ).all()
        return [_to_campaign(record) for record in records]


def _upsert_campaign(session: Session, campaign: Campaign) -> bool:
    canonical_url = (
        canonicalize_url(campaign.campaign_url)
        if campaign.campaign_url is not None
        else None
    )
    fallback_key = campaign_identity(
        title=campaign.title,
        visible_period_text=campaign.visible_period_text,
    )
    identity_key = f"url:{canonical_url}" if canonical_url else fallback_key
    record = _find_existing(
        session,
        canonical_url=canonical_url,
        fallback_key=fallback_key,
        identity_key=identity_key,
    )
    created = record is None
    if record is None:
        record = CampaignRecord(
            identity_key=identity_key,
            canonical_url=canonical_url,
            fallback_key=fallback_key,
            source=campaign.source,
            source_type=campaign.source_type.value,
            title=campaign.title,
            first_seen_at=campaign.first_seen_at or campaign.scraped_at,
            last_seen_at=campaign.last_seen_at or campaign.scraped_at,
            scraped_at=campaign.scraped_at,
            status=campaign.status.value,
        )
        session.add(record)
    else:
        record.identity_key = identity_key
        record.canonical_url = canonical_url or record.canonical_url
        record.fallback_key = fallback_key
        record.last_seen_at = campaign.last_seen_at or campaign.scraped_at
        record.scraped_at = campaign.scraped_at

    _merge_campaign_fields(record, campaign)
    session.flush()
    return created


def _find_existing(
    session: Session,
    *,
    canonical_url: str | None,
    fallback_key: str,
    identity_key: str,
) -> CampaignRecord | None:
    if canonical_url:
        record = session.scalar(
            select(CampaignRecord).where(CampaignRecord.canonical_url == canonical_url)
        )
        if record is not None:
            return record
        return session.scalar(
            select(CampaignRecord).where(
                CampaignRecord.canonical_url.is_(None),
                CampaignRecord.fallback_key == fallback_key,
            )
        )

    fallback_records = session.scalars(
        select(CampaignRecord).where(CampaignRecord.fallback_key == fallback_key)
    ).all()
    if len(fallback_records) == 1:
        return fallback_records[0]
    return session.scalar(
        select(CampaignRecord).where(CampaignRecord.identity_key == identity_key)
    )


def _merge_campaign_fields(record: CampaignRecord, campaign: Campaign) -> None:
    for field in _MERGE_FIELDS:
        value = getattr(campaign, field)
        if value is None:
            continue
        if field in {"source_type", "reward_type", "status"}:
            value = value.value
        setattr(record, field, value)


def _to_campaign(record: CampaignRecord) -> Campaign:
    return Campaign(
        id=record.id,
        source=record.source,
        source_type=record.source_type,
        title=record.title,
        campaign_url=record.campaign_url,
        image_url=record.image_url,
        visible_period_text=record.visible_period_text,
        start_date=record.start_date,
        end_date=record.end_date,
        description=record.description,
        category=record.category,
        requires_entry=record.requires_entry,
        entry_text=record.entry_text,
        reward_text=record.reward_text,
        max_reward_points=record.max_reward_points,
        reward_type=record.reward_type,
        target_payment_text=record.target_payment_text,
        target_store_text=record.target_store_text,
        minimum_spend_text=record.minimum_spend_text,
        exclusions_text=record.exclusions_text,
        raw_text=record.raw_text,
        raw_html_hash=record.raw_html_hash,
        screenshot_path=record.screenshot_path,
        first_seen_at=record.first_seen_at,
        last_seen_at=record.last_seen_at,
        scraped_at=record.scraped_at,
        status=record.status,
    )
