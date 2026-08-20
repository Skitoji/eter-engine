# src/eter_core/domain/types.py
from typing import NewType
from dataclasses import dataclass
from enum import Enum, auto

EntityID = NewType("EntityID", int)

class FaccionTipo(Enum):
    SANTA_IGLESIA = auto()
    TORRE_DE_LOS_MAGOS = auto()
    GREMIO_AVENTUREROS = auto()
    GREMIO_AGRICOLA = auto()
    GREMIO_MERCANTE = auto()
    FACCIÓN_CULTISTA_OSCURA = auto()
    EJERCITO_DEMONIACO = auto()

@dataclass(frozen=True)
class FervorReligioso:
    """Value Object inmutable para representar la fe de una población (0.0 a 1.0)."""
    valor: float

    def __post_init__(self) -> None:
        if not (0.0 <= self.valor <= 1.0):
            raise ValueError(f"El fervor religioso debe estar entre 0.0 y 1.0. Valor dado: {self.valor}")

@dataclass(frozen=True)
class NivelInfeccion:
    """Value Object inmutable que representa la presión demoníaca (0.0 a 1.0)."""
    valor: float

    def __post_init__(self) -> None:
        if not (0.0 <= self.valor <= 1.0):
            raise ValueError(f"La infección debe estar entre 0.0 y 1.0. Valor dado: {self.valor}")