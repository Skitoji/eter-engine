# src/eter_infrastructure/messaging/event_bus.py
from typing import Callable, Dict, List, Type
from eter_core.domain.events import DomainEvent

# Un 'Handler' es una función que recibe un evento específico
EventHandler = Callable[[DomainEvent], None]

class EventBus:
    """
    Bus de eventos centralizado y determinista.
    Permite desacoplar sistemas: cuando la fe cae, el sistema de fe publica un evento
    y el sistema de spawns/reputación reacciona sin importar dónde se ejecute.
    """
    _suscripciones: Dict[Type[DomainEvent], List[EventHandler]] = {}

    @classmethod
    def suscribir(cls, tipo_evento: Type[DomainEvent], handler: EventHandler) -> None:
        if tipo_evento not in cls._suscripciones:
            cls._suscripciones[tipo_evento] = []
        cls._suscripciones[tipo_evento].append(handler)

    @classmethod
    def publicar(cls, evento: DomainEvent) -> None:
        tipo_evento = type(evento)
        if tipo_evento in cls._suscripciones:
            for handler in cls._suscripciones[tipo_evento]:
                handler(evento)