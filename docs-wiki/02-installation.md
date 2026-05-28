# Installation

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Optional Packages](#optional-packages)
3. [Required Files](#required-files)

---

## Prerequisites

```bash
pip install pandas numpy matplotlib networkx
```

> **Note:** NetworkX is required for network analysis utilities (11–15). Ensure you have NetworkX >= 2.5 for community detection features.

---

## Optional Packages

```bash
pip install seaborn       # Required for Utility 16 (transition heatmap) and enhanced visualizations
pip install pygraphviz    # Better graph layouts in Utility 10 (requires Graphviz installed system-wide)
```

`seaborn` is needed specifically for Utility 16. If it is not installed, a clear error message is printed and the utility exits without crashing.

---

## Required Files

Ensure these files are in the same directory before running:

| File | Purpose |
|------|---------|
| `task_analysis_utilities.py` | CLI wrapper — the entry point you run |
| `task_sequence_markov_analysis.py` | Core `TaskSequenceAnalyzer` class |

---

**Next:** [Usage Examples](03-usage-examples.md) — command-line flags and programmatic patterns.
