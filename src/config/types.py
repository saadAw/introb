from enum import Enum

class AlgorithmType(Enum):
    """Enum for different pathfinding algorithms"""
    MANUAL = "Manual Control"
    ASTAR = "A* Algorithm"
    DIJKSTRA = "Dijkstra Algorithm"
    QL = "Q-Learning"
    DQN = "Deep Q-Learning"