# src/eter_core/systems/faith_system.py
from eter_core.components.region_component import RegiónComponent
from eter_core.domain.types import FervorReligioso, NivelInfeccion, FaccionTipo, EntityID
from eter_core.domain.events import HegemoniaIglesiaRotasEvent
from eter_infrastructure.messaging.event_bus import EventBus

class FaithSystem:
    """
    Sistema que procesa la dinámica social entre la Santa Iglesia,
    la infección demoníaca y la aparición de Magos Oscuros.

    Regla de Dominio:
    A menor fervor religioso y mayor infección demoníaca, la tasa de
    aparición de Magos Oscuros aumenta exponencialmente. Si el fervor
    cae por debajo de un umbral crítico, la influencia de la Santa Iglesia se fractura.
    """

    UMBRAL_CRITICO_FE: float = 0.30
    COEFICIENTE_CULTISMO: float = 0.05

    @classmethod
    def evaluar_region(cls, region_id: EntityID, region: RegiónComponent, delta_tiempo: float) -> None:
        # 1. La infección reduce paulatinamente el fervor si la Iglesia no la erradica
        degradacion_fe = region.infeccion.valor * 0.02 * delta_tiempo
        nuevo_fervor_val = max(0.0, region.fervor.valor - degradacion_fe)
        region.fervor = FervorReligioso(nuevo_fervor_val)

        # 2. Cálculo de surgimiento de Magos Oscuros / Cultos
        factor_vulnerabilidad = (1.0 - region.fervor.valor)
        factor_corrupcion = region.infeccion.valor
        
        region.tasa_magos_oscuros = (factor_vulnerabilidad ** 2) * factor_corrupcion * cls.COEFICIENTE_CULTISMO

        # 3. Quiebre de la fe y pérdida de hegemonía de la Santa Iglesia
        if region.fervor.valor < cls.UMBRAL_CRITICO_FE and region.faccion_dominante == FaccionTipo.SANTA_IGLESIA:
            EventBus.publicar(
                HegemoniaIglesiaRotasEvent(
                    region_id=region_id,
                    nombre_region=region.nombre,
                    faccion_anterior=region.faccion_dominante
                )
            )