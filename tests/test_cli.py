from typer.testing import CliRunner

from vpoint_scanner.cli import app

runner = CliRunner()


def test_root_help_lists_commands() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "scrape" in result.stdout
    assert "export" in result.stdout
    assert "summary" in result.stdout


def test_scrape_help_lists_future_options() -> None:
    result = runner.invoke(app, ["scrape", "--help"])

    assert result.exit_code == 0
    assert "--source" in result.stdout
    assert "--screenshots" in result.stdout


def test_export_help_lists_future_options() -> None:
    result = runner.invoke(app, ["export", "--help"])

    assert result.exit_code == 0
    assert "--format" in result.stdout
    assert "--output" in result.stdout
    assert "--ending-within-days" in result.stdout


def test_placeholder_commands_are_honest_and_successful(tmp_path) -> None:
    commands = [
        ["scrape", "--source", "vpoint_public", "--screenshots"],
        ["export", "--format", "json", "--output", str(tmp_path / "campaigns.json")],
        ["summary"],
    ]

    for command in commands:
        result = runner.invoke(app, command)
        assert result.exit_code == 0
        assert "not implemented in Phase 01" in result.stdout
        assert "No campaigns were processed" in result.stdout

    assert list(tmp_path.iterdir()) == []


def test_negative_ending_window_is_rejected() -> None:
    result = runner.invoke(app, ["export", "--ending-within-days", "-1"])

    assert result.exit_code != 0
