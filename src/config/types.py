from enum import Enum, auto

class AlgorithmType(Enum):
    """Enum for different pathfinding algorithms"""
    MANUAL = "Manual Control"
    ASTAR = "A* Algorithm"
    DIJKSTRA = "Dijkstra Algorithm"
    GBFS = "Greedy Best First"
    BFS = "Breadth First"
    QL = "Q-Learning"
    DQN = "Deep Q-Learning"
    SARSA = "SARSA"
    
class TestScenario(Enum):
    DIAGONAL = auto()
    SNAKE = auto()
    OPEN = auto()
    BOTTLENECK = auto()
