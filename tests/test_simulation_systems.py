import os
import random
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))
sys.path.insert(0, os.path.abspath("."))

from eter_core.components.economy_component import EconomyComponent
from eter_core.components.enemy_component import EnemyComponent
from eter_core.components.region_component import RegiónComponent
from eter_core.components.trade_component import TradeComponent
from eter_core.domain.types import FaccionTipo, FervorReligioso, NivelInfeccion
from eter_core.systems.cultist_system import CultistSystem
from eter_core.systems.infection_system import InfectionSystem


def _region(nombre="Test", fervor=0.5, infeccion=0.0):
    return RegiónComponent(
        nombre=nombre,
        poblacion_total=1000,
        fervor=FervorReligioso(fervor),
        infeccion=NivelInfeccion(infeccion),
        faccion_dominante=FaccionTipo.SANTA_IGLESIA,
    )


class InfectionSystemTests(unittest.TestCase):
    def test_propagates_to_adjacent_province(self):
        a = _region("A", infeccion=0.8)
        b = _region("B", infeccion=0.0)
        regiones = {1: a, 2: b}
        adyacencias = {1: {2}, 2: set()}
        InfectionSystem.expandir(regiones, adyacencias)
        self.assertGreater(b.infeccion.valor, 0.0)

    def test_does_not_propagate_below_threshold(self):
        a = _region("A", infeccion=0.3)  # bajo UMBRAL_PROPAGACION (0.40)
        b = _region("B", infeccion=0.0)
        regiones = {1: a, 2: b}
        adyacencias = {1: {2}, 2: set()}
        InfectionSystem.expandir(regiones, adyacencias)
        self.assertEqual(b.infeccion.valor, 0.0)

    def test_infection_is_capped_at_one(self):
        a = _region("A", infeccion=0.9)
        b = _region("B", infeccion=0.99)
        regiones = {1: a, 2: b}
        adyacencias = {1: {2}, 2: set()}
        InfectionSystem.expandir(regiones, adyacencias)
        self.assertLessEqual(b.infeccion.valor, 1.0)


class CultistSystemTests(unittest.TestCase):
    def test_spawns_cultist_when_rate_is_high(self):
        region = _region("A")
        region.tasa_magos_oscuros = 1.0  # forzar spawn
        enemigos = {1: EnemyComponent()}
        CultistSystem.procesar({1: region}, enemigos, rng=random.Random(1))
        self.assertEqual(enemigos[1].cultistas, 1)

    def test_does_not_spawn_when_rate_is_zero(self):
        region = _region("A")
        region.tasa_magos_oscuros = 0.0
        enemigos = {1: EnemyComponent()}
        CultistSystem.procesar({1: region}, enemigos, rng=random.Random(1))
        self.assertEqual(enemigos[1].cultistas, 0)

    def test_respects_max_enemies_per_region(self):
        region = _region("A")
        region.tasa_magos_oscuros = 1.0
        enemigos = {1: EnemyComponent(cultistas=CultistSystem.MAX_ENEMIGOS_POR_REGION)}
        CultistSystem.procesar({1: region}, enemigos, rng=random.Random(1))
        self.assertEqual(enemigos[1].cultistas, CultistSystem.MAX_ENEMIGOS_POR_REGION)


if __name__ == "__main__":
    unittest.main()
