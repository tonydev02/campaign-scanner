import logging
from typing import TextIO

LOGGER_NAME = "vpoint_scanner"
_HANDLER_MARKER = "_vpoint_scanner_handler"


def configure_logging(
    level: str | int = logging.INFO,
    stream: TextIO | None = None,
) -> logging.Logger:
    """Configure and return the application logger without duplicate handlers."""

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)
    logger.propagate = False

    handler = next(
        (
            existing
            for existing in logger.handlers
            if getattr(existing, _HANDLER_MARKER, False)
        ),
        None,
    )
    if handler is None:
        handler = logging.StreamHandler(stream)
        setattr(handler, _HANDLER_MARKER, True)
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        )
        logger.addHandler(handler)
    elif stream is not None:
        handler.setStream(stream)

    handler.setLevel(level)
    return logger
