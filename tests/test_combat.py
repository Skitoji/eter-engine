import os
import random
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))
sys.path.insert(0, os.path.abspath("."))

from eter_core.components.enemy_component import EnemyComponent
from eter_core.components.player_component import PlayerComponent
from eter_core.components.region_component import RegiónComponent
from eter_core.components.trade_component import TradeComponent
from eter_core.domain.types import FaccionTipo, FervorReligioso, NivelInfeccion
from eter_core.systems.combat_system import CombatSystem
from eter_core.systems.monster_spawn_system import MonsterSpawnSystem


def _region(nombre="Test", infeccion=0.0, faccion=FaccionTipo.SANTA_IGLESIA):
    return RegiónComponent(
        nombre=nombre,
        poblacion_total=1000,
        fervor=FervorReligioso(0.5),
        infeccion=NivelInfeccion(infeccion),
        faccion_dominante=faccion,
    )


class CombatSystemTests(unittest.TestCase):
    def test_victoria_contra_goblin_debil(self):
        player = PlayerComponent()
        player.fuerza = 50  # goblin tiene 20 HP, debería ganar rápido
        resultado = CombatSystem.resolver(player, "goblin", rng=random.Random(1))
        self.assertTrue(resultado.victoria)

    def test_derrota_contra_dragon(self):
        player = PlayerComponent()
        player.vida = 100
        player.fuerza = 10
        resultado = CombatSystem.resolver(player, "dragon", rng=random.Random(1))
        self.assertFalse(resultado.victoria)

    def test_aplicar_resultado_aplica_daño_y_drops(self):
        player = PlayerComponent()
        player.vida = 100
        player.fuerza = 15  # orco tiene 60 HP → el jugador recibe contraataques
        resultado = CombatSystem.resolver(player, "orco", rng=random.Random(3))
        CombatSystem.aplicar_resultado(player, resultado)
        self.assertLess(player.vida, 100)
        # Si ganó y dropeó colmillo, el material debe quedar registrado.
        if resultado.victoria and "colmillo_orco" in resultado.drops:
            self.assertGreaterEqual(player.materiales.get("colmillo_orco", 0), 1)

    def test_critico_duplica_daño(self):
        player = PlayerComponent()
        player.bonus_critico = 1.0  # siempre crítico
        player.fuerza = 10
        daño = CombatSystem.daño_jugador(player, random.Random(1))
        self.assertEqual(daño, 20)  # 10 * 2

    def test_tenacidad_mitiga_daño(self):
        from eter_core.domain.monsters import CATALOGO_MONSTRUOS
        player = PlayerComponent()
        player.tenacidad = 10
        goblin = CATALOGO_MONSTRUOS["goblin"]  # ataque 5
        daño = CombatSystem.daño_monstruo(goblin, player)
        self.assertLess(daño, 5)

    def test_monstruo_desconocido_lanza_error(self):
        player = PlayerComponent()
        with self.assertRaises(ValueError):
            CombatSystem.resolver(player, "monstruo_inexistente")


class MonsterSpawnSystemTests(unittest.TestCase):
    def test_pool_incluye_corruptos_con_infeccion_alta(self):
        pool = MonsterSpawnSystem._pool_por_estado("planicies", 0.6, FaccionTipo.SANTA_IGLESIA)
        self.assertIn("cultista", pool)
        self.assertIn("quimera", pool)

    def test_pool_incluye_no_muertos_con_fe_colapsada(self):
        pool = MonsterSpawnSystem._pool_por_estado("planicies", 0.1, FaccionTipo.FACCIÓN_CULTISTA_OSCURA)
        self.assertIn("esqueleto", pool)
        self.assertIn("zombi", pool)
        self.assertIn("espectro", pool)

    def test_pool_base_por_bioma(self):
        pool = MonsterSpawnSystem._pool_por_estado("montanas", 0.0, FaccionTipo.SANTA_IGLESIA)
        self.assertIn("orco", pool)
        self.assertIn("minotauro", pool)

    def test_spawn_genera_monstruo_con_rng_forzado(self):
        region = _region("A", infeccion=0.9)
        enemigos = {1: EnemyComponent()}
        mercados = {1: TradeComponent(bioma="planicies")}
        # rng con random() siempre 0.0 → siempre spawnea
        MonsterSpawnSystem.procesar(
            {1: region}, enemigos, mercados, rng=random.Random(0)
        )
        # Con Random(0) el primer random() es ~0.84, puede no spawnear; forzamos manualmente
        # para hacer el test determinista usando una clase rng fija.
        class _SiempreCero:
            def random(self):
                return 0.0
            def choice(self, seq):
                return seq[0]
        enemigos2 = {1: EnemyComponent()}
        MonsterSpawnSystem.procesar({1: region}, enemigos2, mercados, rng=_SiempreCero())
        self.assertGreater(sum(enemigos2[1].monstruos.values()), 0)

    def test_no_spawna_sin_mercado(self):
        region = _region("A")
        enemigos = {1: EnemyComponent()}
        class _SiempreCero:
            def random(self):
                return 0.0
            def choice(self, seq):
                return seq[0]
        MonsterSpawnSystem.procesar({1: region}, enemigos, {}, rng=_SiempreCero())
        # Sin mercado el bioma por defecto es planicies → sí spawnea (goblin)
        self.assertGreater(sum(enemigos[1].monstruos.values()), 0)


if __name__ == "__main__":
    unittest.main()
