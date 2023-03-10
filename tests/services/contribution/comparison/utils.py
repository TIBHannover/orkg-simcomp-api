# -*- coding: utf-8 -*-
import networkx as nx


def create_subgraph(contribution_id, contribution_dict):
    subgraph = nx.DiGraph()

    subgraph.add_node(
        node_for_adding=contribution_id,
        id=contribution_id,
        label="contribution_id",
        _class="resource",
    )

    for (
        key,
        value,
    ) in contribution_dict.items():
        subgraph.add_node(
            node_for_adding=value,
            id=value,
            label=value,
            _class="literal",
        )
        subgraph.add_edge(
            u_of_edge=contribution_id,
            v_of_edge=value,
            id=key,
            label=key,
        )

    return subgraph
