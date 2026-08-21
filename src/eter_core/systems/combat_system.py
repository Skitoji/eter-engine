import random
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional

from eter_core.components.player_component import PlayerComponent
from eter_core.domain.events import CombateResueltoEvent
from eter_core.domain.monsters import CATALOGO_MONSTRUOS, MonstruoDef
from eter_core.domain.spells import TipoHechizo
from eter_core.systems.hunger_system import HungerSystem
from eter_core.systems.item_system import ItemSystem
from eter_core.systems.set_system import SetSystem
from eter_core.systems.spell_system import SpellSystem
from eter_infrastructure.messaging.event_bus import EventBus


class AccionCombate(Enum):
    """Acciones tácticas disponibles para el jugador en cada turno."""
    ATACAR = auto()
    DEFENDER = auto()
    PARRY = auto()
    HECHIZO = auto()
    OBJETO = auto()
    HUIR = auto()


@dataclass
class CombateEstado:
    """Estado de un combate en curso (separa la sesión del jugador)."""
    monstruo_clave: str
    monstruo: MonstruoDef
    hp_monstruo: int
    turno: int = 0
    monstruo_defendiendo: bool = False
    finalizado: bool = False
    victoria: bool = False
    huido: bool = False
    daño_infligido: int = 0
    daño_recibido: int = 0
    drops: Dict[str, int] = field(default_factory=dict)
    log: List[str] = field(default_factory=list)


@dataclass
class ResultadoTurno:
    """Resultado narrativo y numérico de un turno de combate."""
    accion: AccionCombate
    detalle: str = ""
    daño_infligido: int = 0
    daño_recibido: int = 0
    esquivo_monstruo: bool = False
    esquivo_jugador: bool = False
    parry_exitoso: bool = False
    huida_exitosa: bool = False
    finalizado: bool = False
    victoria: bool = False
    huido: bool = False


