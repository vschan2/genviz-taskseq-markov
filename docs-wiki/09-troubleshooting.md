# Troubleshooting

## Table of Contents

1. ["Missing columns" error](#missing-columns-error)
2. [Empty or blank visualizations](#empty-or-blank-visualizations)
3. [Some goals have very few sequences](#some-goals-have-very-few-sequences)
4. [Network analysis returns empty results](#network-analysis-returns-empty-results)
5. [Community detection shows only 1 community](#community-detection-shows-only-1-community)
6. [All entropy values are similar](#all-entropy-values-are-similar)
7. [Workflow path analysis shows too many paths](#workflow-path-analysis-shows-too-many-paths)

---

## "Missing columns" error

**Cause:** The CSV uses different column names from the defaults (`task_sequence`, `biological_goal`, `tool_name`).

**Solution:** Specify the actual column names with flags:

```bash
python task_analysis_utilities.py --file data.csv \
  --sequence your_sequence_col \
  --goal your_goal_col \
  --tool your_tool_col
```

See [Usage Examples](03-usage-examples.md#example-1-custom-column-names) for a full example.

---

## Empty or blank visualizations

**Cause:** The `min_probability` threshold is too high — all transitions are filtered out.

**Solution:** Lower the threshold in [Utility 10](04-utilities.md#utility-10-visualize-task-flow). In interactive mode, when prompted enter a lower value (e.g., `0.05` instead of `0.1`). Try `0.0` first to confirm any transitions exist.

---

## Some goals have very few sequences

**Cause:** Uneven distribution of goals in the dataset — this is expected.

**Options:**
- Combine similar goals into a single category before loading
- Filter out goals with fewer than 3 sequences before analysis
- Interpret results for small-sample goals with extra caution (probabilities from 1–2 sequences are not statistically reliable)

---

## Network analysis returns empty results

**Cause:** Either `min_probability` is too high (all edges filtered out), the graph is disconnected, or sequences are too short to build meaningful transitions.

**Solution:**
1. Set `min_probability=0.0` and re-run
2. Verify the data has multi-task sequences (not all single-task entries)
3. Check that `calculate_transition_probabilities()` was called (done automatically by `load_csv_data()`)

---

## Community detection shows only 1 community

**Cause:** This is normal for small or highly connected datasets. Greedy modularity needs sufficient graph structure to find distinct clusters.

**Options:**
- Increase `min_probability` to remove weak edges and expose clearer clusters
- Accept the result as valid — it may genuinely mean tasks are well-integrated with no modular subgroups
- Ensure you have at least 10–15 tasks for meaningful detection

See [Utility 13](04-utilities.md#utility-13-community-detection) for modularity score interpretation.

---

## All entropy values are similar

**Cause:** The workflows have uniform structure — users take similarly varied paths from every task. This can be a genuine finding, not a data issue.

**What to do:**
- Compare entropy across goals using `by_goal=True` in [Utility 14](04-utilities.md#utility-14-transition-entropy-analysis) — some goals may be more rigid than others
- Verify you have multiple distinct paths from each task (need sufficient data diversity)
- If entropy is uniformly 0, check that sequences are longer than 2 tasks

---

## Workflow path analysis shows too many paths

**Cause:** `max_path_length` is set too high, or `min_probability` is too low, including many rare paths.

**Solution:**
- Lower `max_path_length` (try 5–7 edges for typical data)
- Increase `min_probability` to filter out rare transitions (try 0.1)
- Focus on the top 10–20 most frequent paths rather than the full list

See [Utility 12](04-utilities.md#utility-12-workflow-path-analysis) for parameter details.

---

**See also:** [Tips & Best Practices](08-tips.md) | [Available Utilities](04-utilities.md)
