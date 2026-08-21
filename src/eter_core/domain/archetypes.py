from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class ArquetipoDef:
    """
    Potencial de Nacimiento (arquetipo base): define la inclinación natural
    del personaje, que luego puede moldearse con objetos, hierbas o pociones.
    """
    clave: str
    nombre: str
    descripcion: str
    vida_maxima: int
    mana_maximo: int
    fuerza: int
    inteligencia: int
    estamina_maxima: int
    tenacidad: int
    bonus_critico: float = 0.0


CATALOGO_ARQUETIPOS: Dict[str, ArquetipoDef] = {
    "tanque": ArquetipoDef(
        clave="tanque",
        nombre="Tanque / Coloso",
        descripcion="Alta salud inicial y tenacidad.",
        vida_maxima=150, mana_maximo=30, fuerza=14, inteligencia=7,
        estamina_maxima=90, tenacidad=18, bonus_critico=0.0,
    ),
    "mago": ArquetipoDef(
        clave="mago",
        nombre="Mago / Erudito",
        descripcion="Alto maná e inteligencia.",
        vida_maxima=80, mana_maximo=130, fuerza=7, inteligencia=17,
        estamina_maxima=85, tenacidad=8, bonus_critico=0.0,
    ),
    "caballero": ArquetipoDef(
        clave="caballero",
        nombre="Caballero / Vanguardia",
        descripcion="Balanceado entre fuerza y estamina.",
        vida_maxima=115, mana_maximo=55, fuerza=12, inteligencia=10,
        estamina_maxima=110, tenacidad=12, bonus_critico=0.05,
    ),
    "asesino": ArquetipoDef(
        clave="asesino",
        nombre="Asesino / Acechador",
        descripcion="Alta estamina y bonificación de daño crítico.",
        vida_maxima=95, mana_maximo=45, fuerza=15, inteligencia=12,
        estamina_maxima=120, tenacidad=7, bonus_critico=0.25,
    ),
}
