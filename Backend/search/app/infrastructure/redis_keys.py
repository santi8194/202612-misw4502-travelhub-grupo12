"""Centralized Redis key constants for the search service.

Import from here to avoid duplication between the infrastructure
adapter and the data seed script.
"""

from __future__ import annotations

DEST_INDEX_KEY = "search:destinations:index"
DEST_DATA_KEY = "search:destinations:data"
