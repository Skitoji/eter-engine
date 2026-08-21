from typing import Optional

from eter_core.components.player_component import PlayerComponent
from eter_core.domain.spells import CATALOGO_HECHIZOS, HechizoDef, TipoHechizo


class SpellSystem:
    """
    Sistema de magia: lanza hechizos consumiendo maná y gestiona los buffs activos.

    Reglas de Dominio:
    - Cada hechizo cuesta maná.
    - Un hechizo instantáneo aplica su efecto de inmediato.
    - Un hechizo de duración >0 se registra en `hechizos_activos` y caduca
      tras N turnos, revirtiendo su efecto.
    - La invisibilidad (AREA) es un estado especial que evita encuentros.
    """

    @classmethod
    def definicion(cls, nombre: str) -> Optional[HechizoDef]:
        return CATALOGO_HECHIZOS.get(nombre)

    @classmethod
    def _hechizos(cls) -> dict:
        """Devuelve el catálogo completo de hechizos."""
        return CATALOGO_HECHIZOS

    @classmethod
    def lanzar(cls, player: PlayerComponent, nombre: str) -> Optional[str]:
        """
        Intenta lanzar un hechizo. Devuelve mensaje descriptivo o None si
        no puede (hechizo inexistente o maná insuficiente).
        """
        hechizo = cls.definicion(nombre)
        if hechizo is None:
            return None
        if player.mana < hechizo.coste_mana:
            return None

        # Consumir maná
        player.mana -= hechizo.coste_mana

        if hechizo.duracion_turnos > 0:
            # Buff temporal: registrar turnos restantes
            player.hechizos_activos[nombre] = hechizo.duracion_turnos
            # Aplicar efecto inmediato (se revertirá al caducar)
            player.aplicar_efectos({k: v for k, v in hechizo.efectos.items() if k != "invisible"})
            return hechizo.descripcion

        # Instantáneo
        player.aplicar_efectos({k: v for k, v in hechizo.efectos.items() if k != "invisible" and k != "dano"})
        return hechizo.descripcion

    @classmethod
    def es_invisible(cls, player: PlayerComponent) -> bool:
        """True si el jugador tiene invisibilidad activa."""
        return player.hechizos_activos.get("invisibilidad_area", 0) > 0

    @classmethod
    def buffs_activos(cls, player: PlayerComponent) -> dict:
        """Devuelve los efectos acumulados de los buffs activos (sin invisible)."""
        total: dict = {}
        for nombre, turnos in player.hechizos_activos.items():
            hechizo = cls.definicion(nombre)
            if hechizo is None:
                continue
            for stat, valor in hechizo.efectos.items():
                if stat == "invisible":
                    continue
                total[stat] = total.get(stat, 0.0) + valor
        return total

    @classmethod
    def avanzar_turno(cls, player: PlayerComponent) -> None:
        """Decrementa la duración de los buffs activos y revierte los caducados."""
        expirados = []
        for nombre, turnos in player.hechizos_activos.items():
            restantes = turnos - 1
            if restantes <= 0:
                expirados.append(nombre)
            else:
                player.hechizos_activos[nombre] = restantes

        for nombre in expirados:
            del player.hechizos_activos[nombre]
            hechizo = cls.definicion(nombre)
            if hechizo is None:
                continue
            # Revertir efecto del buff expirado
            reversion = {k: -v for k, v in hechizo.efectos.items() if k in ("fuerza", "tenacidad", "inteligencia", "defensa", "agilidad")}
            if reversion:
                player.aplicar_efectos(reversion)
