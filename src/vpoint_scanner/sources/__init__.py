"""Campaign source adapters."""

from vpoint_scanner.sources.base import SourceError
from vpoint_scanner.sources.vpoint_public import CollectionResult, collect_vpoint_public

__all__ = ["CollectionResult", "SourceError", "collect_vpoint_public"]
