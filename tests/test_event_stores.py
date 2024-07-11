import pytest
from eventsourcing.event_stores import get_event_class
from eventsourcing.event import IEvent

class NotAnEventClass:
    pass

class AnEventClass(IEvent):
    pass

def test_should_not_find_class():
    with pytest.raises(ValueError):
        get_event_class("ThisClassDoesNotExist")
        
def test_should_raise_not_event_class():
    with pytest.raises(TypeError):
        get_event_class("NotAnEventClass")
        
def test_should_find_event_class():
    cls = get_event_class("AnEventClass")
    assert cls == AnEventClass