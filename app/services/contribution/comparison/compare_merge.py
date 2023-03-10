# -*- coding: utf-8 -*-
from typing import Any, Dict, Iterator, List, Set

import networkx as nx
import numpy as np
from rapidfuzz import fuzz
from sklearn.metrics import pairwise_distances

from app.models.contribution import (
    Comparison,
    ComparisonIndexCell,
    ComparisonTargetCell,
)
from app.services.common.orkg_backend import OrkgBackendWrapperService
from app.services.common.util.text_preprocessing import clean_labels
from app.services.contribution.comparison._common import (
    clean_classes,
    get_contribution_details,
)


class SimilarityMatrix:
    def __init__(self, contributions_predicates: List[Dict[str, str]]):
        self.predicates: Dict[str, str] = {
            k: v for predicate_dict in contributions_predicates for k, v in predicate_dict.items()
        }
        self.ids: List[str] = list(self.predicates.keys())
        self.labels: List[str] = list(self.predicates.values())

        # remove stopwords from labels
        self.clean_labels: List[str] = clean_labels(self.labels)

        self._matrix = None
        self._cache: Dict = {}

        # initialize matrix
        self.get_matrix()

    def compute_similarity(self):
        def _custom_fuzz_metric(s1, s2) -> float:
            i1 = int(s1[0])
            i2 = int(s2[0])
            if i1 == i2:
                return 1.0
            if (i1, i2) in self._cache:
                return self._cache[(i1, i2)]
            similarity = fuzz.ratio(self.clean_labels[i1], self.clean_labels[i2]) * 0.01
            self._cache[(i1, i2)] = similarity
            self._cache[(i2, i1)] = similarity
            return similarity

        self._matrix = pairwise_distances(
            X=np.array(range(len(self.clean_labels))).reshape(-1, 1), metric=_custom_fuzz_metric
        )

    def get_matrix(self):
        if self._matrix is None:
            self.compute_similarity()
        return self._matrix

    def idx_to_pid(self, idx):
        return self.ids[idx]

    def pid_to_label(self, pid):
        return self.predicates[pid]

    def __getitem__(self, i):
        matrix = self.get_matrix()
        return matrix[i]


def compare(
    orkg_backend: OrkgBackendWrapperService,
    contribution_ids: List[str],
):
    # Fetch predicates of these contributions
    contributions_predicates = []
    contributions_details = []
    contributions_graphs = []
    for contribution_id in contribution_ids:
        contribution_details = get_contribution_details(orkg_backend, contribution_id)
        contribution_graph = orkg_backend.get_subgraph(contribution_id)
        contribution_predicates = {
            edge["id"]: edge["label"] for _, _, edge in contribution_graph.edges(data=True)
        }

        if not contribution_details or not contribution_predicates or not contribution_graph:
            continue

        # preparing contribution_details
        contributions_details.append(contribution_details)
        contributions_predicates.append(contribution_predicates)
        contributions_graphs.append(contribution_graph)

    # if not contributions_predicates are present then return an empty comparison
    if not contributions_predicates:
        return Comparison(
            contributions=[],
            predicates=[],
            data=[],
        )

    # Compute similarity matrix and similar predicates
    sim_matrix = SimilarityMatrix(contributions_predicates=contributions_predicates)
    similar_predicates = _identify_similar_predicates(
        contributions_predicates=contributions_predicates,
        similarity_matrix=sim_matrix,
        similarity_threshold=0.85,
    )

    # preparing data
    data = {}
    for index, subgraph in enumerate(contributions_graphs):
        for predicate_id in _similar_iterator(similar_predicates):
            similar_predicate_info = similar_predicates[predicate_id]
            if predicate_id not in data:
                data[predicate_id] = [[{}]] * len(contributions_graphs)

            # Collect the information of this edge plus all similar edges
            similar_ids = similar_predicate_info["similar"]
            targets: List = _extract_values_from_edges(
                similar_ids=similar_ids.union({predicate_id}), subgraph=subgraph
            )
            if not targets:
                continue
            data[predicate_id][index] = targets

    data = {key: data[key] for key in sorted(data.keys())}

    # preparing predicates
    predicates = []
    for (
        predicate_id,
        contributions,
    ) in data.items():
        n_contributions = len([contribution for contribution in contributions if contribution[0]])
        predicates.append(
            ComparisonIndexCell(
                id=predicate_id,
                label=sim_matrix.pid_to_label(predicate_id),
                n_contributions=n_contributions,
                active=similar_predicates[predicate_id]["freq"] >= 2,
                similar_predicates=[
                    sim_matrix.pid_to_label(pid)
                    for pid in similar_predicates[predicate_id]["similar"]
                ],
            )
        )

    return Comparison(
        contributions=contributions_details,
        predicates=predicates,
        data=data,
    )


def _identify_similar_predicates(
    contributions_predicates: List[Dict[str, str]],
    similarity_matrix: SimilarityMatrix,
    similarity_threshold: float,
) -> Dict[str, Any]:
    # Create a mask to filter predicates that are present in contributions
    predicate_ids = similarity_matrix.ids
    mask = np.zeros((len(contributions_predicates), len(predicate_ids)), dtype=bool)
    for i, contribution_predicates in enumerate(contributions_predicates):
        for j, predicate_id in enumerate(predicate_ids):
            if predicate_id in contribution_predicates:
                mask[i][j] = True

    # Compute the frequency and similarity of each predicate
    found = {}
    for idx, predicate in enumerate(predicate_ids):
        if predicate not in found:
            similar_ids = np.where(similarity_matrix[idx] > similarity_threshold)[0]
            freq = np.sum(np.any(mask[:, similar_ids], axis=1))
            similar_ids = {similarity_matrix.idx_to_pid(idx) for idx in similar_ids} - {predicate}
            found[predicate] = {"freq": freq, "similar": similar_ids}

    return found


def _extract_values_from_edges(
    similar_ids: Set[str], subgraph: nx.DiGraph
) -> List[ComparisonTargetCell]:
    targets = []
    source_node = [node for node, in_degree in subgraph.in_degree() if in_degree == 0][0]
    objects = [
        target for _, target, edge in subgraph.edges(data=True) if edge["id"] in similar_ids
    ]
    for obj in objects:
        # Create a path from the source node to the object
        shortest_path = nx.shortest_path(subgraph, source_node, obj)
        path = [source_node]
        path_labels = [subgraph.nodes[source_node]["label"]]
        for i in range(len(shortest_path) - 1):
            edge = subgraph[shortest_path[i]][shortest_path[i + 1]]
            path.append(edge["id"])
            path.append(shortest_path[i + 1])
            path_labels.append(edge["label"])
            path_labels.append(subgraph.nodes[shortest_path[i + 1]]["label"])
        # Add the object to the list of targets
        obj_node = subgraph.nodes[obj]
        targets.append(
            ComparisonTargetCell(
                id=obj_node["id"],
                label=obj_node["label"],
                type=obj_node["_class"],
                classes=clean_classes(obj_node.get("classes", [])),
                path=path[:-1],
                path_labels=path_labels[:-1],
            )
        )
    return targets


def _similar_iterator(x: Dict[str, Any]) -> Iterator[str]:
    seen = set()
    for key in x:
        if key not in seen:
            seen.add(key)
            yield key
            seen |= x[key]["similar"]
