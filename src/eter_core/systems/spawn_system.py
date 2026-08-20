import random
from typing import Any, Dict, Iterable, Optional, Tuple

from eter_core.components.player_component import PlayerComponent


class SpawnSystem:
    """Selecciona una celda terrestre y devuelve su provincia Azgaar."""

    POTENCIALES = {
        "Tanque": {"vida_maxima": 140, "mana_maximo": 30, "fuerza": 14, "inteligencia": 7, "tenacidad": 16},
        "Mago": {"vida_maxima": 80, "mana_maximo": 120, "fuerza": 7, "inteligencia": 16, "tenacidad": 8},
        "Caballero": {"vida_maxima": 110, "mana_maximo": 55, "fuerza": 12, "inteligencia": 10, "tenacidad": 12},
        "Asesino": {"vida_maxima": 90, "mana_maximo": 45, "fuerza": 15, "inteligencia": 12, "tenacidad": 7},
    }

    @classmethod
    def celdas_terrestres(cls, raw_data: Dict[str, Any], valid_province_ids: Iterable[int]) -> list[Tuple[int, int]]:
        valid_ids = set(valid_province_ids)
        cells = raw_data.get("pack", {}).get("cells", [])
        return [
            (int(cell["i"]), int(cell["province"]))
            for cell in cells
            if isinstance(cell, dict)
            and cell.get("province") in valid_ids
            and cell.get("state", 0) != 0
        ]

    @classmethod
    def crear_jugador(
        cls,
        raw_data: Dict[str, Any],
        valid_province_ids: Iterable[int],
        rng: Optional[random.Random] = None,
        potencial: Optional[str] = None,
    ) -> PlayerComponent:
        randomizer = rng or random.Random()
        land_cells = cls.celdas_terrestres(raw_data, valid_province_ids)
        if not land_cells:
            raise ValueError("El mapa no contiene celdas terrestres validas para el spawn.")
        cell_id, province_id = randomizer.choice(land_cells)
        chosen_potential = potencial or randomizer.choice(list(cls.POTENCIALES))
        if chosen_potential not in cls.POTENCIALES:
            raise ValueError(f"Potencial de nacimiento desconocido: {chosen_potential}")
        stats = cls.POTENCIALES[chosen_potential]
        mark = randomizer.choice(["hombro", "pecho", "espalda", "antebrazo", "nuca"])
        return PlayerComponent(
            vida=stats["vida_maxima"],
            vida_maxima=stats["vida_maxima"],
            mana=stats["mana_maximo"],
            mana_maximo=stats["mana_maximo"],
            fuerza=stats["fuerza"],
            inteligencia=stats["inteligencia"],
            tenacidad=stats["tenacidad"],
            potencial_nacimiento=chosen_potential,
            marca_de_la_estrella=mark,
            celda_actual=cell_id,
            provincia_actual=province_id,
        )
