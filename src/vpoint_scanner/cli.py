from enum import StrEnum
from pathlib import Path
from typing import Annotated

import typer

from vpoint_scanner.config import get_settings
from vpoint_scanner.sources import SourceError, collect_vpoint_public

app = typer.Typer(
    help="Collect V Point campaign information for conservative local review.",
    no_args_is_help=True,
)

PLACEHOLDER = (
    "{feature} is not implemented in Phase 01. "
    "No campaigns were processed and no external action was taken."
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
    if screenshots:
        typer.echo(
            "Screenshot capture is introduced in Phase 06; "
            "no screenshot will be saved by this command.",
            err=True,
        )

    settings = get_settings()
    try:
        campaigns = collect_vpoint_public(
            url=settings.vpoint_public_url,
            timeout_ms=settings.browser_timeout_ms,
        )
    except SourceError as exc:
        typer.echo(f"Scrape failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(
        f"Collected {len(campaigns)} campaign cards from {settings.vpoint_public_url}"
    )
    for campaign in campaigns:
        typer.echo(f"- {campaign.title}")


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
) -> None:
    """Expose the future campaign export interface."""

    del output_format, output, ending_within_days
    typer.echo(PLACEHOLDER.format(feature="Export"))


@app.command()
def summary() -> None:
    """Expose the future database summary interface."""

    typer.echo(PLACEHOLDER.format(feature="Summary"))
