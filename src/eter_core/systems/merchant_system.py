from typing import Optional

from eter_core.components.player_component import PlayerComponent
from eter_core.domain.events import ComercioRealizadoEvent
from eter_core.domain.products import CATALOGO_PRODUCTOS
from eter_core.systems.pricing_system import PricingSystem
from eter_infrastructure.messaging.event_bus import EventBus


class MerchantSystem:
    """
    Compra y vende productos (materiales) con el jugador usando oro.

    Reglas de Dominio:
    - El precio depende de la ubicación (bioma) y de la oferta/demanda local.
    - El mercader COMPRA los materiales del jugador a un precio inferior al de
      mercado (su margen) y VENDE a un precio superior.
    """

    MARGEN_COMPRA: float = 0.6   # el mercader paga el 60% del precio de mercado
    MARGEN_VENTA: float = 1.4    # el mercader vende al 140% del precio de mercado

    @classmethod
    def precio_compra(cls, producto: str, bioma: str = "planicies", oferta: float = 100.0, demanda: float = 50.0) -> Optional[float]:
        """Precio al que el mercader compra una unidad del producto al jugador."""
        if producto not in CATALOGO_PRODUCTOS:
            return None
        mercado = PricingSystem.precio(producto, bioma, oferta, demanda)
        return round(mercado * cls.MARGEN_COMPRA, 1)

    @classmethod
    def precio_venta(cls, producto: str, bioma: str = "planicies", oferta: float = 100.0, demanda: float = 50.0) -> Optional[float]:
        """Precio al que el mercader vende una unidad del producto al jugador."""
        if producto not in CATALOGO_PRODUCTOS:
            return None
        mercado = PricingSystem.precio(producto, bioma, oferta, demanda)
        return round(mercado * cls.MARGEN_VENTA, 1)

    @classmethod
    def vender(
        cls,
        player: PlayerComponent,
        producto: str,
        cantidad: int = 1,
        bioma: str = "planicies",
        oferta: float = 100.0,
        demanda: float = 50.0,
    ) -> Optional[str]:
        """
        El jugador vende un material al mercader. Devuelve mensaje descriptivo
        o None si no puede venderlo.
        """
        if producto not in CATALOGO_PRODUCTOS or cantidad <= 0:
            return None
        if not player.tiene_material(producto) or player.materiales.get(producto, 0) < cantidad:
            return None
        precio = cls.precio_compra(producto, bioma, oferta, demanda)
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
    def comprar(
        cls,
        player: PlayerComponent,
        producto: str,
        cantidad: int = 1,
        bioma: str = "planicies",
        oferta: float = 100.0,
        demanda: float = 50.0,
    ) -> Optional[str]:
        """
        El jugador compra un producto al mercader. Devuelve mensaje descriptivo
        o None si no puede comprarlo (sin oro suficiente o producto inválido).
        """
        if producto not in CATALOGO_PRODUCTOS or cantidad <= 0:
            return None
        precio = cls.precio_venta(producto, bioma, oferta, demanda)
        if precio is None:
            return None
        total = precio * cantidad
        if player.oro < total:
            return None
        player.oro -= total
        player.dar_material(producto, cantidad)
        EventBus.publicar(ComercioRealizadoEvent("mercader", producto, total, producto))
        return f"Compras {cantidad} x {producto} por {total:.1f} de oro."
