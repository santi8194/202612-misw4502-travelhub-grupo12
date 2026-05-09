"""Adaptadores para diferentes proveedores PMS."""

from .base_adapter import PMSAdapter
from .mock_pms_adapter import MockPMSAdapter
from .adapter_registry import get_adapter

__all__ = ["PMSAdapter", "MockPMSAdapter", "get_adapter"]
