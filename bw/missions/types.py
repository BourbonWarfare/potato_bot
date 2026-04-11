import uuid
from typing import NewType

MissionTypeTag = NewType('MissionTypeTag', int)
IterationUuid = NewType('IterationUuid', uuid.UUID)
MissionUuid = NewType('MissionUuid', uuid.UUID)
UserUuid = NewType('UserUuid', uuid.UUID)
