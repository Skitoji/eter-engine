import glob
import os
import random
import sys
from typing import Dict, Optional, Tuple

sys.path.insert(0, os.path.abspath("src"))

from eter_core.components.economy_component import EconomyComponent
from eter_core.components.enemy_component import EnemyComponent
from eter_core.components.player_component import PlayerComponent
from eter_core.components.region_component import RegiónComponent, StateComponent, TerritoryComponent
from eter_core.components.trade_component import TradeComponent
from eter_core.domain.events import ComercioRealizadoEvent, HegemoniaIglesiaRotasEvent
from eter_core.domain.types import FaccionTipo, FervorReligioso, NivelInfeccion
from eter_core.engine import EterEngine
from eter_core.systems.economic_system import EconomicSystem
from eter_core.systems.spawn_system import SpawnSystem
from eter_infrastructure.messaging.event_bus import EventBus
from eter_infrastructure.persistence.azgaar_loader import AzgaarTranslator


def al_romperse_hegemonia(evento: HegemoniaIglesiaRotasEvent) -> None:
    print(f"\n[EVENTO CRITICO] La fe ha colapsado en {evento.nombre_region}.")


def al_realizarse_comercio(evento: ComercioRealizadoEvent) -> None:
    print(f"[COMERCIO] Flujo completado: {evento.valor:.1f} de oro.")


EventBus.suscribir(HegemoniaIglesiaRotasEvent, al_romperse_hegemonia)
EventBus.suscribir(ComercioRealizadoEvent, al_realizarse_comercio)


def _ruta_mapa() -> str:
    requested = os.path.join("data", "map_azgaar.json")
    if os.path.exists(requested):
        return requested
    candidates = glob.glob(os.path.join("data", "*Full*.json"))
    if candidates:
        return candidates[0]
    raise FileNotFoundError("No se encontro data/map_azgaar.json ni una exportacion Full de Azgaar.")


def cargar_mundo() -> Tuple[EterEngine, Dict[int, int], Dict[int, int], float]:
    translator = AzgaarTranslator(_ruta_mapa())
    states = translator.extract_states()
    regions = translator.extract_regions()
    engine = EterEngine()
    state_entities: Dict[int, int] = {}
    province_entities: Dict[int, int] = {}
    province_names: Dict[str, int] = {}
    province_state_names: Dict[int, str] = {}

    for state_id, state in states.items():
        entity_id = engine.crear_entidad()
        state_entities[state_id] = entity_id
        engine.agregar_componente(entity_id, StateComponent(state_id, state.name, state.color, list(state.provinces)))
        engine.agregar_componente(entity_id, EconomyComponent(oro=100.0))

    for province_id, data in regions.items():
        entity_id = engine.crear_entidad()
        province_entities[province_id] = entity_id
        state_name = states[data.state_id].name if data.state_id in states else "Estado desconocido"
        population = max(100, len(data.cell_ids) * 100)
        fervor = 0.55 if data.religion_id else 0.35
        infection = min(0.60, 0.05 + (province_id % 7) * 0.03)
        engine.agregar_componente(entity_id, RegiónComponent(data.name, population, FervorReligioso(fervor), NivelInfeccion(infection), FaccionTipo.SANTA_IGLESIA))
        engine.agregar_componente(entity_id, TerritoryComponent(province_id, data.state_id))
        engine.agregar_componente(entity_id, EconomyComponent(oro=50.0, produccion=max(10.0, population / 100.0)))
        market = EconomicSystem.crear_mercado(data.biome, data.coordinates, data.has_city)
        market.nombre_completo = data.full_name
        engine.agregar_componente(entity_id, market)
        engine.agregar_componente(entity_id, EnemyComponent())
        province_names[data.name.casefold()] = entity_id
        province_names[f"{data.name} {province_id}".casefold()] = entity_id
        province_state_names[province_id] = state_name

    raw_adjacencies = translator.extract_adjacencies(set(province_entities))
    engine.adyacencias = {
        province_entities[origin]: {province_entities[destination] for destination in destinations if destination in province_entities}
        for origin, destinations in raw_adjacencies.items()
        if origin in province_entities
    }
    engine.province_names = province_names
    engine.province_state_names = province_state_names
    engine.map_raw = translator.raw_map
    engine.province_entities = province_entities
    return engine, state_entities, province_entities, 5000.0


