# src/eter_core/engine.py
from typing import Dict, Type, Any
from eter_core.domain.types import EntityID
from eter_core.components.region_component import RegiónComponent
from eter_core.systems.faith_system import FaithSystem
from eter_core.components.economy_component import EconomyComponent
from eter_core.components.enemy_component import EnemyComponent
from eter_core.components.trade_component import TradeComponent
from eter_core.components.stock_component import StockComponent
from eter_core.systems.economic_system import EconomicSystem
from eter_core.systems.infection_system import InfectionSystem
from eter_core.systems.cultist_system import CultistSystem
from eter_core.systems.monster_spawn_system import MonsterSpawnSystem
from eter_core.systems.stock_system import StockSystem

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
        # 1. Sistema de Fe: degrada el fervor y calcula la tasa de magos oscuros
        if RegiónComponent in self.componentes:
            for entity_id, region_comp in self.componentes[RegiónComponent].items():
                FaithSystem.evaluar_region(entity_id, region_comp, delta_tiempo)

        # 2. Sistema de Infección: propaga la plaga entre provincias adyacentes
        if RegiónComponent in self.componentes:
            InfectionSystem.expandir(
                self.componentes[RegiónComponent],
                self.adyacencias,
                delta_tiempo,
            )

        # 3. Sistema Económico: genera riqueza por turno
        if RegiónComponent in self.componentes and EconomyComponent in self.componentes:
            EconomicSystem.procesar(
                self.componentes[RegiónComponent],
                self.componentes[EconomyComponent],
                delta_tiempo,
            )

        # 4. Sistema de Cultistas: materializa la tasa de magos oscuros en enemigos
        if RegiónComponent in self.componentes and EnemyComponent in self.componentes:
            CultistSystem.procesar(
                self.componentes[RegiónComponent],
                self.componentes[EnemyComponent],
                delta_tiempo,
            )

        # 5. Sistema de Spawn de Monstruos: fauna salvaje ligada a bioma/infección/fe
        if (
            RegiónComponent in self.componentes
            and EnemyComponent in self.componentes
            and TradeComponent in self.componentes
        ):
            MonsterSpawnSystem.procesar(
                self.componentes[RegiónComponent],
                self.componentes[EnemyComponent],
                self.componentes[TradeComponent],
                delta_tiempo,
            )

        # 6. Sistema de Stock: la oferta/demanda del mercado fluctúa
        if StockComponent in self.componentes:
            for stock in self.componentes[StockComponent].values():
                StockSystem.fluctuar(stock)
