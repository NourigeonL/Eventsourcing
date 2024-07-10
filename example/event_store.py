import json
from eventsourcing.event import IEvent
from eventsourcing.exceptions import ConcurrencyError
from eventsourcing.event_stores import IEventStore
from .events import EVENT_MAP

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
        return [EVENT_MAP[desc.event_type].from_dict(json.loads(desc.event_data)) for desc in event_descriptors]