def _resolver_provincia(engine: EterEngine, text: str) -> Optional[int]:
    return engine.province_names.get(text.strip().casefold())


def _separar_comercio(engine: EterEngine, text: str) -> Optional[Tuple[int, int]]:
    tokens = text.split()
    for split_at in range(1, len(tokens)):
        origin = _resolver_provincia(engine, " ".join(tokens[:split_at]))
        destination = _resolver_provincia(engine, " ".join(tokens[split_at:]))
        if origin is not None and destination is not None:
            return origin, destination
    return None


def _provincia_actual(engine: EterEngine, player: PlayerComponent) -> int:
    return engine.province_entities[player.provincia_actual]


def _celda_de_provincia(engine: EterEngine, province_id: int) -> int:
    cells = SpawnSystem.celdas_terrestres(engine.map_raw, engine.province_entities)
    province_cells = [cell_id for cell_id, cell_province in cells if cell_province == province_id]
    return random.choice(province_cells) if province_cells else 0


def _nombre_actual(engine: EterEngine, player: PlayerComponent) -> str:
    return engine.componentes[RegiónComponent][_provincia_actual(engine, player)].nombre


def _mostrar_estado_jugador(engine: EterEngine, player: PlayerComponent, ciclo: int) -> None:
    territory = engine.componentes[TerritoryComponent][_provincia_actual(engine, player)]
    print("\n" + "=" * 60)
    print(f"HIJO DE LA LUZ | Turno {ciclo} | {_nombre_actual(engine, player)} ({engine.province_state_names[territory.azgaar_id]})")
    print(f"Potencial: {player.potencial_nacimiento} | Marca de la Estrella: {player.marca_de_la_estrella}")
    print(f"HP {player.vida}/{player.vida_maxima} | Mana {player.mana}/{player.mana_maximo} | Estamina {player.estamina}/{player.estamina_maxima}")
    print(f"Fuerza {player.fuerza} | Inteligencia {player.inteligencia} | Tenacidad {player.tenacidad}")
    inventario = ', '.join(f"{item} x{cantidad}" for item, cantidad in player.inventario.items()) or "vacio"
    print(f"Inventario: {inventario} | Equipado: {player.objeto_equipado or 'ninguno'}")
    print("=" * 60)


def _mostrar_menu_local(engine: EterEngine, player: PlayerComponent) -> Dict[str, int]:
    current = _provincia_actual(engine, player)
    neighbours = sorted(engine.adyacencias.get(current, set()), key=lambda entity: engine.componentes[RegiónComponent][entity].nombre)
    print(f"Estas en {_nombre_actual(engine, player)}. Puedes:")
    print("[1] Moverte a una provincia adyacente")
    for index, entity_id in enumerate(neighbours, start=1):
        print(f"    mover {index}: {engine.componentes[RegiónComponent][entity_id].nombre}")
    print("[2] Explorar la zona")
    print("[3] Usar objeto")
    print("[4] Pasar turno")
    return {str(index): entity_id for index, entity_id in enumerate(neighbours, start=1)}


def _mostrar_provincia(engine: EterEngine, entity_id: int) -> None:
    region = engine.componentes[RegiónComponent][entity_id]
    economy = engine.componentes[EconomyComponent][entity_id]
    territory = engine.componentes[TerritoryComponent][entity_id]
    market = engine.componentes[TradeComponent][entity_id]
    print(f"\n--- {region.nombre.upper()} ---")
    print(f"Pais: {engine.province_state_names[territory.azgaar_id]}")
    print(f"Poblacion: {region.poblacion_total} | Infeccion: {region.infeccion.valor * 100:.1f}% | Fervor: {region.fervor.valor * 100:.1f}%")
    print(f"Oro: {economy.oro:.1f} | Produccion: {economy.produccion:.1f} | Desarrollo: {economy.nivel_desarrollo}")
    print(f"Geografia: {market.bioma} | Ciudad: {'si' if market.tiene_ciudad else 'no'} | Productos: {', '.join(market.productos)}")


