from typing import List, Optional

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
