from sqlalchemy import Column, String, JSON, UniqueConstraint

from app.db.connection import Base
from app.db.models.common import BaseTable


class Thing(Base, BaseTable):
    __tablename__ = 'things'

    thing_type = Column(String, nullable=False)
    thing_key = Column(String, nullable=False)
    data = Column(JSON, nullable=False)

    __table_args__ = (
        UniqueConstraint('thing_type', 'thing_key', name='_type_key_unique_constraint'),
    )
