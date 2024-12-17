# -*- coding: utf-8 -*-
import numpy as np
import random
import pygame  # needed only if running stand-alone and showing maze generation. (If not imported code must be modified, though.)
from os.path import exists
from sys import exit


class Maze:
    """
    Generate a maze See https://en.wikipedia.org/wiki/Maze_generation_algorithm
    Returns either
        a (y, x, 2) size Numpy Array with 0 as a passage and 1 as a wall for the down and right walls of each cell; outer edges are always walls.
        a (y * 2 + 1, x * 2 + 1) size Numpy Array with 0 as a corridor and 1 as a wall block; outer edges are wall blocks.

    @author: kalle
    """

    def __init__(self, size_x, size_y):
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
        if current_connections >= 5 or next_connections >= 5:  # Increased from 4 to 5
            return False
            
        # Higher base probability for wall removal
        base_prob = min(1.0, self.path_density * 2.0)  # Increased multiplier
        
        # More permissive probability adjustments
        if current_connections + next_connections >= 6:  # Increased threshold
            return random.random() < 0.4  # Increased probability
        elif current_connections + next_connections >= 4:
            return random.random() < base_prob * 0.9  # Increased multiplier
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
                    # Shuffle valid neighbors and take the first num_neighbors
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

        if self.running:
            self.blocks[1:-1:2, 1:-1:2] = 0
            self.blocks[1:-1:2, 2:-2:2] = self.walls[1:-1, 1:-2, 2]
            self.blocks[2:-2:2, 1:-1:2] = self.walls[1:-2, 1:-1, 1]

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

    def toggle_slow_mode(self):

        # switch between a windowed display and full screen
        self.slow_mode = not(self.slow_mode)

    def toggle_fullscreen(self):

        # toggle between fullscreen and windowed mode
        screen_copy = self.screen.copy()
        pygame.display.toggle_fullscreen()
        self.screen.blit(screen_copy, (0, 0))
        pygame.display.flip()

    def save_image(self):

        # save maze as a png image. Use the first available number to avoid overwriting a previous image.
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



if __name__ == '__main__':

    # Run and display the Maze.
    # Left mouse button or space bar: generate a new maze. Up and down cursor keys: change maze block size. s: save the maze image.
    # ESC or close the window: Quit.

    # set screen size and initialize it
    pygame.display.init()
    disp_size = (1920, 1080)
    rect = np.array([0, 0, disp_size[0], disp_size[1]])
    block_size = 10
    screen = pygame.display.set_mode(disp_size)
    pygame.display.set_caption('Modified Maze Generator with Multiple Paths')
    running = True

    while running:
        # Create and configure maze
        maze = Maze(rect[2] // (block_size * 2) - 1, rect[3] // (block_size * 2) - 1)
        maze.screen = screen
        maze.set_path_density(0.8)  # Set desired path density
        
        screen.fill((0, 0, 0))
        maze.screen_size = np.asarray(disp_size)
        maze.screen_block_size = np.min(rect[2:4] / np.flip(maze.block_size))
        maze.screen_block_offset = rect[0:2] + (rect[2:4] - maze.screen_block_size * 
                                              np.flip(maze.block_size)) // 2

        # Generate maze
        start_time = pygame.time.get_ticks()
        print(f'Generating maze: {maze.wall_size[1]} x {maze.wall_size[0]} cells. '
              f'Block size = {block_size}.')
        maze.gen_maze_2D()
        
        maze.count_removed_walls()

        
        if maze.running:
            print(f'Ready. Time: {(pygame.time.get_ticks() - start_time) / 1000.0:.2f} seconds.')
            print('Controls: ESC/Close=Exit, SPACE=New maze, UP/DOWN=Change size, S=Save image')
        else:
            print('Aborted.')

        # Handle events
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
