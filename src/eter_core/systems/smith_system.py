from typing import Optional

from eter_core.components.player_component import PlayerComponent
from eter_core.domain.items import CATALOGO_OBJETOS
from eter_core.domain.recipes import RECETAS_HERRERIA, Receta
from eter_core.systems.item_system import ItemSystem


class SmithSystem:
    """
    Sistema de forja (herrero): transforma materiales + oro en equipo.

    Reglas de Dominio:
    - El jugador debe poseer todos los materiales requeridos por la receta.
    - El herrero cobra un coste en oro adicional.
    - El resultado es un objeto equipable que pasa al inventario del jugador.
    """

    @classmethod
    def recetas_disponibles(cls) -> list[Receta]:
        return list(RECETAS_HERRERIA.values())

    @classmethod
    def forjar(cls, player: PlayerComponent, receta_clave: str) -> Optional[str]:
        """
        Forja un objeto a partir de una receta. Devuelve mensaje descriptivo
        o None si no puede forjarse (receta inexistente, materiales u oro
        insuficientes).
        """
        receta = RECETAS_HERRERIA.get(receta_clave)
        if receta is None:
            return None
        if receta.resultado not in CATALOGO_OBJETOS:
            return None

        # Validar materiales
        for material, cantidad in receta.materiales.items():
            if player.materiales.get(material, 0) < cantidad:
                return None

        # Validar oro
        if player.oro < receta.coste_oro:
            return None

        # Consumir materiales
        for material, cantidad in receta.materiales.items():
            player.materiales[material] -= cantidad
            if player.materiales[material] <= 0:
                del player.materiales[material]

        # Cobrar oro y entregar el objeto
        player.oro -= receta.coste_oro
        ItemSystem.dar_objeto(player, receta.resultado, 1)

        objeto = CATALOGO_OBJETOS[receta.resultado]
        return f"Forjas {objeto.nombre} ({receta.nombre})."

    @classmethod
    def puede_forjar(cls, player: PlayerComponent, receta_clave: str) -> bool:
        """Comprueba si el jugador puede forjar una receta (sin consumir nada)."""
        receta = RECETAS_HERRERIA.get(receta_clave)
        if receta is None:
            return False
        if player.oro < receta.coste_oro:
            return False
        return all(player.materiales.get(material, 0) >= cantidad for material, cantidad in receta.materiales.items())
