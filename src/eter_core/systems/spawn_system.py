import random
from typing import Any, Dict, Iterable, Optional, Tuple

from eter_core.components.player_component import PlayerComponent
from eter_core.domain.archetypes import CATALOGO_ARQUETIPOS


class SpawnSystem:
    """Selecciona una celda terrestre y crea al Hijo de la Luz con un arquetipo de nacimiento."""

    @classmethod
    def arquetipos_disponibles(cls) -> list[str]:
        """Devuelve las claves de los arquetipos en orden estable."""
        return list(CATALOGO_ARQUETIPOS)

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
        arquetipo: Optional[str] = None,
    ) -> PlayerComponent:
        randomizer = rng or random.Random()
        land_cells = cls.celdas_terrestres(raw_data, valid_province_ids)
        if not land_cells:
            raise ValueError("El mapa no contiene celdas terrestres validas para el spawn.")
        cell_id, province_id = randomizer.choice(land_cells)

        chosen_archetype = arquetipo or randomizer.choice(cls.arquetipos_disponibles())
        if chosen_archetype not in CATALOGO_ARQUETIPOS:
            raise ValueError(f"Arquetipo de nacimiento desconocido: {chosen_archetype}")
        stats = CATALOGO_ARQUETIPOS[chosen_archetype]

        mark = randomizer.choice(["hombro", "pecho", "espalda", "antebrazo", "nuca"])
        return PlayerComponent(
            vida=stats.vida_maxima,
            vida_maxima=stats.vida_maxima,
            mana=stats.mana_maximo,
            mana_maximo=stats.mana_maximo,
            fuerza=stats.fuerza,
            inteligencia=stats.inteligencia,
            estamina=stats.estamina_maxima,
            estamina_maxima=stats.estamina_maxima,
            tenacidad=stats.tenacidad,
            bonus_critico=stats.bonus_critico,
            potencial_nacimiento=chosen_archetype,
            marca_de_la_estrella=mark,
            celda_actual=cell_id,
            provincia_actual=province_id,
        )
