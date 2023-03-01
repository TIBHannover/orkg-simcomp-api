# -*- coding: utf-8 -*-
import os

from app.services.common.base import OrkgSimCompApiService
from app.services.common.es import ElasticsearchService
from app.services.common.orkg_backend import OrkgBackendWrapperService
from app.services.contribution.similarity.document import DocumentCreator


class ContributionSimilarityService(OrkgSimCompApiService):
    def __init__(
        self,
        orkg_backend: OrkgBackendWrapperService,
        es_service: ElasticsearchService,
    ):
        super().__init__(logger_name=__name__)

        self.orkg_backend = orkg_backend
        self.es_service = es_service
        self.index_name = os.getenv(
            "ORKG_SIMCOMP_API_ES_CONTRIBUTIONS_INDEX",
            "contributions",
        )

    def init_index(self):
        self.es_service.delete_index(index=self.index_name)
        self.es_service.create_index(index=self.index_name)

        indexed_contributions = 0
        not_indexed = []

        contribution_ids = self.orkg_backend.get_contribution_ids()
        for contribution_id in contribution_ids:
            # TODO: shall we move the document creation logic to orkg-simcomp-pypi, orkg-pypi or keep it here ?
            document = DocumentCreator.create(self.orkg_backend, contribution_id)

            if not document:
                not_indexed.append(contribution_id)
                continue

            self.es_service.index(
                index=self.index_name,
                document_id=contribution_id,
                document={"text": document},
            )
            indexed_contributions += 1

        return {
            "n_contributions": len(contribution_ids),
            "n_indexed_contributions": indexed_contributions,
            "not_indexed_contributions": not_indexed,
        }

    def index(self, contribution_id):
        if not self.es_service.exists(index=self.index_name):
            self.logger.warning(
                'Index "{}" does not exist. Initializing...'.format(self.index_name)
            )
            self.init_index()

        document = DocumentCreator.create(self.orkg_backend, contribution_id)

        if not document:
            return {"message": "Contribution {} unknown or empty".format(contribution_id)}

        self.es_service.index(
            index=self.index_name,
            document_id=contribution_id,
            document={"text": document},
        )

        return {"message": "Contribution {} indexed".format(contribution_id)}

    def query(self, contribution_id, n_results):
        if not self.es_service.exists(index=self.index_name):
            self.logger.warning(
                'Index "{}" does not exist. Initializing...'.format(self.index_name)
            )
            self.init_index()

        results = []

        q = DocumentCreator.create(self.orkg_backend, contribution_id)
        similar = self.es_service.query(
            index=self.index_name,
            q_key="text",
            q_value=q,
            top_k=n_results,
        )

        if not similar:
            return {"contributions": []}

        for similar_id, score in similar.items():
            details = self.orkg_backend.get_contribution_details(contribution_id=similar_id)
            if similar_id == contribution_id or not details:
                continue

            results.append(
                {
                    "id": similar_id,
                    "label": details.get("label", None),
                    "paper_id": details.get("paper_id", None),
                    "paper_label": details.get("paper_label", None),
                    "similarity_percentage": score,
                }
            )

        results = sorted(
            results,
            key=lambda i: i["similarity_percentage"],
            reverse=True,
        )[:n_results]

        return {"contributions": results}
