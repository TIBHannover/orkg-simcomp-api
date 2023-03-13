# -*- coding: utf-8 -*-
from typing import List

from pydantic import BaseModel

from app.models.common import OrkgStatement


class Review(BaseModel):
    root_review_id: str
    statements: List[OrkgStatement]
