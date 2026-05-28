# Network Analysis Functions

Programmatic API for the five network analysis methods on `TaskSequenceAnalyzer`. These correspond to [Utilities 11–15](04-utilities.md#utility-11-centrality-analysis) in the CLI.

All methods require `calculate_transition_probabilities()` to have been called first — this is done automatically by `load_csv_data()`.

---

## Table of Contents

1. [Setup](#setup)
2. [`calculate_centrality_metrics`](#calculate_centrality_metrics)
3. [`analyze_workflow_paths`](#analyze_workflow_paths)
4. [`detect_communities`](#detect_communities)
5. [`calculate_transition_entropy`](#calculate_transition_entropy)
6. [`analyze_task_persistence`](#analyze_task_persistence)

---

## Setup

```python
from task_analysis_utilities import TaskAnalysisUtilities

utilities = TaskAnalysisUtilities()
utilities.load_csv_data('your_data.csv')
```

NetworkX must be installed (`pip install networkx`). All five functions build a `networkx.DiGraph` from the transition probabilities, filtered by `min_probability`.

---

## `calculate_centrality_metrics`

Calculates degree, betweenness, and PageRank centrality for all tasks in the transition graph.

```python
result = utilities.analyzer.calculate_centrality_metrics(min_probability=0.0)

# Tabular output
for task_info in result['centrality_data']:
    print(f"{task_info['task']:15s} | "
          f"Betweenness: {task_info['betweenness_centrality']:.3f} | "
          f"PageRank: {task_info['pagerank']:.3f}")

# Individual metric dicts
betweenness = result['betweenness_centrality']  # task -> score
pagerank    = result['pagerank']                # task -> score
graph       = result['graph']                   # networkx.DiGraph
```

**Result keys:**

| Key | Type | Description |
|-----|------|-------------|
| `centrality_data` | list of dicts | One entry per task with all metrics |
| `betweenness_centrality` | dict | task → betweenness score |
| `pagerank` | dict | task → PageRank score |
| `graph` | `DiGraph` | The underlying NetworkX graph |

---

## `analyze_workflow_paths`

Counts the actual observed sequences (not all graph-enumerated paths) from `START` to `END`.

```python
result = utilities.analyzer.analyze_workflow_paths(max_path_length=9)

print(f"Total unique workflows: {result['total_unique_paths']}")

print("\nTop 5 most common workflows:")
for i, (path, freq) in enumerate(result['sorted_paths'][:5], 1):
    path_str = ' → '.join(path[1:-1])  # Exclude START/END
    pct = (freq / result['total_path_instances']) * 100
    print(f"{i}. [{freq} times, {pct:.1f}%] {path_str}")

print("\nPath length distribution:")
for length, count in result['path_length_distribution'].items():
    print(f"  {length} edges: {count} paths")
```

**Result keys:**

| Key | Type | Description |
|-----|------|-------------|
| `total_unique_paths` | int | Number of distinct observed paths |
| `total_path_instances` | int | Total occurrences across all paths |
| `sorted_paths` | list of `(path_tuple, freq)` | Paths sorted by frequency descending |
| `path_length_distribution` | dict | edge_count → number of paths of that length |

---

## `detect_communities`

Detects task clusters using greedy modularity optimization. The DiGraph is converted to undirected and `START`/`END` nodes are removed before clustering.

```python
result = utilities.analyzer.detect_communities(min_probability=0.0)

print(f"Found {result['num_communities']} communities")
print(f"Modularity score: {result['modularity']:.4f}")

for idx, community in enumerate(result['communities'], 1):
    tasks = sorted(list(community))
    print(f"\nCommunity {idx} ({len(tasks)} tasks): {', '.join(tasks)}")

# Community assignment for a specific task
task_to_comm = result['task_to_community']
print(f"\n'identify' is in community {task_to_comm['identify'] + 1}")
```

**Result keys:**

| Key | Type | Description |
|-----|------|-------------|
| `num_communities` | int | Number of detected communities |
| `modularity` | float | Modularity score (higher = more distinct communities) |
| `communities` | list of sets | Each set contains the tasks in that community |
| `task_to_community` | dict | task → community index (0-based) |

**Modularity guide:** > 0.3 indicates clear community structure; < 0.3 suggests tasks are well-mixed.

---

## `calculate_transition_entropy`

Calculates Shannon entropy per task over its outgoing transition probabilities — higher entropy means more flexible/uncertain workflow at that step.

```python
result = utilities.analyzer.calculate_transition_entropy(min_probability=0.0)

print(f"Average entropy: {result['avg_entropy']:.3f} bits")
print(f"Max possible entropy: {result['max_entropy']:.3f} bits\n")

for task, entropy in result['sorted_entropies']:
    category = 'Flexible' if entropy > result['avg_entropy'] else 'Deterministic'
    print(f"{task:15s}: {entropy:.3f} bits ({category})")

# High-entropy tasks (decision points)
high_entropy = result['high_entropy_tasks']
print(f"\nDecision points ({len(high_entropy)} tasks):")
for task, entropy in high_entropy:
    print(f"  {task}: {entropy:.3f} bits")
```

**Result keys:**

| Key | Type | Description |
|-----|------|-------------|
| `avg_entropy` | float | Mean entropy across all tasks |
| `max_entropy` | float | log₂(num_tasks) — theoretical maximum |
| `sorted_entropies` | list of `(task, entropy)` | Sorted descending by entropy |
| `high_entropy_tasks` | list of `(task, entropy)` | Tasks above the average |

---

## `analyze_task_persistence`

Measures self-loop probability for each task — how often a user stays on the same task rather than moving to the next.

```python
result = utilities.analyzer.analyze_task_persistence(min_probability=0.0)

print(f"Tasks with persistence: {len(result['tasks_with_persistence'])}")
print(f"Average persistence: {result['avg_persistence']:.3f}\n")

print("Persistent tasks:")
for task, prob in result['tasks_with_persistence']:
    print(f"  {task:15s}: {prob:.3f}")

print(f"\nNon-persistent tasks: {len(result['tasks_without_persistence'])}")
print(f"Sample: {', '.join(result['tasks_without_persistence'][:5])}")

if result['max_persistence']:
    max_task, max_prob = result['max_persistence']
    print(f"\nMost persistent: {max_task} ({max_prob:.3f})")
```

**Result keys:**

| Key | Type | Description |
|-----|------|-------------|
| `tasks_with_persistence` | list of `(task, prob)` | Tasks that have a self-loop, sorted descending |
| `tasks_without_persistence` | list of str | Tasks with no self-loop |
| `avg_persistence` | float | Mean self-loop probability across all tasks |
| `max_persistence` | `(task, prob)` or None | Task with the highest self-loop probability |

**Self-loop guide:** > 0.3 = users iterate significantly; 0.1–0.3 = some repetition; 0.0 = single-pass task.

---

**See also:** [Additional Functions](05-additional-functions.md) | [Utilities 11–15](04-utilities.md#utility-11-centrality-analysis) | [Tips](08-tips.md#network-analysis-tips)
