# AdaPruner-KGQA

Official implementation of:

**AdaPruner-KGQA: An Adaptive Search-Space Pruning Framework for Efficient Multi-Hop Knowledge Graph Question Answering**

## Status

**In progress.** RoG baselines (WebQSP, CWQ) are frozen and verified against
the original paper's reported numbers. Currently running RQ1: read-only
search-space profiling. No AFP results exist yet.

## Supported Benchmarks

- WebQuestionsSP (WebQSP)
- ComplexWebQuestions (CWQ)

## Repository Structure

AdaPruner-KGQA/
- README.md, LICENSE, CITATION.cff, .gitignore, pyproject.toml
- src/adapruner/ -- validated, tested search-space profiler + oracle diagnostics
- tests/ -- unit tests (synthetic graph, no external dependencies)
- notebooks/ -- experimental record (Kaggle notebook)
