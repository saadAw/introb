from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
import json
import statistics
from src.config.types import AlgorithmType, TestScenario

@dataclass
class RunMetrics:
    """Stores metrics for a single algorithm run"""
    algorithm: AlgorithmType
    maze_type: TestScenario
    start_time: datetime
    end_time: Optional[datetime] = None
    path_length: int = 0
    nodes_explored: int = 0
    success: bool = False
    score: float = 0.0
    completion_time: float = 0.0
    memory_used: float = 0.0
    remaining_time: int = 0
    total_time: int = 0
    time_taken: float = 0.0
    steps_per_second: float = 0.0
    exploration_efficiency: float = 0.0

@dataclass
class AlgorithmMetrics:
    """Aggregated metrics for an algorithm across all runs"""
    total_runs: int = 0
    successful_runs: int = 0
    avg_path_length: float = 0.0
    avg_completion_time: float = 0.0
    avg_nodes_explored: float = 0.0
    avg_score: float = 0.0
    avg_steps_per_second: float = 0.0
    avg_exploration_efficiency: float = 0.0
    min_path_length: int = float('inf')
    max_path_length: int = 0
    fastest_completion: float = float('inf')
    slowest_completion: float = 0
    best_score: float = 0
    runs: List[RunMetrics] = field(default_factory=list)


class MetricsManager:
    def __init__(self, save_file: str = "metrics_data.json"):
        self.save_file = save_file
        self.metrics: Dict[str, Dict[str, AlgorithmMetrics]] = {}  # maze_type -> algorithm -> metrics
        self.current_run: Optional[RunMetrics] = None
        self.load_metrics()

    def start_run(self, algorithm: AlgorithmType, maze_type: TestScenario):
        """Start tracking a new algorithm run"""
        self.current_run = RunMetrics(
            algorithm=algorithm,
            maze_type=maze_type,
            start_time=datetime.now()
        )

    def update_run(self, nodes_explored: int, path_length: int, time_taken: float, 
                  remaining_time: int, total_time: int, memory_used: float = 0):
        """Update metrics for current run"""
        if self.current_run:
            self.current_run.nodes_explored = nodes_explored
            self.current_run.path_length = path_length
            self.current_run.time_taken = time_taken
            self.current_run.remaining_time = remaining_time
            self.current_run.total_time = total_time
            self.current_run.memory_used = memory_used
            
            # Calculate derived metrics
            if time_taken > 0:
                self.current_run.steps_per_second = path_length / time_taken
            if nodes_explored > 0:
                # This represents "nodes explored per thousand path steps"  
                efficiency = (path_length / nodes_explored) * 1000
                self.current_run.exploration_efficiency = round(efficiency, 2)

    def end_run(self, success: bool, score: float):
        """End current run and save metrics"""
        if self.current_run:
            self.current_run.end_time = datetime.now()
            self.current_run.success = success
            self.current_run.score = score
            self.current_run.completion_time = (
                self.current_run.end_time - self.current_run.start_time
            ).total_seconds()

            # Add to metrics storage
            maze_key = self.current_run.maze_type.name
            algo_key = self.current_run.algorithm.name

            if maze_key not in self.metrics:
                self.metrics[maze_key] = {}

            if algo_key not in self.metrics[maze_key]:
                self.metrics[maze_key][algo_key] = AlgorithmMetrics()

            algo_metrics = self.metrics[maze_key][algo_key]
            algo_metrics.total_runs += 1
            if success:
                algo_metrics.successful_runs += 1

            # Update averages
            algo_metrics.runs.append(self.current_run)
            self._update_averages(algo_metrics)

            # Save to file
            self.save_metrics()
            self.current_run = None

    def _update_averages(self, metrics: AlgorithmMetrics):
        """Update average metrics"""
        successful_runs = [run for run in metrics.runs if run.success]
        if successful_runs:
            metrics.avg_path_length = statistics.mean(run.path_length for run in successful_runs)
            metrics.avg_completion_time = statistics.mean(run.completion_time for run in successful_runs)
            metrics.avg_nodes_explored = statistics.mean(run.nodes_explored for run in successful_runs)
            metrics.avg_score = statistics.mean(run.score for run in successful_runs)
            metrics.avg_steps_per_second = statistics.mean(run.steps_per_second for run in successful_runs)
            metrics.avg_exploration_efficiency = statistics.mean(run.exploration_efficiency for run in successful_runs)
            
            # Update min/max metrics
            metrics.min_path_length = min(run.path_length for run in successful_runs)
            metrics.max_path_length = max(run.path_length for run in successful_runs)
            metrics.fastest_completion = min(run.completion_time for run in successful_runs)
            metrics.slowest_completion = max(run.completion_time for run in successful_runs)
            metrics.best_score = max(run.score for run in successful_runs)

    def save_metrics(self):
        """Save metrics to file"""
        data = {}
        for maze_type, maze_metrics in self.metrics.items():
            data[maze_type] = {}
            for algo, metrics in maze_metrics.items():
                data[maze_type][algo] = {
                    'total_runs': metrics.total_runs,
                    'successful_runs': metrics.successful_runs,
                    'avg_path_length': metrics.avg_path_length,
                    'avg_completion_time': metrics.avg_completion_time,
                    'avg_nodes_explored': metrics.avg_nodes_explored,
                    'avg_score': metrics.avg_score
                }
        
        with open(self.save_file, 'w') as f:
            json.dump(data, f, indent=4)

    def load_metrics(self):
        """Load metrics from file"""
        try:
            with open(self.save_file, 'r') as f:
                data = json.load(f)
                for maze_type, maze_metrics in data.items():
                    self.metrics[maze_type] = {}
                    for algo, metrics_data in maze_metrics.items():
                        metrics = AlgorithmMetrics(
                            total_runs=metrics_data['total_runs'],
                            successful_runs=metrics_data['successful_runs'],
                            avg_path_length=metrics_data['avg_path_length'],
                            avg_completion_time=metrics_data['avg_completion_time'],
                            avg_nodes_explored=metrics_data['avg_nodes_explored'],
                            avg_score=metrics_data['avg_score']
                        )
                        self.metrics[maze_type][algo] = metrics
        except FileNotFoundError:
            pass

    def get_algorithm_performance(self, algorithm: AlgorithmType, maze_type: TestScenario) -> Optional[AlgorithmMetrics]:
        """Get performance metrics for a specific algorithm and maze type"""
        maze_key = maze_type.name
        algo_key = algorithm.name
        return self.metrics.get(maze_key, {}).get(algo_key)

