from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
import json
import psutil
import os
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
    remaining_time: int = 0
    total_time: int = 0
    time_taken: float = 0.0
    steps_per_second: float = 0.0
    exploration_efficiency: float = 0.0
    # Memory metrics
    memory_start_mb: float = 0.0
    memory_peak_mb: float = 0.0
    memory_increase_mb: float = 0.0

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
    # Add memory fields  
    memory_start_mb: float = 0.0  
    memory_peak_mb: float = 0.0  
    memory_increase_mb: float = 0.0  
    runs: List[RunMetrics] = field(default_factory=list)

class MemoryTracker:  
    def __init__(self):  
        self.process = psutil.Process(os.getpid())  
        self.start_memory = 0  
        self.peak_memory = 0  
        self.baseline_memory = self._get_baseline_memory()  

    def _get_baseline_memory(self):  
        """Get baseline memory after garbage collection"""  
        import gc  
        gc.collect()  # Force garbage collection  
        return self.process.memory_info().rss / 1024 / 1024  # MB  

    def start_tracking(self):  
        """Start tracking memory usage after garbage collection"""  
        import gc  
        gc.collect()  # Force garbage collection  
        self.start_memory = self.process.memory_info().rss / 1024 / 1024  # MB  
        self.peak_memory = self.start_memory  

    def get_current_memory(self):  
        """Get current memory usage"""  
        current = self.process.memory_info().rss / 1024 / 1024  # MB  
        self.peak_memory = max(self.peak_memory, current)  
        return current  

    def get_memory_stats(self):  
        """Get memory statistics with guaranteed non-negative increase"""  
        current = self.get_current_memory()  
        memory_increase = max(0, current - self.start_memory)  # Ensure non-negative  
        return {  
            "start_memory_mb": round(self.start_memory, 2),  
            "current_memory_mb": round(current, 2),  
            "peak_memory_mb": round(self.peak_memory, 2),  
            "memory_increase_mb": round(memory_increase, 2)  
        }

class MetricsManager:  
    def __init__(self, save_file: str = "metrics_data.json"):  
        self.save_file = save_file  
        self.metrics: Dict[str, Dict[str, AlgorithmMetrics]] = {}  
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
              remaining_time: int, total_time: int, memory_stats: dict = None):  
        if self.current_run:  
            # Update basic metrics  
            self.current_run.nodes_explored = nodes_explored  
            self.current_run.path_length = path_length  
            self.current_run.time_taken = time_taken  
            self.current_run.remaining_time = remaining_time  
            self.current_run.total_time = total_time  

            # Update memory stats if provided  
            if memory_stats:  
                self.current_run.memory_start_mb = memory_stats["start_memory_mb"]  
                self.current_run.memory_peak_mb = memory_stats["peak_memory_mb"]  
                self.current_run.memory_increase_mb = memory_stats["memory_increase_mb"]  

            # Calculate derived metrics  
            if time_taken > 0:  
                self.current_run.steps_per_second = path_length / time_taken  
            if nodes_explored > 0:  
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

            # Update memory metrics  
            metrics.memory_start_mb = statistics.mean(run.memory_start_mb for run in successful_runs)  
            metrics.memory_peak_mb = max(run.memory_peak_mb for run in successful_runs)  
            metrics.memory_increase_mb = statistics.mean(run.memory_increase_mb for run in successful_runs)

    def save_metrics(self):  
        data = {}  
        for maze_type, maze_metrics in self.metrics.items():  
            data[maze_type] = {}  
            for algo, metrics in maze_metrics.items():  
                data[maze_type][algo] = {  
                    'total_runs': metrics.total_runs,  
                    'successful_runs': metrics.successful_runs,  
                    'avg_path_length': round(metrics.avg_path_length, 2),  
                    'avg_completion_time': round(metrics.avg_completion_time, 6),  
                    'avg_nodes_explored': round(metrics.avg_nodes_explored, 0),  
                    'avg_score': round(metrics.avg_score, 2),  
                    'avg_steps_per_second': round(metrics.avg_steps_per_second, 2),  
                    'avg_exploration_efficiency': round(metrics.avg_exploration_efficiency, 2),  
                    'min_path_length': metrics.min_path_length,  
                    'max_path_length': metrics.max_path_length,  
                    'fastest_completion': round(metrics.fastest_completion, 6),  
                    'slowest_completion': round(metrics.slowest_completion, 6),  
                    'best_score': round(metrics.best_score, 2),  
                    'memory_start_mb': round(metrics.memory_start_mb, 2),  
                    'memory_peak_mb': round(metrics.memory_peak_mb, 2),  
                    'memory_increase_mb': round(metrics.memory_increase_mb, 2)  
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
                            total_runs=metrics_data.get('total_runs', 0),  
                            successful_runs=metrics_data.get('successful_runs', 0),  
                            avg_path_length=metrics_data.get('avg_path_length', 0.0),  
                            avg_completion_time=metrics_data.get('avg_completion_time', 0.0),  
                            avg_nodes_explored=metrics_data.get('avg_nodes_explored', 0.0),  
                            avg_score=metrics_data.get('avg_score', 0.0),  
                            avg_steps_per_second=metrics_data.get('avg_steps_per_second', 0.0),  
                            avg_exploration_efficiency=metrics_data.get('avg_exploration_efficiency', 0.0),  
                            memory_start_mb=metrics_data.get('memory_start_mb', 0.0),  
                            memory_peak_mb=metrics_data.get('memory_peak_mb', 0.0),  
                            memory_increase_mb=metrics_data.get('memory_increase_mb', 0.0)  
                        )  
                        self.metrics[maze_type][algo] = metrics  
        except FileNotFoundError:  
            pass

    def get_algorithm_performance(self, algorithm: AlgorithmType, maze_type: TestScenario) -> Optional[AlgorithmMetrics]:
        """Get performance metrics for a specific algorithm and maze type"""
        maze_key = maze_type.name
        algo_key = algorithm.name
        return self.metrics.get(maze_key, {}).get(algo_key)

