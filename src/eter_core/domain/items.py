from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict


class TipoObjeto(Enum):
    """Clasificación funcional de un objeto del mundo de Éter."""
    CONSUMIBLE = auto()
    HERRAMIENTA = auto()
    EQUIPABLE = auto()


@dataclass(frozen=True)
class ItemDef:
    """Definición inmutable de un objeto. Los efectos son modificadores de stats del jugador."""
    nombre: str
    tipo: TipoObjeto
    descripcion: str
    efectos: Dict[str, float] = field(default_factory=dict)


# Catálogo central de objetos. Añadir un objeto nuevo es tan simple como
# agregar una entrada aquí: el ItemSystem lo expone automáticamente.
CATALOGO_OBJETOS: Dict[str, ItemDef] = {
    "brujula": ItemDef(
        nombre="brujula",
        tipo=TipoObjeto.HERRAMIENTA,
        descripcion="Revela tus rutas adyacentes.",
    ),
    "raciones": ItemDef(
        nombre="raciones",
        tipo=TipoObjeto.CONSUMIBLE,
        descripcion="Alimento básico de viaje. Restaura 20 HP.",
        efectos={"vida": 20},
    ),
    "antorcha": ItemDef(
        nombre="antorcha",
        tipo=TipoObjeto.CONSUMIBLE,
        descripcion="Ilumina el camino y recupera 10 de estamina.",
        efectos={"estamina": 10},
    ),
    "hierbas": ItemDef(
        nombre="hierbas curativas",
        tipo=TipoObjeto.CONSUMIBLE,
        descripcion="Hierbas medicinales. Restauran 25 HP.",
        efectos={"vida": 25},
    ),
    "pocion_mana": ItemDef(
        nombre="pocion de mana",
        tipo=TipoObjeto.CONSUMIBLE,
        descripcion="Licor azulado que restaura 30 de mana.",
        efectos={"mana": 30},
    ),
}
