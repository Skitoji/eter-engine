from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict


class CategoriaProducto(Enum):
    """Clasificación económica de un producto comercializable."""
    METAL = auto()
    SUBPRODUCTO_MONSTRUO = auto()
    ALIMENTO = auto()
    MATERIAL = auto()


class Rareza(Enum):
    """Escala de rareza: determina el valor y la dificultad de obtención."""
    COMUN = auto()
    POCO_COMUN = auto()
    RARO = auto()
    EPICO = auto()
    LEGENDARIO = auto()


@dataclass(frozen=True)
class ProductoDef:
    """Definición inmutable de un producto del mundo de Éter."""
    nombre: str
    categoria: CategoriaProducto
    rareza: Rareza
    valor_base: float      # oro por unidad
    dificultad: int        # 1 (trivial) .. 10 (extremo)

    @property
    def es_alimento(self) -> bool:
        return self.categoria == CategoriaProducto.ALIMENTO


CATALOGO_PRODUCTOS: Dict[str, ProductoDef] = {
    # ── Metales (minería / herrería) ────────────────────────────────
    "hierro": ProductoDef("Hierro", CategoriaProducto.METAL, Rareza.COMUN, 8.0, 1),
    "hierro_runico": ProductoDef("Hierro Rúnico", CategoriaProducto.METAL, Rareza.RARO, 45.0, 5),
    "mithril": ProductoDef("Mithril", CategoriaProducto.METAL, Rareza.LEGENDARIO, 300.0, 9),

    # ── Subproductos de monstruos ───────────────────────────────────
    "nucleo_slime": ProductoDef("Núcleo de Slime", CategoriaProducto.SUBPRODUCTO_MONSTRUO, Rareza.COMUN, 4.0, 1),
    "oreja_goblin": ProductoDef("Oreja de Goblin", CategoriaProducto.SUBPRODUCTO_MONSTRUO, Rareza.COMUN, 3.0, 1),
    "hueso_no_muerto": ProductoDef("Hueso No Muerto", CategoriaProducto.SUBPRODUCTO_MONSTRUO, Rareza.COMUN, 6.0, 1),
    "piel_lobo": ProductoDef("Piel de Lobo Gigante", CategoriaProducto.SUBPRODUCTO_MONSTRUO, Rareza.POCO_COMUN, 15.0, 2),
    "escama_lagarto": ProductoDef("Escama de Hombre-Lagarto", CategoriaProducto.SUBPRODUCTO_MONSTRUO, Rareza.POCO_COMUN, 12.0, 2),
    "colmillo_orco": ProductoDef("Colmillo de Orco", CategoriaProducto.SUBPRODUCTO_MONSTRUO, Rareza.POCO_COMUN, 18.0, 2),
    "ectoplasma": ProductoDef("Ectoplasma", CategoriaProducto.SUBPRODUCTO_MONSTRUO, Rareza.RARO, 40.0, 4),
    "reliquia_oscura": ProductoDef("Reliquia Oscura", CategoriaProducto.SUBPRODUCTO_MONSTRUO, Rareza.RARO, 55.0, 4),
    "veneno_aracne": ProductoDef("Veneno de Aracne", CategoriaProducto.SUBPRODUCTO_MONSTRUO, Rareza.RARO, 60.0, 4),
    "seda_aracne": ProductoDef("Seda de Aracne", CategoriaProducto.SUBPRODUCTO_MONSTRUO, Rareza.EPICO, 80.0, 5),
    "cuerno_minotauro": ProductoDef("Cuerno de Minotauro", CategoriaProducto.SUBPRODUCTO_MONSTRUO, Rareza.EPICO, 90.0, 5),
    "sangre_quimera": ProductoDef("Sangre de Quimera", CategoriaProducto.SUBPRODUCTO_MONSTRUO, Rareza.EPICO, 120.0, 6),
    "escama_wyvern": ProductoDef("Escama de Wyvern", CategoriaProducto.SUBPRODUCTO_MONSTRUO, Rareza.EPICO, 150.0, 7),
    "escama_dragon": ProductoDef("Escama de Dragón", CategoriaProducto.SUBPRODUCTO_MONSTRUO, Rareza.LEGENDARIO, 400.0, 9),
    "corazon_dragon": ProductoDef("Corazón de Dragón", CategoriaProducto.SUBPRODUCTO_MONSTRUO, Rareza.LEGENDARIO, 1000.0, 10),

    # ── Alimentos ───────────────────────────────────────────────────
    "trigo": ProductoDef("Trigo", CategoriaProducto.ALIMENTO, Rareza.COMUN, 2.0, 1),
    "setas": ProductoDef("Setas", CategoriaProducto.ALIMENTO, Rareza.COMUN, 3.0, 1),
    "pan": ProductoDef("Pan", CategoriaProducto.ALIMENTO, Rareza.COMUN, 4.0, 1),
    "carne": ProductoDef("Carne", CategoriaProducto.ALIMENTO, Rareza.COMUN, 5.0, 1),
}
