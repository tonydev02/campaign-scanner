from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Annotated

import typer

from vpoint_scanner.config import get_settings
from vpoint_scanner.db import (
    PersistenceError,
    create_sqlite_engine,
    initialize_database,
    list_campaigns,
    open_existing_database,
    persist_campaigns,
    summarize_campaigns,
)
from vpoint_scanner.export import ExportError, ExportProfile, write_campaign_export
from vpoint_scanner.sources import SourceError, collect_vpoint_public

app = typer.Typer(
    help="Collect V Point campaign information for conservative local review.",
    no_args_is_help=True,
)


class ExportFormat(StrEnum):
    json = "json"


@app.command()
def scrape(
    source: Annotated[
        str | None,
        typer.Option(help="Limit scraping to one configured source."),
    ] = None,
    screenshots: Annotated[
        bool,
        typer.Option(help="Save public campaign evidence screenshots."),
    ] = False,
) -> None:
    """Collect visible campaign cards from configured public sources."""

    source_name = source or "vpoint_public"
    if source_name != "vpoint_public":
        raise typer.BadParameter(
            f"unsupported source: {source_name}",
            param_hint="--source",
        )
    settings = get_settings()
    try:
        collection = collect_vpoint_public(
            url=settings.vpoint_public_url,
            timeout_ms=settings.browser_timeout_ms,
            screenshots=screenshots,
            screenshots_dir=(
                settings.screenshots_dir / "public"
                if settings.screenshots_dir is not None
                else None
            ),
            detail_delay_seconds=settings.detail_delay_seconds,
        )
    except SourceError as exc:
        typer.echo(f"Scrape failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    if settings.database_path is None:
        typer.echo("Scrape failed: database path is not configured.", err=True)
        raise typer.Exit(code=1)
    try:
        engine = create_sqlite_engine(settings.database_path)
        initialize_database(engine)
        result = persist_campaigns(engine, collection.campaigns)
    except PersistenceError as exc:
        typer.echo(f"Scrape failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(
        f"Collected {len(collection.campaigns)} campaign cards from "
        f"{settings.vpoint_public_url}"
    )
    typer.echo(
        f"Details: {collection.detail_enriched} enriched, "
        f"{collection.detail_skipped} skipped, "
        f"{collection.detail_failed} failed"
    )
    typer.echo(f"Screenshots: {collection.screenshots_saved} saved")
    typer.echo(
        f"Persisted {result.inserted} inserted and {result.updated} updated "
        f"campaigns to {settings.database_path}"
    )


@app.command("export")
def export_campaigns(
    output_format: Annotated[
        ExportFormat,
        typer.Option("--format", help="Campaign export format."),
    ] = ExportFormat.json,
    output: Annotated[
        Path | None,
        typer.Option(help="Destination path for the generated export."),
    ] = None,
    ending_within_days: Annotated[
        int | None,
        typer.Option(
            min=0,
            help="Include campaigns ending within this many days.",
        ),
    ] = None,
    profile: Annotated[
        ExportProfile,
        typer.Option(help="Use compact daily-review or full evidence output."),
    ] = ExportProfile.COMPACT,
) -> None:
    """Export stored campaigns as UTF-8 JSON."""

    del output_format
    settings = get_settings()
    if settings.database_path is None or settings.exports_dir is None:
        typer.echo(
            "Export failed: database or export path is not configured.", err=True
        )
        raise typer.Exit(code=1)
    output_path = output or settings.exports_dir / f"campaigns_{profile.value}.json"
    now = datetime.now().astimezone()
    try:
        engine = open_existing_database(settings.database_path)
        campaigns = list_campaigns(engine)
        envelope = write_campaign_export(
            campaigns,
            output_path=output_path,
            today=now.date(),
            exported_at=now,
            ending_within_days=ending_within_days,
            profile=profile,
        )
    except (PersistenceError, ExportError) as exc:
        typer.echo(f"Export failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(f"Exported {envelope['campaign_count']} campaigns to {output_path}")


@app.command()
def summary() -> None:
    """Show current campaign counts from the local database."""

    settings = get_settings()
    if settings.database_path is None:
        typer.echo("Summary failed: database path is not configured.", err=True)
        raise typer.Exit(code=1)
    try:
        engine = open_existing_database(settings.database_path)
        result = summarize_campaigns(engine, today=datetime.now().astimezone().date())
    except PersistenceError as exc:
        typer.echo(f"Summary failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(f"Campaigns: {result.total}")
    typer.echo(f"Sources: {result.source_count}")
    typer.echo(f"Active: {result.active}")
    typer.echo(f"Ending soon: {result.ending_soon}")
    typer.echo(f"Expired: {result.expired}")
    typer.echo(f"Unknown: {result.unknown}")
