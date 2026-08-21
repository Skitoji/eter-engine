import random
from typing import Optional

from eter_core.components.player_component import PlayerComponent
from eter_core.domain.npcs import CATALOGO_NPCS


class NpcSystem:
    """
    Sistema de NPCs amistosos: interacción con el pueblo.

    Reglas de Dominio:
    - El posadero ofrece descanso (recupera vida y estamina) por oro.
    - La curandera cura heridas por oro.
    - El aldeano comparte rumores según el estado de la región.
    - El capitán informa sobre los peligros (infección) de la zona.
    """

    COSTE_DESCANSO: float = 10.0
    COSTE_CURACION: float = 15.0

    @classmethod
    def descansar(cls, player: PlayerComponent) -> Optional[str]:
        """
        El posadero ofrece descanso: recupera vida y estamina a cambio de oro.
        """
        if player.oro < cls.COSTE_DESCANSO:
            return None
        player.oro -= cls.COSTE_DESCANSO
        player.vida = player.vida_maxima
        player.estamina = player.estamina_maxima
        return f"Descansas en la posada y recuperas toda tu vida y estamina. (-{cls.COSTE_DESCANSO:.0f} oro)"

    @classmethod
    def curar(cls, player: PlayerComponent) -> Optional[str]:
        """
        La curandera cura heridas a cambio de oro.
        """
        if player.vida >= player.vida_maxima:
            return "No tienes heridas que curar."
        if player.oro < cls.COSTE_CURACION:
            return None
        player.oro -= cls.COSTE_CURACION
        player.vida = player.vida_maxima
        return f"La curandera sana tus heridas por completo. (-{cls.COSTE_CURACION:.0f} oro)"

    @classmethod
    def rumor(cls, infeccion: float, fervor: float, rng: Optional[random.Random] = None) -> str:
        """El aldeano comparte un rumor según el estado de la región."""
        randomizer = rng or random
        if infeccion > 0.6:
            rumores = [
                "Dicen que la infección demoníaca ya se ve desde las colinas.",
                "Los caminos del norte ya no son seguros, viajero.",
                "Vi a un wyvern sobrevolando las montañas. Mal presagio.",
            ]
        elif fervor < 0.35:
            rumores = [
                "La gente está perdiendo la fe. Ya nadie va a la iglesia.",
                "Se habla de cultos oscuros en las sombras del pueblo.",
                "La Santa Iglesia ya no responde como antes.",
            ]
        else:
            rumores = [
                "Las cosechas van bien este año, gracias a la Luz.",
                "Un mercader pasó ayer con noticias de la capital.",
                "Dicen que hay hierbas curativas en los valles cercanos.",
            ]
        return randomizer.choice(rumores)

    @classmethod
    def informe_capitan(cls, infeccion: float, monstruos: dict) -> str:
        """El capitán informa sobre la amenaza local."""
        nivel = infeccion * 100
        if monstruos:
            resumen = ', '.join(f"{nombre} x{cantidad}" for nombre, cantidad in monstruos.items())
            return f"Hay {resumen} merodeando. La infección está al {nivel:.0f}%."
        if infeccion > 0.5:
            return f"Zona peligrosa. La infección está al {nivel:.0f}%, aunque no se vean monstruos."
        return f"Zona tranquila. La infección está al {nivel:.0f}%."
