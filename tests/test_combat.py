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
from eter_core.domain.monsters import CATALOGO_MONSTRUOS
from eter_core.domain.types import FaccionTipo, FervorReligioso, NivelInfeccion
from eter_core.systems.combat_system import AccionCombate, CombatSystem
from eter_core.systems.monster_spawn_system import MonsterSpawnSystem


def _region(nombre="Test", infeccion=0.0, faccion=FaccionTipo.SANTA_IGLESIA):
    return RegiónComponent(
        nombre=nombre,
        poblacion_total=1000,
        fervor=FervorReligioso(0.5),
        infeccion=NivelInfeccion(infeccion),
        faccion_dominante=faccion,
    )


class _RngFijo:
    """rng determinista que devuelve siempre el mismo valor."""

    def __init__(self, valor):
        self.valor = valor

    def random(self):
        return self.valor


class _RngSecuencia:
    """rng determinista que devuelve valores en secuencia (y repite el último)."""

    def __init__(self, valores):
        self.valores = list(valores)
        self.i = 0

    def random(self):
        indice = min(self.i, len(self.valores) - 1)
        valor = self.valores[indice]
        self.i += 1
        return valor


class CombatSystemTests(unittest.TestCase):
    def test_victoria_contra_goblin_debil(self):
        player = PlayerComponent()
        player.fuerza = 50
        estado = CombatSystem.iniciar(player, "goblin")
        rng = random.Random(1)
        for _ in range(50):
            if estado.finalizado:
                break
            CombatSystem.turno_jugador(player, estado, AccionCombate.ATACAR, rng=rng)
        self.assertTrue(estado.victoria)

    def test_derrota_contra_dragon(self):
        player = PlayerComponent()
        player.vida = 100
        player.fuerza = 10
        estado = CombatSystem.iniciar(player, "dragon")
        rng = random.Random(1)
        for _ in range(200):
            if estado.finalizado:
                break
            CombatSystem.turno_jugador(player, estado, AccionCombate.ATACAR, rng=rng)
        self.assertFalse(estado.victoria)
        self.assertLessEqual(player.vida, 0)

    def test_victoria_aplica_drops(self):
        player = PlayerComponent()
        player.fuerza = 50
        estado = CombatSystem.iniciar(player, "goblin")
        # [esquiva monstruo, critico, drop] → sin esquiva, sin critico, drop garantizado
        rng = _RngSecuencia([0.99, 0.5, 0.0])
        CombatSystem.turno_jugador(player, estado, AccionCombate.ATACAR, rng=rng)
        self.assertTrue(estado.victoria)
        self.assertGreaterEqual(player.materiales.get("oreja_goblin", 0), 1)

    def test_critico_duplica_daño(self):
        player = PlayerComponent()
        player.bonus_critico = 1.0
        player.fuerza = 10
        daño = CombatSystem.daño_jugador(player, _RngFijo(0.0))
        self.assertEqual(daño, 20)

    def test_tenacidad_mitiga_daño(self):
        player = PlayerComponent()
        player.tenacidad = 10
        goblin = CATALOGO_MONSTRUOS["goblin"]  # ataque 5
        daño = CombatSystem.daño_monstruo(goblin, player)
        self.assertLess(daño, 5)

    def test_defensa_reduce_daño_recibido(self):
        minotauro = CATALOGO_MONSTRUOS["minotauro"]  # ataque 22
        player = PlayerComponent()
        player.tenacidad = 10
        sin_defensa = CombatSystem.daño_monstruo(minotauro, player)
        player.defensa = 10
        con_defensa = CombatSystem.daño_monstruo(minotauro, player)
        self.assertLess(con_defensa, sin_defensa)

    def test_prob_esquiva_con_cap(self):
        self.assertAlmostEqual(CombatSystem.prob_esquiva(10), 0.10)
        self.assertEqual(CombatSystem.prob_esquiva(100), 0.50)

    def test_prob_parry_en_rango(self):
        self.assertAlmostEqual(CombatSystem.prob_parry(10), 0.30)
        self.assertLessEqual(CombatSystem.prob_parry(1000), 0.75)

    def test_prob_huida_favorece_agilidad(self):
        player = PlayerComponent()
        player.agilidad = 10
        goblin = CATALOGO_MONSTRUOS["goblin"]  # agilidad 8, tier 1
        self.assertGreater(CombatSystem.prob_huida(player, goblin), 0.5)

    def test_iniciar_monstruo_desconocido_lanza_error(self):
        player = PlayerComponent()
        with self.assertRaises(ValueError):
            CombatSystem.iniciar(player, "monstruo_inexistente")


