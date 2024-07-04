
from .event import IEvent
import abc


class IEventStore(abc.ABC):
    @abc.abstractmethod
    async def save_events(self, aggregate_id : str, events : list[IEvent], expected_version : int) -> None:...

    @abc.abstractmethod
    async def get_events_for_aggregate(self, aggregate_id : str) -> list[IEvent]:...