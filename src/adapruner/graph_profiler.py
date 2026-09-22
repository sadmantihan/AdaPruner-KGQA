"""
Read-only, per-hop search-space profiler for relation-constrained BFS.

This module intentionally has NO dependency on the RoG codebase, torch, or
transformers -- it operates on any graph object exposing `.neighbors(node)`
and `graph[u][v]["relation"]` (i.e. any networkx.Graph built the way RoG's
`build_graph` builds one), and on plain (start_node, relation_path) inputs.

Verified equivalent (0 mismatches) to RoG's official `bfs_with_rule` on the
full frozen WebQSP and CWQ test sets -- see the project's `verified-facts.md`
for that run's evidence and provenance.
"""
from collections import deque
import time


def bfs_with_rule_profiled_v2(graph, start_node, target_rule):
    """Relation-constrained BFS, instrumented with read-only search-space counters.

    Parameters
    ----------
    graph : a graph exposing `.neighbors(node)` and `graph[u][v]["relation"]`
    start_node : hashable
        The entity to start the walk from.
    target_rule : list[str]
        Ordered relation names the walk must follow, one per hop.

    Returns
    -------
    (result_paths, profile) : tuple[list, dict]
        `result_paths` is identical in contents, order, and multiplicity to
        the official `bfs_with_rule(graph, start_node, target_rule)`.
        `profile` carries the PRD Section 10/11 per-hop search-space counters.
    """
    t0 = time.perf_counter()
    L = len(target_rule)
    result_paths = []
    active_prefixes = [0] * L
    unique_expanded_sets = [set() for _ in range(L)]
    edges_examined = [0] * L
    candidate_branches = [0] * L
    unique_frontier_sets = [set() for _ in range(L)]
    peak_queue_size = 1
    queue = deque([(start_node, [])])
    while queue:
        if len(queue) > peak_queue_size:
            peak_queue_size = len(queue)
        current_node, current_path = queue.popleft()
        if len(current_path) == L:
            result_paths.append(current_path)
        if len(current_path) < L:
            active_prefixes[len(current_path)] += 1
            if current_node not in graph:
                continue
            hop_idx = len(current_path)
            unique_expanded_sets[hop_idx].add(current_node)
            for neighbor in graph.neighbors(current_node):
                edges_examined[hop_idx] += 1
                rel = graph[current_node][neighbor]["relation"]
                if rel != target_rule[hop_idx] or len(current_path) > len(target_rule):
                    continue
                queue.append((neighbor, current_path + [(current_node, rel, neighbor)]))
                candidate_branches[hop_idx] += 1
                unique_frontier_sets[hop_idx].add(neighbor)
    profile = {
        "plan_length": L,
        "active_prefixes": active_prefixes,
        "unique_expanded_nodes": [len(s) for s in unique_expanded_sets],
        "edges_examined": edges_examined,
        "candidate_branches": candidate_branches,
        "unique_frontier_nodes": [len(s) for s in unique_frontier_sets],
        "peak_active_prefixes": max(active_prefixes) if L > 0 else 0,
        "peak_queue_size": peak_queue_size,
        "retrieved_paths": len(result_paths),
        "time_sec_perf": time.perf_counter() - t0,
        "_unique_expanded_node_sets": unique_expanded_sets,
        "_unique_frontier_node_sets": unique_frontier_sets,
    }
    return result_paths, profile


def path_endpoints(paths):
    """Return the set of terminal entities across a list of retrieved paths."""
    endpoints = set()
    for path in paths:
        if path:
            endpoints.add(path[-1][2])
    return endpoints
