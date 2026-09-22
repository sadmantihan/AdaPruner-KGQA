"""Unit tests for graph_profiler on a small synthetic graph.

Run with: pytest tests/ -v
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import networkx as nx
from adapruner.graph_profiler import bfs_with_rule_profiled_v2, path_endpoints


def official_bfs_with_rule(graph, start_node, target_rule):
    """Minimal reference re-implementation (unprofiled) for cross-checking."""
    from collections import deque
    L = len(target_rule)
    result_paths = []
    queue = deque([(start_node, [])])
    while queue:
        current_node, current_path = queue.popleft()
        if len(current_path) == L:
            result_paths.append(current_path)
        if len(current_path) < L and current_node in graph:
            for neighbor in graph.neighbors(current_node):
                rel = graph[current_node][neighbor]["relation"]
                if rel == target_rule[len(current_path)]:
                    queue.append((neighbor, current_path + [(current_node, rel, neighbor)]))
    return result_paths


def _build_toy_graph():
    """A -> B -> D (via r1, r2); A -> C -> D (via r1, r3); A -> E (via r_other)."""
    g = nx.DiGraph()
    g.add_edge("A", "B", relation="r1")
    g.add_edge("B", "D", relation="r2")
    g.add_edge("A", "C", relation="r1")
    g.add_edge("C", "D", relation="r3")
    g.add_edge("A", "E", relation="r_other")
    return g


def test_profiled_matches_official_two_hop():
    g = _build_toy_graph()
    official = official_bfs_with_rule(g, "A", ["r1", "r2"])
    profiled, profile = bfs_with_rule_profiled_v2(g, "A", ["r1", "r2"])
    assert profiled == official
    assert profile["retrieved_paths"] == 1
    assert profile["candidate_branches"][0] == 2
    assert profile["candidate_branches"][1] == 1


def test_reachability_via_path_endpoints():
    g = _build_toy_graph()
    paths, _ = bfs_with_rule_profiled_v2(g, "A", ["r1", "r2"])
    assert path_endpoints(paths) == {"D"}


def test_empty_rule_returns_one_trivial_zero_hop_path():
    """L=0 means the walk terminates immediately at start_node: result_paths
    is [[]] (one trivial empty-relation path), not []. This matches the
    verified-equivalent official BFS's own behavior for a zero-length rule.

    NOTE: the real retrieval pipeline never calls this function with an empty
    rule directly -- it guards with `if len(rule) > 0` beforehand. This test
    documents the function's actual behavior in isolation, not a pipeline path.
    """
    g = _build_toy_graph()
    paths, profile = bfs_with_rule_profiled_v2(g, "A", [])
    assert paths == [[]]
    assert profile["plan_length"] == 0
    assert path_endpoints(paths) == set()
