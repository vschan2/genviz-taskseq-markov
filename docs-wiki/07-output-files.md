# Output Files Reference

All files written to disk by the utilities. Goal names in filenames have spaces replaced with underscores; `&` is kept literally (watch for shell-escaping when referencing these paths).

---

## Table of Contents

1. [Basic Analysis Outputs](#basic-analysis-outputs)
2. [Goal-Stratified Outputs](#goal-stratified-outputs)
3. [Network Analysis Outputs](#network-analysis-outputs)
4. [Visualizations](#visualizations)

---

## Basic Analysis Outputs

| File | Utility | Description |
|------|---------|-------------|
| `transition_matrix.csv` | 3 | Overall transition probability matrix (all goals combined) |
| `pairwise_transitions.csv` | 9 | All individual transitions with `tool`, `goal`, `from_state`, `to_state`, `position`, `sequence_length` |

---

## Goal-Stratified Outputs

| File | Utility | Description |
|------|---------|-------------|
| `goal_[name]_transitions.csv` | 4 | Pairwise transitions filtered to a specific biological goal |
| `goal_comparison_summary.csv` | 4 | Summary row per goal: sequence count, unique tasks, avg length |
| `goal_[name]_matrix.csv` | 5 | Transition probability matrix for a specific goal; used as input to Utility 16 |
| `goal_transition_comparison.csv` | 6 | Per-transition variance, mean, and std deviation across goals |

---

## Network Analysis Outputs

| File | Utility | Description |
|------|---------|-------------|
| `centrality_metrics.csv` | 11 | Betweenness, PageRank, in-degree, out-degree for all tasks (overall) |
| `goal_[name]_centrality.csv` | 11 | Same metrics, filtered to a specific goal |
| `goal_centrality_comparison.csv` | 11 | Centrality metrics side-by-side across all goals |
| `workflow_paths.csv` | 12 | All observed paths with frequency and percentage (overall) |
| `goal_[name]_paths.csv` | 12 | Observed paths for a specific goal |
| `task_communities.csv` | 13 | Task community assignments and modularity score (overall) |
| `goal_[name]_communities.csv` | 13 | Community assignments for a specific goal |
| `transition_entropy.csv` | 14 | Shannon entropy value per task (overall) |
| `goal_[name]_entropy.csv` | 14 | Entropy values for a specific goal |
| `task_persistence.csv` | 15 | Self-loop probability per task (overall) |
| `goal_[name]_persistence.csv` | 15 | Self-loop probabilities for a specific goal |

---

## Visualizations

| File | Utility | Description |
|------|---------|-------------|
| `task_flow_diagram.png` | 10 | Network diagram of all task transitions (overall) |
| `goal_[name]_flow.png` | 10 | Network diagram for a specific goal |
| `transition_heatmap-[matrix_stem].png` | 16 | 300 dpi heatmap generated from a `goal_[name]_matrix.csv`; `matrix_stem` matches the input filename |

---

**Tip:** Run [Utility 9](04-utilities.md#utility-9-export-pairwise-transitions) first to get the raw `pairwise_transitions.csv` — it is the most flexible export format and can be imported into R, Python, or custom tools directly.
