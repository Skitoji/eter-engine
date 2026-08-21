import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))
sys.path.insert(0, os.path.abspath("."))

from eter_core.components.player_component import PlayerComponent
from eter_core.domain.products import CATALOGO_PRODUCTOS
from eter_core.systems.item_system import ItemSystem
from eter_core.systems.merchant_system import MerchantSystem
from eter_core.systems.smith_system import SmithSystem


class MerchantSystemTests(unittest.TestCase):
    def test_vender_material_convierte_en_oro(self):
        player = PlayerComponent()
        player.dar_material("hierro", 2)
        mensaje = MerchantSystem.vender(player, "hierro", 2)
        self.assertIsNotNone(mensaje)
        self.assertEqual(player.materiales.get("hierro", 0), 0)
        self.assertGreater(player.oro, 0)

    def test_vender_sin_material_falla(self):
        player = PlayerComponent()
        self.assertIsNone(MerchantSystem.vender(player, "hierro", 1))

    def test_precio_compra_menor_que_venta(self):
        compra = MerchantSystem.precio_compra("hierro")
        venta = MerchantSystem.precio_venta("hierro")
        self.assertLess(compra, venta)
        self.assertLess(compra, CATALOGO_PRODUCTOS["hierro"].valor_base)

    def test_comprar_consume_oro_y_da_material(self):
        player = PlayerComponent()
        player.oro = 100
        mensaje = MerchantSystem.comprar(player, "hierro", 1)
        self.assertIsNotNone(mensaje)
        self.assertLess(player.oro, 100)
        self.assertEqual(player.materiales.get("hierro", 0), 1)

    def test_comprar_sin_oro_falla(self):
        player = PlayerComponent()
        player.oro = 0
        self.assertIsNone(MerchantSystem.comprar(player, "hierro", 1))

    def test_producto_invalido_devuelve_none(self):
        player = PlayerComponent()
        self.assertIsNone(MerchantSystem.vender(player, "no_existe"))
        self.assertIsNone(MerchantSystem.comprar(player, "no_existe"))


class SmithSystemTests(unittest.TestCase):
    def test_forjar_espada_hierro(self):
        player = PlayerComponent()
        player.dar_material("hierro", 2)
        player.oro = 10
        mensaje = SmithSystem.forjar(player, "espada_hierro")
        self.assertIsNotNone(mensaje)
        self.assertEqual(player.materiales.get("hierro", 0), 0)
        self.assertTrue(player.tiene("espada_hierro"))
        self.assertEqual(player.oro, 0)

    def test_forjar_sin_materiales_falla(self):
        player = PlayerComponent()
        player.oro = 10
        self.assertIsNone(SmithSystem.forjar(player, "espada_hierro"))

    def test_forjar_sin_oro_falla(self):
        player = PlayerComponent()
        player.dar_material("hierro", 2)
        player.oro = 0
        self.assertIsNone(SmithSystem.forjar(player, "espada_hierro"))

    def test_puede_forjar_consistente(self):
        player = PlayerComponent()
        player.dar_material("hierro", 2)
        player.oro = 10
        self.assertTrue(SmithSystem.puede_forjar(player, "espada_hierro"))
        SmithSystem.forjar(player, "espada_hierro")
        self.assertFalse(SmithSystem.puede_forjar(player, "espada_hierro"))

    def test_receta_inexistente_falla(self):
        player = PlayerComponent()
        self.assertIsNone(SmithSystem.forjar(player, "receta_falsa"))

    def test_forjar_mithril_requiere_mucho(self):
        player = PlayerComponent()
        player.dar_material("mithril", 2)
        player.oro = 200
        mensaje = SmithSystem.forjar(player, "espada_mithril")
        self.assertIsNotNone(mensaje)
        self.assertTrue(player.tiene("espada_mithril"))


if __name__ == "__main__":
    unittest.main()
