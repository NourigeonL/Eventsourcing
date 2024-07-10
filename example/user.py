from eventsourcing.aggregates import AggregateRoot
from eventsourcing.event import IEvent
from eventsourcing.encryption import encrypted
from .guid import Guid
from datetime import date
from multipledispatch import dispatch
from datetime import date
from dataclasses import dataclass

@encrypted(subject_id="id", encrypted_members=["first_name", "last_name", "month_of_birth", "day_of_birth"])
@dataclass
class UserCreated(IEvent):
    id : Guid
    first_name : str
    last_name : str
    year_of_birth : int
    month_of_birth : int
    day_of_birth : int
    
    @property
    def type(self) -> str:
        return "UserCreated"


class User(AggregateRoot):
    __id : Guid
    first_name : str
    last_name : str
    date_of_birth : date
    def __init__(self, id : Guid | None = None, first_name: str | None = None, last_name: str | None = None, date_of_birth: date | None = None) -> None:
        super().__init__()
        if id and first_name and last_name and date_of_birth:
            self._apply_change(UserCreated(id, first_name, last_name, date_of_birth.year, date_of_birth.month, date_of_birth.day))
            
    @dispatch(UserCreated)
    def _apply(self, e: UserCreated) -> None:
        self.__id = e.id
        self.first_name = e.first_name
        self.last_name = e.last_name
        self.date_of_birth = date(e.year_of_birth, 1 if isinstance(e.month_of_birth, str) else e.month_of_birth, 1 if isinstance(e.day_of_birth, str) else e.day_of_birth)
        
    @property
    def id(self) -> str:
        return self.__id
    
    @staticmethod
    def to_stream_id(id : str) -> str:
        return f"user-{id}"