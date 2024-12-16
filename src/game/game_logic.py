import pygame

from src.config.constants import GameState, TIME_LIMIT, FPS, COLORS

class GameLogic:
    """Handles game logic, scoring, and UI elements"""
    def __init__(self, map_size=(10, 10)):
        self.state = GameState.PLAYING
        self.time_remaining = TIME_LIMIT * FPS
        self.score = 0
        self.map_size = map_size
        self.font = pygame.font.Font(None, 36)
        self.moves_made = 0
        self.optimal_path_length = 13  # Matches Map.OPTIMAL_PATH_LENGTH

    def update(self):
        """Updates game state including time"""
        if self.state == GameState.PLAYING:
            self.time_remaining -= 1
            if self.time_remaining <= 0:
                self.state = GameState.LOSE

    def check_win_condition(self, robot_pos, goal_pos):
        """Checks if robot has reached the goal"""
        if robot_pos == goal_pos:
            self.state = GameState.WIN
            time_bonus = max(self.time_remaining // FPS, 0)
            efficiency_bonus = max(0, self.optimal_path_length - self.moves_made) * 10
            self.score += time_bonus + efficiency_bonus

    def reset(self):
        """Resets game state"""
        self.state = GameState.PLAYING
        self.time_remaining = TIME_LIMIT * FPS
        self.score = 0
        self.moves_made = 0

    def draw_ui(self, surface):
        """Draws UI elements including time, score and game state"""
        padding = 5
        
        # Draw time
        time_text = f"Time: {self.time_remaining // FPS}"
        color = COLORS['TIMER_WARNING'] if self.time_remaining < 10 * FPS else COLORS['BLACK']
        time_surface = self.font.render(time_text, True, color)
        pygame.draw.rect(surface, COLORS['WHITE'], 
                        (5, 5, time_surface.get_width() + 2*padding, 
                         time_surface.get_height() + 2*padding))
        surface.blit(time_surface, (10, 10))

        # Draw score and moves
        score_text = f"Score: {self.score} | Moves: {self.moves_made}"
        score_surface = self.font.render(score_text, True, COLORS['BLACK'])
        pygame.draw.rect(surface, COLORS['WHITE'],
                        (5, 45, score_surface.get_width() + 2*padding,
                         score_surface.get_height() + 2*padding))
        surface.blit(score_surface, (10, 50))

        # Draw game state
        if self.state != GameState.PLAYING:
            state_text = f"Game {self.state.value}! Press R to restart"
            state_surface = self.font.render(state_text, True, COLORS['BLACK'])
            x = surface.get_width() // 2 - state_surface.get_width() // 2
            y = surface.get_height() // 2 - state_surface.get_height() // 2
            pygame.draw.rect(surface, COLORS['WHITE'],
                           (x - padding, y - padding,
                            state_surface.get_width() + 2*padding,
                            state_surface.get_height() + 2*padding))
            surface.blit(state_surface, (x, y))

    def calculate_reward(self, old_pos, new_pos, goal_pos):
        """Calculates reward for an action"""
        self.moves_made += 1
        
        if new_pos == goal_pos:
            efficiency_bonus = max(0, self.optimal_path_length - self.moves_made)
            return 100 + efficiency_bonus * 10  # Bonus for efficient solutions

        old_distance = abs(old_pos[0] - goal_pos[0]) + abs(old_pos[1] - goal_pos[1])
        new_distance = abs(new_pos[0] - goal_pos[0]) + abs(new_pos[1] - goal_pos[1])

        if new_distance < old_distance:
            return 1  # Small positive reward for moving closer
        elif new_distance > old_distance:
            return -1  # Small negative reward for moving away

        return -0.1  # Minimal negative reward for time/energy usage