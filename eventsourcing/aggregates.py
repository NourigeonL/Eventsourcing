import abc
from .event import IEvent

class AggregateRoot(abc.ABC):
    """
    Abstract base class for aggregate root.
    """
    @property
    @abc.abstractmethod
    def id(self) -> str:
        """
        Abstract property to get the aggregate root's ID.
        """

    def __init__(self) -> None:
        self.__changes : list[IEvent] = []
        self.__version : int = -1


    @staticmethod 
    @abc.abstractmethod
    def to_stream_id(id : str) -> str:
        """
        Abstract method to convert an ID to a stream ID.
        """

    @property
    def version(self) -> int:
        """
        Get the current version of the aggregate root.
        """
        return self.__version

    def get_uncommitted_changes(self) -> list[IEvent]:
        """
        Get the list of uncommitted changes.
        """
        return self.__changes

    def mark_changes_as_committed(self) -> None:
        """
        Mark all uncommitted changes as committed by clearing the changes list.
        """
        self.__changes.clear()


    def loads_from_history(self, history : list[IEvent]) -> None:
        """
        Load the aggregate root from a history of events.
        """
        self.__changes.clear()
        for e in history:
            self.__apply_change(e, False)
            self.__version += 1

    def _apply(self, e : "IEvent") -> None:
        """
        Abstract method to apply a change to the aggregate root.
        """

    def __apply_change(self, event : "IEvent", is_new : bool) -> None:
        """
        Apply a change to the aggregate root and optionally mark it as new.
        """
        self._apply(event)
        if is_new:
            self.__changes.append(event)

    def _apply_change(self, event : "IEvent") -> None:
        """
        Apply a new change to the aggregate root.
        """
        self.__apply_change(event, True)