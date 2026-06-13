from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def test_sensitive_artifacts_are_ignored() -> None:
    gitignore = (REPOSITORY_ROOT / ".gitignore").read_text(encoding="utf-8")
    required_patterns = {
        ".env",
        "data/*.sqlite3",
        "data/raw/private/",
        "data/screenshots/private/",
        ".playwright/",
        "browser-profile/",
        "cookies.json",
        "*.session",
    }

    assert required_patterns <= set(gitignore.splitlines())


def test_environment_example_contains_no_secret_values() -> None:
    example = (REPOSITORY_ROOT / ".env.example").read_text(encoding="utf-8")
    forbidden_terms = ("password=", "secret=", "token=", "cookie=")

    assert all(term not in example.lower() for term in forbidden_terms)
