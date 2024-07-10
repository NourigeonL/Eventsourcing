from uuid import UUID, uuid4
from typing import NewType

Guid = NewType('Guid',str)

def guid()-> Guid:
    return str(uuid4())