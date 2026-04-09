import uuid
from dataclasses import dataclass
from typing import Any

@dataclass
class ServerSentEvent:
    id: uuid.UUID
    event: str
    namespace: str
    data: dict[str, Any]

class ServerSentEventBuilder:
    id: str | None
    event: str
    namespace: str
    data: dict[str, Any]

    def __init__(self):
        self.id = None
        self.event = ''
        self.namespace = ''
        self.data = {}
    
    def with_id(self, id: str):
        self.id = id
    
    def with_event(self, event: str):
        self.namespace, self.event = event.split(':')

    def with_data(self, data: dict[str, Any]):
        self.data = data
    
    def finish(self) -> ServerSentEvent:
        return ServerSentEvent(
            id=uuid.UUID(hex=self.id) if self.id else uuid.UUID(int=0),
            event=self.event,
            namespace=self.namespace,
            data=self.data
        )
