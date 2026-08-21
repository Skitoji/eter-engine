import os
import random
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))
sys.path.insert(0, os.path.abspath("."))

from eter_core.components.economy_component import EconomyComponent
from eter_core.components.region_component import RegiónComponent
from eter_core.systems.economic_system import EconomicSystem
from eter_core.systems.spawn_system import SpawnSystem
from eter_core.components.trade_component import TradeComponent
from main import cargar_mundo


class EconomyIntegrationTests(unittest.TestCase):
    def test_map_creates_expected_entities(self) -> None:
        engine, state_entities, province_entities, _ = cargar_mundo()
        self.assertEqual(len(state_entities), 18)
        self.assertEqual(len(province_entities), 252)
        self.assertEqual(len(engine.componentes[RegiónComponent]), 252)
        self.assertEqual(len(engine.componentes[EconomyComponent]), 270)

    def test_tick_generates_wealth(self) -> None:
        engine, _, province_entities, _ = cargar_mundo()
        entity_id = next(iter(province_entities.values()))
        economy = engine.componentes[EconomyComponent][entity_id]
        initial_gold = economy.oro
        engine.tick()
        self.assertGreater(economy.oro, initial_gold)

    def test_investment_changes_faith_and_infection(self) -> None:
        engine, _, province_entities, _ = cargar_mundo()
        entity_id = next(iter(province_entities.values()))
        region = engine.componentes[RegiónComponent][entity_id]
        economy = engine.componentes[EconomyComponent][entity_id]
        economy.oro = EconomicSystem.COSTE_INVERSION
        initial_infection = region.infeccion.valor
        initial_fervor = region.fervor.valor
        self.assertTrue(EconomicSystem.invertir(region, economy, entity_id))
        self.assertLess(region.infeccion.valor, initial_infection)
        self.assertGreater(region.fervor.valor, initial_fervor)

    def test_trade_requires_adjacency(self) -> None:
        engine, _, province_entities, _ = cargar_mundo()
        origin_id, destinations = next((origin, values) for origin, values in engine.adyacencias.items() if values)
        destination_id = next(iter(destinations))
        economies = engine.componentes[EconomyComponent]
        initial_destination_gold = economies[destination_id].oro
        flow = EconomicSystem.comerciar(origin_id, destination_id, economies, engine.adyacencias)
        self.assertGreater(flow, 0)
        self.assertGreater(economies[destination_id].oro, initial_destination_gold)

    def test_player_spawn_is_land_and_supports_configured_potential(self) -> None:
        engine, _, province_entities, _ = cargar_mundo()
        player = SpawnSystem.crear_jugador(
            engine.map_raw,
            province_entities,
            rng=random.Random(7),
            arquetipo="mago",
        )
        land_cells = dict(SpawnSystem.celdas_terrestres(engine.map_raw, province_entities))
        self.assertIn(player.celda_actual, land_cells)
        self.assertIn(player.provincia_actual, province_entities)
        self.assertEqual(player.potencial_nacimiento, "mago")
        self.assertEqual(player.mana_maximo, 130)
        self.assertIn(player.marca_de_la_estrella, {"hombro", "pecho", "espalda", "antebrazo", "nuca"})

    def test_product_route_uses_distance_and_danger(self) -> None:
        engine, _, _, _ = cargar_mundo()
        origin_id, destinations = next((origin, values) for origin, values in engine.adyacencias.items() if values)
        destination_id = next(iter(destinations))
        market = engine.componentes[TradeComponent][origin_id]
        product = market.productos[0]
        regions = engine.componentes[RegiónComponent]
        infection_type = type(regions[origin_id].infeccion)
        regions[origin_id].infeccion = infection_type(0.0)
        base_price, days, distance = EconomicSystem.calcular_precio(
            product, market, engine.componentes[TradeComponent][destination_id], regions[origin_id], regions[destination_id]
        )
        regions[origin_id].infeccion = infection_type(1.0)
        dangerous_price, _, _ = EconomicSystem.calcular_precio(
            product, market, engine.componentes[TradeComponent][destination_id], regions[origin_id], regions[destination_id]
        )
        self.assertGreaterEqual(days, 1)
        self.assertGreaterEqual(distance, 0.0)
        self.assertGreater(dangerous_price, base_price)


if __name__ == "__main__":
    unittest.main()