from math import hypot
from typing import Dict, Set, Tuple

from eter_core.components.economy_component import EconomyComponent
from eter_core.components.region_component import RegiónComponent
from eter_core.components.trade_component import TradeComponent
from eter_core.domain.events import (
    ComercioRealizadoEvent,
    InversionRealizadaEvent,
    RiquezaGeneradaEvent,
)
from eter_core.domain.types import EntityID, FervorReligioso, NivelInfeccion
from eter_infrastructure.messaging.event_bus import EventBus


class EconomicSystem:
    """Genera riqueza y aplica acciones economicas sin conocer la infraestructura."""

    COSTE_INVERSION = 100.0
    BONO_PRODUCCION_COMERCIO = 0.10
    VELOCIDAD_COMERCIAL = 35.0
    PRODUCTOS_POR_GEOGRAFIA = {
        "costas": ["pescado", "sal", "perlas"],
        "planicies": ["trigo", "ganado", "textiles"],
        "montanas": ["minerales", "hierro", "piedra"],
        "valles": ["trigo", "ganado", "textiles"],
    }
    PRECIOS_BASE = {
        "pescado": 12.0, "sal": 18.0, "perlas": 80.0,
        "trigo": 10.0, "ganado": 35.0, "textiles": 28.0,
        "minerales": 30.0, "hierro": 45.0, "piedra": 15.0,
    }

    @classmethod
    def clasificar_geografia(cls, bioma: str, coordenadas: Tuple[float, float]) -> str:
        value = bioma.casefold() if isinstance(bioma, str) else ""
        if any(token in value for token in ("coast", "sea", "shore", "coastline")):
            return "costas"
        if any(token in value for token in ("mountain", "hill", "highland")):
            return "montanas"
        if any(token in value for token in ("valley", "river")):
            return "valles"
        if isinstance(bioma, int) and bioma in (1, 2, 3, 4, 5):
            return "montanas"
        if isinstance(bioma, int) and bioma in (10, 11, 12, 13, 14):
            return "costas"
        return "planicies"

    @classmethod
    def crear_mercado(cls, bioma: str, coordenadas: Tuple[float, float], tiene_ciudad: bool) -> TradeComponent:
        geografia = cls.clasificar_geografia(bioma, coordenadas)
        productos = cls.PRODUCTOS_POR_GEOGRAFIA[geografia]
        multiplicador = 1.5 if tiene_ciudad else 1.0
        return TradeComponent(
            bioma=geografia,
            productos=list(productos),
            oferta={producto: 100.0 * multiplicador for producto in productos},
            demanda={producto: 50.0 for producto in productos},
            coordenadas=coordenadas,
            tiene_ciudad=tiene_ciudad,
        )

    @staticmethod
    def distancia(origen: TradeComponent, destino: TradeComponent) -> float:
        return hypot(origen.coordenadas[0] - destino.coordenadas[0], origen.coordenadas[1] - destino.coordenadas[1])

    @classmethod
    def calcular_precio(
        cls,
        producto: str,
        origen: TradeComponent,
        destino: TradeComponent,
        region_origen: RegiónComponent,
        region_destino: RegiónComponent,
    ) -> Tuple[float, int, float]:
        if producto not in origen.productos:
            raise ValueError(f"{producto} no se produce en la provincia de origen.")
        distance = cls.distancia(origen, destino)
        days = max(1, round(distance / cls.VELOCIDAD_COMERCIAL))
        offer = max(1.0, origen.oferta.get(producto, 1.0))
        demand = max(1.0, destino.demanda.get(producto, 1.0))
        danger = (region_origen.infeccion.valor + region_destino.infeccion.valor) / 2
        faith_penalty = (1.0 - region_origen.fervor.valor + 1.0 - region_destino.fervor.valor) / 2
        risk = danger * 0.75 + faith_penalty * 0.25
        price = cls.PRECIOS_BASE[producto] * (1.0 + demand / offer + distance / 100.0 + risk)
        return price, days, distance

    @classmethod
    def procesar(
        cls,
        regiones: Dict[EntityID, RegiónComponent],
        economias: Dict[EntityID, EconomyComponent],
        delta_tiempo: float = 1.0,
    ) -> None:
        for entity_id, region in regiones.items():
            economy = economias.get(entity_id)
            if economy is None:
                continue
            factor_social = 0.5 + (region.fervor.valor * 0.5)
            factor_infeccion = max(0.0, 1.0 - region.infeccion.valor)
            riqueza = economy.produccion * factor_social * factor_infeccion * delta_tiempo
            economy.oro += riqueza
            EventBus.publicar(RiquezaGeneradaEvent(entity_id, region.nombre, riqueza))

    @classmethod
    def invertir(cls, region: RegiónComponent, economy: EconomyComponent, entity_id: EntityID) -> bool:
        if economy.oro < cls.COSTE_INVERSION:
            return False
        economy.oro -= cls.COSTE_INVERSION
        region.infeccion = NivelInfeccion(max(0.0, region.infeccion.valor - 0.10))
        region.fervor = FervorReligioso(min(1.0, region.fervor.valor + 0.05))
        economy.nivel_desarrollo += 1
        EventBus.publicar(InversionRealizadaEvent(entity_id, region.nombre, cls.COSTE_INVERSION))
        return True

    @classmethod
    def comerciar(
        cls,
        origen_id: EntityID,
        destino_id: EntityID,
        economias: Dict[EntityID, EconomyComponent],
        adyacencias: Dict[EntityID, Set[EntityID]],
    ) -> float:
        if destino_id not in adyacencias.get(origen_id, set()):
            return 0.0
        origen = economias[origen_id]
        destino = economias[destino_id]
        flujo = min(origen.oro, max(1.0, origen.produccion * cls.BONO_PRODUCCION_COMERCIO))
        origen.oro -= flujo
        destino.oro += flujo
        origen.comercio_activo = True
        destino.comercio_activo = True
        EventBus.publicar(ComercioRealizadoEvent(origen_id, destino_id, flujo))
        return flujo

    @classmethod
    def comerciar_producto(
        cls,
        origen_id: EntityID,
        destino_id: EntityID,
        producto: str,
        economias: Dict[EntityID, EconomyComponent],
        mercados: Dict[EntityID, TradeComponent],
        regiones: Dict[EntityID, RegiónComponent],
        adyacencias: Dict[EntityID, Set[EntityID]],
    ) -> Tuple[float, int, float]:
        if destino_id not in adyacencias.get(origen_id, set()):
            raise ValueError("Las provincias no tienen una ruta terrestre adyacente.")
        price, days, distance = cls.calcular_precio(
            producto, mercados[origen_id], mercados[destino_id], regiones[origen_id], regiones[destino_id]
        )
        if mercados[origen_id].oferta.get(producto, 0.0) <= 0:
            raise ValueError("No hay oferta disponible para ese producto.")
        mercados[origen_id].oferta[producto] -= 1.0
        mercados[destino_id].demanda[producto] = max(0.0, mercados[destino_id].demanda.get(producto, 0.0) - 1.0)
        economias[origen_id].oro += price
        economias[destino_id].oro = max(0.0, economias[destino_id].oro - price * 0.05)
        economias[origen_id].comercio_activo = True
        economias[destino_id].comercio_activo = True
        EventBus.publicar(ComercioRealizadoEvent(origen_id, destino_id, price, producto, distance, days, price))
        return price, days, distance