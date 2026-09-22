"""
Oracle diagnostics for search-space headroom analysis.

IMPORTANT: everything in this module is an ORACLE DIAGNOSTIC, not an inference
method. It uses gold answers as an offline admissibility test to measure how
much relation-valid search was structurally unavoidable vs. avoidable by a
perfect pruner. It must never be used to guide or restrict actual retrieval,
and must never feed into AFP training as a label source without an explicit,
separately-justified design decision.
"""
from collections import deque


def suffix_reachable_dp(graph, rule, gold_answers):
    """reachable[h][node] = True iff a relation-valid path exists from `node`
    through rule[h:] to some gold answer. h ranges 0..L inclusive; h == L is
    the base case (no relations left to follow)."""
    L = len(rule)
    reachable = [dict() for _ in range(L + 1)]
    for node in graph.nodes():
        reachable[L][node] = node in gold_answers
    for h in range(L - 1, -1, -1):
        rel = rule[h]
        for node in graph.nodes():
            ok = False
            for neighbor in graph.neighbors(node):
                if graph[node][neighbor]["relation"] == rel and reachable[h + 1].get(neighbor, False):
                    ok = True
                    break
            reachable[h][node] = ok
    return reachable


def brute_force_suffix_reachable(graph, node, rule_suffix, gold_answers):
    """Exhaustive reference implementation, used only to validate the DP above."""
    if len(rule_suffix) == 0:
        return node in gold_answers
    if node not in graph:
        return False
    for neighbor in graph.neighbors(node):
        if graph[node][neighbor]["relation"] == rule_suffix[0]:
            if brute_force_suffix_reachable(graph, neighbor, rule_suffix[1:], gold_answers):
                return True
    return False


def oracle_headroom_for_plan(graph, start_node, rule, reachable_dp):
    """Attribute edges_examined / candidate_branches per hop to "productive"
    (on some gold-reaching suffix) vs "doomed" (structurally cannot reach gold)
    prefixes. Upper-bounds what a perfect oracle pruner could have avoided."""
    L = len(rule)
    edges_prod, edges_doom = [0] * L, [0] * L
    branch_prod, branch_doom = [0] * L, [0] * L
    queue = deque([(start_node, [])])
    while queue:
        current_node, current_path = queue.popleft()
        if len(current_path) < L:
            if current_node not in graph:
                continue
            h = len(current_path)
            is_productive = reachable_dp[h].get(current_node, False)
            for neighbor in graph.neighbors(current_node):
                if is_productive:
                    edges_prod[h] += 1
                else:
                    edges_doom[h] += 1
                rel = graph[current_node][neighbor]["relation"]
                if rel != rule[h] or len(current_path) > len(rule):
                    continue
                if is_productive:
                    branch_prod[h] += 1
                else:
                    branch_doom[h] += 1
                queue.append((neighbor, current_path + [(current_node, rel, neighbor)]))
    return {
        "edges_examined_productive": edges_prod, "edges_examined_doomed": edges_doom,
        "branches_productive": branch_prod, "branches_doomed": branch_doom,
    }
