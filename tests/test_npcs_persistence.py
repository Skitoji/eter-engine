import os
import random
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath("src"))
sys.path.insert(0, os.path.abspath("."))

from eter_core.components.player_component import PlayerComponent
from eter_core.components.stock_component import StockComponent
from eter_core.domain.npcs import npcs_por_ubicacion
from eter_core.systems.npc_system import NpcSystem
from eter_core.systems.stock_system import StockSystem
from eter_infrastructure.persistence.save_system import SaveSystem


class NpcSystemTests(unittest.TestCase):
    def test_ciudad_tiene_mas_npcs(self):
        self.assertGreater(len(npcs_por_ubicacion(True)), len(npcs_por_ubicacion(False)))

    def test_descansar_recupera_y_cobra(self):
        player = PlayerComponent()
        player.oro = 50
        player.vida = 10
        player.estamina = 5
        mensaje = NpcSystem.descansar(player)
        self.assertIsNotNone(mensaje)
        self.assertEqual(player.vida, player.vida_maxima)
        self.assertEqual(player.estamina, player.estamina_maxima)
        self.assertLess(player.oro, 50)

    def test_descansar_sin_oro_falla(self):
        player = PlayerComponent()
        player.oro = 0
        self.assertIsNone(NpcSystem.descansar(player))

    def test_curar_sin_heridas(self):
        player = PlayerComponent()
        player.oro = 50
        player.vida = player.vida_maxima
        self.assertEqual(NpcSystem.curar(player), "No tienes heridas que curar.")

    def test_rumor_depende_del_estado(self):
        # Solo verificamos que devuelve un string no vacío
        self.assertTrue(NpcSystem.rumor(0.8, 0.5, rng=random.Random(1)))

    def test_informe_capitan_menciona_monstruos(self):
        informe = NpcSystem.informe_capitan(0.3, {"goblin": 3})
        self.assertIn("goblin", informe)


class StockSystemTests(unittest.TestCase):
    def test_stock_nativo_tiene_mas_oferta(self):
        stock = StockSystem.crear_stock("montanas")
        # El hierro es nativo de montañas → más oferta
        self.assertGreater(stock.oferta["hierro"], stock.oferta["trigo"])

    def test_registrar_compra_baja_oferta(self):
        stock = StockSystem.crear_stock("montanas")
        antes = stock.oferta["hierro"]
        StockSystem.registrar_compra(stock, "hierro", 5)
        self.assertLess(stock.oferta["hierro"], antes)

    def test_registrar_venta_sube_oferta(self):
        stock = StockSystem.crear_stock("montanas")
        antes = stock.oferta["hierro"]
        StockSystem.registrar_venta(stock, "hierro", 5)
        self.assertGreater(stock.oferta["hierro"], antes)

    def test_fluctuar_cambia_stock(self):
        stock = StockSystem.crear_stock("montanas")
        antes = dict(stock.oferta)
        StockSystem.fluctuar(stock, rng=random.Random(42))
        # Al menos algún producto cambió (probabilístico pero con seed fijo)
        self.assertNotEqual(antes, stock.oferta)


class SaveSystemTests(unittest.TestCase):
    def test_guardar_y_cargar_roundtrip(self):
        player = PlayerComponent()
        player.oro = 1234.5
        player.nivel = 7
        player.inventario = {"hierbas": 5, "raciones": 2}
        player.materiales = {"hierro": 3}
        player.ayuda_recibida = {1, 2, 3}

        with tempfile.TemporaryDirectory() as tmp:
            ruta = os.path.join(tmp, "save.json")
            SaveSystem.guardar(player, ruta)
            self.assertTrue(SaveSystem.existe_partida(ruta))

            nuevo = PlayerComponent()
            estado = SaveSystem.cargar(ruta)
            SaveSystem.aplicar(nuevo, estado)

            self.assertEqual(nuevo.oro, 1234.5)
            self.assertEqual(nuevo.nivel, 7)
            self.assertEqual(nuevo.inventario, {"hierbas": 5, "raciones": 2})
            self.assertEqual(nuevo.materiales, {"hierro": 3})
            self.assertEqual(nuevo.ayuda_recibida, {1, 2, 3})

    def test_no_existe_partida(self):
        self.assertFalse(SaveSystem.existe_partida("/tmp/no_existe_save_test.json"))


if __name__ == "__main__":
    unittest.main()
