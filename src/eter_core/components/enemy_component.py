from dataclasses import dataclass


@dataclass
class EnemyComponent:
    """Presencia de fuerzas hostiles en una región (magos oscuros y cultistas)."""
    magos_oscuros: int = 0
    cultistas: int = 0
