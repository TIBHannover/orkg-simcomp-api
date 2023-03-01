# -*- coding: utf-8 -*-
from sqlalchemy import Column, String

from app.db.connection import Base
from app.db.models.common import BaseTable


class Link(Base, BaseTable):
    __tablename__ = "links"

    long_url = Column(String, nullable=False)
    short_code = Column(String, nullable=False)
