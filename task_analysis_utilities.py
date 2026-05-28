"""
Task Sequence Analysis Utilities - Interactive CLI Tool
Comprehensive analysis tools for task sequences with biological goal stratification

Usage:
    python task_analysis_utilities.py --file your_data.csv --interactive
    python task_analysis_utilities.py --file your_data.csv --utility 4
"""

import pandas as pd
import numpy as np
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import networkx as nx

# Import the main analyzer
from task_sequence_markov_analysis import TaskSequenceAnalyzer


class TaskAnalysisUtilities:
    """Enhanced utilities for task sequence analysis"""

    def __init__(self, analyzer: TaskSequenceAnalyzer = None):
        self.analyzer = analyzer if analyzer else TaskSequenceAnalyzer()
        self.goal_analyzers = None

    def load_csv_data(self,
                     csv_path: str,
                     sequence_col: str = 'task_sequence',
                     goal_col: str = 'biological_goal',
                     tool_col: str = 'tool_name',
                     delimiter: str = '→') -> Dict:
        """
        Load CSV data into analyzer

        Args:
            csv_path: Path to CSV file
            sequence_col: Column name for task sequences
            goal_col: Column name for biological goals
            tool_col: Column name for tool names
            delimiter: Character separating tasks in sequence

        Returns:
            Dictionary with loading statistics
        """
        print(f"\n{'='*60}")
        print(f"Loading data from: {csv_path}")
        print(f"{'='*60}\n")

        df = pd.read_csv(csv_path)
        print(f"✓ Found {len(df)} rows in CSV")
        print(f"✓ Columns: {list(df.columns)}\n")

        # Validate columns
        missing_cols = []
        if sequence_col not in df.columns:
            missing_cols.append(sequence_col)
        if goal_col not in df.columns:
            missing_cols.append(goal_col)
        if tool_col not in df.columns:
            missing_cols.append(tool_col)

        if missing_cols:
            raise ValueError(f"Missing columns: {missing_cols}\nAvailable columns: {list(df.columns)}")

        loaded = 0
        skipped = 0

        for idx, row in df.iterrows():
            try:
                # Check if sequence exists
                if pd.isna(row[sequence_col]):
                    skipped += 1
                    continue

                # Parse sequence
                sequence_str = str(row[sequence_col])
                if sequence_str.strip() == '' or sequence_str == 'nan':
                    skipped += 1
                    continue

                tasks = sequence_str.split(delimiter)
                tasks = [t.strip().lower() for t in tasks if t.strip()]

                if not tasks:
                    skipped += 1
                    continue

                # Add to analyzer
                self.analyzer.add_sequence(
                    sequence=tasks,
                    goal=row[goal_col] if pd.notna(row[goal_col]) else 'Unknown',
                    tool=row[tool_col] if pd.notna(row[tool_col]) else 'Unknown'
                )
                loaded += 1

            except Exception as e:
                print(f"Warning: Error processing row {idx}: {e}")
                skipped += 1

        # Calculate probabilities
        self.analyzer.calculate_transition_probabilities()

        print(f"\n=== Loading Summary ===")
        print(f"✓ Successfully loaded: {loaded} sequences")
        if skipped > 0:
            print(f"⊘ Skipped: {skipped} rows (empty or invalid)\n")

        return {
            'total_rows': len(df),
            'loaded': loaded,
            'skipped': skipped
        }

    def utility_1_summary_statistics(self):
        """Utility 1: Display comprehensive summary statistics"""
        print(f"\n{'='*60}")
        print("UTILITY 1: SUMMARY STATISTICS")
        print(f"{'='*60}\n")

        stats = self.analyzer.generate_summary_statistics()

        print("Dataset Overview:")
        print(f"  Total sequences: {stats['num_sequences']}")
        print(f"  Unique tasks: {stats['num_unique_tasks']}")
        print(f"  Total transitions: {stats['total_transitions']}")
        print(f"  Unique transition pairs: {stats['num_unique_transitions']}")

        print(f"\nSequence Length Statistics:")
        print(f"  Average: {stats['avg_sequence_length']:.2f} tasks")
        print(f"  Median: {stats['median_sequence_length']:.1f} tasks")
        print(f"  Range: {stats['min_sequence_length']} - {stats['max_sequence_length']} tasks")

        print(f"\nTasks Found:")
        print(f"  {', '.join(stats['tasks'])}")

        return stats

    def utility_2_transition_probabilities(self, top_k: int = 3):
        """Utility 2: Display most likely transitions from each state"""
        print(f"\n{'='*60}")
        print("UTILITY 2: TRANSITION PROBABILITIES")
        print(f"{'='*60}\n")

        print(f"Showing top {top_k} most likely next states from each task:\n")

        results = {}
        for state in sorted(self.analyzer.transition_probs.keys()):
            if state not in ['START', 'END']:
                next_states = self.analyzer.get_most_likely_next_states(state, top_k=top_k)
                if next_states:
                    print(f"From '{state}':")
                    results[state] = []
                    for next_state, prob in next_states:
                        count = self.analyzer.transition_counts[state][next_state]
                        print(f"  → {next_state}: {prob:.3f} (n={count})")
                        results[state].append((next_state, prob, count))
                    print()

        return results

    def utility_3_transition_matrix(self, file_path: str = './', filename: str = 'transition_matrix.csv', export_csv: bool = True):
        """Utility 3: Generate and display transition probability matrix"""
        print(f"\n{'='*60}")
        print("UTILITY 3: TRANSITION MATRIX")
        print(f"{'='*60}\n")

        # Create output directory if it doesn't exist
        output_dir = self._create_output_dir(file_path)

        stats = self.analyzer.generate_summary_statistics_with_startend()
        # states = sorted([s for s in stats['tasks'] if s not in ['START', 'END']])
        states = sorted([s for s in stats['tasks']])

        matrix = self.analyzer.create_transition_matrix(states)

        print("Transition Probability Matrix:")
        print("(Row = From State, Column = To State)\n")
        print(matrix.to_string())

        if export_csv:
            output_file = output_dir / filename
            matrix.to_csv(output_file)
            print(f"\n✓ Exported to: {output_file}")

        return matrix

    def utility_4_goal_stratified_analysis(self, file_path: str = './', export_results: bool = True):
        """
        Utility 4: Analyze transitions separately for each biological goal

        Args:
            file_path: Directory path to save output files (default: current directory)
            export_results: Whether to export results to CSV files
        """
        print(f"\n{'='*60}")
        print("UTILITY 4: GOAL-STRATIFIED ANALYSIS")
        print(f"{'='*60}\n")

        # Create output directory if it doesn't exist
        output_dir = self._create_output_dir(file_path)

        if self.goal_analyzers is None:
            print("Running goal-stratified analysis first...")
            self.goal_analyzers = self.analyzer.analyze_by_goal()

        print(f"Found {len(self.goal_analyzers)} unique biological goals\n")

        results = {}
        for goal, goal_analyzer in self.goal_analyzers.items():
            print(f"\n{'─'*60}")
            print(f"Goal: {goal}")
            print(f"{'─'*60}")

            stats = goal_analyzer.generate_summary_statistics()
            print(f"  Sequences: {stats['num_sequences']}")
            print(f"  Unique tasks: {stats['num_unique_tasks']}")
            print(f"  Avg sequence length: {stats['avg_sequence_length']:.2f} tasks")
            print(f"  Tasks used: {', '.join(stats['tasks'])}")

            # Find top transitions for this goal
            print(f"\n  Top transitions:")
            all_transitions = []
            for from_state, to_states in goal_analyzer.transition_counts.items():
                for to_state, count in to_states.items():
                    if from_state != 'START' and to_state != 'END':
                        prob = goal_analyzer.get_transition_probability(from_state, to_state)
                        all_transitions.append((from_state, to_state, prob, count))

            # Sort by count and show top 5
            all_transitions.sort(key=lambda x: x[3], reverse=True)
            for from_s, to_s, prob, cnt in all_transitions[:5]:
                print(f"    {from_s:12s} → {to_s:12s}: {prob:.3f} (n={cnt})")

            results[goal] = {
                'analyzer': goal_analyzer,
                'stats': stats,
                'top_transitions': all_transitions[:10]
            }

        if export_results:
            self._export_goal_stratified_results(results, output_dir)

        return results
    
    def _create_output_dir(self, file_path: Path = Path('./')):
        """
        Create output directory if it doesn't exist

        Args:
            output_dir: Directory path to save output files
        """
        # Create output directory if it doesn't exist
        output_dir = Path(file_path)
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created output directory: {output_dir.absolute()}\n")
        elif file_path != './':
            print(f"✓ Using output directory: {output_dir.absolute()}\n")

        return output_dir


    def _export_goal_stratified_results(self, results: Dict, output_dir: Path = Path('./')):
        """
        Export goal-stratified results to CSV files

        Args:
            results: Dictionary of results from goal-stratified analysis
            output_dir: Directory path to save output files
        """
        print(f"\n{'='*60}")
        print("Exporting goal-stratified results...")
        print(f"{'='*60}\n")

        # Export transition probabilities for each goal
        for goal, data in results.items():
            safe_filename = goal.replace(' ', '_').replace('/', '_').replace('\\', '_')

            # Export pairwise transitions for this goal
            df_pairs = data['analyzer'].export_pairwise_dataframe()
            pairs_file = output_dir / f'goal_{safe_filename}_transitions.csv'
            df_pairs.to_csv(pairs_file, index=False)
            print(f"✓ {goal}: {pairs_file}")

        # Create summary comparison across goals
        summary_rows = []
        for goal, data in results.items():
            stats = data['stats']
            summary_rows.append({
                'biological_goal': goal,
                'num_sequences': stats['num_sequences'],
                'num_unique_tasks': stats['num_unique_tasks'],
                'avg_sequence_length': stats['avg_sequence_length'],
                'median_sequence_length': stats['median_sequence_length'],
                'min_sequence_length': stats['min_sequence_length'],
                'max_sequence_length': stats['max_sequence_length'],
                'tasks': ', '.join(stats['tasks'])
            })

        df_summary = pd.DataFrame(summary_rows)
        summary_file = output_dir / 'goal_comparison_summary.csv'
        df_summary.to_csv(summary_file, index=False)
        print(f"✓ Goal comparison summary: {summary_file}\n")

    def utility_5_transition_matrix_by_goal(self, file_path: str = './'):
        """Utility 5: Generate transition probability matrices for each biological goal"""
        print(f"\n{'='*60}")
        print("UTILITY 5: TRANSITION MATRICES BY GOAL")
        print(f"{'='*60}\n")

        # Create output directory if it doesn't exist
        output_dir = self._create_output_dir(file_path)

        if self.goal_analyzers is None:
            print("Running goal-stratified analysis first...")
            self.goal_analyzers = self.analyzer.analyze_by_goal()

        matrices = {}
        for goal, goal_analyzer in self.goal_analyzers.items():
            print(f"\n--- Goal: {goal} ---")

            stats = goal_analyzer.generate_summary_statistics_with_startend()
            # states = sorted([s for s in stats['tasks'] if s not in ['START', 'END']])
            states = sorted([s for s in stats['tasks']])

            if not states:
                print("  No tasks found (skipping)")
                continue

            matrix = goal_analyzer.create_transition_matrix(states)
            matrices[goal] = matrix

            print(matrix.to_string())

            # Export
            safe_filename = goal.replace(' ', '_').replace('/', '_').replace('\\', '_')
            output_file = output_dir / f'goal_{safe_filename}_matrix.csv'
            matrix.to_csv(output_file)
            print(f"\n✓ Exported to: {output_file}")

        return matrices

    def utility_6_compare_goals_transitions(self, file_path: str = './'):
        """Utility 6: Compare transition patterns across biological goals"""
        print(f"\n{'='*60}")
        print("UTILITY 6: COMPARE TRANSITIONS ACROSS GOALS")
        print(f"{'='*60}\n")

        # Create output directory if it doesn't exist
        output_dir = self._create_output_dir(file_path)

        if self.goal_analyzers is None:
            print("Running goal-stratified analysis first...")
            self.goal_analyzers = self.analyzer.analyze_by_goal()

        # Collect all transitions across goals
        all_transitions = defaultdict(dict)

        for goal, analyzer in self.goal_analyzers.items():
            for from_state, to_states in analyzer.transition_probs.items():
                for to_state, prob in to_states.items():
                    #if from_state != 'START' and to_state != 'END':
                    transition = f"{from_state} → {to_state}"
                    all_transitions[transition][goal] = prob

        # Create comparison dataframe
        comparison_data = []
        for transition, goal_probs in all_transitions.items():
            row = {'transition': transition}
            row.update(goal_probs)

            # Calculate statistics across goals
            probs = list(goal_probs.values())
            row['mean_prob'] = np.mean(probs)
            row['std_prob'] = np.std(probs)
            row['variance'] = np.var(probs)
            row['num_goals'] = len(probs)
            row['max_prob'] = np.max(probs)
            row['min_prob'] = np.min(probs)

            comparison_data.append(row)

        df_comparison = pd.DataFrame(comparison_data)
        df_comparison = df_comparison.sort_values('variance', ascending=False)

        print("Transitions with HIGHEST variation across goals:")
        print("(High variance = different goals use this transition very differently)\n")
        print(df_comparison.head(15).to_string(index=False))

        # Export
        output_file = output_dir / 'goal_transition_comparison.csv'
        df_comparison.to_csv(output_file, index=False)
        print(f"\n✓ Full comparison exported to: {output_file}")

        return df_comparison

    def utility_7_find_unique_goal_patterns(self):
        """Utility 7: Find transitions unique to specific biological goals"""
        print(f"\n{'='*60}")
        print("UTILITY 7: GOAL-SPECIFIC TRANSITION PATTERNS")
        print(f"{'='*60}\n")

        if self.goal_analyzers is None:
            self.goal_analyzers = self.analyzer.analyze_by_goal()

        # Find transitions for each goal
        goal_transitions = {}
        for goal, analyzer in self.goal_analyzers.items():
            transitions = set()
            for from_state, to_states in analyzer.transition_counts.items():
                for to_state in to_states.keys():
                    if from_state != 'START' and to_state != 'END':
                        transitions.add((from_state, to_state))
            goal_transitions[goal] = transitions

        # Find unique transitions for each goal
        unique_patterns = {}
        shared_patterns = {}

        for goal, transitions in goal_transitions.items():
            other_goals_transitions = set()
            for other_goal, other_trans in goal_transitions.items():
                if other_goal != goal:
                    other_goals_transitions.update(other_trans)

            unique = transitions - other_goals_transitions
            shared = transitions & other_goals_transitions

            if unique:
                unique_patterns[goal] = unique
            shared_patterns[goal] = len(shared)

        print("Transitions UNIQUE to specific biological goals:\n")
        has_unique = False
        for goal, unique_trans in unique_patterns.items():
            has_unique = True
            print(f"{'─'*60}")
            print(f"{goal}")
            print(f"{'─'*60}")
            print(f"Found {len(unique_trans)} unique transitions:")
            for from_state, to_state in sorted(unique_trans):
                count = self.goal_analyzers[goal].transition_counts[from_state][to_state]
                prob = self.goal_analyzers[goal].get_transition_probability(from_state, to_state)
                print(f"  {from_state:12s} → {to_state:12s}: {prob:.3f} (n={count})")
            print()

        if not has_unique:
            print("No unique transitions found. All goals share their transitions with at least one other goal.\n")

        print("\nSummary:")
        for goal in goal_transitions.keys():
            total = len(goal_transitions[goal])
            unique = len(unique_patterns.get(goal, []))
            shared = shared_patterns[goal]
            print(f"{goal}:")
            print(f"  Total transitions: {total}, Unique: {unique}, Shared: {shared}")

        return unique_patterns

    def utility_8_sequence_probability_calculator(self, sequence: List[str] = None):
        """Utility 8: Calculate probability of a specific task sequence"""
        print(f"\n{'='*60}")
        print("UTILITY 8: SEQUENCE PROBABILITY CALCULATOR")
        print(f"{'='*60}\n")

        if sequence is None:
            print("Enter a task sequence (comma-separated):")
            print("Example: locate,identify,lookup,explore")
            user_input = input("> ")
            sequence = [s.strip().lower() for s in user_input.split(',')]

        # Calculate overall probability
        prob = self.analyzer.calculate_sequence_probability(sequence)

        print(f"\nSequence: {' → '.join(sequence)}")
        print(f"Overall Probability: {prob:.6f}")

        if prob == 0:
            print("\n⚠ This sequence has NEVER been observed in the data")
        elif prob < 0.001:
            print("\n⚠ This is a VERY RARE sequence")
        elif prob < 0.01:
            print("\n✓ This is an UNCOMMON sequence")
        elif prob < 0.1:
            print("\n✓ This is a MODERATELY COMMON sequence")
        else:
            print("\n✓ This is a VERY COMMON sequence")

        # Calculate probability by goal
        if self.goal_analyzers is None:
            self.goal_analyzers = self.analyzer.analyze_by_goal()

        print(f"\nProbability by Biological Goal:")
        print(f"{'─'*60}")
        goal_probs = []
        for goal, analyzer in self.goal_analyzers.items():
            goal_prob = analyzer.calculate_sequence_probability(sequence)
            goal_probs.append((goal, goal_prob))
            status = "✓" if goal_prob > 0 else "✗"
            print(f"{status} {goal:40s}: {goal_prob:.6f}")

        # Find which goal this sequence is most associated with
        goal_probs.sort(key=lambda x: x[1], reverse=True)
        if goal_probs[0][1] > 0:
            print(f"\nMost likely goal: {goal_probs[0][0]} (p={goal_probs[0][1]:.6f})")

        return prob

    def utility_9_export_pairwise_transitions(self, file_path: str = './', filename: str = 'pairwise_transitions.csv'):
        """Utility 9: Export all transitions as pairwise dataframe"""
        print(f"\n{'='*60}")
        print("UTILITY 9: EXPORT PAIRWISE TRANSITIONS")
        print(f"{'='*60}\n")

        # Create output directory if it doesn't exist
        output_dir = self._create_output_dir(file_path)
        output_file = output_dir / filename
        
        df = self.analyzer.export_pairwise_dataframe()
        df.to_csv(output_file, index=False)

        print(f"Exported {len(df)} transition pairs to: {filename}")
        print(f"\nDataframe columns:")
        for col in df.columns:
            print(f"  - {col}")

        print(f"\nFirst few rows:")
        print(df.head(10).to_string())

        return df

    def utility_10_visualize_flow(self,
                                  min_probability: float = 0.01,
                                  file_path: str = './',
                                  output_file: str = 'task_flow_diagram.png',
                                  by_goal: bool = False):
        """Utility 10: Create visualization of task flow"""
        print(f"\n{'='*60}")
        print("UTILITY 10: VISUALIZE TASK FLOW")
        print(f"{'='*60}\n")

        # Create output directory if it doesn't exist
        output_dir = self._create_output_dir(file_path)

        if by_goal:
            if self.goal_analyzers is None:
                self.goal_analyzers = self.analyzer.analyze_by_goal()

            print(f"Generating flow diagrams for each goal...")
            print(f"Min probability threshold: {min_probability}\n")

            for goal, analyzer in self.goal_analyzers.items():
                safe_filename = goal.replace(' ', '_').replace('/', '_').replace('\\', '_')
                goal_output_file = output_dir / f'goal_{safe_filename}_flow.png'

                print(f"✓ {goal}: {goal_output_file}")

                analyzer.visualize_flow(
                    min_probability=min_probability,
                    output_file=goal_output_file
                )

            print(f"\n✓ All visualizations saved!")
        else:
            final_output_file = output_dir / output_file

            print(f"Generating overall flow diagram...")
            print(f"  Min probability threshold: {min_probability}")
            print(f"  Output file: {final_output_file}")

            self.analyzer.visualize_flow(
                min_probability=min_probability,
                output_file=final_output_file
            )

            print(f"\n✓ Visualization saved to: {final_output_file}")

    def utility_11_centrality_analysis(self,
                                       min_probability: float = 0.0,
                                       file_path: str = './',
                                       by_goal: bool = False,
                                       export_results: bool = True):
        """
        Utility 11: Calculate node centrality metrics

        Calculates:
        - out_degree_centrality: How many outgoing edges each task has
        - in_degree_centrality: How many incoming edges each task has
        - betweenness_centrality: How often a task is on shortest paths
        - pagerank: Importance score based on network structure

        Args:
            min_probability: Only include transitions with probability >= this threshold
            file_path: Directory path to save output files
            by_goal: Whether to calculate per biological goal
            export_results: Whether to export results to CSV files
        """
        print(f"\n{'='*60}")
        print("UTILITY 11: CENTRALITY ANALYSIS")
        print(f"{'='*60}\n")

        # Create output directory if it doesn't exist
        output_dir = self._create_output_dir(file_path)

        if by_goal:
            if self.goal_analyzers is None:
                print("Running goal-stratified analysis first...")
                self.goal_analyzers = self.analyzer.analyze_by_goal()

            print(f"Analyzing centrality for each biological goal...")
            print(f"Minimum probability threshold: {min_probability}\n")

            all_goal_results = {}
            for goal, goal_analyzer in self.goal_analyzers.items():
                print(f"\n{'─'*60}")
                print(f"Goal: {goal}")
                print(f"{'─'*60}")

                # Calculate centrality using core method
                result = goal_analyzer.calculate_centrality_metrics(min_probability=min_probability)

                if not result['centrality_data']:
                    print("  ⚠ No transitions above threshold - skipping")
                    continue

                centrality_data = result['centrality_data']
                graph = result['graph']

                # Display graph statistics
                print(f"\n  Graph statistics:")
                print(f"    Nodes: {len(graph.nodes())}")
                print(f"    Edges: {len(graph.edges())}")

                # Display top 10
                print(f"\n  Top 10 Tasks by Betweenness Centrality:")
                for i, data in enumerate(centrality_data[:10], 1):
                    print(f"  {i:2d}. {data['task']:20s}: betweenness={data['betweenness_centrality']:.3f}, "
                          f"pagerank={data['pagerank']:.3f}, out_deg={data['out_degree_centrality']:.3f}, "
                          f"in_deg={data['in_degree_centrality']:.3f}")

                all_goal_results[goal] = centrality_data

                # Export for this goal
                if export_results:
                    df = pd.DataFrame(centrality_data)
                    safe_filename = goal.replace(' ', '_').replace('/', '_').replace('\\', '_')
                    output_file = output_dir / f'goal_{safe_filename}_centrality.csv'
                    df.to_csv(output_file, index=False)
                    print(f"\n  ✓ Exported to: {output_file}")

            # Create comparison summary across goals
            if export_results and all_goal_results:
                print(f"\n{'─'*60}")
                print("Creating goal comparison summary...")

                # Collect all unique tasks across goals
                all_tasks = set()
                for data_list in all_goal_results.values():
                    for data in data_list:
                        all_tasks.add(data['task'])

                # Create comparison dataframe
                comparison_rows = []
                for task in sorted(all_tasks):
                    row = {'task': task}
                    for goal, data_list in all_goal_results.items():
                        # Find this task's data in this goal
                        task_data = next((d for d in data_list if d['task'] == task), None)
                        if task_data:
                            safe_goal = goal.replace(' ', '_').replace('/', '_')
                            row[f'{safe_goal}_betweenness'] = task_data['betweenness_centrality']
                            row[f'{safe_goal}_pagerank'] = task_data['pagerank']
                            row[f'{safe_goal}_out_degree'] = task_data['out_degree_centrality']
                            row[f'{safe_goal}_in_degree'] = task_data['in_degree_centrality']
                        else:
                            safe_goal = goal.replace(' ', '_').replace('/', '_')
                            row[f'{safe_goal}_betweenness'] = 0.0
                            row[f'{safe_goal}_pagerank'] = 0.0
                            row[f'{safe_goal}_out_degree'] = 0.0
                            row[f'{safe_goal}_in_degree'] = 0.0

                    comparison_rows.append(row)

                df_comparison = pd.DataFrame(comparison_rows)
                comparison_file = output_dir / 'goal_centrality_comparison.csv'
                df_comparison.to_csv(comparison_file, index=False)
                print(f"✓ Goal comparison saved to: {comparison_file}\n")

            return all_goal_results

        else:
            # Overall analysis
            print(f"Analyzing overall centrality metrics...")
            print(f"Minimum probability threshold: {min_probability}\n")

            # Calculate centrality using core method
            result = self.analyzer.calculate_centrality_metrics(min_probability=min_probability)

            if not result['centrality_data']:
                print("⚠ No transitions above threshold - cannot calculate centrality")
                return {}

            centrality_data = result['centrality_data']
            graph = result['graph']

            # Display graph statistics
            print(f"Graph statistics:")
            print(f"  Nodes: {len(graph.nodes())}")
            print(f"  Edges: {len(graph.edges())}\n")

            # Display results
            print(f"Top 10 Tasks by Betweenness Centrality:")
            for i, data in enumerate(centrality_data[:10], 1):
                print(f"{i:2d}. {data['task']:20s}: betweenness={data['betweenness_centrality']:.3f}, "
                      f"pagerank={data['pagerank']:.3f}, out_deg={data['out_degree_centrality']:.3f}, "
                      f"in_deg={data['in_degree_centrality']:.3f}")

            # Export to CSV
            if export_results:
                df = pd.DataFrame(centrality_data)
                output_file = output_dir / 'centrality_metrics.csv'
                df.to_csv(output_file, index=False)
                print(f"\n✓ Exported to: {output_file}")

            return result

    def utility_12_workflow_path_analysis(self,
                                          min_probability: float = 0.0,
                                          max_path_length: int = 9,
                                          file_path: str = './',
                                          by_goal: bool = False,
                                          export_results: bool = True):
        """
        Utility 12: Analyze workflow paths from START to END

        Reveals dominant workflows and their frequencies by analyzing
        all complete paths through the task sequence graph.

        Args:
            min_probability: Only include transitions with probability >= this threshold
            max_path_length: Maximum path length (number of edges, default 8)
            file_path: Directory path to save output files
            by_goal: Whether to analyze per biological goal
            export_results: Whether to export results to CSV files
        """
        print(f"\n{'='*60}")
        print("UTILITY 12: WORKFLOW PATH ANALYSIS")
        print(f"{'='*60}\n")

        # Create output directory if it doesn't exist
        output_dir = self._create_output_dir(file_path)

        if by_goal:
            if self.goal_analyzers is None:
                print("Running goal-stratified analysis first...")
                self.goal_analyzers = self.analyzer.analyze_by_goal()

            print(f"Analyzing workflow paths for each biological goal...")
            print(f"Minimum probability threshold: {min_probability}")
            print(f"Maximum path length: {max_path_length} edges\n")

            all_goal_results = {}
            for goal, goal_analyzer in self.goal_analyzers.items():
                print(f"\n{'─'*60}")
                print(f"Goal: {goal}")
                print(f"{'─'*60}")

                # Analyze paths using core method
                result = goal_analyzer.analyze_workflow_paths(
                    min_probability=min_probability,
                    max_path_length=max_path_length
                )

                if result['total_unique_paths'] == 0:
                    print("  ⚠ No paths found from START to END")
                    continue

                # Display statistics
                print(f"\n  Path Statistics:")
                print(f"    Total unique paths: {result['total_unique_paths']}")
                print(f"    Total path instances: {result['total_path_instances']}")
                print(f"    Filtered out: {result['filtered_count']} sequences")
                if result['most_common_length']:
                    print(f"    Most common path length: {result['most_common_length'][0]} edges "
                          f"(occurs {result['most_common_length'][1]} times)")

                # Display path length distribution
                print(f"\n  Path Length Distribution:")
                for length in sorted(result['path_length_distribution'].keys()):
                    count = result['path_length_distribution'][length]
                    print(f"    {length} edges: {count} paths")

                # Display top 10 most frequent paths
                print(f"\n  Top 10 Most Frequent Paths:")
                for i, (path, freq) in enumerate(result['sorted_paths'][:10], 1):
                    # Convert path to readable format (exclude START/END for display)
                    path_str = ' → '.join(path[1:-1])  # Exclude START and END
                    path_length = len(path) - 1  # Number of edges
                    print(f"  {i:2d}. [{path_length} edges, freq={freq}] {path_str}")

                all_goal_results[goal] = result

                # Export for this goal
                if export_results:
                    # Create DataFrame with all paths and their frequencies
                    path_data = []
                    for path, freq in result['sorted_paths']:
                        path_data.append({
                            'path': ' → '.join(path),
                            'path_without_start_end': ' → '.join(path[1:-1]),
                            'frequency': freq,
                            'path_length_edges': len(path) - 1,
                            'path_length_nodes': len(path)
                        })

                    df = pd.DataFrame(path_data)
                    safe_filename = goal.replace(' ', '_').replace('/', '_').replace('\\', '_')
                    output_file = output_dir / f'goal_{safe_filename}_paths.csv'
                    df.to_csv(output_file, index=False)
                    print(f"\n  ✓ Exported to: {output_file}")

            return all_goal_results

        else:
            # Overall analysis
            print(f"Analyzing overall workflow paths...")
            print(f"Minimum probability threshold: {min_probability}")
            print(f"Maximum path length: {max_path_length} edges\n")

            # Analyze paths using core method
            result = self.analyzer.analyze_workflow_paths(
                min_probability=min_probability,
                max_path_length=max_path_length
            )

            if result['total_unique_paths'] == 0:
                print("⚠ No paths found from START to END")
                print("  This could mean:")
                print("  - No complete sequences in the data")
                print("  - Minimum probability threshold is too high")
                print("  - Graph is disconnected")
                return {}

            # Display statistics
            print(f"Path Statistics:")
            print(f"  Total unique paths: {result['total_unique_paths']}")
            print(f"  Total path instances: {result['total_path_instances']}")
            print(f"  Filtered out: {result['filtered_count']} sequences")
            if result['most_common_length']:
                print(f"  Most common path length: {result['most_common_length'][0]} edges "
                      f"(occurs {result['most_common_length'][1]} times)")

            # Display path length distribution
            print(f"\nPath Length Distribution:")
            for length in sorted(result['path_length_distribution'].keys()):
                count = result['path_length_distribution'][length]
                pct = (count / result['total_path_instances']) * 100
                print(f"  {length} edges: {count} paths ({pct:.1f}%)")

            # Display top 20 most frequent paths
            print(f"\nTop 20 Most Frequent Paths:")
            for i, (path, freq) in enumerate(result['sorted_paths'][:20], 1):
                # Convert path to readable format (exclude START/END for display)
                path_str = ' → '.join(path[1:-1])  # Exclude START and END
                path_length = len(path) - 1  # Number of edges
                pct = (freq / result['total_path_instances']) * 100
                print(f"{i:2d}. [{path_length} edges, freq={freq}, {pct:.1f}%] {path_str}")

            # Export to CSV
            if export_results:
                # Create DataFrame with all paths and their frequencies
                path_data = []
                for path, freq in result['sorted_paths']:
                    path_data.append({
                        'path': ' → '.join(path),
                        'path_without_start_end': ' → '.join(path[1:-1]),
                        'frequency': freq,
                        'percentage': (freq / result['total_path_instances']) * 100,
                        'path_length_edges': len(path) - 1,
                        'path_length_nodes': len(path)
                    })

                df = pd.DataFrame(path_data)
                output_file = output_dir / 'workflow_paths.csv'
                df.to_csv(output_file, index=False)
                print(f"\n✓ Exported to: {output_file}")

            return result

    def utility_13_community_detection(self, min_probability: float = 0.0,
                                       file_path: str = './',
                                       by_goal: bool = False,
                                       export_results: bool = True):
        """
        Utility 13: Detect task communities using modularity optimization

        This identifies groups of tasks that are densely connected (task clusters),
        revealing modular patterns in workflows.

        Args:
            min_probability: Minimum transition probability threshold
            file_path: Output directory for CSV export
            by_goal: If True, analyze separately for each biological goal
            export_results: If True, export results to CSV
        """
        print(f"\n{'='*70}")
        print("UTILITY 13: Community Detection (Task Clustering)")
        print(f"{'='*70}\n")
        print("Parameters:")
        print(f"  Min probability threshold: {min_probability}")
        print(f"  Analysis mode: {'By Goal' if by_goal else 'Overall'}")
        print(f"  Export results: {export_results}")

        # Create output directory if it doesn't exist
        output_dir = self._create_output_dir(file_path)

        if by_goal:
            # Analyze separately for each goal
            if self.goal_analyzers is None:
                print("Running goal-stratified analysis first...")
                self.goal_analyzers = self.analyzer.analyze_by_goal()

            print("\n" + "="*70)
            print("ANALYZING BY BIOLOGICAL GOAL")
            print("="*70)

            all_goal_results = {}

            for goal, goal_analyzer in self.goal_analyzers.items():
                print(f"\n{'─'*70}")
                print(f"Goal: {goal}")
                print(f"{'─'*70}")

                # Detect communities
                result = goal_analyzer.detect_communities(min_probability=min_probability)

                if result['num_communities'] == 0:
                    print("  ⚠ No communities detected (graph is empty)")
                    continue

                # Display results
                print(f"\n  Community Statistics:")
                print(f"    Number of communities: {result['num_communities']}")
                print(f"    Modularity score: {result['modularity']:.4f}")
                print(f"    Community sizes: {result['community_sizes']}")

                # Display each community
                print(f"\n  Detected Communities:")
                for idx, community in enumerate(result['communities']):
                    tasks = sorted(list(community))
                    print(f"    Community {idx + 1} ({len(tasks)} tasks): {', '.join(tasks)}")

                all_goal_results[goal] = result

                # Export for this goal
                if export_results:
                    # Create DataFrame with task-community mappings
                    community_data = []
                    for task, comm_idx in result['task_to_community'].items():
                        community_data.append({
                            'task': task,
                            'community': comm_idx + 1,  # 1-indexed for readability
                            'community_size': result['community_sizes'][comm_idx]
                        })

                    df = pd.DataFrame(community_data)
                    df = df.sort_values(['community', 'task'])

                    # Export to CSV
                    safe_goal_name = goal.replace('/', '_').replace('\\', '_').replace(' ', '_')
                    output_file = output_dir / f'goal_{safe_goal_name}_communities.csv'
                    df.to_csv(output_file, index=False)
                    print(f"    ✓ Exported to: {output_file}")

            return all_goal_results

        else:
            # Overall analysis
            print("\n" + "="*70)
            print("OVERALL ANALYSIS")
            print("="*70 + "\n")

            result = self.analyzer.detect_communities(min_probability=min_probability)

            if result['num_communities'] == 0:
                print("⚠ No communities detected")
                print("\nPossible reasons:")
                print("  - Graph is empty")
                print("  - Minimum probability threshold is too high")
                return {}

            # Display statistics
            print(f"Community Statistics:")
            print(f"  Number of communities: {result['num_communities']}")
            print(f"  Modularity score: {result['modularity']:.4f}")
            print(f"  Community sizes: {result['community_sizes']}")

            # Display each community
            print(f"\nDetected Communities:")
            for idx, community in enumerate(result['communities']):
                tasks = sorted(list(community))
                print(f"\n  Community {idx + 1} ({len(tasks)} tasks):")
                print(f"    {', '.join(tasks)}")

            # Export to CSV
            if export_results:
                # Create DataFrame with task-community mappings
                community_data = []
                for task, comm_idx in result['task_to_community'].items():
                    community_data.append({
                        'task': task,
                        'community': comm_idx + 1,  # 1-indexed for readability
                        'community_size': result['community_sizes'][comm_idx]
                    })

                df = pd.DataFrame(community_data)
                df = df.sort_values(['community', 'task'])

                # Export to CSV
                output_file = output_dir / 'task_communities.csv'
                df.to_csv(output_file, index=False)
                print(f"\n✓ Exported to: {output_file}")

            return result

    def utility_14_transition_entropy(self, min_probability: float = 0.0,
                                      file_path: str = './',
                                      by_goal: bool = False,
                                      export_results: bool = True):
        """
        Utility 14: Calculate transition entropy to measure workflow uncertainty

        Entropy measures the predictability of transitions from each task.
        High entropy = many possible next tasks (flexible workflow)
        Low entropy = few dominant next tasks (deterministic workflow)

        Args:
            min_probability: Minimum transition probability threshold
            file_path: Output directory for CSV export
            by_goal: If True, analyze separately for each biological goal
            export_results: If True, export results to CSV
        """
        print(f"\n{'='*70}")
        print("UTILITY 14: Transition Entropy Analysis")
        print(f"{'='*70}\n")
        print("Parameters:")
        print(f"  Min probability threshold: {min_probability}")
        print(f"  Analysis mode: {'By Goal' if by_goal else 'Overall'}")
        print(f"  Export results: {export_results}")

        # Create output directory if it doesn't exist
        output_dir = self._create_output_dir(file_path)

        if by_goal:
            # Analyze separately for each goal
            if self.goal_analyzers is None:
                print("Running goal-stratified analysis first...")
                self.goal_analyzers = self.analyzer.analyze_by_goal()

            print("\n" + "="*70)
            print("ANALYZING BY BIOLOGICAL GOAL")
            print("="*70)

            all_goal_results = {}

            for goal, goal_analyzer in self.goal_analyzers.items():
                print(f"\n{'─'*70}")
                print(f"Goal: {goal}")
                print(f"{'─'*70}")

                # Calculate entropy
                result = goal_analyzer.calculate_transition_entropy(min_probability=min_probability)

                if len(result['entropies']) == 0:
                    print("  ⚠ No tasks with transitions (graph is empty)")
                    continue

                # Display statistics
                print(f"\n  Entropy Statistics:")
                print(f"    Average entropy: {result['avg_entropy']:.4f} bits")
                print(f"    Maximum possible entropy: {result['max_entropy']:.4f} bits")
                print(f"    Number of tasks: {len(result['entropies'])}")

                # Display high entropy tasks (flexible/uncertain)
                print(f"\n  High Entropy Tasks (Flexible/Uncertain, > {result['avg_entropy']:.4f}):")
                if result['high_entropy_tasks']:
                    for task, entropy in result['high_entropy_tasks'][:10]:  # Top 10
                        print(f"    {task}: {entropy:.4f} bits")
                else:
                    print("    None")

                # Display low entropy tasks (deterministic/predictable)
                print(f"\n  Low Entropy Tasks (Deterministic/Predictable, ≤ {result['avg_entropy']:.4f}):")
                if result['low_entropy_tasks']:
                    for task, entropy in result['low_entropy_tasks'][:10]:  # Top 10
                        print(f"    {task}: {entropy:.4f} bits")
                else:
                    print("    None")

                all_goal_results[goal] = result

                # Export for this goal
                if export_results:
                    # Create DataFrame with entropy values
                    entropy_data = []
                    for task, entropy in result['sorted_entropies']:
                        category = 'high' if entropy > result['avg_entropy'] else 'low'
                        entropy_data.append({
                            'task': task,
                            'entropy': entropy,
                            'category': category
                        })

                    df = pd.DataFrame(entropy_data)

                    # Export to CSV
                    safe_goal_name = goal.replace('/', '_').replace('\\', '_').replace(' ', '_')
                    output_file = output_dir / f'goal_{safe_goal_name}_entropy.csv'
                    df.to_csv(output_file, index=False)
                    print(f"    ✓ Exported to: {output_file}")

            return all_goal_results

        else:
            # Overall analysis
            print("\n" + "="*70)
            print("OVERALL ANALYSIS")
            print("="*70 + "\n")

            result = self.analyzer.calculate_transition_entropy(min_probability=min_probability)

            if len(result['entropies']) == 0:
                print("⚠ No tasks with transitions")
                print("\nPossible reasons:")
                print("  - Graph is empty")
                print("  - Minimum probability threshold is too high")
                return {}

            # Display statistics
            print(f"Entropy Statistics:")
            print(f"  Average entropy: {result['avg_entropy']:.4f} bits")
            print(f"  Maximum possible entropy: {result['max_entropy']:.4f} bits")
            print(f"  Number of tasks: {len(result['entropies'])}")

            # Display all tasks sorted by entropy
            print(f"\nAll Tasks Sorted by Entropy (Highest to Lowest):")
            for i, (task, entropy) in enumerate(result['sorted_entropies'], 1):
                category = '🔄 Flexible' if entropy > result['avg_entropy'] else '➡️  Deterministic'
                print(f"  {i:2d}. {task:20s} {entropy:6.4f} bits  {category}")

            # Export to CSV
            if export_results:
                # Create DataFrame with entropy values
                entropy_data = []
                for task, entropy in result['sorted_entropies']:
                    category = 'high' if entropy > result['avg_entropy'] else 'low'
                    entropy_data.append({
                        'task': task,
                        'entropy': entropy,
                        'category': category
                    })

                df = pd.DataFrame(entropy_data)

                # Export to CSV
                output_file = output_dir / 'transition_entropy.csv'
                df.to_csv(output_file, index=False)
                print(f"\n✓ Exported to: {output_file}")

            return result

    def utility_15_task_persistence(self, min_probability: float = 0.0,
                                     file_path: str = './',
                                     by_goal: bool = False,
                                     export_results: bool = True):
        """
        Utility 15: Analyze task persistence (self-loop strength)

        Task persistence measures how often users stay on or repeat a task.
        High self-loop = "sticky" task requiring repeated actions or time
        No self-loop = quick transition task

        Args:
            min_probability: Minimum transition probability threshold
            file_path: Output directory for CSV export
            by_goal: If True, analyze separately for each biological goal
            export_results: If True, export results to CSV
        """
        print(f"\n{'='*70}")
        print("UTILITY 15: Task Persistence Analysis (Self-Loop Strength)")
        print(f"{'='*70}\n")
        print("Parameters:")
        print(f"  Min probability threshold: {min_probability}")
        print(f"  Analysis mode: {'By Goal' if by_goal else 'Overall'}")
        print(f"  Export results: {export_results}")

        # Create output directory if it doesn't exist
        output_dir = self._create_output_dir(file_path)

        if by_goal:
            # Analyze separately for each goal
            if self.goal_analyzers is None:
                print("Running goal-stratified analysis first...")
                self.goal_analyzers = self.analyzer.analyze_by_goal()

            print("\n" + "="*70)
            print("ANALYZING BY BIOLOGICAL GOAL")
            print("="*70)

            all_goal_results = {}

            for goal, goal_analyzer in self.goal_analyzers.items():
                print(f"\n{'─'*70}")
                print(f"Goal: {goal}")
                print(f"{'─'*70}")

                # Analyze persistence
                result = goal_analyzer.analyze_task_persistence(min_probability=min_probability)

                if len(result['self_loops']) == 0:
                    print("  ⚠ No tasks found (graph is empty)")
                    continue

                # Display statistics
                print(f"\n  Persistence Statistics:")
                print(f"    Total tasks analyzed: {len(result['self_loops'])}")
                print(f"    Tasks with persistence (self-loops): {len(result['tasks_with_persistence'])}")
                print(f"    Tasks without persistence: {len(result['tasks_without_persistence'])}")
                if result['avg_persistence'] > 0:
                    print(f"    Average persistence (self-loop prob): {result['avg_persistence']:.4f}")
                if result['max_persistence']:
                    print(f"    Highest persistence: {result['max_persistence'][0]} ({result['max_persistence'][1]:.4f})")

                # Display tasks with persistence
                if result['tasks_with_persistence']:
                    print(f"\n  Tasks with Persistence (Self-Loops):")
                    for task, prob in result['tasks_with_persistence'][:10]:  # Top 10
                        print(f"    {task}: {prob:.4f}")
                else:
                    print(f"\n  Tasks with Persistence: None")

                # Display tasks without persistence (sample)
                if result['tasks_without_persistence']:
                    num_to_show = min(5, len(result['tasks_without_persistence']))
                    print(f"\n  Sample Tasks without Persistence ({num_to_show} of {len(result['tasks_without_persistence'])}):")
                    for task in result['tasks_without_persistence'][:num_to_show]:
                        print(f"    {task}: 0.0000")

                all_goal_results[goal] = result

                # Export for this goal
                if export_results:
                    # Create DataFrame with persistence values
                    persistence_data = []
                    for task, prob in result['sorted_self_loops']:
                        category = 'persistent' if prob > 0 else 'non-persistent'
                        persistence_data.append({
                            'task': task,
                            'self_loop_probability': prob,
                            'category': category
                        })

                    df = pd.DataFrame(persistence_data)

                    # Export to CSV
                    safe_goal_name = goal.replace('/', '_').replace('\\', '_').replace(' ', '_')
                    output_file = output_dir / f'goal_{safe_goal_name}_persistence.csv'
                    df.to_csv(output_file, index=False)
                    print(f"    ✓ Exported to: {output_file}")

            return all_goal_results

        else:
            # Overall analysis
            print("\n" + "="*70)
            print("OVERALL ANALYSIS")
            print("="*70 + "\n")

            result = self.analyzer.analyze_task_persistence(min_probability=min_probability)

            if len(result['self_loops']) == 0:
                print("⚠ No tasks found")
                print("\nPossible reasons:")
                print("  - Graph is empty")
                print("  - Minimum probability threshold is too high")
                return {}

            # Display statistics
            print(f"Persistence Statistics:")
            print(f"  Total tasks analyzed: {len(result['self_loops'])}")
            print(f"  Tasks with persistence (self-loops): {len(result['tasks_with_persistence'])}")
            print(f"  Tasks without persistence: {len(result['tasks_without_persistence'])}")
            if result['avg_persistence'] > 0:
                print(f"  Average persistence (self-loop prob): {result['avg_persistence']:.4f}")
            if result['max_persistence']:
                print(f"  Highest persistence: {result['max_persistence'][0]} ({result['max_persistence'][1]:.4f})")

            # Display all tasks sorted by persistence
            print(f"\nAll Tasks Sorted by Persistence (Highest to Lowest):")
            for i, (task, prob) in enumerate(result['sorted_self_loops'], 1):
                if prob > 0:
                    category = '🔁 Persistent (self-loop)'
                    print(f"  {i:2d}. {task:20s} {prob:6.4f}  {category}")

            # Show non-persistent tasks
            if result['tasks_without_persistence']:
                print(f"\nTasks without Persistence (No Self-Loops): {len(result['tasks_without_persistence'])} tasks")
                print(f"  Sample: {', '.join(result['tasks_without_persistence'][:10])}")
                if len(result['tasks_without_persistence']) > 10:
                    print(f"  ... and {len(result['tasks_without_persistence']) - 10} more")

            # Export to CSV
            if export_results:
                # Create DataFrame with persistence values
                persistence_data = []
                for task, prob in result['sorted_self_loops']:
                    category = 'persistent' if prob > 0 else 'non-persistent'
                    persistence_data.append({
                        'task': task,
                        'self_loop_probability': prob,
                        'category': category
                    })

                df = pd.DataFrame(persistence_data)

                # Export to CSV
                output_file = output_dir / 'task_persistence.csv'
                df.to_csv(output_file, index=False)
                print(f"\n✓ Exported to: {output_file}")

            return result

    def utility_16_transition_heatmap(self, matrix_file: str, file_path: str = './', output_file: str = None):
        """Utility 16: Generate transition probability heatmap from a goal matrix CSV"""
        print(f"\n{'='*60}")
        print("UTILITY 16: TRANSITION PROBABILITY HEATMAP")
        print(f"{'='*60}\n")

        try:
            import seaborn as sns
        except ImportError:
            print("Error: seaborn is not installed. Run: pip install seaborn")
            return

        matrix_path = Path(matrix_file)
        if not matrix_path.exists():
            print(f"Error: Matrix file not found: {matrix_file}")
            return

        output_dir = self._create_output_dir(file_path)
        if output_file is None:
            output_file = f"transition_heatmap-{matrix_path.stem}.png"
        output_path = output_dir / output_file

        calibri_paths = [f.fname for f in fm.fontManager.ttflist if 'calibri' in f.name.lower()]
        font_family = 'Calibri' if calibri_paths else 'DejaVu Sans'
        if not calibri_paths:
            print("Warning: Calibri not found, falling back to DejaVu Sans.")

        plt.rcParams['font.family'] = font_family

        matrix = pd.read_csv(matrix_file, sep=',', index_col=0)

        task_order = [
            'START',
            'browse', 'communicate', 'connect', 'contextualize',
            'dissect', 'explore', 'identify', 'locate', 'lookup',
            'measure/quantify/summarize',
            'END'
        ]

        label_map = {
            'measure/quantify/summarize': 'measure/\nquantify/\nsummarize',
        }

        task_order = [t for t in task_order if t in matrix.index]
        matrix = matrix.loc[task_order, task_order]

        annot_labels = matrix.map(lambda v: f'{v:.2f}' if v > 0 else '')

        n = len(task_order)
        fig_w = max(12, n * 1.05)
        fig_h = max(9,  n * 0.9)

        _, ax = plt.subplots(figsize=(fig_w, fig_h))

        sns.heatmap(
            matrix,
            ax=ax,
            cmap='GnBu',
            vmin=0, vmax=1,
            annot=annot_labels,
            fmt='',
            linewidths=0.4,
            linecolor='#e0e0e0',
            cbar_kws={'shrink': 0.6, 'label': 'Transition probability'},
            annot_kws={'size': 12, 'family': font_family},
        )

        ax.set_xlabel('Target task', fontsize=15, labelpad=10, fontfamily=font_family, fontdict={'weight': 'bold'})
        ax.set_ylabel('Source task', fontsize=15, labelpad=10, fontfamily=font_family, fontdict={'weight': 'bold'})

        display_labels = [label_map.get(t, t) for t in task_order]

        ax.set_xticklabels(display_labels, rotation=40, ha='right', fontsize=13, fontfamily=font_family)
        ax.set_yticklabels(display_labels, rotation=0, fontsize=13, fontfamily=font_family)

        cbar = ax.collections[0].colorbar
        cbar.ax.tick_params(labelsize=12)
        cbar.set_label('Transition probability', fontsize=13, fontfamily=font_family)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Heatmap saved to: {output_path}")
        plt.show()


