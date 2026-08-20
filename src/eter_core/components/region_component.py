# src/eter_core/components/region_component.py
from dataclasses import dataclass
from eter_core.domain.types import FervorReligioso, NivelInfeccion, FaccionTipo

@dataclass
class RegiónComponent:
    """Componente que define los índices de un nodo geográfico de Éter."""
    nombre: str
    poblacion_total: int
    fervor: FervorReligioso
    infeccion: NivelInfeccion
    faccion_dominante: FaccionTipo
    tasa_magos_oscuros: float = 0.0  # Calculado por el FaithSystem


@dataclass
class TerritoryComponent:
    """Relaciona una provincia con su estado y conserva su identidad Azgaar."""
    azgaar_id: int
    estado_id: int
    tipo: str = "provincia"


@dataclass
class StateComponent:
    """Datos territoriales propios de una entidad estatal."""
    azgaar_id: int
    nombre: str
    color: str
    provincia_ids: list[int]