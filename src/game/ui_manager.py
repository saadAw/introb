import pygame
from src.game import metrics_manager
from src.config.constants import COLORS, FPS, GameState, UI_PANEL_WIDTH, PADDING
from src.config.types import AlgorithmType

class UIManager:  
    def __init__(self):  
        # Smaller font sizes
        self.font_large = pygame.font.Font(None, 36)  # Reduced from 40
        self.font = pygame.font.Font(None, 28)       # Reduced from 32
        self.font_small = pygame.font.Font(None, 20) # Reduced from 24
        self.metric_click_areas = []
        self.padding = PADDING

    def _draw_section_header(self, text, surface, y):
        """Helper to draw section headers with consistent styling"""
        pygame.draw.line(surface, COLORS['GRID'], 
                        (self.padding, y), 
                        (UI_PANEL_WIDTH - self.padding, y), 1)
        y += 5
        header_surf = self.font.render(text, True, COLORS['UI_HEADER'])
        surface.blit(header_surf, (self.padding, y))
        y += header_surf.get_height() + 5
        pygame.draw.line(surface, COLORS['GRID'], 
                        (self.padding, y), 
                        (UI_PANEL_WIDTH - self.padding, y), 1)
        return y + self.padding

    def _draw_game_state(self, surface, message):  
        """Draw game state message in the center of the game area"""  
        state_surf = self.font_large.render(message, True, COLORS['BLACK'])  

        # Calculate position to center on game area, not including UI panel  
        game_area_center_x = UI_PANEL_WIDTH + (surface.get_width() - UI_PANEL_WIDTH) // 2  
        game_area_center_y = surface.get_height() // 2  

        # Create background rectangle  
        rect_width = state_surf.get_width() + self.padding * 2  
        rect_height = state_surf.get_height() + self.padding * 2  
        rect = pygame.Rect(  
            game_area_center_x - rect_width // 2,  
            game_area_center_y - rect_height // 2,  
            rect_width,  
            rect_height  
        )  

        # Draw background and text  
        pygame.draw.rect(surface, COLORS['WHITE'], rect)  
        surface.blit(state_surf, (  
            game_area_center_x - state_surf.get_width() // 2,  
            game_area_center_y - state_surf.get_height() // 2  
        ))

    def draw_metrics_comparison(self, surface, metrics_manager):
        """Draw simplified metrics comparison with clickable rows"""
        current_y = surface.get_height() - 150  # Reduced height since we show less info

        # Draw section header
        current_y = self._draw_section_header("Algorithm Metrics (Click for details)", surface, current_y)

        # Simplified table layout
        headers = ["Algorithm", "Time(s)"]
        col_width = (UI_PANEL_WIDTH - self.padding * 2) // len(headers)

        # Draw headers
        for i, header in enumerate(headers):
            x = self.padding + i * col_width
            header_surf = self.font_small.render(header, True, COLORS['UI_HEADER'])
            surface.blit(header_surf, (x, current_y))

        current_y += self.font_small.get_height() + 2

        # Store clickable areas for each algorithm
        self.metric_click_areas = []  # Add this as instance variable in __init__

        # Draw metrics rows
        for algo_type in AlgorithmType:
            metrics = metrics_manager.get_average_metrics(algo_type)
            if metrics is None:
                continue

            # Create clickable area for this row
            row_rect = pygame.Rect(
                self.padding, 
                current_y, 
                UI_PANEL_WIDTH - 2 * self.padding,
                self.font_small.get_height()
            )
            self.metric_click_areas.append((row_rect, algo_type))

            # Highlight row if mouse is hovering over it
            mouse_pos = pygame.mouse.get_pos()
            if row_rect.collidepoint(mouse_pos):
                pygame.draw.rect(surface, COLORS['UI_HIGHLIGHT'], row_rect, 1)

            # Draw color indicator
            algo_color = COLORS[f'PATH_{algo_type.name}']
            pygame.draw.circle(surface, algo_color, 
                            (self.padding + 3, current_y + 5), 2)

            # Draw simplified values
            values = [
                algo_type.value[:8],  # Algorithm name
                f"{metrics.execution_time:.2f}"  # Time only
            ]

            for i, value in enumerate(values):
                x = self.padding + i * col_width
                if i == 0:  # Add offset for first column to account for color indicator
                    x += 8
                value_surf = self.font_small.render(value, True, COLORS['UI_TEXT'])
                surface.blit(value_surf, (x, current_y))

            current_y += self.font_small.get_height() + 2

    def draw_game_ui(self, surface, game_logic, current_algorithm, metrics_manager=None):    
        """Draw all UI elements in the left panel"""    
        # Draw UI panel background    
        panel_rect = pygame.Rect(0, 0, UI_PANEL_WIDTH, surface.get_height())    
        pygame.draw.rect(surface, COLORS['UI_BACKGROUND'], panel_rect)    
        pygame.draw.line(surface, COLORS['GRID'],     
                        (UI_PANEL_WIDTH, 0),     
                        (UI_PANEL_WIDTH, surface.get_height()), 2)    

        current_y = self.padding    

        # Game title with reduced padding
        title_surf = self.font_large.render("Robot Navigation", True, COLORS['UI_HEADER'])    
        surface.blit(title_surf, (self.padding, current_y))    
        current_y += title_surf.get_height() + self.padding // 2    

        # Current mode with reduced padding   
        current_y = self._draw_section_header("Current Mode", surface, current_y)    
        mode_surf = self.font.render(current_algorithm.value, True, COLORS['UI_TEXT'])    
        surface.blit(mode_surf, (self.padding, current_y))    
        current_y += mode_surf.get_height() + self.padding    

        # Statistics section with reduced spacing
        if game_logic.state != GameState.WAITING:    
            current_y = self._draw_section_header("Statistics", surface, current_y)    

            stats = [
                (f"Time: {game_logic.time_remaining // FPS}s", 
                 COLORS['TIMER_WARNING'] if game_logic.time_remaining < 10 * FPS else COLORS['UI_TEXT']),
                (f"Score: {game_logic.score}", COLORS['UI_TEXT']),
                (f"Moves: {game_logic.moves_made}", COLORS['UI_TEXT'])
            ]

            for text, color in stats:
                stat_surf = self.font_small.render(text, True, color)
                surface.blit(stat_surf, (self.padding, current_y))
                current_y += stat_surf.get_height() + 3  # Reduced spacing

        # Algorithms section with reduced spacing
        current_y = self._draw_section_header("Available Algorithms", surface, current_y)      
        algorithm_controls = [      
            (AlgorithmType.MANUAL, "1: Manual Mode", COLORS['PATH_MANUAL']),      
            (AlgorithmType.ASTAR, "2: A* Algorithm", COLORS['PATH_ASTAR']),      
            (AlgorithmType.DIJKSTRA, "3: Dijkstra Algorithm", COLORS['PATH_DIJKSTRA']),
            (AlgorithmType.GBFS, "4: Greedy Best-First Search", COLORS['PATH_GBFS']),
            (AlgorithmType.BFS, "5: Breadth-First Search", COLORS['PATH_BFS']),      
            (AlgorithmType.QL, "6: Q-Learning", COLORS['PATH_QL']),      
            (AlgorithmType.DQN, "7: SARSA", COLORS['PATH_SARSA'])      
        ]     

        for algo, text, color in algorithm_controls:      
            pygame.draw.circle(surface, color, (self.padding + 5, current_y + 5), 3)  # Smaller circles

            if algo == current_algorithm:      
                text_color = COLORS['UI_HEADER']  
                text = f"> {text}"
            elif algo in game_logic.used_algorithms:      
                text_color = COLORS['UI_TEXT']      
            else:      
                text_color = COLORS['UI_TEXT']      

            control_surf = self.font_small.render(text, True, text_color)      
            surface.blit(control_surf, (self.padding + 12, current_y))  # Reduced indent
            current_y += control_surf.get_height() + 2  # Minimal spacing

        # Controls section with minimal spacing
        current_y = self._draw_section_header("Controls", surface, current_y)  
        controls = ["Arrow Keys: Move", "R: Reset Game", "ESC: Quit"]  

        for control in controls:  
            control_surf = self.font_small.render(control, True, COLORS['UI_TEXT'])  
            surface.blit(control_surf, (self.padding, current_y))  
            current_y += control_surf.get_height() + 2  # Minimal spacing

        # Draw game state message    
        if game_logic.state == GameState.WAITING:    
            self._draw_game_state(surface, "Select an algorithm to start!")    
        elif game_logic.state != GameState.PLAYING:    
            self._draw_game_state(surface, f"Game {game_logic.state.value}! Press R to restart")

        # Add metrics comparison if game is not in WAITING state  
        if game_logic.state != GameState.WAITING and metrics_manager:
            self.draw_metrics_comparison(surface, metrics_manager)