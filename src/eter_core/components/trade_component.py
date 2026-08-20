from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class TradeComponent:
    """Mercado local derivado de la geografia y el asentamiento Azgaar."""
    bioma: str = ""
    productos: List[str] = field(default_factory=list)
    oferta: Dict[str, float] = field(default_factory=dict)
    demanda: Dict[str, float] = field(default_factory=dict)
    coordenadas: Tuple[float, float] = (0.0, 0.0)
    tiene_ciudad: bool = False
    nombre_completo: str = ""