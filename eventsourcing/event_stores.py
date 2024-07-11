
from .event import IEvent
import abc
import sys

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