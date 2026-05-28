# Tips & Best Practices

## Table of Contents

1. [General Tips](#general-tips)
2. [Data Quality Tips](#data-quality-tips)
3. [Network Analysis Tips](#network-analysis-tips)
4. [Workflow Analysis Tips](#workflow-analysis-tips)

---

## General Tips

1. **Start with Utility 1** — Always run summary statistics first to understand your data before any deeper analysis.

2. **Goal-stratified analysis is key** — [Utility 4](04-utilities.md#utility-4-goal-stratified-transition-analysis) is the most informative starting point for understanding differences between biological goals.

3. **Network analysis for deeper insights** — [Utilities 11–15](04-utilities.md#utility-11-centrality-analysis) reveal hidden patterns and task importance that transition probabilities alone do not show.

4. **Visualizations for presentations** — Use [Utility 10](04-utilities.md#utility-10-visualize-task-flow) for network diagrams and [Utility 16](04-utilities.md#utility-16-transition-probability-heatmap) for heatmaps suitable for papers or slides.

5. **Export everything** — Use [Utility 9](04-utilities.md#utility-9-export-pairwise-transitions) to export raw pairwise data for custom analysis.

6. **Interactive mode for exploration** — Use the `--interactive` flag when you are still learning the dataset; it lets you run any utility without restarting.

---

## Data Quality Tips

7. **Check sample sizes** — Small sample sizes for a goal may produce unreliable probabilities. Interpret results cautiously for goals with fewer than 5–10 sequences.

8. **Minimum probability threshold** — For visualizations and network analysis, adjust `min_probability` to reduce noise. Start at 0.0 and raise it to filter weak transitions.

9. **Validate results** — Cross-check network metrics with domain knowledge. A task scoring high in betweenness should make intuitive sense as a workflow bridge.

---

## Network Analysis Tips

10. **Interpret centrality carefully** — High betweenness does not mean "important"; it means "on many shortest paths." Combine it with PageRank and domain knowledge for a complete picture.

11. **Community detection needs sufficient data** — Expect meaningful results only with 10–15 or more tasks. A single-community result on small data is valid — it means no modular structure exists.

12. **Entropy interpretation** — High entropy means flexibility at a decision point, not necessarily good or bad workflow design. Compare across goals to see where flexibility differs.

13. **Self-loops indicate effort** — Tasks with high self-loop probability require iteration or time. This is a proxy for task difficulty or cognitive load, not a flaw.

14. **Combine metrics** — Look at centrality + entropy + persistence together for a complete picture of each task's role.

---

## Workflow Analysis Tips

15. **Path length matters** — Set `max_path_length` to match your data. Typical range is 7–12 edges; setting it too low truncates valid paths, too high creates noise.

16. **Compare across goals** — Use `by_goal=True` on any network utility to see how task importance and clustering differ between biological goals.

17. **Sequential analysis order** — Run basic analysis (Utilities 1–4) first, then network analysis (Utilities 11–15). Start broad, then drill down.

18. **Export for custom visualization** — Network CSV outputs can be imported into [Gephi](https://gephi.org/), Cytoscape, or R (`igraph`) for advanced graph visualization.

---

**See also:** [Troubleshooting](09-troubleshooting.md) | [Available Utilities](04-utilities.md)
