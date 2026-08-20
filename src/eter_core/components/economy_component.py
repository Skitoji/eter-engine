from dataclasses import dataclass


@dataclass
class EconomyComponent:
    """Datos economicos mutables de una entidad territorial."""
    oro: float = 0.0
    produccion: float = 0.0
    comercio_activo: bool = False
    nivel_desarrollo: int = 1
