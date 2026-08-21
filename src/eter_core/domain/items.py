from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Optional


class TipoObjeto(Enum):
    """Clasificación funcional de un objeto del mundo de Éter."""
    CONSUMIBLE = auto()
    HERRAMIENTA = auto()
    EQUIPABLE = auto()


@dataclass(frozen=True)
class ItemDef:
    """
    Definición inmutable de un objeto.

    - `efectos`: modificadores de stats (vida, mana, estamina, hambre, fuerza...).
      En consumibles se aplican al usarlos; en equipables son el bono pasivo.
    - `slot`: para EQUIPABLE, el hueco que ocupa ("arma", "armadura", "accesorio").
    """
    nombre: str
    tipo: TipoObjeto
    descripcion: str
    efectos: Dict[str, float] = field(default_factory=dict)
    slot: Optional[str] = None


# Catálogo central de objetos. Añadir un objeto nuevo es tan simple como
# agregar una entrada aquí: el ItemSystem lo expone automáticamente.
CATALOGO_OBJETOS: Dict[str, ItemDef] = {
    # ── Herramientas ────────────────────────────────────────────────
    "brujula": ItemDef(
        nombre="brujula",
        tipo=TipoObjeto.HERRAMIENTA,
        descripcion="Revela tus rutas adyacentes.",
    ),
    # ── Consumibles (curación / maná / energía) ─────────────────────
    "raciones": ItemDef(
        nombre="raciones",
        tipo=TipoObjeto.CONSUMIBLE,
        descripcion="Alimento básico de viaje. Restaura 20 HP y 15 de hambre.",
        efectos={"vida": 20, "hambre": 15},
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
    # ── Alimentos (vinculados al catálogo de productos) ──────────────
    "pan": ItemDef(
        nombre="pan",
        tipo=TipoObjeto.CONSUMIBLE,
        descripcion="Hogaza de pan. Sacia 25 de hambre.",
        efectos={"hambre": 25},
    ),
    "carne": ItemDef(
        nombre="carne",
        tipo=TipoObjeto.CONSUMIBLE,
        descripcion="Carne asada. Sacia 40 de hambre.",
        efectos={"hambre": 40},
    ),
    "setas": ItemDef(
        nombre="setas",
        tipo=TipoObjeto.CONSUMIBLE,
        descripcion="Setas silvestres. Sacian 15 de hambre.",
        efectos={"hambre": 15},
    ),
    # ── Equipables ──────────────────────────────────────────────────
    "espada_hierro": ItemDef(
        nombre="espada de hierro",
        tipo=TipoObjeto.EQUIPABLE,
        descripcion="Hoja forjada en hierro. +3 Fuerza.",
        efectos={"fuerza": 3},
        slot="arma",
    ),
    "armadura_cuero": ItemDef(
        nombre="armadura de cuero",
        tipo=TipoObjeto.EQUIPABLE,
        descripcion="Protección ligera. +2 Tenacidad.",
        efectos={"tenacidad": 2},
        slot="armadura",
    ),
    "anillo_estrella": ItemDef(
        nombre="anillo de la estrella",
        tipo=TipoObjeto.EQUIPABLE,
        descripcion="Reliquia de la Luz. +2 Inteligencia.",
        efectos={"inteligencia": 2},
        slot="accesorio",
    ),
    "espada_runica": ItemDef(
        nombre="espada de hierro rúnico",
        tipo=TipoObjeto.EQUIPABLE,
        descripcion="Hoja grabada con runas. +6 Fuerza.",
        efectos={"fuerza": 6},
        slot="arma",
    ),
    "espada_mithril": ItemDef(
        nombre="espada de mithril",
        tipo=TipoObjeto.EQUIPABLE,
        descripcion="El metal más fuerte del mundo. +10 Fuerza.",
        efectos={"fuerza": 10},
        slot="arma",
    ),
    "armadura_mithril": ItemDef(
        nombre="armadura de mithril",
        tipo=TipoObjeto.EQUIPABLE,
        descripcion="Coraza ligendaria. +8 Tenacidad.",
        efectos={"tenacidad": 8},
        slot="armadura",
    ),
}
