# src/game/metrics_manager.py

from dataclasses import dataclass
from typing import Dict, List, Optional
from time import time

import pygame
from src.config.constants import COLORS
from src.config.types import AlgorithmType

@dataclass
class AlgorithmMetrics:
    path_length: int = 0
    execution_time: float = 0.0
    nodes_explored: int = 0
    path_cost: float = 0.0
    success_rate: float = 0.0
    memory_usage: int = 0

class MetricsManager:
    def __init__(self):
        self.metrics: Dict[AlgorithmType, List[AlgorithmMetrics]] = {
            algo_type: [] for algo_type in AlgorithmType
        }
        self.current_run: Dict[AlgorithmType, AlgorithmMetrics] = {}

    def start_run(self, algorithm: AlgorithmType):
        self.current_run[algorithm] = AlgorithmMetrics()
        self.current_run[algorithm].execution_time = time()

    def end_run(self, algorithm: AlgorithmType, success: bool):
        if algorithm in self.current_run:
            metrics = self.current_run[algorithm]
            metrics.execution_time = time() - metrics.execution_time
            metrics.success_rate = 1.0 if success else 0.0
            self.metrics[algorithm].append(metrics)

    def get_average_metrics(self, algorithm: AlgorithmType) -> Optional[AlgorithmMetrics]:
        if not self.metrics[algorithm]:
            return None

        runs = self.metrics[algorithm]
        return AlgorithmMetrics(
            path_length=sum(r.path_length for r in runs) / len(runs),
            execution_time=sum(r.execution_time for r in runs) / len(runs),
            nodes_explored=sum(r.nodes_explored for r in runs) / len(runs),
            path_cost=sum(r.path_cost for r in runs) / len(runs),
            success_rate=sum(r.success_rate for r in runs) / len(runs),
            memory_usage=sum(r.memory_usage for r in runs) / len(runs)
        )
    
class MetricsDetailWindow:  
    def __init__(self):  
        self.font_large = pygame.font.Font(None, 36)  
        self.font = pygame.font.Font(None, 28)  
        self.font_small = pygame.font.Font(None, 20)  
        self.padding = 20  
        self.window_size = (400, 300)  
        self.visible = False  
        self.current_algorithm = None  
        self.metrics = None  
        self.main_window_size = None  

    def show(self, algorithm_type, metrics, main_window_size):  
        self.visible = True  
        self.current_algorithm = algorithm_type  
        self.metrics = metrics  
        self.main_window_size = main_window_size  

        # Create new window  
        self.window = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)  
        pygame.display.set_caption(f"Metrics Details - {algorithm_type.value}")  

    def hide(self):  
        self.visible = False  
        if self.main_window_size:  
            pygame.display.set_mode(self.main_window_size)  # Reset to main window size  

    def draw(self):  
        if not self.visible:  
            return  

        self.window.fill(COLORS['UI_BACKGROUND'])  
        current_y = self.padding  

        # Draw title  
        title_surf = self.font_large.render(  
            f"Metrics for {self.current_algorithm.value}",   
            True,   
            COLORS['UI_HEADER']  
        )  
        self.window.blit(title_surf, (self.padding, current_y))  
        current_y += title_surf.get_height() + self.padding  

        # Draw all metrics  
        metrics_items = [  
            ("Execution Time", f"{self.metrics.execution_time:.3f}s"),  
            ("Path Length", str(self.metrics.path_length)),  
            ("Nodes Explored", str(self.metrics.nodes_explored)),  
            ("Success Rate", f"{self.metrics.success_rate:.1%}"),  
            ("Memory Usage", f"{self.metrics.memory_usage:.2f}MB"),  
            ("Path Cost", str(self.metrics.path_cost))  
        ]  

        for label, value in metrics_items:  
            label_surf = self.font.render(label + ":", True, COLORS['UI_TEXT'])  
            value_surf = self.font.render(value, True, COLORS['UI_HEADER'])  

            self.window.blit(label_surf, (self.padding, current_y))  
            self.window.blit(value_surf, (200, current_y))  
            current_y += label_surf.get_height() + 10  

        # Draw close button  
        close_rect = pygame.Rect(  
            self.window_size[0] - 100 - self.padding,  
            self.window_size[1] - 40 - self.padding,  
            100,  
            40  
        )  
        pygame.draw.rect(self.window, COLORS['UI_TEXT'], close_rect)  
        close_text = self.font_small.render("Close", True, COLORS['UI_BACKGROUND'])  
        text_rect = close_text.get_rect(center=close_rect.center)  
        self.window.blit(close_text, text_rect)  

        pygame.display.flip()  
        return close_rect