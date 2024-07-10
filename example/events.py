from .user import UserCreated
from eventsourcing.event import IEvent


EVENT_MAP : dict[str, type[IEvent]]= {
    "UserCreated": UserCreated,
}