def display_menu():
    """Display interactive menu"""
    print(f"\n{'='*70}")
    print(" " * 15 + "TASK SEQUENCE ANALYSIS UTILITIES")
    print(f"{'='*70}\n")
    print("Available Utilities:")
    print()
    print("  [Basic Analysis]")
    print("  1. Summary Statistics")
    print("  2. Transition Probabilities (Top-K Next States)")
    print("  3. Transition Matrix (Overall)")
    print()
    print("  [Goal-Stratified Analysis]")
    print("  4. Goal-Stratified Transition Analysis")
    print("  5. Transition Matrices by Goal")
    print("  6. Compare Transitions Across Goals")
    print("  7. Find Goal-Specific Patterns")
    print()
    print("  [Sequence Analysis]")
    print("  8. Sequence Probability Calculator")
    print("  9. Export Pairwise Transitions")
    print(" 10. Visualize Task Flow")
    print()
    print("  [Network Analysis]")
    print(" 11. Centrality Analysis (Degree & Betweenness)")
    print(" 12. Workflow Path Analysis (Dominant Paths)")
    print(" 13. Community Detection (Task Clustering)")
    print(" 14. Transition Entropy Analysis (Workflow Uncertainty)")
    print(" 15. Task Persistence Analysis (Self-Loop Strength)")
    print()
    print("  [Visualization]")
    print(" 16. Transition Probability Heatmap")
    print()
    print("  q. Quit")
    print(f"{'='*70}\n")


