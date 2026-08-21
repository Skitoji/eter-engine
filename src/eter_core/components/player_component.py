from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class PlayerComponent:
    """Estado persistente del Hijo de la Luz."""
    vida: int = 100
    vida_maxima: int = 100
    mana: int = 50
    mana_maximo: int = 50
    fuerza: int = 10
    inteligencia: int = 10
    estamina: int = 100
    estamina_maxima: int = 100
    tenacidad: int = 10
    potencial_nacimiento: str = "Caballero"
    inventario: Dict[str, int] = field(default_factory=lambda: {"brujula": 1, "raciones": 3, "antorcha": 1})
    objeto_equipado: Optional[str] = None
    marca_de_la_estrella: str = "pecho"
    celda_actual: int = 0
    provincia_actual: int = 0
    ayuda_recibida: set[int] = field(default_factory=set)

    def esta_vivo(self) -> bool:
        return self.vida > 0

    @property
    def kit_explorador(self) -> list[str]:
        """Compatibilidad de lectura con la interfaz anterior."""
        return [item for item, cantidad in self.inventario.items() for _ in range(cantidad)]

    def tiene(self, nombre: str) -> bool:
        return self.inventario.get(nombre, 0) > 0

    def consumir(self, nombre: str) -> bool:
        if not self.tiene(nombre):
            return False
        self.inventario[nombre] -= 1
        if self.inventario[nombre] <= 0:
            del self.inventario[nombre]
        return True

    def equipar(self, nombre: str) -> bool:
        if not self.tiene(nombre):
            return False
        self.objeto_equipado = nombre
        return True

    def aplicar_efectos(self, efectos: Dict[str, float]) -> None:
        """Aplica modificadores de stats, sin superar los máximos."""
        if "vida" in efectos:
            self.vida = min(self.vida_maxima, self.vida + efectos["vida"])
        if "mana" in efectos:
            self.mana = min(self.mana_maximo, self.mana + efectos["mana"])
        if "estamina" in efectos:
            self.estamina = min(self.estamina_maxima, self.estamina + efectos["estamina"])
        if "fuerza" in efectos:
            self.fuerza += efectos["fuerza"]
        if "inteligencia" in efectos:
            self.inteligencia += efectos["inteligencia"]
        if "tenacidad" in efectos:
            self.tenacidad += efectos["tenacidad"]
