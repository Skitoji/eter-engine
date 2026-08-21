from typing import Optional

from eter_core.components.player_component import PlayerComponent
from eter_core.domain.events import ComercioRealizadoEvent
from eter_core.domain.products import CATALOGO_PRODUCTOS
from eter_infrastructure.messaging.event_bus import EventBus


class MerchantSystem:
    """
    Compra y vende productos (materiales) con el jugador usando oro.

    Reglas de Dominio:
    - El mercader COMPRA los materiales del jugador a un precio de compra
      inferior al valor base (margen del mercader).
    - El mercader VENDE productos al jugador a un precio superior al valor base.
    - Solo comercia con productos del catálogo central.
    """

    MARGEN_COMPRA: float = 0.6   # el mercader paga el 60% del valor base
    MARGEN_VENTA: float = 1.4    # el mercader vende al 140% del valor base

    @classmethod
    def precio_compra(cls, producto: str) -> Optional[float]:
        """Precio al que el mercader compra una unidad del producto al jugador."""
        definicion = CATALOGO_PRODUCTOS.get(producto)
        if definicion is None:
            return None
        return round(definicion.valor_base * cls.MARGEN_COMPRA, 1)

    @classmethod
    def precio_venta(cls, producto: str) -> Optional[float]:
        """Precio al que el mercader vende una unidad del producto al jugador."""
        definicion = CATALOGO_PRODUCTOS.get(producto)
        if definicion is None:
            return None
        return round(definicion.valor_base * cls.MARGEN_VENTA, 1)

    @classmethod
    def vender(cls, player: PlayerComponent, producto: str, cantidad: int = 1) -> Optional[str]:
        """
        El jugador vende un material al mercader. Devuelve mensaje descriptivo
        o None si no puede venderlo.
        """
        if producto not in CATALOGO_PRODUCTOS or cantidad <= 0:
            return None
        if not player.tiene_material(producto) or player.materiales.get(producto, 0) < cantidad:
            return None
        precio = cls.precio_compra(producto)
        if precio is None:
            return None
        player.materiales[producto] -= cantidad
        if player.materiales[producto] <= 0:
            del player.materiales[producto]
        total = precio * cantidad
        player.oro += total
        EventBus.publicar(ComercioRealizadoEvent(producto, "mercader", total, producto))
        return f"Vendes {cantidad} x {producto} por {total:.1f} de oro."

    @classmethod
    def comprar(cls, player: PlayerComponent, producto: str, cantidad: int = 1) -> Optional[str]:
        """
        El jugador compra un producto al mercader. Devuelve mensaje descriptivo
        o None si no puede comprarlo (sin oro suficiente o producto inválido).
        """
        if producto not in CATALOGO_PRODUCTOS or cantidad <= 0:
            return None
        precio = cls.precio_venta(producto)
        if precio is None:
            return None
        total = precio * cantidad
        if player.oro < total:
            return None
        player.oro -= total
        player.dar_material(producto, cantidad)
        EventBus.publicar(ComercioRealizadoEvent("mercader", producto, total, producto))
        return f"Compras {cantidad} x {producto} por {total:.1f} de oro."
