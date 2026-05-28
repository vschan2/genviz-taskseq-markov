# Task Analysis Utilities - Quick Reference Card

## Command Line Usage

```bash
# Interactive mode (recommended for first-time users)
python task_analysis_utilities.py --file data.csv --interactive

# Run specific utility
python task_analysis_utilities.py --file data.csv --utility 4

# Custom column names
python task_analysis_utilities.py --file data.csv \
  --sequence VTA_Task_Combinations \
  --goal DC_Primary_Goal \
  --tool Tool_Name
```

---

## 16 Available Utilities

### Basic Analysis (1–3)
| # | Utility | Purpose | Key Output |
|---|---------|---------|------------|
| 1 | Summary Statistics | Dataset overview | Counts, averages, task list |
| 2 | Transition Probabilities | Most likely next states | Top-K transitions per task |
| 3 | Transition Matrix | Full probability matrix | `transition_matrix.csv` |

### Goal-Stratified Analysis (4–7)
| # | Utility | Purpose | Key Output |
|---|---------|---------|------------|
| 4 | Goal-Stratified Analysis ⭐ | Separate analysis by goal | Per-goal CSV files |
| 5 | Matrices by Goal | Goal-specific matrices | Per-goal matrix CSV files |
| 6 | Compare Goals | Find varying transitions | `goal_transition_comparison.csv` |
| 7 | Goal-Specific Patterns | Unique transitions per goal | Unique vs shared breakdown |

### Sequence Analysis (8–10)
| # | Utility | Purpose | Key Output |
|---|---------|---------|------------|
| 8 | Sequence Probability | Calculate sequence likelihood | Probability + goal prediction |
| 9 | Export Pairwise | Raw transition data | `pairwise_transitions.csv` |
| 10 | Visualize Flow | Network diagrams | PNG files |

### Network Analysis (11–15)
| # | Utility | Purpose | Key Output |
|---|---------|---------|------------|
| 11 | Centrality Analysis | Find important/central tasks | `centrality_metrics.csv` |
| 12 | Workflow Path Analysis | Discover dominant workflows | `workflow_paths.csv` |
| 13 | Community Detection | Identify task clusters | `task_communities.csv` |
| 14 | Transition Entropy | Measure workflow flexibility | `transition_entropy.csv` |
| 15 | Task Persistence | Identify sticky tasks | `task_persistence.csv` |

### Visualization (16)
| # | Utility | Purpose | Key Output |
|---|---------|---------|------------|
| 16 | Transition Heatmap | Publication-quality heatmap from a goal matrix CSV | `transition_heatmap_*.png` |

⭐ = Addresses question about separating analysis by biological_goal

---

## Which Utility Should I Use?

### "I want to understand my data"
→ Start with **Utility 1** (Summary Statistics)

### "How do tasks flow together?"
→ Use **Utility 2** (Transition Probabilities)

### "Do different biological goals use different workflows?"
→ Use **Utility 4** (Goal-Stratified Analysis) ⭐

### "Which transitions are unique to each goal?"
→ Use **Utility 7** (Goal-Specific Patterns)

### "Which tasks are most important/central?"
→ Use **Utility 11** (Centrality Analysis)

### "What are the most common complete workflows?"
→ Use **Utility 12** (Workflow Path Analysis)

### "Are there groups of related tasks?"
→ Use **Utility 13** (Community Detection)

### "Which tasks have flexible vs rigid workflows?"
→ Use **Utility 14** (Transition Entropy)

### "Which tasks take more time/effort?"
→ Use **Utility 15** (Task Persistence)

### "I need to export data for further analysis"
→ Use **Utility 9** (Export Pairwise)

### "I need visualizations for my paper"
→ Use **Utility 10** (Visualize Flow) or **Utility 16** (Transition Heatmap)

---

## Output Files

### Basic Analysis
| File | Contains |
|------|----------|
| `transition_matrix.csv` | Overall transition probabilities |
| `pairwise_transitions.csv` | All transitions with metadata |

### Goal-Stratified Analysis
| File | Contains |
|------|----------|
| `goal_[name]_transitions.csv` | Transitions for specific goal |
| `goal_[name]_matrix.csv` | Matrix for specific goal |
| `goal_comparison_summary.csv` | Goal statistics comparison |
| `goal_transition_comparison.csv` | Transition variance across goals |

### Network Analysis
| File | Contains |
|------|----------|
| `centrality_metrics.csv` | Overall centrality metrics (degree, betweenness, pagerank) |
| `goal_[name]_centrality.csv` | Centrality metrics for specific goal |
| `goal_centrality_comparison.csv` | Centrality comparison across goals |
| `workflow_paths.csv` | All workflow paths with frequencies |
| `goal_[name]_paths.csv` | Workflow paths for specific goal |
| `task_communities.csv` | Task community assignments |
| `goal_[name]_communities.csv` | Communities for specific goal |
| `transition_entropy.csv` | Entropy values for all tasks |
| `goal_[name]_entropy.csv` | Entropy values for specific goal |
| `task_persistence.csv` | Self-loop probabilities |
| `goal_[name]_persistence.csv` | Self-loop probabilities for specific goal |

### Visualizations
| File | Contains |
|------|----------|
| `task_flow_diagram.png` | Overall network visualization |
| `goal_[name]_flow.png` | Goal-specific network visualization |
| `transition_heatmap_[name].png` | Transition probability heatmap (Utility 16) |

---

## Tips

1. Always run Utility 1 first to understand your data
2. Use Utility 4 for goal comparisons (answers question c)
3. Run Utility 11 to identify important/central tasks
4. Use Utility 12 to discover dominant workflow patterns
5. Export with Utility 9 for custom analysis
6. Visualize with Utility 10 for network diagrams, Utility 16 for heatmaps
7. Check sample sizes before interpreting network metrics
8. Use interactive mode for exploration
9. Combine utilities (e.g., 4 + 11) for goal-specific network analysis

---

## Need Help?

- **Full documentation**: See `TASK_ANALYSIS_UTILITIES_GUIDE.md`
- **Code examples**: See `task_sequence_markov_analysis.py`

---

**Quick Start:**
```bash
python task_analysis_utilities.py --file your_data.csv --interactive
```

**Recommended first utilities:** 1 (overview), 4 (goal analysis), 11 (centrality)
