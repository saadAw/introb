from datetime import datetime
import pygame
from typing import List, Dict, Any, Callable
from src.config.constants import COLORS, FPS, GameState, UI_PANEL_WIDTH, PADDING, TIME_LIMIT
from src.config.types import AlgorithmType

class UISection:
    """Base class for UI sections"""
    def __init__(self, name: str, font: pygame.font.Font, padding: int):
        self.name = name
        self.font = font
        self.padding = padding

    def render(self, surface: pygame.Surface, current_y: int) -> int:
        """Render method to be implemented by child classes"""
        raise NotImplementedError("Subclasses must implement render method")

class AlgorithmSection(UISection):
    """Section for displaying available algorithms"""
    def __init__(self, name: str, font: pygame.font.Font, padding: int, 
                 algorithms: List[tuple], current_algorithm: AlgorithmType, 
                 used_algorithms: set):
        super().__init__(name, font, padding)
        self.algorithms = algorithms
        self.current_algorithm = current_algorithm
        self.used_algorithms = used_algorithms

    def render(self, surface: pygame.Surface, current_y: int) -> int:
        """Render algorithm section"""
        # Draw section header
        current_y = self._draw_section_header(surface, current_y)

        for algo, text, color in self.algorithms:
            # Draw color indicator
            pygame.draw.circle(surface, color, (self.padding + 5, current_y + 7), 5)

            # Determine text styling
            if algo == self.current_algorithm:
                text_color = COLORS['UI_HEADER']
                text = f"> {text}"
            elif algo in self.used_algorithms:
                text_color = COLORS['UI_TEXT']
            else:
                text_color = COLORS['UI_TEXT']

            control_surf = pygame.font.Font(None, 24).render(text, True, text_color)
            surface.blit(control_surf, (self.padding + 15, current_y))
            current_y += control_surf.get_height() + 5

        return current_y + self.padding

    def _draw_section_header(self, surface: pygame.Surface, y: int) -> int:
        """Draw section header with lines"""
        pygame.draw.line(surface, COLORS['GRID'], 
                        (self.padding, y), 
                        (UI_PANEL_WIDTH - self.padding, y), 1)
        y += 5
        header_surf = self.font.render(self.name, True, COLORS['UI_HEADER'])
        surface.blit(header_surf, (self.padding, y))
        y += header_surf.get_height() + 5
        pygame.draw.line(surface, COLORS['GRID'], 
                        (self.padding, y), 
                        (UI_PANEL_WIDTH - self.padding, y), 1)
        return y + self.padding

class ControlsSection(UISection):
    """Section for displaying game controls"""
    def __init__(self, name: str, font: pygame.font.Font, padding: int, controls: List[str]):
        super().__init__(name, font, padding)
        self.controls = controls

    def render(self, surface: pygame.Surface, current_y: int) -> int:
        """Render controls section"""
        current_y = self._draw_section_header(surface, current_y)

        for control in self.controls:
            control_surf = self.font.render(control, True, COLORS['UI_TEXT'])
            surface.blit(control_surf, (self.padding, current_y))
            current_y += control_surf.get_height() + 5

        return current_y

    def _draw_section_header(self, surface: pygame.Surface, y: int) -> int:
        """Draw section header with lines"""
        pygame.draw.line(surface, COLORS['GRID'], 
                        (self.padding, y), 
                        (UI_PANEL_WIDTH - self.padding, y), 1)
        y += 5
        header_surf = self.font.render(self.name, True, COLORS['UI_HEADER'])
        surface.blit(header_surf, (self.padding, y))
        y += header_surf.get_height() + 5
        pygame.draw.line(surface, COLORS['GRID'], 
                        (self.padding, y), 
                        (UI_PANEL_WIDTH - self.padding, y), 1)
        return y + self.padding

