from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict


class TipoMonstruo(Enum):
    """Naturaleza de la amenaza, vincula con el lore (fe, infección, bioma)."""
    BESTIA = auto()
    HUMANOIDE = auto()
    NO_MUERTO = auto()
    CORRUPTO = auto()
    DRAGON = auto()
    ABERRACION = auto()


@dataclass(frozen=True)
class MonstruoDef:
    """Definición inmutable de un monstruo del bestiario de Éter."""
    nombre: str
    tier: int                 # 1 (fodder) .. 5 (boss)
    tipo: TipoMonstruo
    vida: int
    ataque: int
    drops: Dict[str, float] = field(default_factory=dict)  # producto -> probabilidad (0..1)
    descripcion: str = ""


CATALOGO_MONSTRUOS: Dict[str, MonstruoDef] = {
    # ── Tier 1 — Fodder / inicio de aventura ─────────────────────────
    "goblin": MonstruoDef(
        nombre="Goblin", tier=1, tipo=TipoMonstruo.HUMANOIDE, vida=20, ataque=5,
        drops={"oreja_goblin": 0.8},
        descripcion="Clásico indiscutible. Se organiza en hordas primitivas en las periferias.",
    ),
    "slime": MonstruoDef(
        nombre="Slime", tier=1, tipo=TipoMonstruo.ABERRACION, vida=25, ataque=4,
        drops={"nucleo_slime": 0.9},
        descripcion="Gelatinoso. Va de mascota simpática a variante ácida que absorbe materia.",
    ),
    "lobo_gigante": MonstruoDef(
        nombre="Lobo Gigante", tier=1, tipo=TipoMonstruo.BESTIA, vida=30, ataque=8,
        drops={"piel_lobo": 0.7},
        descripcion="Depredador veloz que caza en manada en bosques y planicies.",
    ),

    # ── Tier 2 — Fuerzas de asalto y brutos ──────────────────────────
    "orco": MonstruoDef(
        nombre="Orco", tier=2, tipo=TipoMonstruo.HUMANOIDE, vida=60, ataque=12,
        drops={"colmillo_orco": 0.6},
        descripcion="Guerrero corpulento y agresivo. Protagoniza incursiones contra rutas comerciales.",
    ),
    "hombre_lagarto": MonstruoDef(
        nombre="Hombre-Lagarto", tier=2, tipo=TipoMonstruo.HUMANOIDE, vida=55, ataque=11,
        drops={"escama_lagarto": 0.6},
        descripcion="Tribal de pantanos y ríos; combina astucia táctica con cultura tribal.",
    ),
    "esqueleto": MonstruoDef(
        nombre="Esqueleto", tier=2, tipo=TipoMonstruo.NO_MUERTO, vida=40, ataque=9,
        drops={"hueso_no_muerto": 0.7},
        descripcion="Resultado clásico de la necromancia. Abunda donde la fe ha colapsado.",
    ),
    "zombi": MonstruoDef(
        nombre="Zombi", tier=2, tipo=TipoMonstruo.NO_MUERTO, vida=50, ataque=10,
        drops={"hueso_no_muerto": 0.7},
        descripcion="Carne animada por la descomposición mágica y la Generación Oscura.",
    ),
    "cultista": MonstruoDef(
        nombre="Cultista", tier=2, tipo=TipoMonstruo.CORRUPTO, vida=45, ataque=12,
        drops={"reliquia_oscura": 0.5},
        descripcion="Humano corrompido que perdió la cordura ante una deidad oscura.",
    ),

    # ── Tier 3 ───────────────────────────────────────────────────────
    "minotauro": MonstruoDef(
        nombre="Minotauro", tier=3, tipo=TipoMonstruo.BESTIA, vida=120, ataque=22,
        drops={"cuerno_minotauro": 0.45},
        descripcion="Bestia colosal que custodia ruinas antiguas y pasos montañosos.",
    ),
    "aracne": MonstruoDef(
        nombre="Aracne", tier=3, tipo=TipoMonstruo.ABERRACION, vida=90, ataque=18,
        drops={"seda_aracne": 0.5, "veneno_aracne": 0.3},
        descripcion="Araña gigante de cuevas y bosques densos; inmoviliza con telarañas.",
    ),
    "espectro": MonstruoDef(
        nombre="Espectro", tier=3, tipo=TipoMonstruo.NO_MUERTO, vida=80, ataque=20,
        drops={"ectoplasma": 0.5},
        descripcion="Entidad incorpórea que ataca el maná y la tenacidad del personaje.",
    ),

    # ── Tier 4 — Bestias mitológicas ─────────────────────────────────
    "banshee": MonstruoDef(
        nombre="Banshee", tier=4, tipo=TipoMonstruo.NO_MUERTO, vida=110, ataque=28,
        drops={"ectoplasma": 0.6},
        descripcion="Lamento que drena la energía espiritual de quien lo escucha.",
    ),
    "quimera": MonstruoDef(
        nombre="Quimera", tier=4, tipo=TipoMonstruo.ABERRACION, vida=180, ataque=32,
        drops={"sangre_quimera": 0.4},
        descripcion="Híbrido aberrante creado por experimentos arcanos o mutación demoníaca.",
    ),
    "wyvern": MonstruoDef(
        nombre="Wyvern", tier=4, tipo=TipoMonstruo.DRAGON, vida=200, ataque=30,
        drops={"escama_wyvern": 0.4},
        descripcion="Señor de los cielos y las cumbres. Migra a zonas pobladas buscando refugio.",
    ),

    # ── Tier 5 — Jefes de zona ───────────────────────────────────────
    "dragon": MonstruoDef(
        nombre="Dragón", tier=5, tipo=TipoMonstruo.DRAGON, vida=500, ataque=50,
        drops={"escama_dragon": 0.5, "corazon_dragon": 0.1},
        descripcion="Ser ancestral y noble. Su sola presencia cerca de reinos es un presagio cósmico.",
    ),
}
