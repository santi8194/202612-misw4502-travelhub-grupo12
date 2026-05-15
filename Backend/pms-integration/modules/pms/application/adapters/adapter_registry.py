"""
Registry para obtener el adaptador PMS correcto según el proveedor.
"""

from modules.pms.application.adapters.base_adapter import PMSAdapter
from modules.pms.application.adapters.mock_pms_adapter import MockPMSAdapter


_ADAPTERS = {
    "mock": MockPMSAdapter,
}


def get_adapter(provider_name: str = "mock") -> PMSAdapter:
    """
    Factory para obtener el adaptador PMS correcto.
    
    Args:
        provider_name: Nombre del proveedor PMS ("mock", "opera", "mews", etc.)
        
    Returns:
        Instancia del adaptador correspondiente
        
    Raises:
        ValueError: Si el proveedor no está registrado
    """
    provider_name = provider_name.lower()
    
    if provider_name not in _ADAPTERS:
        raise ValueError(
            f"Proveedor PMS '{provider_name}' no soportado. "
            f"Proveedores disponibles: {list(_ADAPTERS.keys())}"
        )
    
    adapter_class = _ADAPTERS[provider_name]
    return adapter_class()
