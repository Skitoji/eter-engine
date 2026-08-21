import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))
sys.path.insert(0, os.path.abspath("."))

from eter_core.components.player_component import PlayerComponent
from eter_core.domain.archetypes import CATALOGO_ARQUETIPOS
from eter_core.domain.monsters import CATALOGO_MONSTRUOS, TipoMonstruo
from eter_core.domain.products import CATALOGO_PRODUCTOS, CategoriaProducto
from eter_core.systems.item_system import ItemSystem
from eter_core.systems.spawn_system import SpawnSystem


class ArchetypeTests(unittest.TestCase):
    def test_cuatro_arquetipos_definidos(self):
        self.assertEqual(len(CATALOGO_ARQUETIPOS), 4)

    def test_asesino_tiene_bonus_critico(self):
        asesino = CATALOGO_ARQUETIPOS["asesino"]
        self.assertGreater(asesino.bonus_critico, 0.0)
        self.assertEqual(asesino.estamina_maxima, 120)

    def test_mago_alto_mana_inteligencia(self):
        mago = CATALOGO_ARQUETIPOS["mago"]
        self.assertEqual(mago.mana_maximo, 130)
        self.assertGreater(mago.inteligencia, mago.fuerza)

    def test_spawn_respeta_arquetipo_elegido(self):
        raw = {"pack": {"cells": [{"i": 1, "province": 10, "state": 2}]}}
        player = SpawnSystem.crear_jugador(raw, {10}, arquetipo="asesino")
        self.assertEqual(player.potencial_nacimiento, "asesino")
        self.assertEqual(player.bonus_critico, 0.25)


class ProductTests(unittest.TestCase):
    def test_metales_progresan_en_valor(self):
        hierro = CATALOGO_PRODUCTOS["hierro"]
        runico = CATALOGO_PRODUCTOS["hierro_runico"]
        mithril = CATALOGO_PRODUCTOS["mithril"]
        self.assertLess(hierro.valor_base, runico.valor_base)
        self.assertLess(runico.valor_base, mithril.valor_base)

    def test_alimentos_marcados_correctamente(self):
        self.assertTrue(CATALOGO_PRODUCTOS["pan"].es_alimento)
        self.assertFalse(CATALOGO_PRODUCTOS["hierro"].es_alimento)

    def test_categorias_vinculan_productos_y_objetos(self):
        # Todo alimento consumible del catálogo de objetos debe existir como producto
        for nombre in ("pan", "carne", "setas"):
            self.assertIn(nombre, CATALOGO_PRODUCTOS)
            self.assertEqual(CATALOGO_PRODUCTOS[nombre].categoria, CategoriaProducto.ALIMENTO)


class MonsterTests(unittest.TestCase):
    def test_bestiario_tiene_todos_los_tiers(self):
        tiers = {monstruo.tier for monstruo in CATALOGO_MONSTRUOS.values()}
        self.assertEqual(tiers, {1, 2, 3, 4, 5})

    def test_drops_referencian_productos_validos(self):
        for monstruo in CATALOGO_MONSTRUOS.values():
            for producto in monstruo.drops:
                self.assertIn(producto, CATALOGO_PRODUCTOS)

    def test_no_muertos_vinculados_a_fe(self):
        # Los no-muertos y corruptos son los que florecen donde la fe cae
        for monstruo in CATALOGO_MONSTRUOS.values():
            if monstruo.tipo in (TipoMonstruo.NO_MUERTO, TipoMonstruo.CORRUPTO):
                self.assertIn(monstruo.nombre, ("Esqueleto", "Zombi", "Espectro", "Banshee", "Cultista"))


class EquipmentTests(unittest.TestCase):
    def test_equipar_otorga_bono_pasivo(self):
        player = PlayerComponent()
        player.inventario = {"espada_hierro": 1}
        mensaje = ItemSystem.equipar(player, "espada_hierro")
        self.assertIsNotNone(mensaje)
        self.assertEqual(player.equipamiento["arma"], "espada_hierro")
        self.assertEqual(ItemSystem.bonos_equipados(player)["fuerza"], 3)

    def test_desequipar_retira_bono(self):
        player = PlayerComponent()
        player.inventario = {"espada_hierro": 1}
        ItemSystem.equipar(player, "espada_hierro")
        ItemSystem.desequipar(player, "arma")
        self.assertEqual(ItemSystem.bonos_equipados(player), {})

    def test_equipar_reemplaza_slot(self):
        player = PlayerComponent()
        player.inventario = {"espada_hierro": 1, "anillo_estrella": 1}
        ItemSystem.equipar(player, "espada_hierro")
        self.assertIsNotNone(ItemSystem.equipar(player, "anillo_estrella"))  # distinto slot, ok
        self.assertIn("arma", player.equipamiento)
        self.assertIn("accesorio", player.equipamiento)

    def test_comida_sacia_hambre(self):
        player = PlayerComponent()
        player.hambre = 50
        player.inventario = {"pan": 1}
        ItemSystem.usar_objeto(player, "pan")
        self.assertEqual(player.hambre, 75)


if __name__ == "__main__":
    unittest.main()
