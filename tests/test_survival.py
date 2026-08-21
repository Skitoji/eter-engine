import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))
sys.path.insert(0, os.path.abspath("."))

from eter_core.components.player_component import PlayerComponent
from eter_core.domain.products import CATALOGO_PRODUCTOS
from eter_core.systems.hunger_system import HungerSystem
from eter_core.systems.pricing_system import PricingSystem
from eter_core.systems.weight_system import WeightSystem


class PricingSystemTests(unittest.TestCase):
    def test_producto_nativo_mas_barato(self):
        # El hierro es nativo de montañas → más barato allí que en la costa
        en_montanas = PricingSystem.precio("hierro", "montanas")
        en_costas = PricingSystem.precio("hierro", "costas")
        self.assertLess(en_montanas, en_costas)

    def test_producto_sin_geografia_neutro(self):
        # El ectoplasma no tiene geografía nativa → mismo precio en cualquier bioma
        en_montanas = PricingSystem.precio("ectoplasma", "montanas")
        en_costas = PricingSystem.precio("ectoplasma", "costas")
        self.assertEqual(en_montanas, en_costas)

    def test_oferta_baja_demanda_alta_suben_precio(self):
        barato = PricingSystem.precio("hierro", "montanas", oferta=200.0, demanda=10.0)
        caro = PricingSystem.precio("hierro", "montanas", oferta=10.0, demanda=200.0)
        self.assertLess(barato, caro)

    def test_pescado_mas_barato_en_costa(self):
        # El pescado (análogo: trigo en planicies) es nativo donde se produce
        trigo_planicie = PricingSystem.precio("trigo", "planicies")
        trigo_montana = PricingSystem.precio("trigo", "montanas")
        self.assertLess(trigo_planicie, trigo_montana)


class WeightSystemTests(unittest.TestCase):
    def test_peso_inventario_suma_objetos(self):
        player = PlayerComponent()
        # inventario inicial: brujula (0.2) + 3 raciones (1.5) + 1 antorcha (0.5)
        peso = WeightSystem.peso_inventario(player)
        self.assertAlmostEqual(peso, 2.2, places=1)

    def test_capacidad_crece_con_fuerza(self):
        debil = PlayerComponent()
        debil.fuerza = 5
        fuerte = PlayerComponent()
        fuerte.fuerza = 20
        self.assertGreater(WeightSystem.capacidad_maxima(fuerte), WeightSystem.capacidad_maxima(debil))

    def test_mithril_mas_liviano_que_hierro(self):
        # El mithril es el metal más fuerte y también más ligero
        from eter_core.domain.items import CATALOGO_OBJETOS
        self.assertLess(CATALOGO_OBJETOS["espada_mithril"].peso, CATALOGO_OBJETOS["espada_hierro"].peso)

    def test_sobrecargado_detecta_exceso(self):
        player = PlayerComponent()
        player.fuerza = 5  # capacidad baja
        player.dar_material("hierro", 100)  # mucho peso
        self.assertTrue(WeightSystem.esta_sobrecargado(player))


class HungerSystemTests(unittest.TestCase):
    def test_avanzar_reduce_hambre(self):
        player = PlayerComponent()
        player.hambre = 100
        HungerSystem.avanzar(player)
        self.assertLess(player.hambre, 100)

    def test_saciado_sin_penalizacion(self):
        player = PlayerComponent()
        player.hambre = 90
        self.assertEqual(HungerSystem.penalizaciones(player), {})

    def test_hambre_leve_penaliza_fuerza_guerrero(self):
        player = PlayerComponent()
        player.potencial_nacimiento = "caballero"
        player.hambre = 50
        penalizaciones = HungerSystem.penalizaciones(player)
        self.assertIn("fuerza", penalizaciones)

    def test_hambre_leve_penaliza_mana_mago(self):
        player = PlayerComponent()
        player.potencial_nacimiento = "mago"
        player.hambre = 50
        penalizaciones = HungerSystem.penalizaciones(player)
        self.assertIn("mana_maximo", penalizaciones)

    def test_hambre_severa_penaliza_mas(self):
        player = PlayerComponent()
        player.potencial_nacimiento = "caballero"
        player.hambre = 20
        severa = HungerSystem.penalizaciones(player)["fuerza"]
        player.hambre = 50
        leve = HungerSystem.penalizaciones(player)["fuerza"]
        self.assertLess(severa, leve)

    def test_estado_legible(self):
        player = PlayerComponent()
        player.hambre = 100
        self.assertEqual(HungerSystem.estado(player), "saciado")
        player.hambre = 50
        self.assertEqual(HungerSystem.estado(player), "hambre leve")
        player.hambre = 10
        self.assertEqual(HungerSystem.estado(player), "famélico")


if __name__ == "__main__":
    unittest.main()
