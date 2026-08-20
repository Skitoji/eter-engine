# src/eter_core/engine.py
from typing import Dict, Type, Any
from eter_core.domain.types import EntityID
from eter_core.components.region_component import RegiónComponent
from eter_core.systems.faith_system import FaithSystem
from eter_core.components.economy_component import EconomyComponent
from eter_core.systems.economic_system import EconomicSystem

class EterEngine:
    def __init__(self):
        self.entidades_secuencia = 1
        
        # Almacén estructurado de componentes: {TipoComponente: {EntityID: InstanciaComponente}}
        self.componentes: Dict[Type, Dict[EntityID, Any]] = {}
        self.adyacencias: Dict[EntityID, set[EntityID]] = {}

    def crear_entidad(self) -> EntityID:
        """Genera un ID único para un nuevo elemento en el mundo."""
        nuevo_id = EntityID(self.entidades_secuencia)
        self.entidades_secuencia += 1
        return nuevo_id

    def agregar_componente(self, entidad: EntityID, componente: Any) -> None:
        """Vincula un componente de datos a un ID de entidad."""
        tipo = type(componente)
        if tipo not in self.componentes:
            self.componentes[tipo] = {}
        self.componentes[tipo][entidad] = componente

    def tick(self, delta_tiempo: float = 1.0) -> None:
        """El latido del mundo. Avanza el tiempo según los turnos del jugador."""
        # 1. Ejecutar el Sistema de Fe
        # Busca todas las entidades en el mundo que tengan el componente "Región"
        if RegiónComponent in self.componentes:
            for entity_id, region_comp in self.componentes[RegiónComponent].items():
                # El sistema procesa los datos y los muta según las reglas matemáticas
                FaithSystem.evaluar_region(entity_id, region_comp, delta_tiempo)
        if RegiónComponent in self.componentes and EconomyComponent in self.componentes:
            EconomicSystem.procesar(
                self.componentes[RegiónComponent],
                self.componentes[EconomyComponent],
                delta_tiempo,
            )
        # InfectionSystem.expandir(...)