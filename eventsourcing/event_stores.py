import abc
import sys
import json
from .event import IEvent
from .exceptions import ConcurrencyError


class IEventStore(abc.ABC):
    @abc.abstractmethod
    async def save_events(self, aggregate_id : str, events : list[IEvent], expected_version : int) -> None:...

    @abc.abstractmethod
    async def get_events_for_aggregate(self, aggregate_id : str) -> list[IEvent]:...
    

def get_event_class(class_name) -> type[IEvent]:
    for module in sys.modules.values():
        if hasattr(module, class_name):
            cls = getattr(module, class_name)
            if not issubclass(cls, IEvent):
                raise TypeError(f"{class_name} is not an Event")
            return cls
    raise ValueError(f"Class '{class_name}' not found.")

class EventDescriptor:
    def __init__(self, id : str, event_type: str, event_data : str, version : int) -> None:
        self.event_type = event_type
        self.__event_data = event_data
        self.__version = version
        self.__id = id

    @property
    def event_data(self) -> IEvent:
        return self.__event_data

    @property
    def version(self) -> int:
        return self.__version

    @property
    def id(self) -> str:
        return self.__id

class InMemEventStore(IEventStore):

    def __init__(self) -> None:
        self.current : dict[str, list[EventDescriptor]] = {}

    async def save_events(self, aggregate_id: str, events: list[IEvent], expected_version: int) -> None:
        event_descriptors = self.current.get(aggregate_id)
        if not event_descriptors:
            event_descriptors = []
            self.current[aggregate_id] = event_descriptors

        elif event_descriptors[len(event_descriptors)-1].version != expected_version and expected_version != -1:
            raise ConcurrencyError()

        i = expected_version

        for event in events:
            i += 1
            event_descriptors.append(EventDescriptor(aggregate_id, event.type,json.dumps(event.to_dict()), i))

    async def get_events_for_aggregate(self, aggregate_id: str) -> list[IEvent] | None:
        event_descriptors = self.current.get(aggregate_id)
        if event_descriptors is None:
            return None
        return [get_event_class(desc.event_type).from_dict(json.loads(desc.event_data)) for desc in event_descriptors]
