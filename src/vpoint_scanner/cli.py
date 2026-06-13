from enum import StrEnum
from pathlib import Path
from typing import Annotated

import typer

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
    """Expose the future public campaign scraping interface."""

    del source, screenshots
    typer.echo(PLACEHOLDER.format(feature="Scraping"))


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
