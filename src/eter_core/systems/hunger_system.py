from typing import Dict

from eter_core.components.player_component import PlayerComponent
from eter_core.domain.archetypes import CATALOGO_ARQUETIPOS


class HungerSystem:
    """
    Sistema de hambre ligado al ciclo del día.

    Reglas de Dominio:
    - El hambre baja cada turno (un turno ≈ un día).
    - El nivel de hambre afecta a los stats según el arquetipo:
      * Guerreros (fuerza) pierden Fuerza.
      * Magos pierden Maná máximo e Inteligencia.
    - Comer 2 veces al día te mantiene saciado; comer 1 vez te deja en un
      estado leve; no comer te degrada progresivamente.
    """

    HAMBRE_POR_TURNO: float = 25.0   # unidades de hambre que bajan por turno/día

    # Umbrales de hambre (0-100)
    UMBRAL_SACIADO: float = 70.0
    UMBRAL_HAMBRE_LEVE: float = 40.0

    @classmethod
    def _estat_por_arquetipo(cls, arquetipo: str) -> str:
        """Stat principal que degrada el hambre según el arquetipo."""
        return CATALOGO_ARQUETIPOS.get(arquetipo, None) and {
            "mago": "mana",
            "tanque": "tenacidad",
            "caballero": "fuerza",
            "asesino": "fuerza",
        }.get(arquetipo, "fuerza")

    @classmethod
    def avanzar(cls, player: PlayerComponent, delta_tiempo: float = 1.0) -> None:
        """Reduce el hambre del jugador al pasar el tiempo (un turno = un día)."""
        player.hambre = max(0, player.hambre - cls.HAMBRE_POR_TURNO * delta_tiempo)

    @classmethod
    def penalizaciones(cls, player: PlayerComponent) -> Dict[str, float]:
        """
        Devuelve las penalizaciones de stats según el hambre actual.
        Vacío si está saciado.
        """
        if player.hambre >= cls.UMBRAL_SACIADO:
            return {}

        stat = cls._estat_por_arquetipo(player.potencial_nacimiento)

        if player.hambre >= cls.UMBRAL_HAMBRE_LEVE:
            # Hambre leve: pequeña penalización al stat principal
            penalizacion: Dict[str, float] = {}
            if stat == "mana":
                penalizacion["mana_maximo"] = -10.0
            else:
                penalizacion[stat] = -2.0
            return penalizacion

        # Hambre severa: penalización fuerte al stat principal + debilidad general
        penalizacion = {"fuerza": -4.0, "tenacidad": -3.0}
        if stat == "mana":
            penalizacion = {"mana_maximo": -30.0, "inteligencia": -4.0}
        return penalizacion

    @classmethod
    def estado(cls, player: PlayerComponent) -> str:
        """Descripción legible del estado de hambre."""
        if player.hambre >= cls.UMBRAL_SACIADO:
            return "saciado"
        if player.hambre >= cls.UMBRAL_HAMBRE_LEVE:
            return "hambre leve"
        return "famélico"
