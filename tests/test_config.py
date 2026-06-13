import logging

import pytest
from pydantic import ValidationError

from vpoint_scanner.config import PROJECT_ROOT, Settings
from vpoint_scanner.logging import LOGGER_NAME, configure_logging


def test_default_paths_are_repository_local() -> None:
    settings = Settings()

    assert settings.data_dir == PROJECT_ROOT / "data"
    assert settings.raw_data_dir == settings.data_dir / "raw"
    assert settings.screenshots_dir == settings.data_dir / "screenshots"
    assert settings.exports_dir == settings.data_dir / "exports"
    assert settings.database_path == settings.data_dir / "vpoint_campaigns.sqlite3"


def test_policy_defaults_are_conservative() -> None:
    settings = Settings()

    assert settings.extra_spending_allowed == 0
    assert settings.auto_entry_allowed is False
    assert settings.new_credit_card_application_allowed is False


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("extra_spending_allowed", 1),
        ("auto_entry_allowed", True),
        ("new_credit_card_application_allowed", True),
    ],
)
def test_policy_defaults_cannot_be_relaxed(field: str, value: object) -> None:
    with pytest.raises(ValidationError):
        Settings(**{field: value})


def test_data_directory_override_derives_child_paths(tmp_path) -> None:
    settings = Settings(data_dir=tmp_path)

    assert settings.raw_data_dir == tmp_path / "raw"
    assert settings.screenshots_dir == tmp_path / "screenshots"
    assert settings.exports_dir == tmp_path / "exports"
    assert settings.database_path == tmp_path / "vpoint_campaigns.sqlite3"


def test_logging_configuration_is_idempotent() -> None:
    logger = logging.getLogger(LOGGER_NAME)
    original_handlers = logger.handlers.copy()
    logger.handlers.clear()

    try:
        first = configure_logging()
        second = configure_logging()

        assert first is second
        assert len(logger.handlers) == 1
        assert logger.handlers[0].stream is not None
    finally:
        logger.handlers.clear()
        logger.handlers.extend(original_handlers)
