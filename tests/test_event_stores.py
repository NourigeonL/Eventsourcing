import pytest
import unittest
from eventsourcing.event_stores import get_event_class, InMemEventStore, EventDescriptor
from eventsourcing.event import IEvent
from dataclasses import dataclass
from eventsourcing.exceptions import ConcurrencyError

class NotAnEventClass:
    pass

class AnEventClass(IEvent):
    pass

@dataclass
class EventOne(IEvent):
    val_one : int
    
    @property
    def type(self) -> str:
        return "EventOne"
    
@dataclass
class EventTwo(IEvent):
    val_two : str
    
    @property
    def type(self) -> str:
        return "EventTwo"

def test_should_not_find_class():
    with pytest.raises(ValueError):
        get_event_class("ThisClassDoesNotExist")
        
def test_should_raise_not_event_class():
    with pytest.raises(TypeError):
        get_event_class("NotAnEventClass")
        
def test_should_find_event_class():
    cls = get_event_class("AnEventClass")
    assert cls == AnEventClass
    
class InMemEventStoreTest(unittest.IsolatedAsyncioTestCase):
    """
    Test suite for testing the in-memory event store.
    """
    def setUp(self):
        """
        Set up a InMemEventStore for each test.
        """
        self.event_store = InMemEventStore()

    async def test_should_save_two_events(self):
        aggregate_id = "1234"
        event_1 = EventOne(1)
        event_2 = EventTwo("two")
        await self.event_store.save_events(aggregate_id, [event_1, event_2],-1)
        
        assert len(self.event_store.current[aggregate_id]) == 2
        event_desc_1 = self.event_store.current[aggregate_id][0]
        event_desc_2 = self.event_store.current[aggregate_id][1]
        assert event_desc_1.event_type == event_1.type
        assert event_desc_2.event_type == event_2.type
        assert event_desc_1.id == aggregate_id
        assert event_desc_2.id == aggregate_id
        assert event_desc_1.version == 0
        assert event_desc_2.version == 1
        
    async def test_should_raise_concurrency_error(self):
        aggregate_id = "1234"
        event_1 = EventOne(1)
        event_2 = EventTwo("two")
        with pytest.raises(ConcurrencyError):
            await self.event_store.save_events(aggregate_id, [event_1],1)
        await self.event_store.save_events(aggregate_id, [event_1],-1)
        with pytest.raises(ConcurrencyError):
            await self.event_store.save_events(aggregate_id, [event_2],1)
        
    
    async def test_should_retrieve_no_events(self):
        aggregate_id = "1234"
        lst_events = await self.event_store.get_events_for_aggregate(aggregate_id)
        assert len(lst_events) == 0
        
    async def test_should_retrieve_two_events(self):
        aggregate_id = "1234"
        event_1 = EventOne(1)
        event_2 = EventTwo("two")
        await self.event_store.save_events(aggregate_id, [event_1, event_2],-1)
        lst_events = await self.event_store.get_events_for_aggregate(aggregate_id)
        assert len(lst_events) == 2
        assert lst_events[0] == event_1
        assert lst_events[1] == event_2