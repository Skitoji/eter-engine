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
    bonus_critico: float = 0.0
    potencial_nacimiento: str = "caballero"
    oro: float = 0.0           # riqueza líquida del jugador
    hambre: int = 100          # 100 = saciado, 0 = famélico
    inventario: Dict[str, int] = field(default_factory=lambda: {"brujula": 1, "raciones": 3, "antorcha": 1})
    materiales: Dict[str, int] = field(default_factory=dict)  # productos/drops de monstruos
    equipamiento: Dict[str, str] = field(default_factory=dict)  # slot -> clave de objeto
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

    def dar_material(self, nombre: str, cantidad: int = 1) -> None:
        """Añade un material/producto (drop de monstruo, mineral, alimento) al inventario."""
        self.materiales[nombre] = self.materiales.get(nombre, 0) + cantidad

    def tiene_material(self, nombre: str) -> bool:
        return self.materiales.get(nombre, 0) > 0

    def equipar(self, slot: str, nombre: str) -> None:
        """Equipa un objeto en un slot (arma, armadura, accesorio...)."""
        self.equipamiento[slot] = nombre

    def desequipar(self, slot: str) -> Optional[str]:
        """Retira y devuelve el objeto equipado en un slot, o None si estaba vacío."""
        return self.equipamiento.pop(slot, None)

    def aplicar_efectos(self, efectos: Dict[str, float]) -> None:
        """Aplica modificadores de stats, sin superar los máximos."""
        if "vida" in efectos:
            self.vida = min(self.vida_maxima, self.vida + efectos["vida"])
        if "mana" in efectos:
            self.mana = min(self.mana_maximo, self.mana + efectos["mana"])
        if "estamina" in efectos:
            self.estamina = min(self.estamina_maxima, self.estamina + efectos["estamina"])
        if "hambre" in efectos:
            self.hambre = min(100, max(0, self.hambre + efectos["hambre"]))
        if "fuerza" in efectos:
            self.fuerza += efectos["fuerza"]
        if "inteligencia" in efectos:
            self.inteligencia += efectos["inteligencia"]
        if "tenacidad" in efectos:
            self.tenacidad += efectos["tenacidad"]
