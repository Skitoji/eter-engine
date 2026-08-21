from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict


class TipoHechizo(Enum):
    """Clasificación funcional de un hechizo."""
    BUFF = auto()          # mejora stats del jugador temporalmente
    CURACION = auto()      # restaura vida/mana
    AREA = auto()          # afecta un área (ej. invisibilidad en área)
    DANO = auto()          # inflige daño a enemigos


@dataclass(frozen=True)
class HechizoDef:
    """Definición inmutable de un hechizo."""
    nombre: str
    tipo: TipoHechizo
    coste_mana: float
    descripcion: str
    efectos: Dict[str, float] = field(default_factory=dict)  # stats que modifica
    duracion_turnos: int = 0  # 0 = instantáneo; >0 = buff temporal


# Catálogo central de hechizos. El Mago/Erudito tiene más mana para lanzarlos.
CATALOGO_HECHIZOS: Dict[str, HechizoDef] = {
    "invisibilidad_area": HechizoDef(
        nombre="Invisibilidad en Área",
        tipo=TipoHechizo.AREA,
        coste_mana=40.0,
        descripcion="Oculta al jugador y aliados de los enemigos durante 3 turnos.",
        efectos={"invisible": 1.0},
        duracion_turnos=3,
    ),
    "bendicion": HechizoDef(
        nombre="Bendición",
        tipo=TipoHechizo.BUFF,
        coste_mana=15.0,
        descripcion="Aumenta la Fuerza en +5 durante 2 turnos.",
        efectos={"fuerza": 5.0},
        duracion_turnos=2,
    ),
    "escudo_arcano": HechizoDef(
        nombre="Escudo Arcano",
        tipo=TipoHechizo.BUFF,
        coste_mana=20.0,
        descripcion="Aumenta la Tenacidad en +5 durante 2 turnos.",
        efectos={"tenacidad": 5.0},
        duracion_turnos=2,
    ),
    "curacion": HechizoDef(
        nombre="Curación",
        tipo=TipoHechizo.CURACION,
        coste_mana=25.0,
        descripcion="Restaura 40 puntos de vida.",
        efectos={"vida": 40.0},
        duracion_turnos=0,
    ),
    "restaurar_mana": HechizoDef(
        nombre="Restaurar Maná",
        tipo=TipoHechizo.CURACION,
        coste_mana=0.0,
        descripcion="Canaliza la luz para restaurar 30 de maná.",
        efectos={"mana": 30.0},
        duracion_turnos=0,
    ),
    "rayo_arcano": HechizoDef(
        nombre="Rayo Arcano",
        tipo=TipoHechizo.DANO,
        coste_mana=30.0,
        descripcion="Inflige 50 de daño mágico directo a un enemigo.",
        efectos={"dano": 50.0},
        duracion_turnos=0,
    ),
}
