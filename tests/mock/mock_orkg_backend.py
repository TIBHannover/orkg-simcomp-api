# -*- coding: utf-8 -*-
import networkx as nx


class OrkgBackendWrapperServiceMock:
    def __init__(self):
        self.contributions = {
            "123": {
                "subgraph": self.__create_subgraph("123"),
                "details": {
                    "label": "test label",
                    "paper_id": "test paper_id",
                    "paper_label": "test paper_label",
                    "paper_year": "2007",
                },
            },
            "234": {
                "subgraph": self.__create_subgraph("234"),
                "details": {
                    "label": "test label",
                    "paper_id": "test paper_id",
                    "paper_label": "test paper_label",
                    "paper_year": "2007",
                },
            },
            "345": {
                "subgraph": self.__create_subgraph("345"),
                "details": {
                    "label": "test label",
                    "paper_id": "test paper_id",
                    "paper_label": "test paper_label",
                    "paper_year": "2007",
                },
            },
        }

        self.papers = {"test paper_id": {"year": "2007"}}

    @staticmethod
    def get_instance():
        yield OrkgBackendWrapperServiceMock()

    def get_contribution_ids(self):
        return list(self.contributions.keys())

    def get_subgraph(self, thing_id):
        return self.contributions.get(thing_id, {}).get("subgraph", None)

    def get_contribution_details(self, contribution_id):
        return self.contributions.get(contribution_id, {}).get("details", None)

    def get_paper_year(self, paper_id):
        return self.papers.get(paper_id, {}).get("year", None)

    @staticmethod
    def __create_subgraph(thing_id):
        subgraph = nx.DiGraph()

        subgraph.add_node(
            node_for_adding=thing_id,
            id=thing_id,
            label="Contribution {}".format(thing_id),
            _class="resource",
        )
        subgraph.add_node(
            node_for_adding=thing_id + " target",
            id=thing_id + " target",
            label="Contribution {}".format(thing_id),
            _class="literal",
        )
        subgraph.add_edge(
            u_of_edge=thing_id,
            v_of_edge=thing_id + " target",
            id=thing_id + thing_id + " target",
            label="Predicate {}".format(thing_id),
        )

        return subgraph