def _contexto_local(engine: EterEngine, player: PlayerComponent) -> None:
    entity_id = _provincia_actual(engine, player)
    region = engine.componentes[RegiónComponent][entity_id]
    market = engine.componentes[TradeComponent][entity_id]
    if market.tiene_ciudad:
        print(f"La ciudad de {region.nombre} mantiene sus mercados abiertos pese a la crisis.")
    elif region.infeccion.valor > 0.45:
        print("El camino esta casi desierto: la infeccion demoníaca ha espantado a los viajeros.")
    else:
        print(f"El entorno es de {market.bioma}; los lugarenos hablan de {', '.join(market.productos[:2])}.")
    if region.fervor.valor < 0.35:
        print("Los aldeanos desconfian de tu Marca de la Estrella y vigilan tus movimientos.")
    else:
        print("Una aldeana reconoce tu Marca de la Estrella y ofrece hierbas curativas.")


def _explorar(engine: EterEngine, player: PlayerComponent) -> None:
    if player.estamina < 15:
        print("Estas demasiado agotado para explorar.")
        return
    player.estamina -= 15
    _contexto_local(engine, player)
    if player.consumir("raciones") and random.random() < 0.5:
        print("Exploras la zona y consumes una racion. Encuentras rastros de actividad demoniaca.")
    else:
        player.mana = min(player.mana_maximo, player.mana + 5)
        print("Exploras la zona y encuentras un santuario olvidado. Recuperas 5 de mana.")


def _usar_objeto(player: PlayerComponent) -> None:
    if player.tiene("raciones") and player.vida < player.vida_maxima:
        player.consumir("raciones")
        player.vida = min(player.vida_maxima, player.vida + 20)
        print("Usas una racion y recuperas 20 HP.")
    elif player.tiene("antorcha"):
        player.consumir("antorcha")
        player.estamina = min(player.estamina_maxima, player.estamina + 10)
        print("Enciendes la antorcha y recuperas 10 de estamina.")
    else:
        print("No tienes un objeto util ahora mismo.")


