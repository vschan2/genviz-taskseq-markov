# Usage Examples

## Table of Contents

1. [Run in Interactive Mode](#example-1-run-in-interactive-mode)
2. [Custom Column Names](#example-2-custom-column-names)
3. [Different Delimiter](#example-3-different-delimiter)
4. [Run a Specific Utility](#example-4-run-specific-utility)
5. [Programmatic Usage](#example-5-programmatic-usage)

---

## Example 1: Run in Interactive Mode

Load data and enter interactive mode:

```bash
python task_analysis_utilities.py --file your_data.csv --interactive
```

## Example 2: Custom Column Names

If your CSV uses different column names (e.g., from an SLR extraction schema):

```bash
python task_analysis_utilities.py \
  --file biodiversity_data.csv \
  --sequence VTA_Task_Combinations \
  --goal DC_Primary_Goal \
  --tool Tool_Name \
  --interactive
```

| Flag | Default | Description |
|------|---------|-------------|
| `--sequence` | `task_sequence` | Column containing the task sequence |
| `--goal` | `biological_goal` | Column containing the biological goal |
| `--tool` | `tool_name` | Column containing the tool name |

---

## Example 3: Different Delimiter

If your tasks are separated by `|` instead of `→`:

```bash
python task_analysis_utilities.py \
  --file data.csv \
  --delimiter "|" \
  --interactive
```

---

## Example 4: Run Specific Utility

```bash
# Run only goal-stratified analysis (Utility 4)
python task_analysis_utilities.py --file data.csv --utility 4

# Run only visualization (Utility 10)
python task_analysis_utilities.py --file data.csv --utility 10
```

See [04-utilities.md](04-utilities.md) for a full list of utility numbers and what each does.

---

## Example 5: Programmatic Usage

```python
from task_analysis_utilities import TaskAnalysisUtilities

# Initialize
utilities = TaskAnalysisUtilities()

# Load data
utilities.load_csv_data('your_data.csv')

# Run specific analysis
results = utilities.utility_4_goal_stratified_analysis()

# Access goal-specific analyzers
for goal, data in results.items():
    print(f"Goal: {goal}")
    print(f"Sequences: {data['stats']['num_sequences']}")
```

For the full programmatic API (direct access to `TaskSequenceAnalyzer`), see [05-additional-functions.md](05-additional-functions.md) and [06-network-analysis.md](06-network-analysis.md).

---

**Next:** [Available Utilities](04-utilities.md) — parameters and example output for all 16 utilities.