def interactive_mode(utilities: TaskAnalysisUtilities):
    """Run interactive CLI mode"""
    while True:
        display_menu()
        choice = input("Select utility (1-16, q to quit): ").strip()

        if choice == 'q':
            print("\nGoodbye!")
            break
        elif choice == '1':
            utilities.utility_1_summary_statistics()
        elif choice == '2':
            top_k = input("Enter number of top transitions to show (default 3): ").strip()
            top_k = int(top_k) if top_k else 3
            utilities.utility_2_transition_probabilities(top_k=top_k)
        elif choice == '3':
            filename = input("Enter output filename (default: transition_matrix.csv): ").strip()
            filename = filename if filename else 'transition_matrix.csv'
            file_path = input("Enter output folder name (default: current directory): ").strip()
            file_path = file_path if file_path else './'
            utilities.utility_3_transition_matrix(file_path=file_path, filename=filename)
        elif choice == '4':
            file_path = input("Enter output folder name (default: current directory): ").strip()
            file_path = file_path if file_path else './'
            utilities.utility_4_goal_stratified_analysis(file_path=file_path)
        elif choice == '5':
            file_path = input("Enter output folder name (default: current directory): ").strip()
            file_path = file_path if file_path else './'
            utilities.utility_5_transition_matrix_by_goal()
        elif choice == '6':
            file_path = input("Enter output folder name (default: current directory): ").strip()
            file_path = file_path if file_path else './'
            utilities.utility_6_compare_goals_transitions(file_path=file_path)
        elif choice == '7':
            utilities.utility_7_find_unique_goal_patterns()
        elif choice == '8':
            utilities.utility_8_sequence_probability_calculator()
        elif choice == '9':
            filename = input("Enter output filename (default: pairwise_transitions.csv): ").strip()
            filename = filename if filename else 'pairwise_transitions.csv'
            file_path = input("Enter output folder name (default: current directory): ").strip()
            file_path = file_path if file_path else './'
            utilities.utility_9_export_pairwise_transitions(file_path=file_path, filename=filename)
        elif choice == '10':
            by_goal_choice = input("Visualize by goal? (y/n, default n): ").strip().lower()
            by_goal = by_goal_choice == 'y'
            min_prob = input("Enter minimum probability threshold (default 0.01): ").strip()
            min_prob = float(min_prob) if min_prob else 0.01
            file_path = input("Enter output folder name (default: current directory): ").strip()
            file_path = file_path if file_path else './'
            utilities.utility_10_visualize_flow(file_path=file_path, min_probability=min_prob, by_goal=by_goal)
        elif choice == '11':
            by_goal_choice = input("Analyze by goal? (y/n, default n): ").strip().lower()
            by_goal = by_goal_choice == 'y'
            min_prob = input("Enter minimum probability threshold (default 0.0): ").strip()
            min_prob = float(min_prob) if min_prob else 0.0
            file_path = input("Enter output folder name (default: current directory): ").strip()
            file_path = file_path if file_path else './'
            utilities.utility_11_centrality_analysis(min_probability=min_prob, file_path=file_path, by_goal=by_goal)
        elif choice == '12':
            by_goal_choice = input("Analyze by goal? (y/n, default n): ").strip().lower()
            by_goal = by_goal_choice == 'y'
            min_prob = input("Enter minimum probability threshold (default 0.0): ").strip()
            min_prob = float(min_prob) if min_prob else 0.0
            max_len = input("Enter maximum path length in edges (default 9): ").strip()
            max_len = int(max_len) if max_len else 9
            file_path = input("Enter output folder name (default: current directory): ").strip()
            file_path = file_path if file_path else './'
            utilities.utility_12_workflow_path_analysis(min_probability=min_prob, max_path_length=max_len,
                                                       file_path=file_path, by_goal=by_goal)
        elif choice == '13':
            by_goal_choice = input("Analyze by goal? (y/n, default n): ").strip().lower()
            by_goal = by_goal_choice == 'y'
            min_prob = input("Enter minimum probability threshold (default 0.0): ").strip()
            min_prob = float(min_prob) if min_prob else 0.0
            file_path = input("Enter output folder name (default: current directory): ").strip()
            file_path = file_path if file_path else './'
            utilities.utility_13_community_detection(min_probability=min_prob, file_path=file_path, by_goal=by_goal)
        elif choice == '14':
            by_goal_choice = input("Analyze by goal? (y/n, default n): ").strip().lower()
            by_goal = by_goal_choice == 'y'
            min_prob = input("Enter minimum probability threshold (default 0.0): ").strip()
            min_prob = float(min_prob) if min_prob else 0.0
            file_path = input("Enter output folder name (default: current directory): ").strip()
            file_path = file_path if file_path else './'
            utilities.utility_14_transition_entropy(min_probability=min_prob, file_path=file_path, by_goal=by_goal)
        elif choice == '15':
            by_goal_choice = input("Analyze by goal? (y/n, default n): ").strip().lower()
            by_goal = by_goal_choice == 'y'
            min_prob = input("Enter minimum probability threshold (default 0.0): ").strip()
            min_prob = float(min_prob) if min_prob else 0.0
            file_path = input("Enter output folder name (default: current directory): ").strip()
            file_path = file_path if file_path else './'
            utilities.utility_15_task_persistence(min_probability=min_prob, file_path=file_path, by_goal=by_goal)
        elif choice == '16':
            matrix_file = input("Enter path to goal matrix CSV file: ").strip()
            file_path = input("Enter output folder name (default: current directory): ").strip()
            file_path = file_path if file_path else './'
            output_file = input("Enter output PNG filename (default: transition_heatmap-<stem>.png): ").strip()
            output_file = output_file if output_file else None
            utilities.utility_16_transition_heatmap(matrix_file=matrix_file, file_path=file_path, output_file=output_file)
        else:
            print("\n⚠ Invalid choice. Please try again.")

        input("\nPress Enter to continue...")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Task Sequence Analysis Utilities',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Load data and enter interactive mode
  python task_analysis_utilities.py --file data.csv --interactive

  # Load data with custom columns
  python task_analysis_utilities.py --file data.csv --sequence VTA_Task_Combinations --goal DC_Primary_Goal --tool Tool_Name

  # Run specific utility
  python task_analysis_utilities.py --file data.csv --utility 4
        """
    )

    parser.add_argument('--file', '-f', type=str, help='Path to CSV file')
    parser.add_argument('--sequence', type=str, default='task_sequence',
                       help='Column name for task sequences (default: task_sequence)')
    parser.add_argument('--goal', type=str, default='biological_goal',
                       help='Column name for biological goals (default: biological_goal)')
    parser.add_argument('--tool', type=str, default='tool_name',
                       help='Column name for tool names (default: tool_name)')
    parser.add_argument('--delimiter', type=str, default='→',
                       help='Task delimiter in sequence (default: →)')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Enter interactive mode after loading')
    parser.add_argument('--utility', '-u', type=int, choices=range(1, 17),
                       help='Run specific utility (1-16)')
    args = parser.parse_args()

    # Initialize utilities
    utilities = TaskAnalysisUtilities()

    # Load data if file provided
    if args.file:
        if not Path(args.file).exists():
            print(f"Error: File not found: {args.file}")
            sys.exit(1)

        utilities.load_csv_data(
            csv_path=args.file,
            sequence_col=args.sequence,
            goal_col=args.goal,
            tool_col=args.tool,
            delimiter=args.delimiter
        )
    else:
        print("No data file provided.")
        print("\nOptions:")
        print("  1. Provide CSV file with --file option")
        print("  2. Run with --help for more information")
        sys.exit(1)

    # Run specific utility
    if args.utility is not None:
        file_path = input("Enter output folder name (default: current directory): ").strip()
        file_path = file_path if file_path else './'

        if args.utility == 1:
            utilities.utility_1_summary_statistics()
        elif args.utility == 2:
            utilities.utility_2_transition_probabilities()
        elif args.utility == 3:
            utilities.utility_3_transition_matrix(file_path=file_path)
        elif args.utility == 4:
            utilities.utility_4_goal_stratified_analysis(file_path=file_path)
        elif args.utility == 5:
            utilities.utility_5_transition_matrix_by_goal(file_path=file_path)
        elif args.utility == 6:
            utilities.utility_6_compare_goals_transitions(file_path=file_path)
        elif args.utility == 7:
            utilities.utility_7_find_unique_goal_patterns()
        elif args.utility == 8:
            utilities.utility_8_sequence_probability_calculator()
        elif args.utility == 9:
            utilities.utility_9_export_pairwise_transitions(file_path=file_path)
        elif args.utility == 10:
            utilities.utility_10_visualize_flow(file_path=file_path)
        elif args.utility == 11:
            utilities.utility_11_centrality_analysis(file_path=file_path)
        elif args.utility == 12:
            utilities.utility_12_workflow_path_analysis(file_path=file_path)
        elif args.utility == 13:
            utilities.utility_13_community_detection(file_path=file_path)
        elif args.utility == 14:
            utilities.utility_14_transition_entropy(file_path=file_path)
        elif args.utility == 15:
            utilities.utility_15_task_persistence(file_path=file_path)
        elif args.utility == 16:
            matrix_file = input("Enter path to goal matrix CSV file: ").strip()
            output_file = input("Enter output PNG filename (default: transition_heatmap-<stem>.png): ").strip()
            output_file = output_file if output_file else None
            utilities.utility_16_transition_heatmap(matrix_file=matrix_file, file_path=file_path, output_file=output_file)

    # Enter interactive mode
    if args.interactive or args.utility is None:
        interactive_mode(utilities)


if __name__ == "__main__":
    main()
