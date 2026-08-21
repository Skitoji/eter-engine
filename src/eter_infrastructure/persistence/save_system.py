import json
import os
from typing import Any, Dict, Optional

from eter_core.components.player_component import PlayerComponent
from eter_core.engine import EterEngine


class SaveSystem:
    """
    Sistema de persistencia: guarda y carga el estado del jugador.

    Reglas de Dominio:
    - Se guarda el estado completo del jugador (stats, inventario, equipamiento,
      oro, hambre, nivel, XP, posición) en un archivo JSON.
    - El mundo (mapa) se reconstruye desde Azgaar al cargar, así que solo se
      persiste el estado del jugador.
    """

    RUTA_DEFECTO: str = "save.json"

    @classmethod
    def guardar(cls, player: PlayerComponent, ruta: str = RUTA_DEFECTO) -> str:
        """Serializa el estado del jugador y lo escribe a disco. Devuelve la ruta."""
        estado = {
            "vida": player.vida,
            "vida_maxima": player.vida_maxima,
            "mana": player.mana,
            "mana_maximo": player.mana_maximo,
            "fuerza": player.fuerza,
            "inteligencia": player.inteligencia,
            "estamina": player.estamina,
            "estamina_maxima": player.estamina_maxima,
            "tenacidad": player.tenacidad,
            "bonus_critico": player.bonus_critico,
            "potencial_nacimiento": player.potencial_nacimiento,
            "nivel": player.nivel,
            "experiencia": player.experiencia,
            "oro": player.oro,
            "hambre": player.hambre,
            "inventario": dict(player.inventario),
            "materiales": dict(player.materiales),
            "equipamiento": dict(player.equipamiento),
            "hechizos_activos": dict(player.hechizos_activos),
            "marca_de_la_estrella": player.marca_de_la_estrella,
            "celda_actual": player.celda_actual,
            "provincia_actual": player.provincia_actual,
            "ayuda_recibida": sorted(player.ayuda_recibida),
        }
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(estado, f, ensure_ascii=False, indent=2)
        return ruta

    @classmethod
    def existe_partida(cls, ruta: str = RUTA_DEFECTO) -> bool:
        return os.path.exists(ruta)

    @classmethod
    def cargar(cls, ruta: str = RUTA_DEFECTO) -> Dict[str, Any]:
        """Carga el estado guardado del jugador desde disco."""
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    def aplicar(cls, player: PlayerComponent, estado: Dict[str, Any]) -> None:
        """Restaura el estado guardado sobre un PlayerComponent existente."""
        player.vida = estado.get("vida", player.vida)
        player.vida_maxima = estado.get("vida_maxima", player.vida_maxima)
        player.mana = estado.get("mana", player.mana)
        player.mana_maximo = estado.get("mana_maximo", player.mana_maximo)
        player.fuerza = estado.get("fuerza", player.fuerza)
        player.inteligencia = estado.get("inteligencia", player.inteligencia)
        player.estamina = estado.get("estamina", player.estamina)
        player.estamina_maxima = estado.get("estamina_maxima", player.estamina_maxima)
        player.tenacidad = estado.get("tenacidad", player.tenacidad)
        player.bonus_critico = estado.get("bonus_critico", player.bonus_critico)
        player.potencial_nacimiento = estado.get("potencial_nacimiento", player.potencial_nacimiento)
        player.nivel = estado.get("nivel", player.nivel)
        player.experiencia = estado.get("experiencia", player.experiencia)
        player.oro = estado.get("oro", player.oro)
        player.hambre = estado.get("hambre", player.hambre)
        player.inventario = dict(estado.get("inventario", player.inventario))
        player.materiales = dict(estado.get("materiales", player.materiales))
        player.equipamiento = dict(estado.get("equipamiento", player.equipamiento))
        player.hechizos_activos = dict(estado.get("hechizos_activos", player.hechizos_activos))
        player.marca_de_la_estrella = estado.get("marca_de_la_estrella", player.marca_de_la_estrella)
        player.celda_actual = estado.get("celda_actual", player.celda_actual)
        player.provincia_actual = estado.get("provincia_actual", player.provincia_actual)
        player.ayuda_recibida = set(estado.get("ayuda_recibida", player.ayuda_recibida))
