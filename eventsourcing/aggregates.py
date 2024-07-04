import abc
from .event import IEvent

class AggregateRoot(abc.ABC):
    @property
    @abc.abstractmethod
    def id(self) -> str:...

    def __init__(self) -> None:
        self.__changes : list[IEvent] = []
        self.__version : int = -1


    @staticmethod 
    @abc.abstractmethod
    def to_stream_id(id : str) -> str:...

    @property
    def version(self) -> int:
        return self.__version

    def get_uncommitted_changes(self) -> list[IEvent]:
        return self.__changes

    def mark_changes_as_committed(self) -> None:
        self.__changes.clear()


    def loads_from_history(self, history : list[IEvent]) -> None:
        self.__changes.clear()
        for e in history:
            self.__apply_change(e, False)
            self.__version += 1

    def _apply(self, e : "IEvent") -> None:
        return

    def __apply_change(self, event : "IEvent", is_new : bool) -> None:
        self._apply(event)
        if is_new:
            self.__changes.append(event)

    def _apply_change(self, event : "IEvent") -> None:
        self.__apply_change(event, True)