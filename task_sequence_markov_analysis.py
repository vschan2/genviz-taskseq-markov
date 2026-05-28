"""
Task Sequence Markov Chain Analysis for Comparative Genomics Visualization
Based on systematic literature review data extraction

This script demonstrates:
1. Data preparation from extracted sequences
2. First-order Markov chain construction
3. Transition probability calculation
4. Visualization of task flow patterns
"""

import pandas as pd
import numpy as np
from collections import defaultdict, Counter
import networkx as nx
import networkx.algorithms.community as nx_community
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict

class TaskSequenceAnalyzer:
    """Analyzes task sequences using Markov chain models"""
    
    def __init__(self):
        self.transition_counts = defaultdict(Counter)
        self.transition_probs = {}
        self.sequences = []
        
    def add_sequence(self, sequence: List[str], goal: str = None, tool: str = None):
        """
        Add a task sequence to the analyzer
        
        Args:
            sequence: List of tasks in order, e.g., ['locate', 'identify', 'lookup']
            goal: Optional biological goal associated with sequence
            tool: Optional tool name
        """
        # Add START and END tokens
        full_sequence = ['START'] + sequence + ['END']
        
        # Store metadata
        self.sequences.append({
            'sequence': full_sequence,
            'goal': goal,
            'tool': tool,
            'length': len(sequence)
        })
        
        # Count transitions
        for i in range(len(full_sequence) - 1):
            from_state = full_sequence[i]
            to_state = full_sequence[i + 1]
            self.transition_counts[from_state][to_state] += 1
    
    def calculate_transition_probabilities(self):
        """Calculate P(to_state | from_state) for all observed transitions"""
        for from_state, to_states in self.transition_counts.items():
            total = sum(to_states.values())
            self.transition_probs[from_state] = {
                to_state: count / total 
                for to_state, count in to_states.items()
            }
    
    def get_transition_probability(self, from_state: str, to_state: str) -> float:
        """Get probability of transitioning from one state to another"""
        if from_state not in self.transition_probs:
            return 0.0
        return self.transition_probs[from_state].get(to_state, 0.0)
    
    def get_most_likely_next_states(self, current_state: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """Get the k most likely next states from current state"""
        if current_state not in self.transition_probs:
            return []
        
        probs = self.transition_probs[current_state]
        sorted_states = sorted(probs.items(), key=lambda x: x[1], reverse=True)
        return sorted_states[:top_k]
    
    def export_pairwise_dataframe(self) -> pd.DataFrame:
        """Export transitions as pairwise dataframe for further analysis"""
        rows = []
        for seq_info in self.sequences:
            sequence = seq_info['sequence']
            for i, (from_state, to_state) in enumerate(zip(sequence[:-1], sequence[1:])):
                rows.append({
                    'tool': seq_info['tool'],
                    'goal': seq_info['goal'],
                    'from_state': from_state,
                    'to_state': to_state,
                    'position': i,
                    'sequence_length': seq_info['length']
                })
        return pd.DataFrame(rows)
    
    def create_transition_matrix(self, states: List[str] = None) -> pd.DataFrame:
        """Create transition probability matrix"""
        if states is None:
            states = sorted(set(self.transition_counts.keys()))
        
        matrix = pd.DataFrame(0.0, index=states, columns=states)
        
        for from_state in states:
            if from_state in self.transition_probs:
                for to_state, prob in self.transition_probs[from_state].items():
                    if to_state in states:
                        matrix.loc[from_state, to_state] = prob
        
        return matrix
    
    def visualize_flow(self, min_probability: float = 0.1, output_file: str = None):
        """
        Visualize task flow as directed graph

        Args:
            min_probability: Only show transitions with probability >= this threshold
            output_file: If provided, save figure to this path
        """
        G = nx.DiGraph()

        # Add edges with weights
        for from_state, to_states in self.transition_probs.items():
            for to_state, prob in to_states.items():
                if prob >= min_probability:
                    G.add_edge(from_state, to_state, weight=prob)

        # Layout        
        pos = nx.nx_agraph.graphviz_layout(G, prog='dot', args='-Grankdir=LR')
        # pos = nx.spring_layout(G, k=2, iterations=50)

        # Draw
        plt.figure(figsize=(14, 10))

        # Define task categories by color
        search_tasks = {'lookup', 'locate', 'browse', 'explore'}
        comparative_tasks = {'identify', 'dissect', 'measure/quantify/summarize', 'connect',
                         'contextualize', 'communicate'}

        # Draw nodes with category-based colors
        node_colors = []
        for node in G.nodes():
            if node == 'START':
                node_colors.append('lightgreen')
            elif node == 'END':
                node_colors.append('lightcoral')
            elif node.lower() in search_tasks:
                node_colors.append('lightblue')
            elif node.lower() in comparative_tasks:
                node_colors.append('#ffcc99')  # light orange
            else:
                node_colors.append('lightgray')  # default for any other tasks

        nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                              node_size=3000, alpha=0.9)
        
        # Draw edges with varying thickness
        edges = G.edges()
        weights = [G[u][v]['weight'] for u, v in edges]
        nx.draw_networkx_edges(G, pos, width=[w * 5 for w in weights],
                              alpha=0.6, edge_color='gray',
                              arrows=True, arrowsize=20,
                              connectionstyle="arc3,rad=0.1")
        
        # Draw labels
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
        
        # Draw edge labels (probabilities)
        edge_labels = {(u, v): f"{G[u][v]['weight']:.2f}"
                      for u, v in G.edges()}
        nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=8)

        # Add title
        plt.title("Task Sequence Flow (Markov Chain Transitions)",
                 fontsize=16, fontweight='bold', pad=20)

        # Add legend for task categories
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='lightgreen', edgecolor='black', label='START'),
            Patch(facecolor='lightcoral', edgecolor='black', label='END'),
            Patch(facecolor='lightblue', edgecolor='black',
                  label='Search (locate, browse, lookup, explore)'),
            Patch(facecolor='#ffcc99', edgecolor='black',
                  label='Comparative (identify, measure, connect, etc.)')
        ]
        plt.legend(handles=legend_elements, loc='upper left',
                  fontsize=10, framealpha=0.9)

        plt.axis('off')
        plt.tight_layout()

        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.show()
    
    def analyze_by_goal(self) -> Dict[str, dict]:
        """Stratified analysis by biological goal"""
        goal_analyzers = defaultdict(lambda: TaskSequenceAnalyzer())
        
        for seq_info in self.sequences:
            goal = seq_info['goal']
            if goal:
                # Remove START/END tokens for re-adding
                sequence = seq_info['sequence'][1:-1]
                goal_analyzers[goal].add_sequence(
                    sequence, goal=goal, tool=seq_info['tool']
                )
        
        # Calculate probabilities for each goal
        for goal, analyzer in goal_analyzers.items():
            analyzer.calculate_transition_probabilities()
        
        return dict(goal_analyzers)
    
    def calculate_sequence_probability(self, sequence: List[str]) -> float:
        """Calculate probability of observing a specific sequence"""
        full_sequence = ['START'] + sequence + ['END']
        prob = 1.0
        
        for i in range(len(full_sequence) - 1):
            from_state = full_sequence[i]
            to_state = full_sequence[i + 1]
            trans_prob = self.get_transition_probability(from_state, to_state)
            
            if trans_prob == 0:
                return 0.0
            prob *= trans_prob
        
        return prob
    
    def generate_summary_statistics(self) -> Dict:
        """Generate summary statistics about the sequences"""
        lengths = [s['length'] for s in self.sequences]
        
        # Count unique states
        all_states = set()
        for s in self.sequences:
            all_states.update(s['sequence'])
        all_states.discard('START')
        all_states.discard('END')
        
        return {
            'num_sequences': len(self.sequences),
            'num_unique_tasks': len(all_states),
            'avg_sequence_length': np.mean(lengths),
            'median_sequence_length': np.median(lengths),
            'min_sequence_length': np.min(lengths),
            'max_sequence_length': np.max(lengths),
            'total_transitions': sum(sum(c.values()) for c in self.transition_counts.values()),
            'num_unique_transitions': sum(len(c) for c in self.transition_counts.values()),
            'tasks': sorted(all_states)
        }
    
    def generate_summary_statistics_with_startend(self) -> Dict:
        """Generate summary statistics about the sequences"""
        lengths = [s['length'] for s in self.sequences]
        
        # Count unique states
        all_states = set()
        for s in self.sequences:
            all_states.update(s['sequence'])
        
        return {
            'num_sequences': len(self.sequences),
            'num_unique_tasks': len(all_states),
            'avg_sequence_length': np.mean(lengths),
            'median_sequence_length': np.median(lengths),
            'min_sequence_length': np.min(lengths),
            'max_sequence_length': np.max(lengths),
            'total_transitions': sum(sum(c.values()) for c in self.transition_counts.values()),
            'num_unique_transitions': sum(len(c) for c in self.transition_counts.values()),
            'tasks': sorted(all_states)
        }

    def calculate_centrality_metrics(self, min_probability: float = 0.0) -> Dict:
        """
        Calculate network centrality metrics for task flow graph

        Args:
            min_probability: Only include transitions with probability >= this threshold

        Returns:
            Dictionary containing:
            - centrality_data: List of dicts with task and all centrality metrics
            - out_degree_centrality: Dict mapping task -> out-degree centrality
            - in_degree_centrality: Dict mapping task -> in-degree centrality
            - betweenness_centrality: Dict mapping task -> betweenness centrality
            - pagerank: Dict mapping task -> pagerank score
            - graph: The NetworkX DiGraph object
        """
        # Build directed graph from transition probabilities
        G = nx.DiGraph()

        for from_state, to_states in self.transition_probs.items():
            for to_state, prob in to_states.items():
                if prob >= min_probability:
                    G.add_edge(from_state, to_state, weight=prob)

        # Return empty result if graph is empty
        if len(G.nodes()) == 0:
            return {
                'centrality_data': [],
                'out_degree_centrality': {},
                'in_degree_centrality': {},
                'betweenness_centrality': {},
                'pagerank': {},
                'graph': G
            }

        # Calculate all centrality metrics
        out_degree_cent = nx.out_degree_centrality(G)
        in_degree_cent = nx.in_degree_centrality(G)
        betweenness = nx.betweenness_centrality(G, weight='weight')
        pagerank = nx.pagerank(G, weight='weight')

        # Combine results into structured format
        centrality_data = []
        for node in G.nodes():
            centrality_data.append({
                'task': node,
                'out_degree_centrality': out_degree_cent.get(node, 0.0),
                'in_degree_centrality': in_degree_cent.get(node, 0.0),
                'betweenness_centrality': betweenness.get(node, 0.0),
                'pagerank': pagerank.get(node, 0.0)
            })

        # Sort by betweenness centrality (can be changed as needed)
        centrality_data.sort(key=lambda x: x['betweenness_centrality'], reverse=True)

        return {
            'centrality_data': centrality_data,
            'out_degree_centrality': out_degree_cent,
            'in_degree_centrality': in_degree_cent,
            'betweenness_centrality': betweenness,
            'pagerank': pagerank,
            'graph': G
        }

    def analyze_workflow_paths(self, min_probability: float = 0.0, max_path_length: int = 9) -> Dict:
        """
        Analyze actual workflow paths from data to reveal dominant workflows and their frequencies

        This method counts the actual sequences from your data (not just possible paths).

        Args:
            min_probability: Only include sequences whose transitions all meet this probability threshold
            max_path_length: Maximum path length (number of edges/transitions, not nodes)

        Returns:
            Dictionary containing:
            - all_paths: List of all sequence paths (including duplicates for frequency counting)
            - path_frequencies: Dict mapping path tuple -> frequency count
            - sorted_paths: List of (path, frequency) tuples sorted by frequency
            - path_length_distribution: Dict mapping path length -> count of sequences
            - total_unique_paths: Number of unique sequence patterns
            - total_path_instances: Total number of sequences analyzed
            - most_common_length: Most common path length (length, count)
            - filtered_count: Number of sequences filtered out by criteria
            - graph: The NetworkX DiGraph object (for reference)
        """
        from collections import Counter

        # Build directed graph from transition probabilities (for filtering if needed)
        G = nx.DiGraph()
        for from_state, to_states in self.transition_probs.items():
            for to_state, prob in to_states.items():
                if prob >= min_probability:
                    G.add_edge(from_state, to_state, weight=prob)

        # Analyze actual sequences from data
        valid_sequences = []
        filtered_count = 0

        for seq_info in self.sequences:
            sequence = seq_info['sequence']  # Already includes START and END
            path_length = len(sequence) - 1  # Number of edges

            # Filter by max path length
            if path_length > max_path_length:
                filtered_count += 1
                continue

            # Filter by min_probability: check if all transitions in this sequence meet threshold
            if min_probability > 0.0:
                valid = True
                for i in range(len(sequence) - 1):
                    from_state = sequence[i]
                    to_state = sequence[i + 1]
                    # Check if this transition exists in the filtered graph
                    if not G.has_edge(from_state, to_state):
                        valid = False
                        break
                if not valid:
                    filtered_count += 1
                    continue

            # Add to valid sequences
            valid_sequences.append(tuple(sequence))

        # Return empty result if no valid sequences
        if len(valid_sequences) == 0:
            return {
                'all_paths': [],
                'path_frequencies': {},
                'sorted_paths': [],
                'path_length_distribution': {},
                'total_unique_paths': 0,
                'total_path_instances': 0,
                'most_common_length': None,
                'filtered_count': filtered_count,
                'graph': G
            }

        # Calculate frequency of each unique path
        path_frequencies = Counter(valid_sequences)

        # Sort paths by frequency (most common first)
        sorted_paths = sorted(path_frequencies.items(), key=lambda x: x[1], reverse=True)

        # Calculate path length distribution (length = number of edges)
        path_lengths = Counter([len(p) - 1 for p in valid_sequences])

        # Find most common path length
        most_common_length = path_lengths.most_common(1)[0] if path_lengths else None

        return {
            'all_paths': valid_sequences,
            'path_frequencies': dict(path_frequencies),
            'sorted_paths': sorted_paths,
            'path_length_distribution': dict(path_lengths),
            'total_unique_paths': len(path_frequencies),
            'total_path_instances': len(valid_sequences),
            'most_common_length': most_common_length,
            'filtered_count': filtered_count,
            'graph': G
        }

    def detect_communities(self, min_probability: float = 0.0) -> Dict:
        """
        Detect communities (task clusters) in the workflow graph using modularity optimization

        Communities represent groups of tasks that are densely connected to each other
        but sparsely connected to other groups, revealing modular workflow patterns.

        Args:
            min_probability: Only include transitions with probability >= this threshold

        Returns:
            Dictionary containing:
            - communities: List of frozensets, each containing task names in a community
            - modularity: Modularity score (higher = better community structure, range -0.5 to 1.0)
            - num_communities: Number of communities detected
            - community_sizes: List of community sizes
            - task_to_community: Dict mapping task name -> community index
            - graph: The undirected graph used (without START/END)
        """
        # Build directed graph from transition probabilities
        G = nx.DiGraph()
        for from_state, to_states in self.transition_probs.items():
            for to_state, prob in to_states.items():
                if prob >= min_probability:
                    G.add_edge(from_state, to_state, weight=prob)

        # Convert to undirected and remove START/END nodes
        G_undirected = G.to_undirected()
        G_core = G_undirected.copy()

        # Remove START and END nodes if they exist
        nodes_to_remove = [node for node in ['START', 'END'] if node in G_core.nodes()]
        G_core.remove_nodes_from(nodes_to_remove)

        # Return empty result if graph is empty
        if len(G_core.nodes()) == 0:
            return {
                'communities': [],
                'modularity': 0.0,
                'num_communities': 0,
                'community_sizes': [],
                'task_to_community': {},
                'graph': G_core
            }

        # Detect communities using greedy modularity optimization
        communities = nx_community.greedy_modularity_communities(G_core, weight='weight')

        # Calculate modularity score
        modularity = nx_community.modularity(G_core, communities, weight='weight')

        # Convert communities to list for easier handling
        communities_list = list(communities)

        # Get community sizes
        community_sizes = [len(c) for c in communities_list]

        # Create mapping from task to community index
        task_to_community = {}
        for idx, community in enumerate(communities_list):
            for task in community:
                task_to_community[task] = idx

        return {
            'communities': communities_list,
            'modularity': modularity,
            'num_communities': len(communities_list),
            'community_sizes': community_sizes,
            'task_to_community': task_to_community,
            'graph': G_core
        }

    def calculate_transition_entropy(self, min_probability: float = 0.0) -> Dict:
        """
        Calculate transition entropy for each task to measure workflow uncertainty

        Transition entropy measures the unpredictability of the next task from a current task.
        - High entropy = many possible next tasks with similar probabilities (more flexible/uncertain)
        - Low entropy = few dominant next tasks (more deterministic/predictable)

        Args:
            min_probability: Only include transitions with probability >= this threshold

        Returns:
            Dictionary containing:
            - entropies: Dict mapping task name -> entropy value
            - sorted_entropies: List of (task, entropy) tuples sorted by entropy (high to low)
            - avg_entropy: Average entropy across all tasks
            - max_entropy: Maximum possible entropy (log2 of max branching factor)
            - high_entropy_tasks: Tasks with entropy > avg (flexible/uncertain)
            - low_entropy_tasks: Tasks with entropy < avg (deterministic/predictable)
            - graph: The NetworkX DiGraph object
        """
        # Build directed graph from transition probabilities
        G = nx.DiGraph()
        for from_state, to_states in self.transition_probs.items():
            for to_state, prob in to_states.items():
                if prob >= min_probability:
                    G.add_edge(from_state, to_state, weight=prob)

        def transition_entropy(node):
            """Calculate entropy for a single node"""
            out_edges = list(G.out_edges(node, data='weight'))
            if len(out_edges) == 0:
                return 0.0

            weights = np.array([w for _, _, w in out_edges])
            probs = weights / weights.sum()

            # Shannon entropy: H = -sum(p * log2(p))
            # Add small epsilon to avoid log(0)
            return -np.sum(probs * np.log2(probs + 1e-10))

        # Calculate entropy for each node
        entropies = {node: transition_entropy(node) for node in G.nodes()}

        # Sort by entropy (highest first)
        sorted_entropies = sorted(entropies.items(), key=lambda x: x[1], reverse=True)

        # Calculate statistics
        entropy_values = list(entropies.values())
        avg_entropy = np.mean(entropy_values) if entropy_values else 0.0

        # Maximum possible entropy (when all transitions are equally likely)
        max_branching = max([G.out_degree(node) for node in G.nodes()]) if G.nodes() else 0
        max_entropy = np.log2(max_branching) if max_branching > 0 else 0.0

        # Categorize tasks
        high_entropy_tasks = [(task, ent) for task, ent in sorted_entropies if ent > avg_entropy]
        low_entropy_tasks = [(task, ent) for task, ent in sorted_entropies if ent <= avg_entropy]

        return {
            'entropies': entropies,
            'sorted_entropies': sorted_entropies,
            'avg_entropy': avg_entropy,
            'max_entropy': max_entropy,
            'high_entropy_tasks': high_entropy_tasks,
            'low_entropy_tasks': low_entropy_tasks,
            'graph': G
        }

    def analyze_task_persistence(self, min_probability: float = 0.0) -> Dict:
        """
        Analyze task persistence by measuring self-loop strength

        Task persistence (self-loops) indicates how often users stay on or repeat a task.
        - High self-loop = "sticky" task where users spend time or repeat actions
        - No self-loop = quick transition task

        Args:
            min_probability: Only include transitions with probability >= this threshold

        Returns:
            Dictionary containing:
            - self_loops: Dict mapping task name -> self-loop probability
            - sorted_self_loops: List of (task, probability) tuples sorted by strength (high to low)
            - tasks_with_persistence: List of (task, prob) with self-loops > 0
            - tasks_without_persistence: List of tasks with no self-loops
            - avg_persistence: Average self-loop probability (excluding zero)
            - max_persistence: Task with highest self-loop probability
            - graph: The NetworkX DiGraph object
        """
        # Build directed graph from transition probabilities
        G = nx.DiGraph()
        for from_state, to_states in self.transition_probs.items():
            for to_state, prob in to_states.items():
                if prob >= min_probability:
                    G.add_edge(from_state, to_state, weight=prob)

        # Calculate self-loop strength for each node (excluding START and END)
        self_loops = {}
        for node in G.nodes():
            if node not in ['START', 'END']:
                # Check if self-loop exists
                if G.has_edge(node, node):
                    self_loops[node] = G[node][node]['weight']
                else:
                    self_loops[node] = 0.0

        # Sort by self-loop strength (highest first)
        sorted_self_loops = sorted(self_loops.items(), key=lambda x: x[1], reverse=True)

        # Categorize tasks
        tasks_with_persistence = [(task, prob) for task, prob in sorted_self_loops if prob > 0]
        tasks_without_persistence = [task for task, prob in sorted_self_loops if prob == 0]

        # Calculate statistics
        persistence_values = [prob for prob in self_loops.values() if prob > 0]
        avg_persistence = np.mean(persistence_values) if persistence_values else 0.0

        # Find task with max persistence
        max_persistence = sorted_self_loops[0] if sorted_self_loops and sorted_self_loops[0][1] > 0 else None

        return {
            'self_loops': self_loops,
            'sorted_self_loops': sorted_self_loops,
            'tasks_with_persistence': tasks_with_persistence,
            'tasks_without_persistence': tasks_without_persistence,
            'avg_persistence': avg_persistence,
            'max_persistence': max_persistence,
            'graph': G
        }


