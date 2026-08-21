from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from eter_core.domain.items import CATALOGO_OBJETOS, ItemDef, TipoObjeto


@dataclass(frozen=True)
class SetRopaDef:
    """
    Definición de un set de ropa/armadura por clase y nivel.

    - `clase`: arquetipo destinatario ("tanque", "mago", "caballero", "asesino").
    - `nivel`: "basico", "medio" o "avanzado".
    - `piezas`: claves de objetos (ItemDef) que componen el set.
    - `bonus_set`: buff que se obtiene al llevar el set completo.
    """
    nombre: str
    clase: str
    nivel: str
    piezas: Tuple[str, ...]
    bonus_set: Dict[str, float] = field(default_factory=dict)


# Configuración por clase: stat primario + nombre temático de las piezas.
_CLASES: Dict[str, Dict] = {
    "tanque": {"nombre": "Coloso", "stat": "tenacidad"},
    "mago": {"nombre": "Erudito", "stat": "inteligencia"},
    "caballero": {"nombre": "Vanguardia", "stat": "fuerza"},
    "asesino": {"nombre": "Acechador", "stat": "fuerza"},
}

# Configuración por nivel: material, bono por pieza y bono de set completo.
_NIVELES: Dict[str, Dict] = {
    "basico": {"material": "Hierro", "pieza": 2.0, "bonus": 3.0, "crit": 0.05, "peso": 3.0},
    "medio": {"material": "Rúnico", "pieza": 4.0, "bonus": 6.0, "crit": 0.10, "peso": 3.5},
    "avanzado": {"material": "Mithril", "pieza": 7.0, "bonus": 12.0, "crit": 0.15, "peso": 2.5},
}

# Piezas del set: (slot, nombre_pieza)
_PIEZAS: List[Tuple[str, str]] = [
    ("casco", "casco"),
    ("armadura", "coraza"),
    ("botas", "botas"),
]

CATALOGO_SETS: Dict[str, SetRopaDef] = {}


def _nombre_pieza(slot: str, clase_nombre: str, material: str) -> str:
    """Genera el nombre legible de una pieza."""
    if slot == "casco":
        return f"Casco de {material} del {clase_nombre}"
    if slot == "armadura":
        return f"Coraza de {material} del {clase_nombre}"
    return f"Botas de {material} del {clase_nombre}"


def _registrar_sets() -> None:
    """Genera las piezas de cada set y las registra en el catálogo de objetos."""
    for clase, config in _CLASES.items():
        stat = config["stat"]
        clase_nombre = config["nombre"]
        for nivel, nivel_cfg in _NIVELES.items():
            piezas: List[str] = []
            material = nivel_cfg["material"]
            for slot, _ in _PIEZAS:
                clave = f"{slot}_{clase}_{nivel}"
                piezas.append(clave)
                CATALOGO_OBJETOS[clave] = ItemDef(
                    nombre=_nombre_pieza(slot, clase_nombre, material),
                    tipo=TipoObjeto.EQUIPABLE,
                    descripcion=f"Pieza de {material.lower()} del set {nivel} de {clase_nombre}.",
                    efectos={stat: nivel_cfg["pieza"]},
                    slot=slot,
                    peso=nivel_cfg["peso"],
                    conjunto=f"set_{clase}_{nivel}",
                )

            bonus: Dict[str, float] = {stat: nivel_cfg["bonus"]}
            if clase == "asesino":
                bonus["bonus_critico"] = nivel_cfg["crit"]

            CATALOGO_SETS[f"set_{clase}_{nivel}"] = SetRopaDef(
                nombre=f"Set {nivel.capitalize()} del {clase_nombre}",
                clase=clase,
                nivel=nivel,
                piezas=tuple(piezas),
                bonus_set=bonus,
            )


_registrar_sets()


def sets_por_clase(clase: str) -> List[SetRopaDef]:
    """Devuelve los sets (básico→medio→avanzado) de una clase."""
    orden = {"basico": 0, "medio": 1, "avanzado": 2}
    return sorted(
        (s for s in CATALOGO_SETS.values() if s.clase == clase),
        key=lambda s: orden.get(s.nivel, 9),
    )


def listar_sets() -> List[SetRopaDef]:
    return list(CATALOGO_SETS.values())
