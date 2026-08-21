from typing import Dict, Optional

from eter_core.components.player_component import PlayerComponent
from eter_core.domain.items import CATALOGO_OBJETOS, ItemDef, TipoObjeto


class ItemSystem:
    """
    Sistema de objetos: entrega, consume y aplica los efectos de los ítems
    definidos en el catálogo central (domain/items.py).

    Regla de Dominio:
    - Los objetos CONSUMIBLES se agotan al usarse y aplican sus efectos de stats.
    - Las HERRAMIENTAS se usan sin consumirse (ej. la brújula).
    - Un efecto de curación no se aplica si el stat ya está al máximo
      (no puedes comer una ración con la vida llena).
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
        o None si el objeto no existe, no está en el inventario o no puede usarse
        (por ejemplo, curar con la vida ya llena).
        """
        definicion = cls.definicion(nombre)
        if definicion is None:
            return None
        if not player.tiene(nombre):
            return None

        efectos = definicion.efectos

        # Regla: no aplicar curación/recuperación sobre un stat ya lleno.
        if definicion.tipo == TipoObjeto.CONSUMIBLE and efectos:
            if "vida" in efectos and player.vida >= player.vida_maxima:
                return None
            if "mana" in efectos and player.mana >= player.mana_maximo:
                return None
            if "estamina" in efectos and player.estamina >= player.estamina_maxima:
                return None

        # Aplicar efectos antes de consumir, por claridad (o consumir primero da igual).
        player.aplicar_efectos(efectos)

        # Consumir solo si es consumible.
        if definicion.tipo == TipoObjeto.CONSUMIBLE:
            player.consumir(nombre)

        return definicion.descripcion
