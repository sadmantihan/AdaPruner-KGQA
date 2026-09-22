import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import networkx as nx
from adapruner.oracle import suffix_reachable_dp, brute_force_suffix_reachable


def _build_toy_graph():
    g = nx.DiGraph()
    g.add_edge("A", "B", relation="r1")
    g.add_edge("B", "D", relation="r2")
    g.add_edge("A", "C", relation="r1")
    g.add_edge("C", "D", relation="r3")
    g.add_edge("A", "E", relation="r_other")
    return g


def test_dp_matches_brute_force():
    g = _build_toy_graph()
    gold = {"D"}
    rule = ["r1", "r2"]
    reachable = suffix_reachable_dp(g, rule, gold)
    for h in range(len(rule) + 1):
        for node in g.nodes():
            assert reachable[h].get(node, False) == brute_force_suffix_reachable(g, node, rule[h:], gold)


def test_c_is_doomed_at_hop_1():
    g = _build_toy_graph()
    gold = {"D"}
    rule = ["r1", "r2"]
    reachable = suffix_reachable_dp(g, rule, gold)
    assert reachable[1]["C"] is False
    assert reachable[1]["B"] is True