def iniciar_simulacion() -> None:
    engine, state_entities, province_entities, fondos_jugador = cargar_mundo()
    engine.province_entities = province_entities
    player_entity = engine.crear_entidad()
    player = SpawnSystem.crear_jugador(engine.map_raw, province_entities, potencial=None)
    engine.agregar_componente(player_entity, player)

    print("--- BIENVENIDO A ETER ---")
    print(f"Mapa cargado: {len(state_entities)} estados y {len(province_entities)} provincias.")
    print(f"Has despertado en {_nombre_actual(engine, player)}. No necesitas conocer el mapa: las rutas locales te guiaran.")
    ciclo = 1
    while player.esta_vivo():
        _mostrar_estado_jugador(engine, player, ciclo)
        movimiento = _mostrar_menu_local(engine, player)
        comando = input("\nAccion [1-4, mover N, explorar, objeto, pasar, ayuda, salir] > ").strip().casefold()
        if comando == "salir":
            print("Abandonaste a Eter a su suerte. Fin de la simulacion.")
            return
        if comando in ("ayuda", "menu"):
            continue
        if comando in ("1", "mover"):
            print("Elige un indice de vecino, por ejemplo: mover 1.")
            continue
        if comando.startswith("mover "):
            index = comando.split(maxsplit=1)[1]
            destination = movimiento.get(index)
            if destination is None:
                print("Ese destino no esta disponible desde tu provincia actual.")
                continue
            if player.estamina < 10:
                print("No tienes suficiente estamina para viajar.")
                continue
            territory = engine.componentes[TerritoryComponent][destination]
            player.provincia_actual = territory.azgaar_id
            player.celda_actual = _celda_de_provincia(engine, territory.azgaar_id)
            player.estamina -= 10
            print(f"Viajas a {engine.componentes[RegiónComponent][destination].nombre}.")
            _contexto_local(engine, player)
        elif comando in ("2", "explorar"):
            _explorar(engine, player)
        elif comando in ("3", "objeto", "usar objeto"):
            print("Uso: objeto ver | objeto usar [nombre o numero] | objeto equipar [nombre]")
        elif comando == "objeto ver":
            _mostrar_estado_jugador(engine, player, ciclo)
        elif comando.startswith("objeto equipar "):
            nombre_objeto = comando.removeprefix("objeto equipar ").strip()
            print("Objeto equipado." if player.equipar(nombre_objeto) else "No tienes ese objeto.")
        elif comando.startswith("objeto usar "):
            nombre_objeto = comando.removeprefix("objeto usar ").strip()
            if nombre_objeto.isdigit():
                nombres = list(player.inventario)
                nombre_objeto = nombres[int(nombre_objeto) - 1] if 0 < int(nombre_objeto) <= len(nombres) else ""
            if nombre_objeto == "raciones" and player.vida < player.vida_maxima:
                _usar_objeto(player)
            elif nombre_objeto == "antorcha":
                _usar_objeto(player)
            elif nombre_objeto == "brujula":
                print("La brujula revela tus rutas adyacentes.")
            else:
                print("No puedes usar ese objeto ahora.")
        elif comando in ("4", "pasar"):
            print("Pasas el turno. El mundo continua su marcha.")
        elif comando == "estado":
            print(f"Fondos de la expedicion: {fondos_jugador:.1f}")
            continue
        elif comando.startswith("inspeccionar "):
            entity_id = _resolver_provincia(engine, comando.removeprefix("inspeccionar "))
            if entity_id is None:
                print("Provincia no encontrada.")
            else:
                _mostrar_provincia(engine, entity_id)
            continue
        elif comando.startswith("invertir "):
            entity_id = _resolver_provincia(engine, comando.removeprefix("invertir "))
            if entity_id is None or fondos_jugador < EconomicSystem.COSTE_INVERSION:
                print("Provincia no encontrada o fondos insuficientes.")
                continue
            economy = engine.componentes[EconomyComponent][entity_id]
            fondos_jugador -= EconomicSystem.COSTE_INVERSION
            EconomicSystem.invertir(engine.componentes[RegiónComponent][entity_id], economy, entity_id)
            print("Inversion realizada.")
            continue
        elif comando.startswith("comerciar "):
            raw_trade = comando.removeprefix("comerciar ")
            legacy_pair = _separar_comercio(engine, raw_trade)
            if legacy_pair is not None:
                flujo = EconomicSystem.comerciar(legacy_pair[0], legacy_pair[1], engine.componentes[EconomyComponent], engine.adyacencias)
                print("Comercio ejecutado." if flujo else "Las provincias no son adyacentes.")
                continue
            trade_args = raw_trade.split(maxsplit=1)
            producto = trade_args[0] if len(trade_args) == 2 else ""
            pair = _separar_comercio(engine, trade_args[1]) if len(trade_args) == 2 else None
            if pair is None:
                print("Uso: comerciar [producto] [provincia origen] [provincia destino].")
                continue
            try:
                price, days, distance = EconomicSystem.comerciar_producto(
                    pair[0], pair[1], producto,
                    engine.componentes[EconomyComponent],
                    engine.componentes[TradeComponent],
                    engine.componentes[RegiónComponent],
                    engine.adyacencias,
                )
                print(f"Ruta de {producto}: {price:.1f} oro, {distance:.1f} km, {days} dias de transporte.")
            except ValueError as error:
                print(str(error))
            continue
        else:
            print("Accion no reconocida. Escribe ayuda para ver el menu local.")
            continue

        player.estamina = min(player.estamina_maxima, player.estamina + 5)
        engine.tick()
        ciclo += 1

    print("La Marca de la Estrella se apaga. Fin de la partida.")


if __name__ == "__main__":
    iniciar_simulacion()
