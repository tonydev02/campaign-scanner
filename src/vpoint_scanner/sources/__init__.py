"""Campaign source adapters."""

from vpoint_scanner.sources.base import SourceError
from vpoint_scanner.sources.vpoint_public import collect_vpoint_public

__all__ = ["SourceError", "collect_vpoint_public"]
