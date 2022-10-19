from uuid import uuid4
from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID


class BaseTable:

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    def __repr__(self):
        return ' '.join(['{}={}'.format(key, value) for key, value in self.__dict__.items() if not key.startswith('_')])
