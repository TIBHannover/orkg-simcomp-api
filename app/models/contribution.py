from enum import Enum
from typing import List, Optional, Any, Dict, Union

from pydantic import BaseModel

from app.models.common import Response


class ContributionSimilarityInitIndexResponse(Response):

    class Payload(BaseModel):
        n_contributions: int
        n_indexed_contributions: int
        not_indexed_contributions: List[str]

    payload: Payload


class ContributionSimilarityIndexResponse(Response):

    class Payload(BaseModel):
        message: str

    payload: Payload


class ContributionSimilaritySimilarResponse(Response):
    class Payload(BaseModel):

        class SimilarContribution(BaseModel):
            id: str
            label: Optional[str]
            paper_id: Optional[str]
            paper_label: Optional[str]
            similarity_percentage: float

        contributions: List[SimilarContribution]

    payload: Payload


class ComparisonType(str, Enum):
    PATH = 'PATH'
    MERGE = 'MERGE'


class ComparisonHeaderCell(BaseModel):
    id: str
    label: str
    paper_id: str
    paper_label: str
    paper_year: str


class ComparisonIndexCell(BaseModel):
    id: str
    label: str
    n_contributions: int
    active: bool


class ComparisonTargetCell(BaseModel):
    id: str
    label: str
    type: str
    classes: List[str]
    path: List[str]
    path_labels: List[str]


class Comparison(BaseModel):
    contributions: List[ComparisonHeaderCell] = []
    predicates: List[ComparisonIndexCell] = []
    data: Dict[str, List[List[Union[ComparisonTargetCell, dict]]]] = {}


class ContributionComparisonResponse(Response):

    class Payload(BaseModel):
        comparison: Comparison

    payload: Payload
