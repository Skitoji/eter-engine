import os
import random
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))
sys.path.insert(0, os.path.abspath("."))

from eter_core.components.player_component import PlayerComponent
from eter_core.components.trade_component import TradeComponent
from eter_core.domain.spells import CATALOGO_HECHIZOS
from eter_core.systems.progression_system import ProgressionSystem
from eter_core.systems.random_event_system import RandomEventSystem
from eter_core.systems.spell_system import SpellSystem
from eter_core.systems.travel_system import TravelSystem


class SpellSystemTests(unittest.TestCase):
    def test_lanzar_hechizo_consume_mana(self):
        player = PlayerComponent()
        player.mana = 100
        mensaje = SpellSystem.lanzar(player, "curacion")
        self.assertIsNotNone(mensaje)
        self.assertLess(player.mana, 100)

    def test_sin_mana_suficiente_falla(self):
        player = PlayerComponent()
        player.mana = 0
        self.assertIsNone(SpellSystem.lanzar(player, "invisibilidad_area"))

    def test_invisibilidad_es_temporal(self):
        player = PlayerComponent()
        player.mana = 100
        SpellSystem.lanzar(player, "invisibilidad_area")
        self.assertTrue(SpellSystem.es_invisible(player))
        # Avanzar turnos hasta que caduque
        SpellSystem.avanzar_turno(player)
        SpellSystem.avanzar_turno(player)
        SpellSystem.avanzar_turno(player)
        self.assertFalse(SpellSystem.es_invisible(player))

    def test_buff_se_revierte_al_caducar(self):
        player = PlayerComponent()
        player.mana = 100
        fuerza_inicial = player.fuerza
        SpellSystem.lanzar(player, "bendicion")
        self.assertEqual(player.fuerza, fuerza_inicial + 5)
        SpellSystem.avanzar_turno(player)
        SpellSystem.avanzar_turno(player)
        self.assertEqual(player.fuerza, fuerza_inicial)

    def test_hechizo_inexistente_falla(self):
        player = PlayerComponent()
        self.assertIsNone(SpellSystem.lanzar(player, "no_existe"))


class ProgressionSystemTests(unittest.TestCase):
    def test_xp_por_tier_creciente(self):
        self.assertLess(ProgressionSystem.xp_por_tier(1), ProgressionSystem.xp_por_tier(5))

    def test_subir_nivel_aumenta_stats(self):
        player = PlayerComponent()
        vida_inicial = player.vida_maxima
        xp_necesaria = ProgressionSystem.xp_requerida(player.nivel)
        niveles = ProgressionSystem.otorgar_xp(player, int(xp_necesaria))
        self.assertEqual(len(niveles), 1)
        self.assertEqual(player.nivel, 2)
        self.assertGreater(player.vida_maxima, vida_inicial)

    def test_xp_insuficiente_no_sube_nivel(self):
        player = PlayerComponent()
        niveles = ProgressionSystem.otorgar_xp(player, 10)
        self.assertEqual(niveles, [])
        self.assertEqual(player.nivel, 1)

    def test_xp_requerida_crece_con_nivel(self):
        self.assertLess(ProgressionSystem.xp_requerida(1), ProgressionSystem.xp_requerida(5))


class TravelSystemTests(unittest.TestCase):
    def test_distancia_mayor_cuesta_mas(self):
        cerca = TradeComponent(coordenadas=(0.0, 0.0))
        lejos = TradeComponent(coordenadas=(100.0, 0.0))
        self.assertGreater(
            TravelSystem.coste_viaje(cerca, lejos),
            TravelSystem.coste_viaje(cerca, TradeComponent(coordenadas=(10.0, 0.0))),
        )

    def test_cruce_frontera_cuesta_mas(self):
        origen = TradeComponent(coordenadas=(0.0, 0.0))
        destino = TradeComponent(coordenadas=(10.0, 0.0))
        mismo_estado = TravelSystem.coste_viaje(origen, destino, mismo_estado=True)
        cruce = TravelSystem.coste_viaje(origen, destino, mismo_estado=False)
        self.assertGreater(cruce, mismo_estado)

    def test_dias_viaje_minimo_uno(self):
        origen = TradeComponent(coordenadas=(0.0, 0.0))
        destino = TradeComponent(coordenadas=(1.0, 1.0))
        self.assertGreaterEqual(TravelSystem.dias_viaje(origen, destino), 1)


class RandomEventSystemTests(unittest.TestCase):
    def test_evento_cuchillo_requiere_invisibilidad(self):
        # Sin invisibilidad, el evento cuchillo no puede ocurrir
        player = PlayerComponent()
        player.hechizos_activos = {}
        # Forzar con un rng que siempre da 0 (primera tirada) para el evento viento
        # Verificamos que el cuchillo no se aplica si no hay invisibilidad
        evento = RandomEventSystem.procesar(player, rng=random.Random(0))
        if evento is not None:
            self.assertNotEqual(evento.nombre, "cuchillo_cae")

    def test_evento_cuchillo_rompe_invisibilidad(self):
        player = PlayerComponent()
        player.hechizos_activos = {"invisibilidad_area": 3}
        # rng determinista que fuerce el cuchillo: usamos una clase fija
        class _FuerzaCuchillo:
            def random(self):
                return 0.0  # siempre < 0.03
        evento = RandomEventSystem.procesar(player, rng=_FuerzaCuchillo())
        self.assertIsNotNone(evento)
        self.assertEqual(evento.nombre, "cuchillo_cae")
        self.assertNotIn("invisibilidad_area", player.hechizos_activos)


if __name__ == "__main__":
    unittest.main()
