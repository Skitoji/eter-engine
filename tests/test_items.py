import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))
sys.path.insert(0, os.path.abspath("."))

from eter_core.components.player_component import PlayerComponent
from eter_core.systems.item_system import ItemSystem


class ItemSystemTests(unittest.TestCase):
    def test_dar_objeto_agrega_al_inventario(self):
        player = PlayerComponent()
        self.assertTrue(ItemSystem.dar_objeto(player, "hierbas", 2))
        self.assertEqual(player.inventario.get("hierbas"), 2)

    def test_dar_objeto_desconocido_falla(self):
        player = PlayerComponent()
        self.assertFalse(ItemSystem.dar_objeto(player, "objeto_inexistente"))

    def test_usar_raciones_cura_y_consume(self):
        player = PlayerComponent()
        player.vida = 50
        player.inventario = {"raciones": 1}
        mensaje = ItemSystem.usar_objeto(player, "raciones")
        self.assertIsNotNone(mensaje)
        self.assertEqual(player.vida, 70)
        self.assertNotIn("raciones", player.inventario)

    def test_no_consume_racion_con_vida_llena(self):
        player = PlayerComponent()
        player.vida = player.vida_maxima
        player.inventario = {"raciones": 1}
        mensaje = ItemSystem.usar_objeto(player, "raciones")
        self.assertIsNone(mensaje)
        self.assertEqual(player.inventario["raciones"], 1)  # no se consume

    def test_herramienta_no_se_consume(self):
        player = PlayerComponent()
        mensaje = ItemSystem.usar_objeto(player, "brujula")
        self.assertIsNotNone(mensaje)
        self.assertEqual(player.inventario["brujula"], 1)  # sigue ahí

    def test_usar_objeto_sin_tenerlo_falla(self):
        player = PlayerComponent()
        player.inventario = {}
        self.assertIsNone(ItemSystem.usar_objeto(player, "hierbas"))

    def test_ayuda_recibida_evita_duplicados(self):
        player = PlayerComponent()
        player.ayuda_recibida.add(7)
        # Simula la lógica del aldeano: no debe volver a dar hierbas
        if 7 not in player.ayuda_recibida:
            ItemSystem.dar_objeto(player, "hierbas", 1)
        self.assertNotIn("hierbas", player.inventario)


if __name__ == "__main__":
    unittest.main()
