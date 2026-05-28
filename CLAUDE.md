# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Context

This is a research toolkit for a Systematic Literature Review (SLR) on biodiversity genomics visualization tools. It applies Markov chain analysis of task sequences to analyze how researchers navigate analytical workflows across different biological goals. 

## Dependencies

```bash
pip install pandas numpy matplotlib networkx seaborn
```

`transition_matrix_to_heatmap.py` additionally requires `seaborn`. Flow diagram visualization in `task_sequence_markov_analysis.py` requires `graphviz` (system-level) for `nx.nx_agraph.graphviz_layout`.

## Running the Analysis

```bash
# Interactive mode — recommended entry point
python task_analysis_utilities.py --file your_data.csv --interactive

# Run a specific utility by number (1–16)
python task_analysis_utilities.py --file your_data.csv --utility 4

# Custom column names (when CSV differs from defaults)
python task_analysis_utilities.py --file slr_data.csv \
  --sequence VTA_Task_Combinations \
  --goal DC_Primary_Goal \
  --tool Tool_Name \
  --interactive
```

Default column names expected by the loader: `task_sequence`, `biological_goal`, `tool_name`. Tasks in a sequence are `→`-delimited (not `->` or `,`).

To generate a heatmap from an already-computed transition matrix CSV:

```bash
python transition_matrix_to_heatmap.py
```

Edit `matrix_name` at the top of that script to target a different goal's matrix file.

## Architecture

### Core class: `TaskSequenceAnalyzer` (`task_sequence_markov_analysis.py`)

All Markov chain logic lives here. Key internals:
- `transition_counts`: `defaultdict(Counter)` — raw co-occurrence counts for each `(from_state, to_state)` pair.
- `transition_probs`: dict of dicts — computed after calling `calculate_transition_probabilities()`. Must be called before any analysis method.
- `sequences`: list of dicts with keys `sequence` (always includes `START`/`END` tokens), `goal`, `tool`, `length`.

Sequences are normalized to lowercase at load time. `START` and `END` sentinel tokens are added by `add_sequence()` and are present in `sequences[i]['sequence']` but excluded from most analysis outputs.

Analysis methods on the class (all require `calculate_transition_probabilities()` to have been called first):
- `calculate_centrality_metrics()` — degree, betweenness, PageRank via NetworkX
- `analyze_workflow_paths()` — counts actual observed sequences (not graph-enumerated paths)
- `detect_communities()` — converts DiGraph to undirected, removes START/END, runs greedy modularity
- `calculate_transition_entropy()` — Shannon entropy per node over outgoing edge weights
- `analyze_task_persistence()` — self-loop probability per node

### CLI wrapper: `TaskAnalysisUtilities` (`task_analysis_utilities.py`)

Wraps `TaskSequenceAnalyzer` with 15 numbered utilities, CSV loading, and file export. The `load_csv_data()` method parses CSV, splits sequences on `→`, lowercases tasks, and calls `calculate_transition_probabilities()` at the end. Utilities 4–7 call `analyzer.analyze_by_goal()` which returns a dict of per-goal `TaskSequenceAnalyzer` instances (each with probabilities already calculated).

### Heatmap script: `transition_matrix_to_heatmap.py`

Standalone script (not integrated into the CLI). Reads a `goal_*_matrix.csv` from `output_data/`, applies a fixed task display order, and produces a publication-quality PNG. Change `matrix_name` at the top to switch targets. Font falls back from Calibri to DejaVu Sans automatically.

## Task Vocabulary

Tasks belong to two frameworks:
- **Nusrat search tasks**: `lookup`, `locate`, `browse`, `explore`
- **Gleicher comparative tasks**: `identify`, `dissect`, `measure/quantify/summarize`, `connect`, `contextualize`, `communicate`

`measure/quantify/summarize` is a compound label used as a single token. The heatmap script has a `label_map` dict to render it with line breaks for display.

## Biological Goals in the Dataset

Four goals appear in the output data: Species Identification & Marker Development, Evolutionary Study & Phylogenetic Analysis, Genomic Structure & Diversity Assessment, Population Structure Analysis.

Goal names in output filenames have spaces replaced with underscores and `&` kept literally (watch for shell-escaping when referencing these paths).

If there are new goals from the data, inform and remind the author to update the goal list as in this file.
