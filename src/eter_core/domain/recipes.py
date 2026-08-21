from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class Receta:
    """Receta de forja: transforma materiales en un objeto equipable."""
    nombre: str
    resultado: str                          # clave del objeto en CATALOGO_OBJETOS
    materiales: Dict[str, int]               # material -> cantidad requerida
    coste_oro: float = 0.0                   # oro adicional que cobra el herrero


# Catálogo central de recetas de herrería. La dificultad del material (metales
# y subproductos de monstruos) determina la calidad del equipo resultante.
RECETAS_HERRERIA: Dict[str, Receta] = {
    "espada_hierro": Receta(
        nombre="Espada de Hierro",
        resultado="espada_hierro",
        materiales={"hierro": 2},
        coste_oro=10.0,
    ),
    "espada_runica": Receta(
        nombre="Espada de Hierro Rúnico",
        resultado="espada_runica",
        materiales={"hierro_runico": 3},
        coste_oro=40.0,
    ),
    "espada_mithril": Receta(
        nombre="Espada de Mithril",
        resultado="espada_mithril",
        materiales={"mithril": 2},
        coste_oro=200.0,
    ),
    "armadura_cuero": Receta(
        nombre="Armadura de Cuero",
        resultado="armadura_cuero",
        materiales={"piel_lobo": 3},
        coste_oro=15.0,
    ),
    "armadura_mithril": Receta(
        nombre="Armadura de Mithril",
        resultado="armadura_mithril",
        materiales={"mithril": 3, "escama_dragon": 1},
        coste_oro=500.0,
    ),
    "anillo_estrella": Receta(
        nombre="Anillo de la Estrella",
        resultado="anillo_estrella",
        materiales={"reliquia_oscura": 1, "ectoplasma": 2},
        coste_oro=60.0,
    ),
}


def listar_recetas() -> List[Receta]:
    return list(RECETAS_HERRERIA.values())