class UIManager:
    """Handles all UI rendering and management with modular sections"""
    def __init__(self):
        self.fonts = {
            'large': pygame.font.Font(None, 40),
            'medium': pygame.font.Font(None, 32),
            'small': pygame.font.Font(None, 24)
        }
        self.padding = PADDING
        self.sections: List[UISection] = []

    def add_section(self, section: UISection):
        """Add a new UI section"""
        self.sections.append(section)

    def clear_sections(self):
        """Clear all existing sections"""
        self.sections.clear()

    def draw_game_ui(self, surface, game_logic, current_algorithm):
            """Draw game UI with comprehensive information"""
            try:
                y_offset = PADDING

                # Title Section
                title_text = self.fonts['large'].render("Robot Navigation", True, COLORS['UI_HEADER'])
                surface.blit(title_text, (PADDING, y_offset))
                y_offset += title_text.get_height() + PADDING

                # Selection Guides - Only shown in WAITING state
                if game_logic.state_manager.state == GameState.WAITING:
                    # Maze Selection Guide
                    maze_guide_text = self.fonts['medium'].render("Select Maze:", True, COLORS['UI_HEADER'])
                    surface.blit(maze_guide_text, (PADDING, y_offset))
                    y_offset += maze_guide_text.get_height() + 10

                    maze_keys = [
                        "F1: Diagonal Maze (variations)",
                        "F2: Snake Maze (variations)",
                        "F3: Open Maze (variations)",
                        "F4: Bottleneck Maze (variations)"
                    ]
                    for key_text in maze_keys:
                        key_render = self.fonts['small'].render(key_text, True, COLORS['UI_TEXT'])
                        surface.blit(key_render, (PADDING, y_offset))
                        y_offset += key_render.get_height() + 5

                    y_offset += PADDING

                    # Algorithm Selection Guide
                    guide_text = self.fonts['medium'].render("Select Algorithm:", True, COLORS['UI_HEADER'])
                    surface.blit(guide_text, (PADDING, y_offset))
                    y_offset += guide_text.get_height() + 10

                    algo_keys = [
                        "1: Manual",
                        "2: A*",
                        "3: Dijkstra",
                        "4: GBFS",
                        "5: BFS",
                        "6: Q-Learning",
                        "7: SARSA"
                    ]
                    for key_text in algo_keys:
                        key_render = self.fonts['small'].render(key_text, True, COLORS['UI_TEXT'])
                        surface.blit(key_render, (PADDING, y_offset))
                        y_offset += key_render.get_height() + 5

                    y_offset += PADDING

                # Maze Type Section - Always shown
                maze_title = self.fonts['medium'].render("Maze Type:", True, COLORS['UI_HEADER'])
                surface.blit(maze_title, (PADDING, y_offset))
                y_offset += maze_title.get_height() + 5

                # Display current maze type and variation
                maze_text = self.fonts['small'].render(
                    f"{game_logic.current_maze.name} Maze",
                    True,
                    COLORS['UI_TEXT']
                )
                surface.blit(maze_text, (PADDING, y_offset))
                y_offset += maze_text.get_height() + PADDING

                # Algorithm Section - Always shown
                algo_title = self.fonts['medium'].render("Algorithm:", True, COLORS['UI_HEADER'])
                surface.blit(algo_title, (PADDING, y_offset))
                y_offset += algo_title.get_height() + 5

                algo_name = self.fonts['small'].render(
                    current_algorithm.name if current_algorithm else "Not Selected",
                    True,
                    COLORS['PATH_ASTAR']
                )
                surface.blit(algo_name, (PADDING, y_offset))
                y_offset += algo_name.get_height() + PADDING

                # Game State Section - Always shown
                state_title = self.fonts['medium'].render("Game State:", True, COLORS['UI_HEADER'])
                surface.blit(state_title, (PADDING, y_offset))
                y_offset += state_title.get_height() + 5

                state_text = self.fonts['small'].render(
                    game_logic.state_manager.state.name,
                    True,
                    {
                        GameState.WAITING: COLORS['PATH_MANUAL'],
                        GameState.PLAYING: COLORS['GREEN'],
                        GameState.WIN: COLORS['PATH_DQN'],
                        GameState.LOSE: COLORS['RED']
                    }.get(game_logic.state_manager.state, COLORS['UI_TEXT'])
                )
                surface.blit(state_text, (PADDING, y_offset))
                y_offset += state_text.get_height() + PADDING

                # Score Section - Always shown
                score_title = self.fonts['medium'].render("Score:", True, COLORS['UI_HEADER'])  
                surface.blit(score_title, (PADDING, y_offset))  
                y_offset += score_title.get_height() + 5  

                if game_logic.state_manager.state == GameState.PLAYING:  
                    live_score = game_logic.get_live_score()  
                    score_text = self.fonts['small'].render(  
                        f"Current: {live_score:.2f}",  
                        True,  
                        COLORS['GREEN']  
                    )  
                    surface.blit(score_text, (PADDING, y_offset))  
                    y_offset += score_text.get_height() + 15  

                    if game_logic.start_time:  
                        nodes_text = self.fonts['small'].render(  
                            f"Nodes: {game_logic.total_nodes_explored}",  
                            True,  
                            COLORS['UI_TEXT']  
                        )  
                        surface.blit(nodes_text, (PADDING, y_offset))  
                        y_offset += nodes_text.get_height() + 10 

                        path_text = self.fonts['small'].render(  
                            f"Path: {game_logic.score_manager.moves_made}",  
                            True,  
                            COLORS['UI_TEXT']  
                        )  
                        surface.blit(path_text, (PADDING, y_offset))  
                        y_offset += path_text.get_height() + 15 

                elif game_logic.state_manager.state in [GameState.WIN, GameState.LOSE]:  
                    score_text = self.fonts['small'].render(  
                        f"Final: {game_logic.score:.2f}",  
                        True,  
                        COLORS['RED'] if game_logic.state_manager.state == GameState.LOSE else COLORS['PATH_DQN']  
                    )  
                    surface.blit(score_text, (PADDING, y_offset))  
                    y_offset += score_text.get_height() + PADDING  
                else:  
                    score_text = self.fonts['small'].render(  
                        "0.00",  
                        True,  
                        COLORS['UI_TEXT']  
                    )  
                    surface.blit(score_text, (PADDING, y_offset))  
                    y_offset += score_text.get_height() + PADDING

                # Time Section - Always shown
                time_title = self.fonts['medium'].render("Time:", True, COLORS['UI_HEADER'])
                surface.blit(time_title, (PADDING, y_offset))
                y_offset += time_title.get_height() + 5

                time_remaining = game_logic.time_manager.remaining_seconds
                time_color = (
                    COLORS['RED'] if time_remaining < 30 else
                    COLORS['TIMER_WARNING'] if time_remaining < 60 else
                    COLORS['UI_TEXT']
                )

                time_text = self.fonts['small'].render(
                    f"{time_remaining} seconds",
                    True,
                    time_color
                )
                surface.blit(time_text, (PADDING, y_offset))
                y_offset += time_text.get_height() + PADDING

                # Game Over Section - Only shown in WIN/LOSE states
                if game_logic.state_manager.state in [GameState.WIN, GameState.LOSE]:
                    game_over_text = self.fonts['medium'].render(
                        "Game Over!",
                        True,
                        COLORS['RED']
                    )
                    surface.blit(game_over_text, (PADDING, y_offset))
                    y_offset += game_over_text.get_height() + 10

                    restart_text = self.fonts['small'].render(
                        "Press 'R' to Restart",
                        True,
                        COLORS['UI_TEXT']
                    )
                    surface.blit(restart_text, (PADDING, y_offset))

            except Exception as e:
                print(f"Error in draw_game_ui: {e}")