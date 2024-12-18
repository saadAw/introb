# -*- coding: utf-8 -*-
import numpy as np
import random
import pygame
from os.path import exists
from sys import exit


class Maze:
    """
    Generate a maze and then optionally reshape it into different patterns (snake, open, bottleneck).
    Maze types:
        - normal: default generation
        - snake: one long winding path
        - open: mostly open space
        - bottleneck: two open areas separated by a narrow passage
    """

    def __init__(self, size_x, size_y, maze_type='normal'):
        self.maze_type = maze_type
        self.screen = None
        self.screen_size = None
        self.screen_block_size = None
        self.screen_block_offset = None
        self.prev_update = 0
        self.clock = pygame.time.Clock()
        self.slow_mode = False
        self.running = True
        self.path_density = 0.8  # Increased default path density

        # Initialize walls array
        self.wall_size = np.array([size_y, size_x], dtype=np.int16)
        self.walls = np.ones((self.wall_size[0] + 2, self.wall_size[1] + 2, 3), dtype=np.byte)
        self.walls[:, 0, 0] = -1
        self.walls[:, self.wall_size[1] + 1, 0] = -1
        self.walls[0, :, 0] = -1
        self.walls[self.wall_size[0] + 1, :, 0] = -1

        # Initialize blocks array
        self.block_size = np.array([size_y * 2 + 1, size_x * 2 + 1], dtype=np.int16)
        self.blocks = np.ones((self.block_size[0], self.block_size[1]), dtype=np.byte)

    def set_path_density(self, density):
        self.path_density = max(0.0, min(1.0, density))

    def should_remove_wall(self, cell, direction):
        """Enhanced wall removal logic for more paths"""
        y, x = cell
        if direction == 1:  # down wall
            next_cell = (y + 1, x)
        else:  # right wall
            next_cell = (y, x + 1)

        current_connections = self.count_connections(cell)
        next_connections = self.count_connections(next_cell)

        # Allow more connections while preventing excessive openness
        if current_connections >= 5 or next_connections >= 5:
            return False

        # Higher base probability for wall removal
        base_prob = min(1.0, self.path_density * 2.0)

        # More permissive probability adjustments
        if current_connections + next_connections >= 6:
            return random.random() < 0.4
        elif current_connections + next_connections >= 4:
            return random.random() < base_prob * 0.9
        else:
            return random.random() < base_prob

    def count_connections(self, cell):
        """Count how many connections a cell has"""
        y, x = cell
        count = 0
        # Check down wall
        if y < self.wall_size[0] and self.walls[y, x, 1] == 0:
            count += 1
        # Check up wall
        if y > 1 and self.walls[y-1, x, 1] == 0:
            count += 1
        # Check right wall
        if x < self.wall_size[1] and self.walls[y, x, 2] == 0:
            count += 1
        # Check left wall
        if x > 1 and self.walls[y, x-1, 2] == 0:
            count += 1
        return count

    def gen_maze_walls(self, corridor_len=999):
        cell = np.array([random.randrange(2, self.wall_size[0]),
                         random.randrange(2, self.wall_size[1])], dtype=np.int16)
        self.walls[cell[0], cell[1], 0] = 0

        directions = [
            np.array([-1, 0], dtype=np.int16),  # up
            np.array([1, 0], dtype=np.int16),   # down
            np.array([0, -1], dtype=np.int16),  # left
            np.array([0, 1], dtype=np.int16)    # right
        ]

        need_cell_range = False
        round_nr = 0
        corridor_start = 0
        if corridor_len <= 4:
            corridor_len = 5

        while np.size(cell) > 0 and self.running:
            round_nr += 1
            cell_neighbors = np.vstack([cell + d for d in directions])

            valid_neighbors = cell_neighbors[
                (self.walls[cell_neighbors[:, 0], cell_neighbors[:, 1], 0] >= 0) &
                (self.walls[cell_neighbors[:, 0], cell_neighbors[:, 1], 0] <= 1)
            ]

            if np.size(valid_neighbors) > 0:
                # Safe multiple path creation
                if len(valid_neighbors) > 1 and random.random() < self.path_density:
                    # Randomly select how many neighbors to process (up to 2)
                    num_neighbors = min(2, len(valid_neighbors))
                    neighbor_indices = list(range(len(valid_neighbors)))
                    random.shuffle(neighbor_indices)

                    for idx in neighbor_indices[:num_neighbors]:
                        neighbor = valid_neighbors[idx]
                        if self.walls[neighbor[0], neighbor[1], 0] == 1:
                            self.process_neighbor(cell, neighbor)

                    # Use the last processed neighbor for continuation
                    neighbor = valid_neighbors[neighbor_indices[0]]
                else:
                    # Regular single neighbor processing
                    neighbor_idx = random.randrange(0, len(valid_neighbors))
                    neighbor = valid_neighbors[neighbor_idx]
                    self.process_neighbor(cell, neighbor)

                if round_nr - corridor_start < corridor_len:
                    cell = np.array([neighbor[0], neighbor[1]], dtype=np.int16)
                else:
                    need_cell_range = True
            else:
                need_cell_range = True

            if need_cell_range:
                cell = np.transpose(np.nonzero(self.walls[1:-1, 1:-1, 0] == 0)) + 1
                if cell.size == 0:
                    break
                valid_neighbor_exists = np.array([
                    self.walls[cell[:, 0] - 1, cell[:, 1], 0],
                    self.walls[cell[:, 0] + 1, cell[:, 1], 0],
                    self.walls[cell[:, 0], cell[:, 1] - 1, 0],
                    self.walls[cell[:, 0], cell[:, 1] + 1, 0]
                ]).max(axis=0)
                cell_no_neighbors = cell[valid_neighbor_exists != 1]
                self.walls[cell_no_neighbors[:, 0], cell_no_neighbors[:, 1], 0] = -1
                corridor_start = round_nr
                need_cell_range = False

        if self.running:
            return self.walls[1:-1, 1:-1, 1:3]

    def gen_maze_2D(self, corridor_len=999):
        self.gen_maze_walls(corridor_len)
        if not self.running:
            return None

        self.blocks[1:-1:2, 1:-1:2] = 0
        self.blocks[1:-1:2, 2:-2:2] = self.walls[1:-1, 1:-2, 2]
        self.blocks[2:-2:2, 1:-1:2] = self.walls[1:-2, 1:-1, 1]

        # Post-process the maze depending on the type
        if self.maze_type == 'snake':
            self.post_process_snake_maze()
        elif self.maze_type == 'open':
            self.post_process_open_maze()
        elif self.maze_type == 'bottleneck':
            self.post_process_bottleneck_maze()

        # After post-processing, redraw the final maze layout:
        if self.screen is not None and self.running:
            self.redraw_final_maze()

        maze_list = self.blocks.tolist()
        print("saved maze_data")
        with open('experimental/mazes/maze_data.py', 'w') as f:
            f.write(f"LAYOUT = {maze_list}\n")

        return self.blocks

    def process_neighbor(self, cell, neighbor):
        """Process a single neighbor cell, potentially removing walls"""
        if np.size(cell) > 2:
            cell = cell[np.sum(abs(cell - neighbor), axis=1) == 1]
            if len(cell) > 0:
                cell = cell[random.randrange(0, np.shape(cell)[0]), :]
            else:
                return

        # Check if wall should be removed
        wall_dir = 1 + abs(neighbor[1] - cell[1])  # 1 for down, 2 for right
        if self.should_remove_wall((min(cell[0], neighbor[0]), min(cell[1], neighbor[1])), wall_dir):
            self.walls[min(cell[0], neighbor[0]), min(cell[1], neighbor[1]), wall_dir] = 0

        self.walls[neighbor[0], neighbor[1], 0] = 0

        if self.screen is not None:
            self.draw_cell(cell, neighbor)

    def draw_cell(self, cell, neighbor):
        min_coord = (np.flip(np.minimum(cell, neighbor) * 2 - 1) * self.screen_block_size + self.screen_block_offset).astype(np.int16)
        max_coord = (np.flip(np.maximum(cell, neighbor) * 2 - 1) * self.screen_block_size + int(self.screen_block_size) + self.screen_block_offset).astype(np.int16)
        pygame.draw.rect(self.screen, (200, 200, 200), (min_coord, max_coord - min_coord))

        if self.slow_mode or pygame.time.get_ticks() > self.prev_update + 50:
            self.prev_update = pygame.time.get_ticks()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    if event.key == pygame.K_f:
                        self.toggle_fullscreen()
                    if event.key == pygame.K_m:
                        self.toggle_slow_mode()

        if self.slow_mode:
            pygame.time.wait(3)

    def redraw_final_maze(self):
        """Redraw the entire maze after post-processing."""
        if self.screen is None:
            return
        self.screen.fill((0, 0, 0))
        h, w = self.blocks.shape
        for i in range(h):
            for j in range(w):
                color = (200, 200, 200) if self.blocks[i, j] == 0 else (0, 0, 0)
                top_left = (j * self.screen_block_size + self.screen_block_offset[0],
                            i * self.screen_block_size + self.screen_block_offset[1])
                pygame.draw.rect(self.screen, color, (top_left, (self.screen_block_size, self.screen_block_size)))
        pygame.display.flip()

    def toggle_slow_mode(self):
        self.slow_mode = not self.slow_mode

    def toggle_fullscreen(self):
        screen_copy = self.screen.copy()
        pygame.display.toggle_fullscreen()
        self.screen.blit(screen_copy, (0, 0))
        pygame.display.flip()

    def save_image(self):
        for file_nr in range(1, 1000):
            file_name = 'Maze_' + ('00' + str(file_nr))[-3:] + '.png'
            if not exists(file_name):
                pygame.image.save(self.screen, file_name)
                break

    def count_removed_walls(self):
        down_walls = np.sum(self.walls[1:-1, 1:-1, 1] == 0)
        right_walls = np.sum(self.walls[1:-1, 1:-1, 2] == 0)
        total_cells = (self.wall_size[0]) * (self.wall_size[1])

        print(f"\nMaze Statistics:")
        print(f"Total cells: {total_cells}")
        print(f"Removed down walls: {down_walls}")
        print(f"Removed right walls: {right_walls}")
        print(f"Total removed walls: {down_walls + right_walls}")
        print(f"Average paths per cell: {(down_walls + right_walls) / total_cells:.2f}")

    # --- Post-processing methods for different maze types ---

    def post_process_snake_maze(self):
        self.blocks[:, :] = 1
        h, w = self.blocks.shape
        
        # Main spine carving:
        row = 1
        direction = 1  # 1 = right, -1 = left
        while row < h - 1:
            # Decide how far we carve in this row
            # Randomize the horizontal carve length a bit
            carve_length = w - 2
            start_col = 1 if direction == 1 else w-2
            end_col = start_col + (carve_length * direction)

            # Carve the main row
            col_range = range(start_col, end_col+direction, direction)
            for col in col_range:
                self.blocks[row, col] = 0

            # Random chance to only move down by one row or two rows
            step_down = 2 if random.random() > 0.3 else 1
            if row + step_down < h - 1:
                # Create a vertical connection
                connect_col = start_col if direction == 1 else end_col
                # Carve down vertically
                for dr in range(1, step_down+1):
                    self.blocks[row+dr, connect_col] = 0
                row += step_down
            else:
                break

            # Flip direction for next segment
            direction = -direction
        
        # Now add some random loops and branches:
        # Choose random spots along the carved path and carve small side paths
        # We know that carved cells have value 0, so collect all such coordinates.
        carved_cells = [(r,c) for r in range(h) for c in range(w) if self.blocks[r,c] == 0]

        # Attempt to create a few loops
        for _ in range(int(len(carved_cells)*0.05)):  # 5% of carved cells attempt a loop
            r, c = random.choice(carved_cells)
            # Try carving a small loop of length 3-6 cells
            loop_length = random.randint(3,6)
            directions = [(0,1),(0,-1),(1,0),(-1,0)]
            random.shuffle(directions)
            # Try a random direction to start carving
            for dr, dc in directions:
                rr, cc = r, c
                path = []
                valid = True
                for _ in range(loop_length):
                    rr += dr
                    cc += dc
                    if rr < 1 or rr >= h-1 or cc < 1 or cc >= w-1:
                        valid = False
                        break
                    path.append((rr, cc))
                if valid:
                    # Check if the end of this path can connect back to a carved cell, forming a loop
                    neighbors = [(rr+nr, cc+nc) for nr,nc in directions]
                    # If at least one neighbor at the end is carved, we form a loop
                    if any(0 <= nr < h and 0 <= nc < w and self.blocks[nr,nc] == 0 for nr,nc in neighbors):
                        # Carve the path
                        for pr, pc in path:
                            self.blocks[pr, pc] = 0
                        break


    def post_process_open_maze(self):
        # Mostly open: keep outer walls but clear internal ones
        h, w = self.blocks.shape
        for i in range(1, h-1):
            for j in range(1, w-1):
                # 20% chance to remain a wall, otherwise free
                if random.random() > 0.2:
                    self.blocks[i, j] = 0
                else:
                    self.blocks[i, j] = 1

    def post_process_bottleneck_maze(self):
        h, w = self.blocks.shape
        self.blocks[1:-1, 1:-1] = 0

        # We'll create multiple "bottleneck lines".
        # For simplicity, let's create three vertical lines spaced evenly across the width:
        num_lines = 3
        line_positions = [w*(i+1)//(num_lines+1) for i in range(num_lines)]
        
        for line_col in line_positions:
            # Carve a vertical line
            for i in range(1, h-1):
                self.blocks[i, line_col] = 1
            # Create 1-2 gaps in this line at random positions
            gap_count = random.randint(1, 2)
            gaps = random.sample(range(2, h-2), gap_count)
            for gap_row in gaps:
                self.blocks[gap_row, line_col] = 0

        # Add random obstacles in each "section" between bottleneck lines
        # The maze now has (num_lines+1) sections. Add obstacles in each:
        columns = [1] + line_positions + [w-2]
        for section_idx in range(len(columns)-1):
            left_bound = columns[section_idx] + 1 if section_idx > 0 else 1
            right_bound = columns[section_idx+1] - 1 if section_idx < len(columns)-1 else w-2
            # Fill with some random walls
            for i in range(2, h-2):
                for j in range(left_bound, right_bound):
                    if random.random() < 0.1:
                        self.blocks[i,j] = 1


if __name__ == '__main__':

    # Try changing maze_type to 'snake', 'open', or 'bottleneck' and see the difference.
    maze_type = 'bottleneck'
    pygame.display.init()
    disp_size = (1080, 1080)
    rect = np.array([0, 0, disp_size[0], disp_size[1]])
    block_size = 10
    screen = pygame.display.set_mode(disp_size)
    pygame.display.set_caption('Modified Maze Generator with Multiple Paths')
    running = True

    while running:
        # Create and configure maze
        maze = Maze(rect[2] // (block_size * 2) - 1, rect[3] // (block_size * 2) - 1, maze_type=maze_type)
        maze.screen = screen
        maze.set_path_density(0.8)

        screen.fill((0, 0, 0))
        maze.screen_size = np.asarray(disp_size)
        maze.screen_block_size = np.min(rect[2:4] / np.flip(maze.block_size))
        maze.screen_block_offset = rect[0:2] + (rect[2:4] - maze.screen_block_size *
                                                np.flip(maze.block_size)) // 2

        # Generate maze
        start_time = pygame.time.get_ticks()
        print(f'Generating {maze_type} maze: {maze.wall_size[1]} x {maze.wall_size[0]} cells. '
              f'Block size = {block_size}.')
        maze.gen_maze_2D()
        maze.count_removed_walls()

        if maze.running:
            print(f'Ready. Time: {(pygame.time.get_ticks() - start_time) / 1000.0:.2f} seconds.')
            print('Controls: ESC/Close=Exit, SPACE=New maze, UP/DOWN=Change size, S=Save image')
        else:
            print('Aborted.')

        pygame.event.clear()
        running = maze.running
        pausing = maze.running

        while pausing:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                pausing = False
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pausing = False
                elif event.key == pygame.K_f:
                    maze.toggle_fullscreen()
                elif event.key == pygame.K_s:
                    maze.save_image()
                elif event.key == pygame.K_DOWN:
                    block_size = max(1, block_size - 1)
                    pausing = False
                elif event.key == pygame.K_UP:
                    block_size = min(min(rect[2], rect[3]) // 10, block_size + 1)
                    pausing = False
                elif event.key == pygame.K_ESCAPE:
                    pausing = False
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pausing = False

    pygame.quit()
    exit()
