from dataclasses import dataclass, field
from typing import Dict


@dataclass
class StockComponent:
    """Stock de mercancías de los NPCs de una provincia (mercader/herrero)."""
    oferta: Dict[str, float] = field(default_factory=dict)   # producto -> cantidad ofertada
    demanda: Dict[str, float] = field(default_factory=dict)  # producto -> demanda local
