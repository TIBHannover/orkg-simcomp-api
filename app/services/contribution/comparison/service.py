# -*- coding: utf-8 -*-
from app.common.errors import OrkgSimCompApiError
from app.models.contribution import ComparisonType
from app.services.common.base import OrkgSimCompApiService
from app.services.common.orkg_backend import OrkgBackendWrapperService
from app.services.contribution.comparison import compare_merge, compare_path
from app.services.thing.export import ComparisonExporter


class ContributionComparisonService(OrkgSimCompApiService):
    def __init__(
        self,
        orkg_backend: OrkgBackendWrapperService,
    ):
        super().__init__(logger_name=__name__)

        self.orkg_backend = orkg_backend

    def compare(
        self,
        contribution_ids,
        comparison_type,
        format,
    ):
        try:
            comparison = {
                ComparisonType.PATH: compare_path,
                ComparisonType.MERGE: compare_merge,
            }[comparison_type].compare(
                self.orkg_backend,
                contribution_ids,
            )
        except KeyError:
            raise OrkgSimCompApiError(
                message="Unknown comparison_type={}".format(comparison_type),
                cls=self.__class__,
            )

        if format:
            return ComparisonExporter.export(comparison, format=format)

        return {"comparison": comparison}
