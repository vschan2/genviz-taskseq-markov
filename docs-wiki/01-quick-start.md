# Quick Start

Get up and running with Task Analysis Utilities in a few minutes.

---

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Expected CSV Format](#expected-csv-format)

---

## Basic Usage

```bash
# Load data and enter interactive mode
python task_analysis_utilities.py --file your_data.csv --interactive

# Run a specific utility (e.g., goal-stratified analysis)
python task_analysis_utilities.py --file your_data.csv --utility 4
```

Interactive mode (`--interactive`) is the recommended entry point when exploring a new dataset — it lets you run any of the 16 utilities without restarting the script.

---

## Expected CSV Format

Your CSV should have these columns (customizable via flags — see [Usage Examples](03-usage-examples.md)):

| Column | Description | Example value |
|--------|-------------|---------------|
| `task_sequence` | Tasks separated by `→` | `Locate→Identify→Lookup→Explore` |
| `biological_goal` | The biological goal | `Species identification` |
| `tool_name` | The tool name | `ToolA` |

**Example CSV:**

```csv
tool_name,biological_goal,task_sequence
ToolA,Species identification,Locate→Identify→Lookup→Explore
ToolB,Genetic diversity,Browse→Identify→Measure→Connect
ToolC,Species identification,Locate→Identify→Explore
```

> **Note:** Tasks are `→`-delimited (not `->` or `,`). They are normalized to lowercase at load time.

---

**Next:** [Installation](02-installation.md) — set up dependencies before running.