def example_usage():
    """Demonstrate usage with example data"""
    
    # Initialize analyzer
    analyzer = TaskSequenceAnalyzer()
    
    # Example sequences from your extraction (simplified for demonstration)
    # Format: (sequence, goal, tool)
    example_data = [
        (['locate', 'identify', 'lookup', 'explore', 'contextualize'], 
         'Species identification', 'ToolA'),
        (['browse', 'identify', 'measure', 'connect'], 
         'Genetic diversity assessment', 'ToolB'),
        (['locate', 'identify', 'dissect', 'quantify'], 
         'Population structure analysis', 'ToolC'),
        (['lookup', 'explore', 'contextualize'], 
         'Species identification', 'ToolA'),
        (['browse', 'locate', 'identify', 'measure', 'compare'], 
         'Evolutionary relationship reconstruction', 'ToolD'),
        (['identify', 'lookup', 'explore', 'quantify', 'communicate'], 
         'Conservation prioritization', 'ToolE'),
    ]
    
    # Add sequences
    for sequence, goal, tool in example_data:
        analyzer.add_sequence(sequence, goal=goal, tool=tool)
    
    # Calculate probabilities
    analyzer.calculate_transition_probabilities()
    
    # Generate summary
    print("=== SUMMARY STATISTICS ===")
    stats = analyzer.generate_summary_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n=== TRANSITION PROBABILITIES ===")
    print("Most likely transitions from each state:")
    for state in sorted(analyzer.transition_probs.keys()):
        if state != 'END':
            next_states = analyzer.get_most_likely_next_states(state, top_k=3)
            print(f"\nFrom '{state}':")
            for next_state, prob in next_states:
                print(f"  → {next_state}: {prob:.3f}")
    
    # Export pairwise dataframe
    print("\n=== PAIRWISE TRANSITIONS DATAFRAME ===")
    df_pairs = analyzer.export_pairwise_dataframe()
    print(df_pairs.head(10))
    
    # Transition matrix
    print("\n=== TRANSITION MATRIX ===")
    # Get all unique states except START/END for cleaner matrix
    states = sorted([s for s in stats['tasks'] if s not in ['START', 'END']])
    transition_matrix = analyzer.create_transition_matrix(states)
    print(transition_matrix)
    
    # Goal-stratified analysis
    print("\n=== GOAL-STRATIFIED ANALYSIS ===")
    goal_analyzers = analyzer.analyze_by_goal()
    for goal, goal_analyzer in goal_analyzers.items():
        print(f"\nGoal: {goal}")
        print(f"  Sequences: {len(goal_analyzer.sequences)}")
        print(f"  Most common transition:")
        # Find most common transition for this goal
        max_prob = 0
        max_transition = None
        for from_state, to_states in goal_analyzer.transition_probs.items():
            for to_state, prob in to_states.items():
                if from_state != 'START' and to_state != 'END' and prob > max_prob:
                    max_prob = prob
                    max_transition = (from_state, to_state)
        if max_transition:
            print(f"  {max_transition[0]} → {max_transition[1]}: {max_prob:.3f}")
    
    # Visualize (uncomment to generate visualization)
    # analyzer.visualize_flow(min_probability=0.15, output_file='task_flow.png')
    
    return analyzer


if __name__ == "__main__":
    analyzer = example_usage()
    print("\n=== ANALYSIS COMPLETE ===")
    print("\nNext steps:")
    print("1. Load your 34 articles' extracted data")
    print("2. Use analyzer.add_sequence() for each extracted task combination")
    print("3. Run calculate_transition_probabilities()")
    print("4. Explore patterns using the analysis methods above")
