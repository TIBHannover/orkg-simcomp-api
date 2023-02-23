import networkx as nx
from typing import List, Dict, Tuple, Any, Optional, Union

from app.services.common.orkg_backend import OrkgBackendWrapperService
from app.models.contribution import ComparisonHeaderCell, ComparisonIndexCell, ComparisonTargetCell, Comparison


def compare(orkg_backend: OrkgBackendWrapperService, contribution_ids: List[str]) -> Comparison:
    contributions_details = []
    contributions_paths = []
    for contribution_id in contribution_ids:
        contribution_details = _get_contribution_details(orkg_backend, contribution_id)
        contribution_paths = _get_contribution_paths(orkg_backend, contribution_id)

        if not contribution_details or not contribution_paths:
            continue

        # preparing contribution_details
        contributions_details.append(contribution_details)
        contributions_paths.append(contribution_paths)

    # preparing data
    data = {}
    for index, contribution_paths in enumerate(contributions_paths):
        for path_id, path_targets in contribution_paths.items():

            if path_id not in data:
                data[path_id] = [[{}]] * len(contributions_paths)

            data[path_id][index] = path_targets

    data = {key: data[key] for key in sorted(data.keys())}

    # preparing predicates
    predicates = []
    for pathed_predicate_label, contributions in data.items():
        n_contributions = len([contribution for contribution in contributions if contribution[0]])

        predicates.append(ComparisonIndexCell(
            id=pathed_predicate_label,
            label=pathed_predicate_label,
            n_contributions=n_contributions,
            active=n_contributions >= 2
        ))

    return Comparison(
        contributions=contributions_details,
        predicates=predicates,
        data=data
    )


def _get_contribution_details(
        orkg_backend: OrkgBackendWrapperService, contribution_id: str
) -> Optional[ComparisonHeaderCell]:
    # TODO: this call should be replaced by another optimized one from the backend.
    contribution_details = orkg_backend.get_contribution_details(contribution_id)

    if not contribution_details:
        return None

    return ComparisonHeaderCell(
        id=contribution_id,
        label=contribution_details['label'],
        paper_id=contribution_details['paper_id'],
        paper_label=contribution_details['paper_label'],
        paper_year=orkg_backend.get_paper_year(contribution_details['paper_id'])
    )


def _get_contribution_paths(
        orkg_backend: OrkgBackendWrapperService, contribution_id: str
) -> Dict[str, List[ComparisonTargetCell]]:
    subgraph = orkg_backend.get_subgraph(thing_id=contribution_id)

    if not subgraph:
        return {}

    contribution_paths = {}
    for target_id in list(subgraph.nodes()):

        paths = nx.all_simple_paths(subgraph, source=contribution_id, target=target_id, cutoff=5)

        for path in paths:
            complete_path_ids, complete_path_labels = _nodes_to_nodes_and_edges(subgraph, path)

            pathed_predicate_ids = complete_path_ids[:-1]
            pathed_predicate_labels, target_label = complete_path_labels[:-1], complete_path_labels[-1]
            pathed_predicate_label_str = '/'.join(pathed_predicate_labels[1:]).lower()

            if pathed_predicate_label_str not in contribution_paths:
                contribution_paths[pathed_predicate_label_str] = []

            contribution_paths[pathed_predicate_label_str].append(ComparisonTargetCell(
                id=target_id,
                label=target_label.lower(),
                type=subgraph.nodes[target_id]['_class'],
                classes=_clean_classes(subgraph.nodes[target_id].get('classes', [])),
                path=pathed_predicate_ids,
                path_labels=list(map(lambda s: s.lower(), pathed_predicate_labels))
            ))

    return contribution_paths


def _nodes_to_nodes_and_edges(subgraph: nx.DiGraph, path: List[str]) -> Tuple[List[str], List[str]]:
    complete_path_ids = []
    complete_path_labels = []

    for i in range(len(path) - 1):
        if i == 0:
            complete_path_ids.append(path[i])
            node = subgraph.nodes[path[i]]
            complete_path_labels.append(node.get('formatted_label') or node.get('label'))

        complete_path_ids.append(subgraph.edges[path[i], path[i + 1]]['id'])
        complete_path_labels.append(subgraph.edges[path[i], path[i + 1]]['label'])

        complete_path_ids.append(path[i + 1])
        node = subgraph.nodes[path[i + 1]]
        complete_path_labels.append(node.get('formatted_label') or node.get('label'))

    return complete_path_ids, complete_path_labels


def _clean_classes(classes: List[str]) -> List[str]:
    return [c for c in classes if c not in ['Thing', 'Literal', 'AuditableEntity', 'Resource']]
