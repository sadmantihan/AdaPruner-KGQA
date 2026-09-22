"""Equivalence testing: profiled BFS vs. any reference/official BFS implementation."""
from .graph_profiler import bfs_with_rule_profiled_v2, path_endpoints


def run_equivalence_test(planning_recs, build_graph_fn, official_bfs_fn, dataset_label=""):
    """Check bfs_with_rule_profiled_v2 against a reference implementation.

    Parameters
    ----------
    planning_recs : list[dict]
        Each dict needs keys: "graph", "a_entity", "q_entity", "predicted_paths".
    build_graph_fn : callable(raw_graph) -> graph
        Builds the queryable graph object from a record's raw "graph" field.
    official_bfs_fn : callable(graph, start_node, rule) -> list[path]
        The reference implementation to check against.

    Returns
    -------
    dict with checked/mismatches/reachability_mismatches/path_count_mismatches
    """
    checked = mismatches = reachability_mismatches = path_count_mismatches = 0
    for rec in planning_recs:
        graph = build_graph_fn(rec["graph"])
        gold_answers = set(rec["a_entity"])
        for entity in rec["q_entity"]:
            for rule in rec["predicted_paths"]:
                checked += 1
                official_result = official_bfs_fn(graph, entity, rule)
                profiled_result, _ = bfs_with_rule_profiled_v2(graph, entity, rule)
                if official_result != profiled_result:
                    mismatches += 1
                    continue
                official_reachable = len(path_endpoints(official_result) & gold_answers) > 0
                profiled_reachable = len(path_endpoints(profiled_result) & gold_answers) > 0
                if official_reachable != profiled_reachable:
                    reachability_mismatches += 1
                if len(official_result) != len(profiled_result):
                    path_count_mismatches += 1
    return {
        "dataset_label": dataset_label,
        "checked": checked,
        "mismatches": mismatches,
        "reachability_mismatches": reachability_mismatches,
        "path_count_mismatches": path_count_mismatches,
        "passed": mismatches == 0 and reachability_mismatches == 0 and path_count_mismatches == 0,
    }
