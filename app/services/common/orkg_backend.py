import os
import orkg
import networkx as nx

from typing import List, Tuple, Any, Callable, Union, Optional
from orkg import ORKG

from app.services.common.base import OrkgSimCompApiService


class OrkgBackendWrapperService(OrkgSimCompApiService):

    def __init__(self, host: str = os.getenv('ORKG_BACKEND_API_HOST', 'http://localhost')):
        super().__init__(logger_name=__name__)

        self.connector = ORKG(host=host)

    @staticmethod
    def get_instance():
        yield OrkgBackendWrapperService()

    def get_contribution_ids(self) -> List[str]:
        self.logger.debug('Getting all contributions in the ORKG ...')

        contributions = self._call_pageable(
            self.connector.classes.get_resource_by_class,
            args={
                'class_id': 'Contribution'
            },
            params={
                'sort': True,
                'page': 0,
                'size': 300
            }
        )

        return [contribution['id'] for contribution in contributions]

    def get_subgraph(
            self,
            thing_id: str,
            blacklist: Union[str, List[str]] = 'ResearchField',
            max_level: int = -1
    ) -> Optional[nx.DiGraph]:

        self.logger.debug('Getting subgraph for thing_id={}'.format(thing_id))

        try:
            graph = orkg.subgraph(client=self.connector, thing_id=thing_id, blacklist=blacklist, max_level=max_level)
        except ValueError:
            self.logger.warning('An error occurred while obtaining a subgraph representation for {}'.format(thing_id))
            return None

        return graph

    def get_contribution_details(self, contribution_id: str) -> dict:
        self.logger.debug('Getting details for contribution_id={}'.format(contribution_id))

        response = self.connector.statements.get_by_object_and_predicate(object_id=contribution_id, predicate_id='P31')

        if not response.succeeded or not isinstance(response.content, list) or not len(response.content) == 1:
            self.logger.warning('An error occurred while calling orkg.statements.get_by_object_and_predicate()')
            return {}

        statement = response.content[0]
        return {
            'label': statement['object']['label'],
            'paper_id': statement['subject']['id'],
            'paper_label': statement['subject']['label']
        }

    def get_paper_year(self, paper_id: str) -> Optional[str]:
        self.logger.debug('Getting paper year for paper_id={}'.format(paper_id))

        response = self.connector.statements.get_by_subject_and_predicate(subject_id=paper_id, predicate_id='P29')

        if not response.succeeded or not isinstance(response.content, list) or not len(response.content) == 1:
            self.logger.warning('An error occurred while calling orkg.statements.get_by_subject_and_predicate()')
            return None

        statement = response.content[0]
        return statement['object']['label']

    def _call_pageable(self, func: Callable[..., Any], args: dict, params: dict) -> List[dict]:

        def _call_one_page(page: int) -> Tuple[int, List[dict]]:
            params['page'] = page
            response = func(**args, params=params)

            if not response.succeeded:
                self.logger.warning('An error occurred while calling {}(args={}, params={})'.format(func, args, params))
                return 0, []

            return response.page_info['totalPages'], response.content

        all_items = []
        n_pages, items = _call_one_page(page=0)
        all_items.extend(items)

        for i in range(1, n_pages):
            _, items = _call_one_page(page=i)
            all_items.extend(items)

        return all_items
