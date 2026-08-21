from typing import Dict, Optional

from eter_core.components.player_component import PlayerComponent
from eter_core.domain.items import CATALOGO_OBJETOS, ItemDef, TipoObjeto


class ItemSystem:
    """
    Sistema de objetos: entrega, consume, equipa y aplica efectos.

    Regla de Dominio:
    - CONSUMIBLE: se agota al usarse y aplica sus efectos de stats.
    - HERRAMIENTA: se usa sin consumirse (ej. la brújula).
    - EQUIPABLE: ocupa un slot y otorga un bono pasivo mientras esté equipado.
    - Un efecto de curación no se aplica si el stat ya está al máximo.
    """

    @classmethod
    def definicion(cls, nombre: str) -> Optional[ItemDef]:
        """Devuelve la definición de un objeto por su clave del catálogo, o None."""
        return CATALOGO_OBJETOS.get(nombre)

    @classmethod
    def dar_objeto(cls, player: PlayerComponent, nombre: str, cantidad: int = 1) -> bool:
        """Añade un objeto al inventario del jugador. Devuelve True si se entregó."""
        if nombre not in CATALOGO_OBJETOS or cantidad <= 0:
            return False
        player.inventario[nombre] = player.inventario.get(nombre, 0) + cantidad
        return True

    @classmethod
    def usar_objeto(cls, player: PlayerComponent, nombre: str) -> Optional[str]:
        """
        Intenta usar un objeto. Devuelve un mensaje descriptivo del resultado,
        o None si no puede usarse (no existe, no está en el inventario, o el
        stat objetivo ya está al máximo).
        """
        definicion = cls.definicion(nombre)
        if definicion is None:
            return None
        if not player.tiene(nombre):
            return None

        efectos = definicion.efectos

        # Regla: solo se bloquea el uso si TODOS los efectos del objeto ya están
        # al máximo. Si al menos uno puede aplicarse (p. ej. curar vida aunque ya
        # estés saciado), el objeto es usable.
        if definicion.tipo == TipoObjeto.CONSUMIBLE and efectos:
            stats_llenos = {
                "vida": player.vida >= player.vida_maxima,
                "mana": player.mana >= player.mana_maximo,
                "estamina": player.estamina >= player.estamina_maxima,
                "hambre": player.hambre >= 100,
            }
            if all(stats_llenos.get(stat, False) for stat in efectos):
                return None

        player.aplicar_efectos(efectos)

        if definicion.tipo == TipoObjeto.CONSUMIBLE:
            player.consumir(nombre)

        return definicion.descripcion

    @classmethod
    def equipar(cls, player: PlayerComponent, nombre: str) -> Optional[str]:
        """
        Equipa un objeto EQUIPABLE en su slot correspondiente. Devuelve un
        mensaje descriptivo o None si no puede equiparse.
        """
        definicion = cls.definicion(nombre)
        if definicion is None or definicion.tipo != TipoObjeto.EQUIPABLE:
            return None
        if not player.tiene(nombre) or definicion.slot is None:
            return None
        anterior = player.equipamiento.get(definicion.slot)
        player.equipar(definicion.slot, nombre)
        if anterior and anterior != nombre:
            return f"Equipas {definicion.nombre} en {definicion.slot} (reemplazas {anterior})."
        return f"Equipas {definicion.nombre} en {definicion.slot}."

    @classmethod
    def desequipar(cls, player: PlayerComponent, slot: str) -> Optional[str]:
        """Retira el objeto equipado en un slot. Devuelve mensaje o None."""
        anterior = player.desequipar(slot)
        if anterior is None:
            return None
        return f"Retiras {anterior} del slot {slot}."

    @classmethod
    def bonos_equipados(cls, player: PlayerComponent) -> Dict[str, float]:
        """Suma los efectos pasivos de todo el equipamiento del jugador."""
        total: Dict[str, float] = {}
        for nombre in player.equipamiento.values():
            definicion = cls.definicion(nombre)
            if definicion is None:
                continue
            for stat, valor in definicion.efectos.items():
                total[stat] = total.get(stat, 0.0) + valor
        return total
