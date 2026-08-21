from math import hypot

from eter_core.components.trade_component import TradeComponent


class TravelSystem:
    """
    Sistema de distancias y viajes.

    Reglas de Dominio:
    - Viajar entre provincias cuesta estamina según la distancia real entre ellas.
    - Viajar entre provincias del mismo país es más barato que cruzar fronteras
      (no es lo mismo ciudad↔ciudad que país↔país).
    """

    ESTAMINA_BASE: float = 10.0
    ESTAMINA_POR_KM: float = 0.05
    RECARGO_CRUCE_FRONTERA: float = 15.0  # estamina extra por cruzar a otro estado

    @classmethod
    def distancia_km(cls, origen: TradeComponent, destino: TradeComponent) -> float:
        """Distancia euclidiana entre dos mercados (coordenadas)."""
        return hypot(
            origen.coordenadas[0] - destino.coordenadas[0],
            origen.coordenadas[1] - destino.coordenadas[1],
        )

    @classmethod
    def coste_viaje(
        cls,
        origen: TradeComponent,
        destino: TradeComponent,
        mismo_estado: bool = True,
    ) -> float:
        """
        Coste en estamina para viajar entre dos provincias.
        A mayor distancia, mayor coste; cruzar frontera añade recargo.
        """
        distancia = cls.distancia_km(origen, destino)
        coste = cls.ESTAMINA_BASE + distancia * cls.ESTAMINA_POR_KM
        if not mismo_estado:
            coste += cls.RECARGO_CRUCE_FRONTERA
        return round(coste, 1)

    @classmethod
    def dias_viaje(cls, origen: TradeComponent, destino: TradeComponent) -> int:
        """Días que tarda un viaje (para el bucle temporal)."""
        distancia = cls.distancia_km(origen, destino)
        return max(1, round(distancia / 30.0))
