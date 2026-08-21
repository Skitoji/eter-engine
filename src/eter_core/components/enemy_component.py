from dataclasses import dataclass, field
from typing import Dict


@dataclass
class EnemyComponent:
    """
    Presencia de fuerzas hostiles en una región.

    - `magos_oscuros` y `cultistas`: generados por FaithSystem (amenaza religiosa).
    - `monstruos`: criaturas salvajes del bestiario, clave -> cantidad.
    """
    magos_oscuros: int = 0
    cultistas: int = 0
    monstruos: Dict[str, int] = field(default_factory=dict)