class CombatSystem:
    """
    Combate táctico por turnos entre el Hijo de la Luz y un monstruo del bestiario.

    El jugador elige una acción cada turno y el monstruo responde con una IA
    simple (ataca, carga un golpe fuerte o se defiende).

    Reglas de Dominio:
    - Daño del jugador = Fuerza (+equipo/sets/buffs) con probabilidad de crítico.
    - La Tenacidad mitiga daño (cuerpo) y la Defensa lo bloquea (armadura).
    - Agilidad determina esquiva, parry e iniciativa de huida.
    - Defender reduce el daño recibido a la mitad y recupera estamina.
    - Parry anula el golpe y permite ripostar, pero fallar expone al jugador.
    """

    MITIGACION_TENACIDAD: float = 0.5
    MULTIPLICADOR_CRITICO: float = 2.0
    REDUCCION_DEFENDER: float = 0.5
    MULTIPLICADOR_GOLPE_FUERTE: float = 1.5
    PROB_ESQUIVA_POR_AGILIDAD: float = 0.01
    CAP_ESQUIVA: float = 0.50
    PARRY_BASE: float = 0.20
    PARRY_POR_AGILIDAD: float = 0.01
    CAP_PARRY: float = 0.75
    HUIR_BASE: float = 0.55
    HUIR_POR_DIF_AGILIDAD: float = 0.03
    HUIR_POR_TIER: float = 0.10
    COSTE_ESTAMINA_ATACAR: int = 5
    ESTAMINA_DEFENDER: int = 10

    # ── Stats derivados ─────────────────────────────────────────────
    @classmethod
    def _agilidad_jugador(cls, player: PlayerComponent) -> float:
        bonos = ItemSystem.bonos_equipados(player)
        sets = SetSystem.bonus_sets(player)
        return player.agilidad + bonos.get("agilidad", 0.0) + sets.get("agilidad", 0.0)

    @classmethod
    def _defensa_jugador(cls, player: PlayerComponent) -> float:
        bonos = ItemSystem.bonos_equipados(player)
        sets = SetSystem.bonus_sets(player)
        return player.defensa + bonos.get("defensa", 0.0) + sets.get("defensa", 0.0)

    @classmethod
    def _tenacidad_jugador(cls, player: PlayerComponent) -> float:
        bonos = ItemSystem.bonos_equipados(player)
        sets = SetSystem.bonus_sets(player)
        penalizaciones = HungerSystem.penalizaciones(player)
        return (
            player.tenacidad
            + bonos.get("tenacidad", 0.0)
            + sets.get("tenacidad", 0.0)
            + penalizaciones.get("tenacidad", 0.0)
        )

    @classmethod
    def _mitigacion_jugador(cls, player: PlayerComponent) -> float:
        return cls._tenacidad_jugador(player) * cls.MITIGACION_TENACIDAD + cls._defensa_jugador(player)

    # ── Cálculo de daño ─────────────────────────────────────────────
    @classmethod
    def daño_jugador(cls, player: PlayerComponent, rng: random.Random) -> int:
        """Daño de un golpe del jugador (con crítico y penalización de hambre)."""
        bonos = ItemSystem.bonos_equipados(player)
        bonos_set = SetSystem.bonus_sets(player)
        penalizaciones = HungerSystem.penalizaciones(player)
        fuerza = (
            player.fuerza
            + bonos.get("fuerza", 0.0)
            + bonos_set.get("fuerza", 0.0)
            + penalizaciones.get("fuerza", 0.0)
        )
        daño = max(1, int(fuerza))
        critico = player.bonus_critico + bonos_set.get("bonus_critico", 0.0)
        if rng.random() < critico:
            daño = int(daño * cls.MULTIPLICADOR_CRITICO)
        return daño

    @classmethod
    def daño_monstruo(cls, monstruo: MonstruoDef, player: PlayerComponent, base: Optional[int] = None) -> int:
        """Daño que el monstruo inflige, mitigado por tenacidad y defensa."""
        base_daño = monstruo.ataque if base is None else base
        return max(1, int(base_daño - cls._mitigacion_jugador(player)))

    # ── Probabilidades ──────────────────────────────────────────────
    @classmethod
    def prob_esquiva(cls, agilidad: float) -> float:
        """Probabilidad de esquivar un golpe (1% por punto de agilidad, máx 50%)."""
        return min(cls.CAP_ESQUIVA, max(0.0, agilidad * cls.PROB_ESQUIVA_POR_AGILIDAD))

    @classmethod
    def prob_parry(cls, agilidad: float) -> float:
        """Probabilidad de parar y ripostar (base + 1% por punto, máx 75%)."""
        return min(cls.CAP_PARRY, max(0.0, cls.PARRY_BASE + agilidad * cls.PARRY_POR_AGILIDAD))

    @classmethod
    def prob_huida(cls, player: PlayerComponent, monstruo: MonstruoDef) -> float:
        """Probabilidad de huir con éxito (agilidad propia vs. agilidad y tier del monstruo)."""
        agilidad = cls._agilidad_jugador(player)
        prob = (
            cls.HUIR_BASE
            + (agilidad - monstruo.agilidad) * cls.HUIR_POR_DIF_AGILIDAD
            - (monstruo.tier - 1) * cls.HUIR_POR_TIER
        )
        return min(0.95, max(0.05, prob))

    # ── Ciclo de vida del combate ───────────────────────────────────
    @classmethod
    def iniciar(cls, player: PlayerComponent, monstruo_clave: str) -> CombateEstado:
        """Crea el estado inicial de un combate contra un monstruo del bestiario."""
        if monstruo_clave not in CATALOGO_MONSTRUOS:
            raise ValueError(f"Monstruo desconocido: {monstruo_clave}")
        monstruo = CATALOGO_MONSTRUOS[monstruo_clave]
        return CombateEstado(monstruo_clave=monstruo_clave, monstruo=monstruo, hp_monstruo=monstruo.vida)

    @classmethod
    def turno_jugador(
        cls,
        player: PlayerComponent,
        estado: CombateEstado,
        accion: AccionCombate,
        rng: Optional[random.Random] = None,
        nombre: Optional[str] = None,
    ) -> ResultadoTurno:
        """
        Resuelve un turno completo: la acción del jugador y la respuesta del monstruo.

        - `accion`: qué hace el jugador este turno.
        - `nombre`: clave del hechizo (HECHIZO) o del objeto (OBJETO).
        """
        randomizer = rng or random.Random()
        res = ResultadoTurno(accion=accion)

        if estado.finalizado:
            res.detalle = "El combate ya ha terminado."
            res.finalizado = True
            res.victoria = estado.victoria
            res.huido = estado.huido
            return res

        estado.turno += 1

        if accion == AccionCombate.ATACAR:
            cls._resolver_ataque(player, estado, randomizer, res)
        elif accion == AccionCombate.DEFENDER:
            cls._resolver_defender(player, res)
        elif accion == AccionCombate.PARRY:
            res.detalle = "Adoptas una postura de parry, listo para desviar y ripostar."
        elif accion == AccionCombate.HECHIZO:
            cls._resolver_hechizo(player, estado, nombre, res)
        elif accion == AccionCombate.OBJETO:
            cls._resolver_objeto(player, nombre, res)
        elif accion == AccionCombate.HUIR:
            return cls._resolver_huida(player, estado, randomizer, res)
        else:
            res.detalle = "Acción desconocida."

        if estado.hp_monstruo <= 0:
            return cls._resolver_victoria(player, estado, randomizer, res)

        cls._turno_monstruo(player, estado, randomizer, res, accion)

        if estado.hp_monstruo <= 0:
            return cls._resolver_victoria(player, estado, randomizer, res)
        if player.vida <= 0:
            return cls._resolver_derrota(player, estado, res)

        return res

    # ── Acciones del jugador ────────────────────────────────────────
    @classmethod
    def _resolver_ataque(cls, player, estado, rng, res) -> None:
        monstruo = estado.monstruo
        player.estamina = max(0, player.estamina - cls.COSTE_ESTAMINA_ATACAR)
        if rng.random() < cls.prob_esquiva(monstruo.agilidad):
            res.esquivo_monstruo = True
            res.detalle = f"{monstruo.nombre} esquiva tu golpe."
            return
        daño = cls.daño_jugador(player, rng)
        extras: List[str] = []
        if estado.monstruo_defendiendo:
            daño = max(1, int(daño * cls.REDUCCION_DEFENDER))
            estado.monstruo_defendiendo = False
            extras.append("se defendía")
        daño = max(1, daño - monstruo.defensa)
        estado.hp_monstruo -= daño
        estado.daño_infligido += daño
        res.daño_infligido += daño
        sufijo = f" ({', '.join(extras)})" if extras else ""
        res.detalle = f"Golpeas a {monstruo.nombre} por {daño} de daño{sufijo}."

    @classmethod
    def _resolver_defender(cls, player, res) -> None:
        player.estamina = min(player.estamina_maxima, player.estamina + cls.ESTAMINA_DEFENDER)
        res.detalle = "Te pones en guardia: recibirás la mitad de daño este turno y recuperas estamina."

    @classmethod
    def _resolver_hechizo(cls, player, estado, nombre, res) -> None:
        monstruo = estado.monstruo
        hechizo = SpellSystem.definicion(nombre) if nombre else None
        if hechizo is None:
            res.detalle = "No conoces ese hechizo."
            return
        mensaje = SpellSystem.lanzar(player, nombre)
        if mensaje is None:
            res.detalle = f"No puedes lanzar {hechizo.nombre} (maná insuficiente)."
            return
        if hechizo.tipo == TipoHechizo.DANO:
            daño = max(1, int(hechizo.efectos.get("dano", 0)) - monstruo.defensa)
            estado.hp_monstruo -= daño
            estado.daño_infligido += daño
            res.daño_infligido += daño
            res.detalle = f"{mensaje} Infliges {daño} de daño mágico a {monstruo.nombre}."
        else:
            res.detalle = mensaje

    @classmethod
    def _resolver_objeto(cls, player, nombre, res) -> None:
        if not nombre:
            res.detalle = "Debes indicar un objeto."
            return
        mensaje = ItemSystem.usar_objeto(player, nombre)
        res.detalle = mensaje if mensaje else f"No puedes usar {nombre} ahora."

    @classmethod
    def _resolver_huida(cls, player, estado, rng, res) -> ResultadoTurno:
        if rng.random() < cls.prob_huida(player, estado.monstruo):
            res.huida_exitosa = True
            res.huido = True
            estado.huido = True
            estado.finalizado = True
            res.finalizado = True
            res.detalle = f"Consigues huir de {estado.monstruo.nombre}."
            cls._publicar_evento(estado)
            return res
        daño = cls.daño_monstruo(estado.monstruo, player)
        player.vida = max(0, player.vida - daño)
        estado.daño_recibido += daño
        res.daño_recibido += daño
        res.detalle = f"No consigues huir. {estado.monstruo.nombre} te golpea por {daño}."
        if player.vida <= 0:
            return cls._resolver_derrota(player, estado, res)
        return res

    # ── Turno del monstruo ──────────────────────────────────────────
    @classmethod
    def _turno_monstruo(cls, player, estado, rng, res, accion_jugador) -> None:
        monstruo = estado.monstruo
        roll = rng.random()
        if roll < 0.10:
            estado.monstruo_defendiendo = True
            res.detalle += f" {monstruo.nombre} se prepara para defenderse."
            return
        multiplicador = cls.MULTIPLICADOR_GOLPE_FUERTE if roll < 0.30 else 1.0
        cls._ataque_monstruo(player, estado, rng, res, accion_jugador, multiplicador)

    @classmethod
    def _ataque_monstruo(cls, player, estado, rng, res, accion_jugador, multiplicador) -> None:
        monstruo = estado.monstruo

        if accion_jugador == AccionCombate.PARRY:
            if rng.random() < cls.prob_parry(cls._agilidad_jugador(player)):
                res.parry_exitoso = True
                riposta = max(1, cls.daño_jugador(player, rng) - monstruo.defensa)
                estado.hp_monstruo -= riposta
                estado.daño_infligido += riposta
                res.daño_infligido += riposta
                res.detalle += f" ¡Parry! Desvías el golpe de {monstruo.nombre} y ripostas por {riposta}."
                return
            res.detalle += " Intentas parar y fallas."
        elif rng.random() < cls.prob_esquiva(cls._agilidad_jugador(player)):
            res.esquivo_jugador = True
            res.detalle += f" Esquivas el golpe de {monstruo.nombre}."
            return

        base = int(monstruo.ataque * multiplicador)
        daño = cls.daño_monstruo(monstruo, player, base=base)
        if accion_jugador == AccionCombate.DEFENDER:
            daño = max(1, int(daño * cls.REDUCCION_DEFENDER))
        player.vida = max(0, player.vida - daño)
        estado.daño_recibido += daño
        res.daño_recibido += daño
        desc = "golpe cargado" if multiplicador > 1.0 else "golpe"
        res.detalle += f" {monstruo.nombre} te asesta un {desc} por {daño} de daño."

    # ── Finalización ────────────────────────────────────────────────
    @classmethod
    def _resolver_victoria(cls, player, estado, rng, res) -> ResultadoTurno:
        estado.finalizado = True
        estado.victoria = True
        res.finalizado = True
        res.victoria = True
        for producto, probabilidad in estado.monstruo.drops.items():
            if rng.random() < probabilidad:
                estado.drops[producto] = estado.drops.get(producto, 0) + 1
        for producto, cantidad in estado.drops.items():
            player.dar_material(producto, cantidad)
        res.detalle += f" 🏆 ¡Vences a {estado.monstruo.nombre}!"
        cls._publicar_evento(estado)
        return res

    @classmethod
    def _resolver_derrota(cls, player, estado, res) -> ResultadoTurno:
        estado.finalizado = True
        res.finalizado = True
        res.detalle += " 💀 Has caído en combate."
        cls._publicar_evento(estado)
        return res

    @classmethod
    def _publicar_evento(cls, estado) -> None:
        EventBus.publicar(
            CombateResueltoEvent(
                monstruo=estado.monstruo_clave,
                victoria=estado.victoria,
                daño_infligido=estado.daño_infligido,
                daño_recibido=estado.daño_recibido,
                drops=dict(estado.drops),
                huido=estado.huido,
            )
        )
