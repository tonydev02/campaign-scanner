from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Local paths and non-negotiable safety defaults."""

    model_config = SettingsConfigDict(
        env_prefix="VPOINT_",
        extra="ignore",
        validate_default=True,
    )

    data_dir: Path = PROJECT_ROOT / "data"
    raw_data_dir: Path | None = None
    screenshots_dir: Path | None = None
    exports_dir: Path | None = None
    database_path: Path | None = None
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    extra_spending_allowed: Literal[0] = 0
    auto_entry_allowed: Literal[False] = False
    new_credit_card_application_allowed: Literal[False] = False

    @model_validator(mode="after")
    def derive_data_paths(self) -> "Settings":
        if self.raw_data_dir is None:
            self.raw_data_dir = self.data_dir / "raw"
        if self.screenshots_dir is None:
            self.screenshots_dir = self.data_dir / "screenshots"
        if self.exports_dir is None:
            self.exports_dir = self.data_dir / "exports"
        if self.database_path is None:
            self.database_path = self.data_dir / "vpoint_campaigns.sqlite3"
        return self


@lru_cache
def get_settings() -> Settings:
    """Return one validated settings object for the current process."""

    return Settings()
