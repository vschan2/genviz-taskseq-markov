# Available Utilities

All 16 numbered utilities available via `--utility <n>` or interactive mode.

---

## Table of Contents

1. [Utility 1: Summary Statistics](#utility-1-summary-statistics)
2. [Utility 2: Transition Probabilities](#utility-2-transition-probabilities)
3. [Utility 3: Transition Matrix](#utility-3-transition-matrix)
4. [Utility 4: Goal-Stratified Transition Analysis ⭐](#utility-4-goal-stratified-transition-analysis)
5. [Utility 5: Transition Matrices by Goal](#utility-5-transition-matrices-by-goal)
6. [Utility 6: Compare Transitions Across Goals ⭐](#utility-6-compare-transitions-across-goals)
7. [Utility 7: Find Goal-Specific Patterns ⭐](#utility-7-find-goal-specific-patterns)
8. [Utility 8: Sequence Probability Calculator](#utility-8-sequence-probability-calculator)
9. [Utility 9: Export Pairwise Transitions](#utility-9-export-pairwise-transitions)
10. [Utility 10: Visualize Task Flow](#utility-10-visualize-task-flow)
11. [Utility 11: Centrality Analysis](#utility-11-centrality-analysis)
12. [Utility 12: Workflow Path Analysis](#utility-12-workflow-path-analysis)
13. [Utility 13: Community Detection](#utility-13-community-detection)
14. [Utility 14: Transition Entropy Analysis](#utility-14-transition-entropy-analysis)
15. [Utility 15: Task Persistence Analysis](#utility-15-task-persistence-analysis)
16. [Utility 16: Transition Probability Heatmap](#utility-16-transition-probability-heatmap)

---

## Utility 1: Summary Statistics

**What it does:** Provides an overview of your dataset — the right first step before any deeper analysis.

**Output:**
- Total sequences
- Unique tasks
- Total transitions
- Sequence length statistics (average, median, range)
- List of all tasks found

**Example output:**
```
Dataset Overview:
  Total sequences: 34
  Unique tasks: 10
  Total transitions: 156

Sequence Length Statistics:
  Average: 4.5 tasks
  Median: 4.0 tasks
  Range: 2 - 8 tasks

Tasks Found:
  locate, identify, lookup, explore, browse, measure, ...
```

---

## Utility 2: Transition Probabilities

**What it does:** Shows the most likely next states from each task.

**Parameters:**
- `top_k`: Number of top transitions to show (default: 3)

**Output:** For each task, the top-K most likely next tasks with probabilities and counts.

**Example output:**
```
From 'locate':
  → identify: 0.933 (n=28)
  → explore: 0.050 (n=2)
  → lookup: 0.017 (n=1)

From 'identify':
  → lookup: 0.500 (n=15)
  → measure: 0.333 (n=10)
  → explore: 0.167 (n=5)
```

**Interpretation:**
- After `locate`, users go to `identify` 93.3% of the time
- After `identify`, there are three common paths (`lookup`, `measure`, `explore`)

---

## Utility 3: Transition Matrix

**What it does:** Creates a full matrix of transition probabilities between all states.

**Output:**
- CSV file: `transition_matrix.csv`
- Console display of the matrix

**Example output:**
```
              locate  identify  lookup  explore  ...
locate          0.00      0.93    0.02     0.05  ...
identify        0.00      0.00    0.50     0.17  ...
lookup          0.00      0.00    0.00     0.60  ...
```

**Row interpretation:** From `locate`, the probability of going to `identify` is 0.93.

**When to use:** Statistical analysis, or exporting to other tools (R, SPSS, etc.).

---

## Utility 4: Goal-Stratified Transition Analysis ⭐

**What it does:** Separates the Markov analysis by biological goal. Answers the question: *do different goals produce different task workflows?*

**Output:**
- Separate transition analysis printed for each goal
- CSV files for each goal: `goal_[goalname]_transitions.csv`
- Comparison summary: `goal_comparison_summary.csv`

**Example output:**
```
Goal: Species identification
  Sequences: 15
  Unique tasks: 8
  Avg sequence length: 4.3 tasks
  Tasks used: locate, identify, lookup, explore, contextualize

  Top transitions:
    locate       → identify    : 0.950 (n=14)
    identify     → lookup      : 0.700 (n=10)
    lookup       → explore     : 0.600 (n=6)

Goal: Genetic diversity
  Sequences: 12
  Unique tasks: 7
  Avg sequence length: 4.8 tasks
  Tasks used: browse, identify, measure, connect, compare

  Top transitions:
    browse       → identify    : 0.800 (n=10)
    identify     → measure     : 0.750 (n=9)
    measure      → connect     : 0.667 (n=6)
```

**Key insight:** Different goals have different task patterns.

---

## Utility 5: Transition Matrices by Goal

**What it does:** Creates separate transition matrices for each biological goal.

**Output:**
- Multiple CSV files: `goal_[goalname]_matrix.csv`
- Console display for each goal

**When to use:** Statistical comparison between goals, or when you need goal-specific matrices as input to Utility 16 (heatmap).

---

## Utility 6: Compare Transitions Across Goals ⭐

**What it does:** Identifies which transitions vary most between goals.

**Output:**
- CSV file: `goal_transition_comparison.csv`
- Variance, mean, and standard deviation across goals for each transition

**Example output:**
```
Transitions with HIGHEST variation across goals:

transition          Species ID  Genetic Div  Conservation  variance
identify → measure      0.100        0.750         0.200     0.085
browse → measure        0.000        0.800         0.100     0.107
locate → explore        0.600        0.100         0.500     0.063
```

**Interpretation:**
- `identify → measure` is very common for "Genetic diversity" but rare for others
- High variance = goal-specific behavior; Low variance = universal pattern

---

## Utility 7: Find Goal-Specific Patterns ⭐

**What it does:** Finds transitions that appear **only** in specific goals — the signature workflows of each goal.

**Output:**
- List of unique transitions per goal
- Summary of total / unique / shared transition counts

**Example output:**
```
Transitions UNIQUE to specific biological goals:

Species identification
  Found 3 unique transitions:
  locate       → contextualize: 0.500 (n=2)
  explore      → contextualize: 0.750 (n=3)

Genetic diversity
  Found 2 unique transitions:
  measure      → compare      : 0.600 (n=5)
  compare      → connect      : 0.800 (n=4)

Summary:
Species identification:
  Total transitions: 12, Unique: 3, Shared: 9
Genetic diversity:
  Total transitions: 10, Unique: 2, Shared: 8
```

---

## Utility 8: Sequence Probability Calculator

**What it does:** Calculates the probability of a specific task sequence under the overall model and per-goal models. Interactive mode prompts for input.

**Output:**
- Overall sequence probability
- Probability for each goal
- Most likely associated goal

**Example output:**
```
Enter a task sequence (comma-separated):
> locate,identify,lookup,explore

Sequence: locate → identify → lookup → explore
Overall Probability: 0.042000

✓ This is a MODERATELY COMMON sequence

Probability by Biological Goal:
✓ Species identification        : 0.120000
✗ Genetic diversity             : 0.000000
✓ Conservation prioritization   : 0.015000

Most likely goal: Species identification (p=0.120000)
```

**When to use:** Validate hypothetical workflows or predict which goal a new sequence belongs to.

---

## Utility 9: Export Pairwise Transitions

**What it does:** Exports all individual transitions with full metadata to a flat CSV.

**Output:** CSV file: `pairwise_transitions.csv`

**Columns:**

| Column | Description |
|--------|-------------|
| `tool` | Tool name |
| `goal` | Biological goal |
| `from_state` | Starting task |
| `to_state` | Next task |
| `position` | Position in sequence (0, 1, 2, …) |
| `sequence_length` | Total length of the sequence |

**Example:**
```csv
tool,goal,from_state,to_state,position,sequence_length
ToolA,Species ID,START,locate,0,5
ToolA,Species ID,locate,identify,1,5
ToolA,Species ID,identify,lookup,2,5
```

**When to use:** Raw data export for custom analysis, or import into other tools.

---

## Utility 10: Visualize Task Flow

**What it does:** Creates network diagrams of task transitions as PNG files.

**Parameters:**
- `min_probability`: Only show transitions above this threshold
- `by_goal`: Create separate visualizations for each goal

**Output:**
- Overall: `task_flow_diagram.png`
- By goal: `goal_[goalname]_flow.png`

**Diagram features:**

| Element | Meaning |
|---------|---------|
| Green node | START |
| Red node | END |
| Blue nodes | Tasks |
| Arrow thickness | Probability strength |
| Edge labels | Exact probabilities |

**Tip:** If the diagram is empty, lower `min_probability` (try 0.05 instead of 0.1).

---

## Utility 11: Centrality Analysis

**What it does:** Calculates network centrality metrics to identify important or central tasks in workflows.

**Parameters:**
- `min_probability`: Minimum transition probability threshold (default: 0.0)
- `file_path`: Output directory for CSV files
- `by_goal`: Analyze separately for each biological goal (default: False)
- `export_results`: Export results to CSV (default: True)

**Metrics calculated:**

| Metric | Meaning |
|--------|---------|
| Out-degree centrality | How many outgoing edges (next tasks) each task has |
| In-degree centrality | How many incoming edges (previous tasks) each task has |
| Betweenness centrality | How often a task appears on shortest paths between other tasks |
| PageRank | Overall importance score based on network structure |

**Output:**
- CSV file: `centrality_metrics.csv` (overall)
- CSV files: `goal_[name]_centrality.csv` (per goal if `by_goal=True`)
- CSV file: `goal_centrality_comparison.csv` (comparison across goals)

**Example output:**
```
Top 10 Tasks by Betweenness Centrality:

 1. identify           : betweenness=0.450, pagerank=0.185, out_deg=0.600, in_deg=0.700
 2. lookup             : betweenness=0.280, pagerank=0.142, out_deg=0.500, in_deg=0.550
 3. measure            : betweenness=0.210, pagerank=0.125, out_deg=0.400, in_deg=0.450
 4. explore            : betweenness=0.180, pagerank=0.098, out_deg=0.450, in_deg=0.380
 5. locate             : betweenness=0.120, pagerank=0.110, out_deg=0.200, in_deg=0.100
```

**Interpretation:**
- **High betweenness**: Task acts as a bridge/hub (e.g., `identify` connects different workflow stages)
- **High PageRank**: Task is important in the overall workflow structure
- **High out-degree**: Task has many possible next steps (flexible)
- **High in-degree**: Task can be reached from many previous tasks

For programmatic access, see [06-network-analysis.md](06-network-analysis.md#calculate_centrality_metrics).

---

## Utility 12: Workflow Path Analysis

**What it does:** Analyzes actual workflow paths from START to END to reveal dominant workflow patterns.

**Parameters:**
- `min_probability`: Minimum transition probability threshold (default: 0.0)
- `max_path_length`: Maximum path length in edges (default: 9)
- `file_path`: Output directory for CSV files
- `by_goal`: Analyze separately for each biological goal (default: False)
- `export_results`: Export results to CSV (default: True)

**Output:**
- CSV file: `workflow_paths.csv` (overall)
- CSV files: `goal_[name]_paths.csv` (per goal if `by_goal=True`)
- Path frequency distribution and most common path lengths

**Example output:**
```
Path Statistics:
  Total unique paths: 45
  Total path instances: 182
  Most common path length: 4 edges (occurs 78 times)

Path Length Distribution:
  2 edges: 12 paths (6.6%)
  3 edges: 45 paths (24.7%)
  4 edges: 78 paths (42.9%)
  5 edges: 35 paths (19.2%)

Top 10 Most Frequent Paths:
 1. [4 edges, freq=28, 15.4%] locate → identify → lookup → explore
 2. [3 edges, freq=22, 12.1%] browse → identify → measure
 3. [4 edges, freq=18, 9.9%] locate → identify → measure → connect
 4. [5 edges, freq=15, 8.2%] locate → identify → lookup → explore → contextualize
```

**Note:** This utility counts actual observed sequences, not all graph-enumerated paths.

For programmatic access, see [06-network-analysis.md](06-network-analysis.md#analyze_workflow_paths).

---

## Utility 13: Community Detection

**What it does:** Identifies task clusters/communities using modularity optimization.

**Parameters:**
- `min_probability`: Minimum transition probability threshold (default: 0.0)
- `file_path`: Output directory for CSV files
- `by_goal`: Analyze separately for each biological goal (default: False)
- `export_results`: Export results to CSV (default: True)

**Output:**
- CSV file: `task_communities.csv` (overall)
- CSV files: `goal_[name]_communities.csv` (per goal if `by_goal=True`)
- Community assignments and modularity score

**Example output:**
```
Community Statistics:
  Number of communities: 3
  Modularity score: 0.4523
  Community sizes: [4, 5, 3]

Detected Communities:

  Community 1 (4 tasks):
    browse, explore, locate, lookup

  Community 2 (5 tasks):
    connect, contextualize, identify, measure, quantify

  Community 3 (3 tasks):
    communicate, dissect, compare
```

**Interpretation:**
- **Community 1**: Search/discovery tasks (finding data)
- **Community 2**: Analysis/comparative tasks (working with data)
- **Community 3**: Output/reporting tasks (sharing results)
- **High modularity (> 0.3)**: Clear community structure
- **Low modularity (< 0.3)**: Tasks are well-mixed, less modular

> **Note:** Community detection converts the DiGraph to undirected and removes START/END before running greedy modularity. Need at least 10–15 tasks for meaningful results.

For programmatic access, see [06-network-analysis.md](06-network-analysis.md#detect_communities).

---

## Utility 14: Transition Entropy Analysis

**What it does:** Measures workflow uncertainty/flexibility by calculating Shannon entropy per task over its outgoing transition probabilities.

**Parameters:**
- `min_probability`: Minimum transition probability threshold (default: 0.0)
- `file_path`: Output directory for CSV files
- `by_goal`: Analyze separately for each biological goal (default: False)
- `export_results`: Export results to CSV (default: True)

**Entropy interpretation:**
- **High entropy**: Many possible next tasks with similar probabilities — flexible or uncertain workflow
- **Low entropy**: Few dominant next tasks — deterministic or predictable workflow

**Output:**
- CSV file: `transition_entropy.csv` (overall)
- CSV files: `goal_[name]_entropy.csv` (per goal if `by_goal=True`)
- Tasks categorized into high / low entropy

**Example output:**
```
Entropy Statistics:
  Average entropy: 1.245 bits
  Maximum possible entropy: 2.807 bits
  Number of tasks: 12

All Tasks Sorted by Entropy (Highest to Lowest):
  1. identify            1.8543 bits  🔄 Flexible
  2. explore             1.6234 bits  🔄 Flexible
  3. measure             1.4521 bits  🔄 Flexible
  4. lookup              0.9123 bits  ➡️  Deterministic
  5. contextualize       0.7234 bits  ➡️  Deterministic
  6. communicate         0.3421 bits  ➡️  Deterministic
```

For programmatic access, see [06-network-analysis.md](06-network-analysis.md#calculate_transition_entropy).

---

## Utility 15: Task Persistence Analysis

**What it does:** Analyzes self-loop strength to identify tasks where users spend more time or repeat actions.

**Parameters:**
- `min_probability`: Minimum transition probability threshold (default: 0.0)
- `file_path`: Output directory for CSV files
- `by_goal`: Analyze separately for each biological goal (default: False)
- `export_results`: Export results to CSV (default: True)

**Self-loop interpretation:**
- **High self-loop probability**: "Sticky" task requiring repeated actions
- **No self-loop**: Quick transition task

**Output:**
- CSV file: `task_persistence.csv` (overall)
- CSV files: `goal_[name]_persistence.csv` (per goal if `by_goal=True`)
- Tasks categorized into persistent vs. non-persistent

**Example output:**
```
Persistence Statistics:
  Total tasks analyzed: 12
  Tasks with persistence (self-loops): 4
  Tasks without persistence: 8
  Average persistence (self-loop prob): 0.2453
  Highest persistence: measure (0.4500)

Tasks with Persistence (Self-Loops):
  measure: 0.4500
  quantify: 0.3200
  dissect: 0.2100
  connect: 0.1200

Sample Tasks without Persistence (5 of 8):
  locate: 0.0000
  lookup: 0.0000
  browse: 0.0000
  explore: 0.0000
  communicate: 0.0000
```

**Interpretation:**
- **High (> 0.3)**: Users spend significant time or iterate (e.g., `measure` — refining measurements)
- **Medium (0.1–0.3)**: Some repetition
- **None (0.0)**: Quick transition, single-pass task (e.g., `locate` — once found, move on)

For programmatic access, see [06-network-analysis.md](06-network-analysis.md#analyze_task_persistence).

---

## Utility 16: Transition Probability Heatmap

**What it does:** Generates a publication-quality heatmap from a goal-specific transition matrix CSV. Reads a `goal_[name]_matrix.csv` produced by [Utility 5](#utility-5-transition-matrices-by-goal), applies a fixed task display order, annotates cells with two-decimal probabilities, and saves a 300 dpi PNG.

**Prerequisites:** Requires `seaborn`:
```bash
pip install seaborn
```

**Parameters:**
- `matrix_file`: Path to a goal matrix CSV (e.g., `output_data/goal_Species_Identification_&_Marker_Development_matrix.csv`)
- `file_path`: Output directory (default: `./`)
- `output_file`: PNG filename (default: `transition_heatmap-<matrix_stem>.png`)

**Output:**
- PNG file: `transition_heatmap-[matrix_stem].png` — 300 dpi, tight layout
- GnBu colormap, probabilities from 0 to 1; cells annotated with two-decimal values (blank for zero)
- Fixed task display order: `START → browse → communicate → connect → contextualize → dissect → explore → identify → locate → lookup → measure/quantify/summarize → END` (tasks absent from the matrix are omitted automatically)
- Font: Calibri (auto-falls back to DejaVu Sans if Calibri is unavailable)

**Example output:**
```
✓ Heatmap saved to: output_data/transition_heatmap-goal_Species_Identification_&_Marker_Development_matrix.png
```

---

**See also:** [Output Files Reference](07-output-files.md) | [Tips & Best Practices](08-tips.md) | [Troubleshooting](09-troubleshooting.md)
