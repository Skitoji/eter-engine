import random
from typing import Dict, Optional

from eter_core.components.stock_component import StockComponent
from eter_core.domain.products import CATALOGO_PRODUCTOS
from eter_core.domain.types import EntityID


class StockSystem:
    """
    Sistema de stock: simula la oferta y demanda fluctuante de cada provincia.

    Reglas de Dominio:
    - El stock inicial se deriva de la geografía: los productos nativos del
      bioma tienen más oferta y menos demanda; los foráneos, al revés.
    - Cada turno el stock fluctúa ligeramente (reabastecimiento y consumo).
    - El mercader y el herrero usan este stock para fijar precios reales.
    """

    OFERTA_NATIVA: float = 150.0
    OFERTA_FORANEA: float = 40.0
    DEMANDA_NATIVA: float = 30.0
    DEMANDA_FORANEA: float = 80.0
    FLUCTUACION: float = 0.15  # ±15% por turno

    @classmethod
    def crear_stock(cls, bioma: str) -> StockComponent:
        """Genera el stock inicial de una provincia según su bioma."""
        stock = StockComponent()
        for producto, definicion in CATALOGO_PRODUCTOS.items():
            es_nativo = bioma in definicion.geografias_nativas
            if es_nativo:
                stock.oferta[producto] = cls.OFERTA_NATIVA
                stock.demanda[producto] = cls.DEMANDA_NATIVA
            elif definicion.geografias_nativas:
                stock.oferta[producto] = cls.OFERTA_FORANEA
                stock.demanda[producto] = cls.DEMANDA_FORANEA
            else:
                # Sin geografía: oferta neutra
                stock.oferta[producto] = 80.0
                stock.demanda[producto] = 50.0
        return stock

    @classmethod
    def fluctuar(
        cls,
        stock: StockComponent,
        rng: Optional[random.Random] = None,
    ) -> None:
        """Ajusta la oferta y demanda ligeramente para simular el mercado vivo."""
        randomizer = rng or random
        for producto in stock.oferta:
            factor = 1.0 + (randomizer.random() - 0.5) * 2 * cls.FLUCTUACION
            stock.oferta[producto] = max(1.0, stock.oferta[producto] * factor)
        for producto in stock.demanda:
            factor = 1.0 + (randomizer.random() - 0.5) * 2 * cls.FLUCTUACION
            stock.demanda[producto] = max(1.0, stock.demanda[producto] * factor)

    @classmethod
    def registrar_compra(cls, stock: StockComponent, producto: str, cantidad: int = 1) -> None:
        """El jugador compra: baja la oferta y sube la demanda (escasez)."""
        if producto in stock.oferta:
            stock.oferta[producto] = max(0.0, stock.oferta[producto] - cantidad)
        if producto in stock.demanda:
            stock.demanda[producto] += cantidad

    @classmethod
    def registrar_venta(cls, stock: StockComponent, producto: str, cantidad: int = 1) -> None:
        """El jugador vende: sube la oferta y baja la demanda (abundancia)."""
        if producto in stock.oferta:
            stock.oferta[producto] += cantidad
        if producto in stock.demanda:
            stock.demanda[producto] = max(0.0, stock.demanda[producto] - cantidad)
