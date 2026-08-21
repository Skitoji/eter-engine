import random
from typing import Dict, Optional

from eter_core.components.enemy_component import EnemyComponent
from eter_core.components.region_component import RegiónComponent
from eter_core.components.trade_component import TradeComponent
from eter_core.domain.events import MonstruoAvistadoEvent
from eter_core.domain.monsters import CATALOGO_MONSTRUOS, TipoMonstruo
from eter_core.domain.types import EntityID, FaccionTipo
from eter_infrastructure.messaging.event_bus import EventBus


class MonsterSpawnSystem:
    """
    Genera monstruos salvajes en las regiones de forma emergente, ligada al
    estado del mundo (bioma, infección y fe). Esto hace que el mundo esté vivo
    incluso sin el jugador.

    Reglas de Dominio:
    - Cada bioma tiene una fauna base (bestias y humanoides tribales).
    - La infección demoníaca alta atrae corruptos y aberraciones.
    - El colapso de la fe (facción cultista) atrae no-muertos.
    - La probabilidad de spawn crece con la infección de la región.
    """

    # Monstruos base por bioma (clave del TradeComponent.bioma)
    FAUNA_POR_BIOMA: Dict[str, list[str]] = {
        "planicies": ["goblin", "lobo_gigante"],
        "montanas": ["orco", "minotauro"],
        "valles": ["goblin", "slime"],
        "costas": ["hombre_lagarto", "slime"],
    }

    PROBABILIDAD_BASE: float = 0.10
    MAX_MONSTRUOS_POR_REGION: int = 20

    @classmethod
    def _pool_por_estado(cls, bioma: str, infeccion: float, faccion: FaccionTipo) -> list[str]:
        """Construye el pool de monstruos posibles según bioma, infección y fe."""
        pool: list[str] = list(cls.FAUNA_POR_BIOMA.get(bioma, ["goblin"]))

        if infeccion > 0.45:
            pool += ["cultista", "quimera"]
        if faccion == FaccionTipo.FACCIÓN_CULTISTA_OSCURA:
            pool += ["esqueleto", "zombi", "espectro"]

        # En regiones muy infectadas también pueden aparecer bestias mitológicas.
        if infeccion > 0.70:
            pool += ["wyvern", "aracne"]

        return pool

    @classmethod
    def procesar(
        cls,
        regiones: Dict[EntityID, RegiónComponent],
        enemigos: Dict[EntityID, EnemyComponent],
        mercados: Dict[EntityID, TradeComponent],
        delta_tiempo: float = 1.0,
        rng: Optional[random.Random] = None,
    ) -> None:
        randomizer = rng or random
        for entity_id, region in regiones.items():
            mercado = mercados.get(entity_id)
            bioma = mercado.bioma if mercado else "planicies"
            pool = cls._pool_por_estado(bioma, region.infeccion.valor, region.faccion_dominante)
            if not pool:
                continue

            enemigo = enemigos.get(entity_id)
            if enemigo is None:
                continue
            if sum(enemigo.monstruos.values()) >= cls.MAX_MONSTRUOS_POR_REGION:
                continue

            # La infección acelera la aparición de monstruos.
            probabilidad = cls.PROBABILIDAD_BASE * (1.0 + region.infeccion.valor) * delta_tiempo
            if randomizer.random() >= probabilidad:
                continue

            elegido = randomizer.choice(pool)
            if elegido not in CATALOGO_MONSTRUOS:
                continue
            enemigo.monstruos[elegido] = enemigo.monstruos.get(elegido, 0) + 1
            EventBus.publicar(
                MonstruoAvistadoEvent(
                    region_id=entity_id,
                    nombre_region=region.nombre,
                    monstruo=elegido,
                    total_monstruos=sum(enemigo.monstruos.values()),
                )
            )
