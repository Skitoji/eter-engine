from typing import Dict, Optional

from eter_core.components.player_component import PlayerComponent
from eter_core.domain.armor_sets import CATALOGO_SETS, SetRopaDef


class SetSystem:
    """
    Sistema de sets de armadura: detecta sets completos y otorga sus buffs.

    Reglas de Dominio:
    - Un set se considera completo cuando el jugador lleva equipadas TODAS sus piezas.
    - Llevar el set completo otorga un bonus adicional de stats (buff pasivo).
    - Solo se puede tener un set completo por clase/nivel, pero se suman si hay varios.
    """

    @classmethod
    def sets_completos(cls, player: PlayerComponent) -> Dict[str, SetRopaDef]:
        """
        Devuelve los sets completos equipados, indexados por su clave.
        """
        equipadas = set(player.equipamiento.values())
        completos: Dict[str, SetRopaDef] = {}
        for clave, set_def in CATALOGO_SETS.items():
            if all(pieza in equipadas for pieza in set_def.piezas):
                completos[clave] = set_def
        return completos

    @classmethod
    def bonus_sets(cls, player: PlayerComponent) -> Dict[str, float]:
        """Suma los buffs de todos los sets completos equipados."""
        total: Dict[str, float] = {}
        for set_def in cls.sets_completos(player).values():
            for stat, valor in set_def.bonus_set.items():
                total[stat] = total.get(stat, 0.0) + valor
        return total

    @classmethod
    def conjunto_actual(cls, player: PlayerComponent, slot: str) -> Optional[str]:
        """Devuelve el id de conjunto de la pieza equipada en un slot, o None."""
        pieza = player.equipamiento.get(slot)
        if pieza is None:
            return None
        from eter_core.domain.items import CATALOGO_OBJETOS
        item = CATALOGO_OBJETOS.get(pieza)
        return item.conjunto if item else None
