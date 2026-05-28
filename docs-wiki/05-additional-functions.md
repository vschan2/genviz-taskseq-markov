# Additional Functions

Programmatic API for direct use of `TaskSequenceAnalyzer` — beyond the 16 numbered utilities.

For network-specific functions (`calculate_centrality_metrics`, `analyze_workflow_paths`, `detect_communities`, `calculate_transition_entropy`, `analyze_task_persistence`), see [06-network-analysis.md](06-network-analysis.md).

---

## Table of Contents

1. [Setup](#setup)
2. [`get_transition_probability`](#get_transition_probability)
3. [`get_most_likely_next_states`](#get_most_likely_next_states)
4. [`calculate_sequence_probability`](#calculate_sequence_probability)
5. [`analyze_by_goal`](#analyze_by_goal)
6. [`export_pairwise_dataframe`](#export_pairwise_dataframe)
7. [`create_transition_matrix`](#create_transition_matrix)
8. [`generate_summary_statistics`](#generate_summary_statistics)
9. [Direct access: `transition_counts`](#direct-access-transition_counts)
10. [Direct access: `transition_probs`](#direct-access-transition_probs)
11. [Direct access: `sequences`](#direct-access-sequences)

---

## Setup

```python
from task_analysis_utilities import TaskAnalysisUtilities

utilities = TaskAnalysisUtilities()
utilities.load_csv_data('your_data.csv')
```

`load_csv_data()` parses the CSV, splits sequences on `→`, lowercases all task names, and calls `calculate_transition_probabilities()` internally. All methods below require probabilities to be calculated first — loading via `load_csv_data()` handles this automatically.

---

## `get_transition_probability`

Returns the probability of transitioning from one task to another.

```python
prob = utilities.analyzer.get_transition_probability('locate', 'identify')
print(f"P(identify | locate) = {prob:.3f}")
```

---

## `get_most_likely_next_states`

Returns the top-K most likely next tasks from a given state.

```python
next_states = utilities.analyzer.get_most_likely_next_states('identify', top_k=5)
for state, prob in next_states:
    print(f"  → {state}: {prob:.3f}")
```

---

## `calculate_sequence_probability`

Calculates the joint probability of an entire task sequence under the Markov model.

```python
sequence = ['locate', 'identify', 'lookup', 'explore']
prob = utilities.analyzer.calculate_sequence_probability(sequence)
print(f"Probability: {prob:.6f}")
```

The probability is the product of each consecutive transition probability in the sequence (including `START → first_task`).

---

## `analyze_by_goal`

Returns a dict of per-goal `TaskSequenceAnalyzer` instances, each with `calculate_transition_probabilities()` already called.

```python
goal_analyzers = utilities.analyzer.analyze_by_goal()

# Access a specific goal
species_analyzer = goal_analyzers['Species identification']

# Get stats for this goal only
stats = species_analyzer.generate_summary_statistics()
print(f"Species ID has {stats['num_sequences']} sequences")
```

This is what Utilities 4–7 call internally.

---

## `export_pairwise_dataframe`

Returns all transitions as a pandas DataFrame — useful for custom filtering and aggregation.

```python
df = utilities.analyzer.export_pairwise_dataframe()

# Standard pandas operations
print(df['goal'].value_counts())
print(df.groupby('from_state')['to_state'].value_counts())

# Filter to a specific task
identify_transitions = df[df['from_state'] == 'identify']
print(identify_transitions)
```

---

## `create_transition_matrix`

Creates a transition probability matrix (pandas DataFrame) for a specified set of states, or all states if none are given.

```python
# Matrix for specific tasks only
states = ['locate', 'identify', 'lookup', 'explore']
matrix = utilities.analyzer.create_transition_matrix(states)
print(matrix)

# Matrix for all states
all_matrix = utilities.analyzer.create_transition_matrix()
```

---

## `generate_summary_statistics`

Returns a dict of summary statistics for the loaded data.

```python
stats = utilities.analyzer.generate_summary_statistics()

print(f"Total sequences: {stats['num_sequences']}")
print(f"Unique tasks: {stats['num_unique_tasks']}")
print(f"Average length: {stats['avg_sequence_length']}")
print(f"Tasks: {stats['tasks']}")
print(f"Total transitions: {stats['total_transitions']}")
```

---

## Direct Access: `transition_counts`

Raw co-occurrence counts as a `defaultdict(Counter)`.

```python
# How many times did 'locate → identify' occur?
count = utilities.analyzer.transition_counts['locate']['identify']
print(f"locate → identify occurred {count} times")

# All transitions from 'identify'
for to_state, count in utilities.analyzer.transition_counts['identify'].items():
    print(f"identify → {to_state}: {count} times")
```

---

## Direct Access: `transition_probs`

Computed probabilities as a dict of dicts. Available after `calculate_transition_probabilities()` has been called.

```python
for to_state, prob in utilities.analyzer.transition_probs['locate'].items():
    print(f"locate → {to_state}: {prob:.3f}")
```

---

## Direct Access: `sequences`

All loaded sequences with metadata. Each entry is a dict with keys: `sequence` (list, always includes `START`/`END` tokens), `goal`, `tool`, `length`.

```python
# Examine each sequence
for seq_info in utilities.analyzer.sequences:
    print(f"Tool: {seq_info['tool']}")
    print(f"Goal: {seq_info['goal']}")
    print(f"Length: {seq_info['length']}")
    print(f"Sequence: {' → '.join(seq_info['sequence'])}")

# Filter by goal
species_seqs = [s for s in utilities.analyzer.sequences
                if s['goal'] == 'Species identification']
print(f"Found {len(species_seqs)} species identification sequences")
```

> **Note:** `START` and `END` sentinel tokens are always present in `seq_info['sequence']` but are excluded from most analysis outputs.

---

**See also:** [Network Analysis Functions](06-network-analysis.md) | [Available Utilities](04-utilities.md)
