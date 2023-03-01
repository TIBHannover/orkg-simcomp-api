# -*- coding: utf-8 -*-
import re

import networkx as nx

from app.services.common.orkg_backend import OrkgBackendWrapperService


class DocumentCreator:
    @staticmethod
    def create(
        orkg_backend: OrkgBackendWrapperService,
        contribution_id: str,
    ):
        """
        creates a document for a contribution_id
        """

        graph = orkg_backend.get_subgraph(thing_id=contribution_id)

        if not graph:
            return None

        document = []
        node_to_nodes = {}
        for u, v in nx.bfs_edges(graph, source=contribution_id):
            node_to_nodes.setdefault(u, []).append(v)

        for u, V in node_to_nodes.items():
            u_node = graph.nodes[u]
            u_label = u_node.get("formatted_label") or u_node.get("label")
            document.append(u_label)

            visited_edges = []
            for v in V:
                edge = graph.edges[(u, v)]["label"]
                if edge not in visited_edges:
                    document.append(edge)
                    visited_edges.append(edge)

                v_node = graph.nodes[v]
                v_label = v_node.get("formatted_label") or v_node.get("label")
                document.append(v_label)

        document = " ".join(document)
        return postprocess(document)


def postprocess(string):
    if not string:
        return string

    # replace each occurrence of one of the following characters with ''
    characters = [
        "<files>",
        r"\\[]",
        r"\\[",
        r"\\]",
        ":",
        r"\\?",
        "'",
    ]
    regex = "|".join(characters)
    string = re.sub(regex, "", string)

    # replace each occurrence of one of the following characters with ' '
    characters = [r"\\s+-\\s+"]
    regex = "|".join(characters)
    string = re.sub(regex, " ", string)

    # terms are lower-cased and only seperated by a space character
    return " ".join(string.split()).lower()
