from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class NpcDef:
    """Definición de un NPC amistoso que habita en ciudades y pueblos."""
    nombre: str
    rol: str
    descripcion: str
    saludo: str


CATALOGO_NPCS: Dict[str, NpcDef] = {
    "posadero": NpcDef(
        nombre="Posadero",
        rol="posadero",
        descripcion="Ofrece descanso a cambio de oro.",
        saludo="Entra, viajero. Una cama caliente y una buena comida te esperan.",
    ),
    "cura": NpcDef(
        nombre="Curandera",
        rol="cura",
        descripcion="Sana tus heridas con hierbas y plegarias.",
        saludo="La Luz te proteja. Déjame ver esas heridas.",
    ),
    "herrero": NpcDef(
        nombre="Herrero",
        rol="herrero",
        descripcion="Forja armas y armaduras con los materiales que le traigas.",
        saludo="El metal canta cuando se trabaja. ¿Qué necesitas forjar?",
    ),
    "mercader": NpcDef(
        nombre="Mercader",
        rol="mercader",
        descripcion="Compra y vende mercancías de todo Éter.",
        saludo="Bienvenido, bienvenido. Tengo lo que buscas... por un precio justo.",
    ),
    "capitan": NpcDef(
        nombre="Capitán de la Guardia",
        rol="capitan",
        descripcion="Conoce los peligros de la región y los monstruos cercanos.",
        saludo="Mantente alerta fuera de las murallas. La infección se acerca.",
    ),
    "aldeano": NpcDef(
        nombre="Aldeano",
        rol="aldeano",
        descripcion="Comparte rumores y consejos locales.",
        saludo="¿Has oído las últimas noticias del camino?",
    ),
}


def npcs_por_ubicacion(tiene_ciudad: bool) -> list[str]:
    """
    Devuelve los roles de NPC presentes según la ubicación.
    Las ciudades tienen servicios completos; los pueblos, menos.
    """
    if tiene_ciudad:
        return ["posadero", "cura", "herrero", "mercader", "capitan", "aldeano"]
    return ["aldeano", "cura"]