class CombateTacticoTests(unittest.TestCase):
    def test_parry_exitoso_riposta_sin_recibir_daño(self):
        player = PlayerComponent()
        estado = CombatSystem.iniciar(player, "goblin")
        # [IA normal, parry ok, critico no] → ataca normal, parry éxito, riposta sin crítico
        rng = _RngSecuencia([0.5, 0.0, 0.5])
        res = CombatSystem.turno_jugador(player, estado, AccionCombate.PARRY, rng=rng)
        self.assertTrue(res.parry_exitoso)
        self.assertEqual(res.daño_recibido, 0)
        self.assertGreater(res.daño_infligido, 0)
        self.assertEqual(player.vida, 100)

    def test_parry_fallido_recibe_daño(self):
        player = PlayerComponent()
        estado = CombatSystem.iniciar(player, "minotauro")
        # [IA normal, parry falla] → recibe el golpe completo
        rng = _RngSecuencia([0.5, 0.99])
        res = CombatSystem.turno_jugador(player, estado, AccionCombate.PARRY, rng=rng)
        self.assertFalse(res.parry_exitoso)
        self.assertGreater(res.daño_recibido, 0)
        self.assertLess(player.vida, 100)

    def test_defender_reduce_daño_a_la_mitad(self):
        player = PlayerComponent()
        estado = CombatSystem.iniciar(player, "minotauro")
        full = CombatSystem.daño_monstruo(estado.monstruo, player)
        # [IA normal, esquiva falla] → golpe normal reducido a la mitad
        rng = _RngSecuencia([0.5, 0.5])
        res = CombatSystem.turno_jugador(player, estado, AccionCombate.DEFENDER, rng=rng)
        esperado = max(1, int(full * CombatSystem.REDUCCION_DEFENDER))
        self.assertEqual(res.daño_recibido, esperado)
        self.assertLess(res.daño_recibido, full)

    def test_huida_exitosa_termina_combate(self):
        player = PlayerComponent()
        estado = CombatSystem.iniciar(player, "goblin")
        rng = _RngFijo(0.0)
        res = CombatSystem.turno_jugador(player, estado, AccionCombate.HUIR, rng=rng)
        self.assertTrue(res.huido)
        self.assertTrue(estado.huido)
        self.assertTrue(estado.finalizado)

    def test_huida_fallida_monstruo_golpea(self):
        player = PlayerComponent()
        estado = CombatSystem.iniciar(player, "minotauro")
        rng = _RngFijo(0.99)
        res = CombatSystem.turno_jugador(player, estado, AccionCombate.HUIR, rng=rng)
        self.assertFalse(res.huido)
        self.assertGreater(res.daño_recibido, 0)
        self.assertLess(player.vida, 100)

    def test_hechizo_dano_daña_monstruo(self):
        player = PlayerComponent()
        player.mana = 100
        estado = CombatSystem.iniciar(player, "goblin")
        res = CombatSystem.turno_jugador(player, estado, AccionCombate.HECHIZO, nombre="rayo_arcano", rng=_RngFijo(0.5))
        self.assertGreaterEqual(res.daño_infligido, 50)
        self.assertTrue(estado.victoria)

    def test_hechizo_sin_mana_falla(self):
        player = PlayerComponent()
        player.mana = 0
        estado = CombatSystem.iniciar(player, "goblin")
        res = CombatSystem.turno_jugador(player, estado, AccionCombate.HECHIZO, nombre="rayo_arcano", rng=_RngFijo(0.5))
        self.assertIn("maná", res.detalle)
        self.assertFalse(estado.victoria)

    def test_monstruo_defendiendo_reduce_daño_siguiente(self):
        player = PlayerComponent()
        player.fuerza = 50
        player.bonus_critico = 0.0
        estado = CombatSystem.iniciar(player, "goblin")
        estado.monstruo_defendiendo = True
        # [esquiva monstruo falla, critico no] → golpe de 50 reducido a 25
        rng = _RngSecuencia([0.99, 0.5])
        res = CombatSystem.turno_jugador(player, estado, AccionCombate.ATACAR, rng=rng)
        # 50 * 0.5 = 25, menos defensa 0 → 25 de daño infligido
        self.assertEqual(res.daño_infligido, 25)
        self.assertFalse(estado.monstruo_defendiendo)


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
        self.assertGreater(sum(enemigos[1].monstruos.values()), 0)


if __name__ == "__main__":
    unittest.main()
