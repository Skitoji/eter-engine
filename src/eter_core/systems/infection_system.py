from typing import Dict, Set

from eter_core.components.region_component import RegiónComponent
from eter_core.domain.events import InfeccionExtendidaEvent
from eter_core.domain.types import EntityID, NivelInfeccion
from eter_infrastructure.messaging.event_bus import EventBus


class InfectionSystem:
    """
    Sistema que propaga la Infección Demoníaca entre provincias adyacentes.

    Regla de Dominio:
    Una provincia con infección superior a UMBRAL_PROPAGACION "contagia" a sus
    vecinas una fracción de su nivel por turno. La plaga no se genera de la nada:
    avanza geográficamente por el grafo de adyacencias.
    """

    UMBRAL_PROPAGACION: float = 0.40  # Por debajo de este nivel, la plaga no se expande
    TASA_PROPAGACION: float = 0.05    # Fracción del nivel que se filtra a cada vecino por turno

    @classmethod
    def expandir(
        cls,
        regiones: Dict[EntityID, RegiónComponent],
        adyacencias: Dict[EntityID, Set[EntityID]],
        delta_tiempo: float = 1.0,
    ) -> None:
        # 1. Snapshot de niveles para que el resultado sea determinista
        #    (no depende del orden de iteración ni de mutaciones parciales).
        niveles: Dict[EntityID, float] = {eid: r.infeccion.valor for eid, r in regiones.items()}
        deltas: Dict[EntityID, float] = {eid: 0.0 for eid in regiones}
        origen_principal: Dict[EntityID, EntityID] = {}

        # 2. Acumular el contagio que cada provincia recibe de sus vecinas infectadas
        for origen_id, region in regiones.items():
            nivel = niveles[origen_id]
            if nivel < cls.UMBRAL_PROPAGACION:
                continue
            for destino_id in adyacencias.get(origen_id, set()):
                if destino_id not in regiones or destino_id == origen_id:
                    continue
                incremento = nivel * cls.TASA_PROPAGACION * delta_tiempo
                deltas[destino_id] += incremento
                actual = origen_principal.get(destino_id)
                if actual is None or niveles[actual] < nivel:
                    origen_principal[destino_id] = origen_id

        # 3. Aplicar los deltas y emitir eventos
        for destino_id, delta in deltas.items():
            if delta <= 0.0:
                continue
            region = regiones[destino_id]
            nuevo = min(1.0, niveles[destino_id] + delta)
            region.infeccion = NivelInfeccion(nuevo)
            EventBus.publicar(
                InfeccionExtendidaEvent(
                    origen_id=origen_principal[destino_id],
                    destino_id=destino_id,
                    nuevo_nivel_infeccion=nuevo,
                )
            )
