# src/eter_core/domain/events.py
from dataclasses import dataclass, field
from time import time
from eter_core.domain.types import EntityID, FaccionTipo

@dataclass(frozen=True)
class DomainEvent:
    """Clase base inmutable para todos los eventos del mundo."""
    # init=False evita que cause conflictos de herencia.
    # default_factory=time asegura que cada evento tenga la hora exacta en que ocurrió.
    timestamp: float = field(init=False, default_factory=time)

@dataclass(frozen=True)
class HegemoniaIglesiaRotasEvent(DomainEvent):
    """Se emite cuando una región cae por debajo del umbral de fe."""
    region_id: EntityID
    nombre_region: str
    faccion_anterior: FaccionTipo

@dataclass(frozen=True)
class InfeccionExtendidaEvent(DomainEvent):
    """Se emite cuando la peste demoníaca avanza a un nodo adyacente."""
    origen_id: EntityID
    destino_id: EntityID
    nuevo_nivel_infeccion: float


@dataclass(frozen=True)
class RiquezaGeneradaEvent(DomainEvent):
    """Se emite cuando una provincia genera riqueza durante un turno."""
    region_id: EntityID
    nombre_region: str
    oro_generado: float


@dataclass(frozen=True)
class InversionRealizadaEvent(DomainEvent):
    """Se emite tras una inversion del jugador en una provincia."""
    region_id: EntityID
    nombre_region: str
    coste: float


@dataclass(frozen=True)
class ComercioRealizadoEvent(DomainEvent):
    """Se emite cuando dos provincias adyacentes intercambian riqueza."""
    origen_id: EntityID
    destino_id: EntityID
    valor: float
    producto: str = "oro"
    distancia: float = 0.0
    dias_transporte: int = 0
    precio: float = 0.0


@dataclass(frozen=True)
class CultistasSurgidosEvent(DomainEvent):
    """Se emite cuando un cultista/mago oscuro surge en una región."""
    region_id: EntityID
    nombre_region: str
    total_cultistas: int