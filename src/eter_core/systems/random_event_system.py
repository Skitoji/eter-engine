import random
from dataclasses import dataclass
from typing import Callable, List, Optional

from eter_core.components.player_component import PlayerComponent


@dataclass(frozen=True)
class EventoAleatorio:
    """Evento de baja probabilidad que puede ocurrir durante el turno."""
    nombre: str
    descripcion: str
    probabilidad: float  # 0..1
    # Condición opcional: recibe al jugador y devuelve True si puede ocurrir
    condicion: Optional[Callable[[PlayerComponent], bool]] = None


class RandomEventSystem:
    """
    Sistema de eventos aleatorios de baja probabilidad.

    Reglas de Dominio:
    - Cada turno, se evalúan eventos de baja probabilidad.
    - Algunos eventos tienen condiciones (ej. el cuchillo que cae y alerta al
      dragón solo puede ocurrir si el jugador está invisible).
    - Un evento puede cancelar la invisibilidad (romper el sigilo).
    """

    @classmethod
    def _eventos_base(cls) -> List[EventoAleatorio]:
        def _esta_invisible(player: PlayerComponent) -> bool:
            return player.hechizos_activos.get("invisibilidad_area", 0) > 0

        return [
            EventoAleatorio(
                nombre="cuchillo_cae",
                descripcion="A un aliado se le cae un cuchillo. El ruido alerta a los enemigos y se rompe la invisibilidad.",
                probabilidad=0.03,
                condicion=_esta_invisible,
            ),
            EventoAleatorio(
                nombre="viento_favorable",
                descripcion="Un viento favorable acelera tu marcha. Recuperas 10 de estamina.",
                probabilidad=0.06,
            ),
            EventoAleatorio(
                nombre="hallazgo_moneda",
                descripcion="Encuentras una bolsa de monedas olvidada en el camino. +15 de oro.",
                probabilidad=0.05,
            ),
            EventoAleatorio(
                nombre="hambre_repentina",
                descripcion="El esfuerzo te abre el apetito. Pierdes 10 de hambre.",
                probabilidad=0.05,
            ),
        ]

    @classmethod
    def procesar(cls, player: PlayerComponent, rng: Optional[random.Random] = None) -> Optional[EventoAleatorio]:
        """
        Evalúa los eventos aleatorios del turno. Devuelve el evento ocurrido o None.
        """
        randomizer = rng or random
        for evento in cls._eventos_base():
            if evento.condicion is not None and not evento.condicion(player):
                continue
            if randomizer.random() < evento.probabilidad:
                cls._aplicar(player, evento)
                return evento
        return None

    @classmethod
    def _aplicar(cls, player: PlayerComponent, evento: EventoAleatorio) -> None:
        """Aplica las consecuencias del evento al jugador."""
        if evento.nombre == "cuchillo_cae":
            # Rompe la invisibilidad
            player.hechizos_activos.pop("invisibilidad_area", None)
        elif evento.nombre == "viento_favorable":
            player.estamina = min(player.estamina_maxima, player.estamina + 10)
        elif evento.nombre == "hallazgo_moneda":
            player.oro += 15.0
        elif evento.nombre == "hambre_repentina":
            player.hambre = max(0, player.hambre - 10)
