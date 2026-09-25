# AdaPruner-KGQA

Official implementation of:

**AdaPruner-KGQA: An Adaptive Search-Space Pruning Framework for Efficient Multi-Hop Knowledge Graph Question Answering**

AdaPruner-KGQA extends relation-constrained multi-hop KGQA with an
**Adaptive Frontier Pruner (AFP)** that reduces unnecessary graph exploration
while preserving the original RoG planner and downstream reasoner.

## Status

**Experimental pipeline implemented and frozen.**

The repository contains the reproducible experimental pipeline for RoG baseline
reproduction, RQ1 search-space profiling, AFP development and validation-only
selection, controlled frozen-TEST evaluation, feature ablations, and downstream
RoG-vs-AFP LLM reasoning on WebQSP and CWQ.

In the final frozen downstream evaluation, AFP achieves **85.7 Hits@1 / 69.9 F1
on WebQSP** compared with **86.1 / 70.1 for RoG**, and **60.4 Hits@1 / 53.2 F1
on CWQ** compared with **60.9 / 53.7 for RoG**, while reducing examined graph
edges by **2.24% on WebQSP** and **5.05% on CWQ**.
## Research Questions

The experiments are organized around three research questions:

**RQ1.** Where and to what extent does residual search-space growth occur
during RoG relation-constrained multi-hop retrieval?

**RQ2.** Can adaptive frontier pruning reduce unnecessary graph exploration
more effectively than unpruned RoG and simple fixed-pruning strategies?

**RQ3.** Can the reduced search space preserve RoG-reachable answers and
downstream KGQA performance while improving retrieval efficiency?

## Method Overview

RoG constrains graph traversal using predicted relation paths, but multiple
entities may still satisfy the same relation at intermediate hops. This can
produce substantial residual branch growth even when the relation sequence is
already fixed.

AdaPruner-KGQA introduces the **Adaptive Frontier Pruner (AFP)** at these
intermediate branch-expansion points.

AFP:

- preserves RoG's predicted relation plans;
- preserves the underlying knowledge graph;
- preserves relation matching and candidate generation;
- preserves the original downstream RoG reasoner;
- scores only relation-valid intermediate candidates;
- adaptively controls how many candidate branches continue;
- keeps the final hop unpruned under the frozen experimental policy.

AFP therefore changes **which relation-valid intermediate branches are
continued**, rather than replacing the RoG planner or performing unrestricted
graph search.

## Supported Benchmarks

- **WebQuestionsSP (WebQSP)**
- **ComplexWebQuestions (CWQ)**

Both benchmarks use Freebase-based multi-hop knowledge graph question
answering settings.

## Repository Structure

```text
AdaPruner-KGQA/
├── README.md
├── LICENSE
├── CITATION.cff
├── .gitignore
├── pyproject.toml
│
├── src/
│   └── adapruner/
│       └── validated search-space profiling and AFP-related utilities
│
├── tests/
│   └── unit tests using synthetic graphs with no external KG dependency
│
└── notebooks/
    ├── 01_rog_webqsp_baseline.ipynb
    ├── 02_rog_cwq_baseline.ipynb
    ├── 03_rq1_search_space_profiling.ipynb
    ├── 04_rq2_training_feature_and_selector_development.ipynb
    ├── 05_rq2_validation_tuning_and_ablations.ipynb
    ├── 06_final_test_rq1_profiling_and_recovery.ipynb
    ├── 06_rq2_final_frozen_test_ablation.ipynb
    ├── 07_final_test_rq2_controlled_comparison.ipynb
    └── 07_rq3_llm_reasoning.ipynb
```
## Key Results

The final frozen evaluation compares AdaPruner's **Adaptive Frontier Pruner (AFP)**
against the unpruned RoG retrieval pipeline while preserving the same relation
plans and downstream RoG reasoner.

### Downstream KGQA Performance

| Dataset | Method | Hits@1 | F1 | Δ Hits@1 vs. RoG | Δ F1 vs. RoG |
|---|---|---:|---:|---:|---:|
| WebQSP | RoG | 86.1 | 70.1 | — | — |
| WebQSP | AFP | 85.7 | 69.9 | -0.4 pp | -0.2 pp |
| CWQ | RoG | 60.9 | 53.7 | — | — |
| CWQ | AFP | 60.4 | 53.2 | -0.5 pp | -0.5 pp |

AFP therefore reduces graph exploration while keeping downstream QA performance
close to the frozen RoG baseline.

### Retrieval Efficiency and Answer Retention

| Dataset | Search-Space Reduction | Answer Retention | Retrieved-Path Reduction | Reasoner-Input Token Reduction |
|---|---:|---:|---:|---:|
| WebQSP | 2.24% | 99.20% | 21.8% | 10.6% |
| CWQ | 5.05% | 98.72% | 27.0% | 6.2% |

**Search-space reduction** is measured using examined graph edges relative to
the unpruned RoG traversal. **Answer retention** measures the proportion of
RoG-reachable questions that remain reachable after AFP pruning.

These results should not be interpreted as AFP being the most aggressive
pruning strategy in every setting. The controlled experiments evaluate the
trade-off between reduced graph exploration and preservation of answer
reachability and downstream KGQA performance.

