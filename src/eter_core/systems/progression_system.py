from eter_core.components.player_component import PlayerComponent
from eter_core.domain.archetypes import CATALOGO_ARQUETIPOS


class ProgressionSystem:
    """
    Sistema de progresión: XP y niveles.

    Reglas de Dominio:
    - El jugador gana XP al cazar monstruos (según su tier).
    - Al acumular suficiente XP sube de nivel.
    - Cada nivel aumenta los stats del jugador (según su arquetipo).
    """

    XP_BASE_POR_NIVEL: float = 100.0
    INCREMENTO_POR_NIVEL: float = 50.0
    VIDA_POR_NIVEL: int = 5
    MANA_POR_NIVEL: int = 3
    STAT_PRIMARIO_POR_NIVEL: int = 2

    @classmethod
    def xp_por_tier(cls, tier: int) -> int:
        """XP que otorga derrotar un monstruo según su tier (1-5)."""
        return tier * 20

    @classmethod
    def xp_requerida(cls, nivel: int) -> float:
        """XP necesaria para pasar de `nivel` a `nivel+1`."""
        return cls.XP_BASE_POR_NIVEL + (nivel - 1) * cls.INCREMENTO_POR_NIVEL

    @classmethod
    def otorgar_xp(cls, player: PlayerComponent, xp: int) -> list[int]:
        """
        Otorga XP y procesa subidas de nivel. Devuelve la lista de niveles alcanzados.
        """
        if xp <= 0:
            return []
        player.experiencia += xp
        niveles_ganados: list[int] = []
        while player.experiencia >= cls.xp_requerida(player.nivel):
            player.experiencia -= cls.xp_requerida(player.nivel)
            player.nivel += 1
            cls._aplicar_subida(player)
            niveles_ganados.append(player.nivel)
        return niveles_ganados

    @classmethod
    def _aplicar_subida(cls, player: PlayerComponent) -> None:
        """Aumenta los stats al subir de nivel, según el arquetipo."""
        player.vida_maxima += cls.VIDA_POR_NIVEL
        player.vida += cls.VIDA_POR_NIVEL
        player.mana_maximo += cls.MANA_POR_NIVEL
        player.mana = min(player.mana_maximo, player.mana + cls.MANA_POR_NIVEL)

        arquetipo = CATALOGO_ARQUETIPOS.get(player.potencial_nacimiento)
        stat_principal = "fuerza"
        if arquetipo is not None:
            if arquetipo.nombre.startswith("Mago"):
                stat_principal = "inteligencia"
            elif arquetipo.nombre.startswith("Tanque"):
                stat_principal = "tenacidad"
            elif arquetipo.nombre.startswith("Asesino"):
                stat_principal = "fuerza"

        if stat_principal == "inteligencia":
            player.inteligencia += cls.STAT_PRIMARIO_POR_NIVEL
        elif stat_principal == "tenacidad":
            player.tenacidad += cls.STAT_PRIMARIO_POR_NIVEL
        else:
            player.fuerza += cls.STAT_PRIMARIO_POR_NIVEL
