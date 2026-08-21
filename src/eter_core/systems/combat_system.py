import random
from dataclasses import dataclass, field
from typing import Dict, Optional

from eter_core.components.player_component import PlayerComponent
from eter_core.domain.events import CombateResueltoEvent
from eter_core.domain.monsters import CATALOGO_MONSTRUOS, MonstruoDef
from eter_core.systems.hunger_system import HungerSystem
from eter_core.systems.item_system import ItemSystem
from eter_infrastructure.messaging.event_bus import EventBus


@dataclass
class ResultadoCombate:
    """Resultado inmutable de un combate jugador vs monstruo."""
    victoria: bool
    monstruo: str
    turnos: int
    daño_infligido: int
    daño_recibido: int
    drops: Dict[str, int] = field(default_factory=dict)


class CombatSystem:
    """
    Resuelve combates por turnos entre el Hijo de la Luz y un monstruo del bestiario.

    Reglas de Dominio:
    - El daño del jugador se basa en su Fuerza (más bonos de equipamiento).
    - El jugador tiene probabilidad `bonus_critico` de golpe crítico (x2).
    - La Tenacidad del jugador reduce el daño recibido.
    - Al vencer, el monstruo suelta sus drops según la probabilidad del bestiario.
    """

    MITIGACION_TENACIDAD: float = 0.5   # cada punto de tenacidad reduce X de daño
    MULTIPLICADOR_CRITICO: float = 2.0

    @classmethod
    def daño_jugador(cls, player: PlayerComponent, rng: random.Random) -> int:
        """Calcula el daño de un golpe del jugador (con crítico y penalización de hambre)."""
        bonos = ItemSystem.bonos_equipados(player)
        penalizaciones = HungerSystem.penalizaciones(player)
        fuerza = player.fuerza + bonos.get("fuerza", 0.0) + penalizaciones.get("fuerza", 0.0)
        daño = max(1, int(fuerza))
        if rng.random() < player.bonus_critico:
            daño = int(daño * cls.MULTIPLICADOR_CRITICO)
        return daño

    @classmethod
    def daño_monstruo(cls, monstruo: MonstruoDef, player: PlayerComponent) -> int:
        """Calcula el daño que el monstruo inflige, mitigado por la tenacidad."""
        penalizaciones = HungerSystem.penalizaciones(player)
        tenacidad = player.tenacidad + penalizaciones.get("tenacidad", 0.0)
        mitigacion = max(0.0, tenacidad) * cls.MITIGACION_TENACIDAD
        return max(1, int(monstruo.ataque - mitigacion))

    @classmethod
    def resolver(
        cls,
        player: PlayerComponent,
        monstruo_clave: str,
        rng: Optional[random.Random] = None,
        max_turnos: int = 50,
    ) -> ResultadoCombate:
        """Simula el combate por turnos y devuelve el resultado (no muta al jugador)."""
        if monstruo_clave not in CATALOGO_MONSTRUOS:
            raise ValueError(f"Monstruo desconocido: {monstruo_clave}")
        randomizer = rng or random.Random()
        monstruo = CATALOGO_MONSTRUOS[monstruo_clave]

        hp_monstruo = monstruo.vida
        hp_jugador = player.vida
        turnos = 0
        daño_infligido = 0
        daño_recibido = 0

        while hp_monstruo > 0 and hp_jugador > 0 and turnos < max_turnos:
            turnos += 1
            # Golpe del jugador
            golpe = cls.daño_jugador(player, randomizer)
            hp_monstruo -= golpe
            daño_infligido += golpe
            if hp_monstruo <= 0:
                break
            # Contraataque del monstruo
            golpe_recibido = cls.daño_monstruo(monstruo, player)
            hp_jugador -= golpe_recibido
            daño_recibido += golpe_recibido

        victoria = hp_monstruo <= 0
        drops: Dict[str, int] = {}
        if victoria:
            for producto, probabilidad in monstruo.drops.items():
                if randomizer.random() < probabilidad:
                    drops[producto] = drops.get(producto, 0) + 1

        resultado = ResultadoCombate(
            victoria=victoria,
            monstruo=monstruo_clave,
            turnos=turnos,
            daño_infligido=daño_infligido,
            daño_recibido=daño_recibido,
            drops=drops,
        )
        EventBus.publicar(
            CombateResueltoEvent(
                monstruo=monstruo_clave,
                victoria=victoria,
                daño_infligido=daño_infligido,
                daño_recibido=daño_recibido,
                drops=drops,
            )
        )
        return resultado

    @classmethod
    def aplicar_resultado(cls, player: PlayerComponent, resultado: ResultadoCombate) -> None:
        """Aplica las consecuencias del combate: daño recibido y drops al ganar."""
        player.vida = max(0, player.vida - resultado.daño_recibido)
        for producto, cantidad in resultado.drops.items():
            player.dar_material(producto, cantidad)
