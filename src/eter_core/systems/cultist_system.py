import random
from typing import Dict, Optional

from eter_core.components.enemy_component import EnemyComponent
from eter_core.components.region_component import RegiónComponent
from eter_core.domain.events import CultistasSurgidosEvent
from eter_core.domain.types import EntityID
from eter_infrastructure.messaging.event_bus import EventBus


class CultistSystem:
    """
    Consume la tasa de magos oscuros calculada por FaithSystem y materializa
    la amenaza en forma de cultistas presentes en cada región.

    Regla de Dominio:
    Cada turno, una región tiene probabilidad `tasa_magos_oscuros` de que surja
    un nuevo cultista. La tasa la produce FaithSystem como consecuencia de la
    pérdida de fe y el avance de la infección: a más desesperación, más cultos.
    """

    UMBRAL_TASA: float = 0.001          # Por debajo de esta tasa no se intenta spawn
    MAX_ENEMIGOS_POR_REGION: int = 25   # Límite para evitar acumulación infinita

    @classmethod
    def procesar(
        cls,
        regiones: Dict[EntityID, RegiónComponent],
        enemigos: Dict[EntityID, EnemyComponent],
        delta_tiempo: float = 1.0,
        rng: Optional[random.Random] = None,
    ) -> None:
        randomizer = rng or random
        for entity_id, region in regiones.items():
            tasa = region.tasa_magos_oscuros
            if tasa <= cls.UMBRAL_TASA:
                continue
            if randomizer.random() >= tasa * delta_tiempo:
                continue
            enemigo = enemigos.get(entity_id)
            if enemigo is None:
                continue
            if enemigo.magos_oscuros + enemigo.cultistas >= cls.MAX_ENEMIGOS_POR_REGION:
                continue
            enemigo.cultistas += 1
            EventBus.publicar(
                CultistasSurgidosEvent(
                    region_id=entity_id,
                    nombre_region=region.nombre,
                    total_cultistas=enemigo.cultistas,
                )
            )
