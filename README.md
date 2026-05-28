# Task Sequence Analysis for Biodiversity Genomics Visualization Tools

Markov chain analysis toolkit for analyzing task sequences from systematic literature review (SLR) data.

**Title:** Domain-Task Mapping Framework for Multi-View Biodiversity Comparative Genomics Visualization: A Systematic Literature Review

**Authors:** Vei Siang Chan, Farhan Bin Mohamed, Faezah Binti Mohd Salleh, Andres Iglesias, Alfie Abdul-Rahman, Marilyn Miga, Fallah H. Najjar, Chunqing Cao

**For The Visual Computer Submission Requirement:** Chan, V. S., Mohamed, F. B., Salleh, F. B. M., Iglesias, A., Abdul-Rahman, A., Miga, M., Najjar, F. H., & Cao, C. (2026). Domain-Task Mapping Framework for Multi-View Biodiversity Comparative Genomics Visualization: A Systematic Literature Review. The Visual Computer. Manuscript submitted for review.

---

## What This Does

Analyzes task sequences from SLR data to understand how researchers navigate visualization tool workflows. Computes Markov chain transition probabilities, separates analysis by biological goal, and provides 16 utilities covering summary statistics, goal-stratified analysis, network centrality, community detection, entropy, task persistence, and publication-quality heatmap visualization.

---

## Quick Start

### 1. Install Dependencies
```bash
pip install pandas numpy matplotlib networkx seaborn
```

### 2. Prepare Your Data

Create a CSV with these columns:
- `task_sequence`: Tasks separated by `→` (e.g., `Locate→Identify→Lookup`)
- `biological_goal`: The biological goal
- `tool_name`: The tool name

### 3. Run Analysis
```bash
# Interactive mode (recommended)
python task_analysis_utilities.py --file your_data.csv --interactive

# Run a specific utility by number (1–16)
python task_analysis_utilities.py --file your_data.csv --utility 4

# Custom column names
python task_analysis_utilities.py --file slr_data.csv \
  --sequence VTA_Task_Combinations \
  --goal DC_Primary_Goal \
  --tool Tool_Name \
  --interactive
```

---

## Files

| File | Purpose |
|------|---------|
| `task_analysis_utilities.py` | Main interactive CLI — start here |
| `task_sequence_markov_analysis.py` | Core Markov chain analyzer (imported by main tool) |
| `QUICK_REFERENCE.md` | CLI commands and utility list |
| `docs-wiki/*.md` | Complete documentation |

---

## Documentation

- **Full guide:** [Task Analysis Utilities — Documentation](docs-wiki/README.md)
- **Quick lookup:** [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
