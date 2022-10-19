from sqlalchemy import Column, String, JSON

from app.db.connection import Base
from app.db.models.common import BaseTable


class Example(Base, BaseTable):
    __tablename__ = 'examples'

    service_name = Column(String, nullable=False)
    data = Column(JSON, nullable=False)
