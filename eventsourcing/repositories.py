from __future__ import annotations
import abc

from .aggregates import AggregateRoot
from typing import Generic, TypeVar
from .event_stores import IEventStore
from .exceptions import AggregateNotFoundError

T = TypeVar('T', bound=AggregateRoot)

class IRepository(Generic[T], abc.ABC):
    @abc.abstractmethod
    async def save(self, aggregate : AggregateRoot, expected_version : int) -> None:...

    @abc.abstractmethod
    async def get_by_id(self, id : str) -> T: ...

class EventStoreRepository(IRepository[T], Generic[T]):
    __storage : IEventStore

    def __init__(self, storage : IEventStore, class_type : type[T]) -> None:
        self.__storage = storage
        self.class_type = class_type

    async def save(self, aggregate : AggregateRoot, expected_version : int) -> None:
        await self.__storage.save_events(aggregate.to_stream_id(aggregate.id), aggregate.get_uncommitted_changes(), aggregate.version)
        aggregate.mark_changes_as_committed()

    async def get_by_id(self, id: str) -> T:
        obj = self.class_type()
        e = await self.__storage.get_events_for_aggregate(obj.to_stream_id(id))
        if not e:
            raise AggregateNotFoundError(id)
        obj.loads_from_history(e)
        return obj
