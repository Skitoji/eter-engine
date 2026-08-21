from eter_core.components.player_component import PlayerComponent
from eter_core.domain.items import CATALOGO_OBJETOS
from eter_core.domain.products import CATALOGO_PRODUCTOS


class WeightSystem:
    """
    Sistema de peso/carga: limita cuánto puede transportar el jugador.

    Reglas de Dominio:
    - Cada objeto y material tiene un peso.
    - El jugador tiene una capacidad máxima basada en su Fuerza.
    - Si supera la capacidad, queda sobrecargado (penaliza estamina/velocidad).
    """

    CAPACIDAD_BASE: float = 30.0
    CAPACIDAD_POR_FUERZA: float = 3.0

    @classmethod
    def capacidad_maxima(cls, player: PlayerComponent) -> float:
        """Capacidad de carga del jugador en unidades de peso."""
        return cls.CAPACIDAD_BASE + (player.fuerza * cls.CAPACIDAD_POR_FUERZA)

    @classmethod
    def peso_inventario(cls, player: PlayerComponent) -> float:
        """Peso total de los objetos del inventario."""
        total = 0.0
        for nombre, cantidad in player.inventario.items():
            definicion = CATALOGO_OBJETOS.get(nombre)
            if definicion is None:
                continue
            total += definicion.peso * cantidad
        return round(total, 2)

    @classmethod
    def peso_materiales(cls, player: PlayerComponent) -> float:
        """Peso total de los materiales/productos transportados."""
        total = 0.0
        for nombre, cantidad in player.materiales.items():
            definicion = CATALOGO_PRODUCTOS.get(nombre)
            if definicion is None:
                continue
            total += definicion.peso * cantidad
        return round(total, 2)

    @classmethod
    def peso_total(cls, player: PlayerComponent) -> float:
        """Peso total transportado (objetos + materiales)."""
        return round(cls.peso_inventario(player) + cls.peso_materiales(player), 2)

    @classmethod
    def esta_sobrecargado(cls, player: PlayerComponent) -> bool:
        """True si el jugador transporta más peso del que puede."""
        return cls.peso_total(player) > cls.capacidad_maxima(player)
