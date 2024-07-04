import abc
from dataclasses import asdict, dataclass
from .encryption import Data

@dataclass
class IEvent(Data, metaclass=abc.ABCMeta):
    #version : int | None

    @property
    @abc.abstractmethod
    def type(self) -> str:...