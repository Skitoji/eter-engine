from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Tuple


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
    """
    Definición inmutable de un producto del mundo de Éter.

    - `geografias_nativas`: biomas donde el producto se produce de forma natural.
      Un producto es más barato donde es nativo y más caro donde es importado.
      Si está vacío, no está ligado a una ubicación (precio neutral).
    - `peso`: peso en unidades de carga por unidad del producto.
    """
    nombre: str
    categoria: CategoriaProducto
    rareza: Rareza
    valor_base: float      # oro por unidad (referencia)
    dificultad: int        # 1 (trivial) .. 10 (extremo)
    geografias_nativas: Tuple[str, ...] = ()
    peso: float = 0.0

    @property
    def es_alimento(self) -> bool:
        return self.categoria == CategoriaProducto.ALIMENTO


CATALOGO_PRODUCTOS: Dict[str, ProductoDef] = {
    # ── Metales (minería / herrería) ────────────────────────────────
    "hierro": ProductoDef("Hierro", CategoriaProducto.METAL, Rareza.COMUN, 8.0, 1, ("montanas",), 2.0),
    "hierro_runico": ProductoDef("Hierro Rúnico", CategoriaProducto.METAL, Rareza.RARO, 45.0, 5, ("montanas",), 2.5),
    "mithril": ProductoDef("Mithril", CategoriaProducto.METAL, Rareza.LEGENDARIO, 300.0, 9, ("montanas",), 1.5),

    # ── Subproductos de monstruos ───────────────────────────────────
    "nucleo_slime": ProductoDef("Núcleo de Slime", CategoriaProducto.SUBPRODUCTO_MONSTRUO, Rareza.COMUN, 4.0, 1, ("valles",), 0.5),
    "oreja_goblin": ProductoDef("Oreja de Goblin", CategoriaProducto.SUBPRODUCTO_MONSTRUO, Rareza.COMUN, 3.0, 1, ("planicies", "valles"), 0.1),
    "hueso_no_muerto": ProductoDef("Hueso No Muerto", CategoriaProducto.SUBPRODUCTO_MONSTRUO, Rareza.COMUN, 6.0, 1, (), 0.5),
    "piel_lobo": ProductoDef("Piel de Lobo Gigante", CategoriaProducto.SUBPRODUCTO_MONSTRUO, Rareza.POCO_COMUN, 15.0, 2, ("planicies", "montanas"), 1.0),
    "escama_lagarto": ProductoDef("Escama de Hombre-Lagarto", CategoriaProducto.SUBPRODUCTO_MONSTRUO, Rareza.POCO_COMUN, 12.0, 2, ("costas", "valles"), 0.8),
    "colmillo_orco": ProductoDef("Colmillo de Orco", CategoriaProducto.SUBPRODUCTO_MONSTRUO, Rareza.POCO_COMUN, 18.0, 2, ("montanas", "planicies"), 0.8),
    "ectoplasma": ProductoDef("Ectoplasma", CategoriaProducto.SUBPRODUCTO_MONSTRUO, Rareza.RARO, 40.0, 4, (), 0.2),
    "reliquia_oscura": ProductoDef("Reliquia Oscura", CategoriaProducto.SUBPRODUCTO_MONSTRUO, Rareza.RARO, 55.0, 4, (), 0.3),
    "veneno_aracne": ProductoDef("Veneno de Aracne", CategoriaProducto.SUBPRODUCTO_MONSTRUO, Rareza.RARO, 60.0, 4, ("valles", "montanas"), 0.2),
    "seda_aracne": ProductoDef("Seda de Aracne", CategoriaProducto.SUBPRODUCTO_MONSTRUO, Rareza.EPICO, 80.0, 5, ("valles", "montanas"), 0.3),
    "cuerno_minotauro": ProductoDef("Cuerno de Minotauro", CategoriaProducto.SUBPRODUCTO_MONSTRUO, Rareza.EPICO, 90.0, 5, ("montanas",), 3.0),
    "sangre_quimera": ProductoDef("Sangre de Quimera", CategoriaProducto.SUBPRODUCTO_MONSTRUO, Rareza.EPICO, 120.0, 6, (), 0.5),
    "escama_wyvern": ProductoDef("Escama de Wyvern", CategoriaProducto.SUBPRODUCTO_MONSTRUO, Rareza.EPICO, 150.0, 7, ("montanas",), 2.0),
    "escama_dragon": ProductoDef("Escama de Dragón", CategoriaProducto.SUBPRODUCTO_MONSTRUO, Rareza.LEGENDARIO, 400.0, 9, ("montanas",), 3.0),
    "corazon_dragon": ProductoDef("Corazón de Dragón", CategoriaProducto.SUBPRODUCTO_MONSTRUO, Rareza.LEGENDARIO, 1000.0, 10, ("montanas",), 5.0),

    # ── Alimentos ───────────────────────────────────────────────────
    "trigo": ProductoDef("Trigo", CategoriaProducto.ALIMENTO, Rareza.COMUN, 2.0, 1, ("planicies", "valles"), 0.5),
    "setas": ProductoDef("Setas", CategoriaProducto.ALIMENTO, Rareza.COMUN, 3.0, 1, ("valles",), 0.3),
    "pan": ProductoDef("Pan", CategoriaProducto.ALIMENTO, Rareza.COMUN, 4.0, 1, ("planicies", "valles", "costas"), 0.3),
    "carne": ProductoDef("Carne", CategoriaProducto.ALIMENTO, Rareza.COMUN, 5.0, 1, ("planicies", "valles"), 0.5),
}
