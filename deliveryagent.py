import heapq
import time
import random
from enum import Enum
from typing import List, Tuple, Dict, Set, Optional
import copy
import pygame
import sys

class Terrain(Enum):
    ROAD = 1
    GRASS = 2
    WATER = 5
    MOUNTAIN = 10

class Cell:
    def __init__(self, terrain: Terrain, is_obstacle: bool = False, dynamic_obstacle: bool = False):
        self.terrain = terrain
        self.is_obstacle = is_obstacle
        self.dynamic_obstacle = dynamic_obstacle
        self.cost = terrain.value
    
    def get_cost(self):
        return self.cost if not self.is_obstacle else float('inf')

class Grid:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid = [[Cell(Terrain.ROAD) for _ in range(width)] for _ in range(height)]
        self.dynamic_obstacles = {}  # pos -> movement pattern
        self.time_step = 0
    
    def set_terrain(self, x: int, y: int, terrain: Terrain):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x].terrain = terrain
            self.grid[y][x].cost = terrain.value
    
    def set_obstacle(self, x: int, y: int, permanent: bool = True):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x].is_obstacle = permanent
            self.grid[y][x].dynamic_obstacle = not permanent
    
    def add_dynamic_obstacle(self, x: int, y: int, pattern: List[Tuple[int, int]]):
        """Add a dynamic obstacle with a movement pattern"""
        self.dynamic_obstacles[(x, y)] = pattern
        self.set_obstacle(x, y, permanent=False)
    
    def update_dynamic_obstacles(self):
        """Update positions of dynamic obstacles"""
        self.time_step += 1
        new_obstacles = {}
        
        # Clear current dynamic obstacles
        for pos in self.dynamic_obstacles.keys():
            x, y = pos
            if 0 <= x < self.width and 0 <= y < self.height:
                self.grid[y][x].is_obstacle = False
        
        # Move to new positions
        for pos, pattern in self.dynamic_obstacles.items():
            x, y = pos
            pattern_index = self.time_step % len(pattern)
            dx, dy = pattern[pattern_index]
            new_x, new_y = x + dx, y + dy
            
            # Ensure new position is within bounds
            if 0 <= new_x < self.width and 0 <= new_y < self.height:
                new_obstacles[(new_x, new_y)] = pattern
                self.grid[new_y][new_x].is_obstacle = True
        
        self.dynamic_obstacles = new_obstacles
    
    def is_valid_position(self, x: int, y: int) -> bool:
        return (0 <= x < self.width and 0 <= y < self.height and 
                not self.grid[y][x].is_obstacle)
    
    def get_cost(self, x: int, y: int) -> float:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x].get_cost()
        return float('inf')
    
    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int, float]]:
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # 4-connected
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self.is_valid_position(nx, ny):
                cost = self.get_cost(nx, ny)
                neighbors.append((nx, ny, cost))
        
        return neighbors

class PygameVisualizer:
    def __init__(self, grid, cell_size=60):
        self.grid = grid
        self.cell_size = cell_size
        self.width = grid.width * cell_size
        self.height = grid.height * cell_size
        
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Delivery Agent Simulation")
        self.clock = pygame.time.Clock()
        
        # Colors
        self.colors = {
            Terrain.ROAD: (200, 200, 200),      # Light gray
            Terrain.GRASS: (100, 200, 100),     # Green
            Terrain.WATER: (100, 100, 255),     # Blue
            Terrain.MOUNTAIN: (150, 150, 150),  # Dark gray
            'obstacle': (50, 50, 50),           # Black
            'agent': (255, 0, 0),               # Red
            'goal': (0, 255, 0),                # Green
            'path': (255, 255, 0),              # Yellow
            'text': (0, 0, 0),                  # Black
            'grid_line': (100, 100, 100)        # Dark gray
        }
        
        # Font for displaying costs
        self.font = pygame.font.Font(None, 20)
    
    def draw_grid(self, agent_pos=None, goal_pos=None, path=None, info_text=""):
        self.screen.fill((0, 0, 0))  # Black background
        
        # Draw cells
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                rect = pygame.Rect(x * self.cell_size, y * self.cell_size, 
                                 self.cell_size, self.cell_size)
                
                if self.grid.grid[y][x].is_obstacle:
                    color = self.colors['obstacle']
                else:
                    color = self.colors[self.grid.grid[y][x].terrain]
                
                pygame.draw.rect(self.screen, color, rect)
                
                # Draw grid lines
                pygame.draw.rect(self.screen, self.colors['grid_line'], rect, 1)
                
                # Draw cost numbers
                if not self.grid.grid[y][x].is_obstacle:
                    cost_text = self.font.render(str(self.grid.grid[y][x].get_cost()), 
                                               True, self.colors['text'])
                    text_rect = cost_text.get_rect(center=(x * self.cell_size + self.cell_size // 2, 
                                                         y * self.cell_size + self.cell_size // 2))
                    self.screen.blit(cost_text, text_rect)
        
        # Draw path
        if path:
            for i in range(len(path) - 1):
                start_pos = (path[i][0] * self.cell_size + self.cell_size // 2,
                           path[i][1] * self.cell_size + self.cell_size // 2)
                end_pos = (path[i+1][0] * self.cell_size + self.cell_size // 2,
                         path[i+1][1] * self.cell_size + self.cell_size // 2)
                pygame.draw.line(self.screen, self.colors['path'], start_pos, end_pos, 3)
            
            for x, y in path:
                center = (x * self.cell_size + self.cell_size // 2, 
                         y * self.cell_size + self.cell_size // 2)
                pygame.draw.circle(self.screen, self.colors['path'], center, 5)
        
        # Draw goal
        if goal_pos:
            x, y = goal_pos
            center = (x * self.cell_size + self.cell_size // 2, 
                     y * self.cell_size + self.cell_size // 2)
            pygame.draw.circle(self.screen, self.colors['goal'], center, 15)
            # Add "G" label
            goal_text = self.font.render("G", True, (255, 255, 255))
            text_rect = goal_text.get_rect(center=center)
            self.screen.blit(goal_text, text_rect)
        
        # Draw agent
        if agent_pos:
            x, y = agent_pos
            center = (x * self.cell_size + self.cell_size // 2, 
                     y * self.cell_size + self.cell_size // 2)
            pygame.draw.circle(self.screen, self.colors['agent'], center, 12)
            # Add "A" label
            agent_text = self.font.render("A", True, (255, 255, 255))
            text_rect = agent_text.get_rect(center=center)
            self.screen.blit(agent_text, text_rect)
        
        # Draw info text
        if info_text:
            info_surface = pygame.font.Font(None, 24).render(info_text, True, (255, 255, 255))
            self.screen.blit(info_surface, (10, 10))
        
        pygame.display.flip()
    
    def animate_path(self, agent, goal, path, algorithm_name="", delay=500):
        """Animate the agent following the path"""
        print(f"Animating path with {len(path)} steps...")
        
        # Show initial position
        self.draw_grid(agent.position, goal, path, f"Algorithm: {algorithm_name} - Ready to start")
        pygame.time.delay(1000)
        
        for step, pos in enumerate(path):
            # Check for quit event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
            
            # Update agent position
            agent.position = pos
            
            # Update dynamic obstacles periodically
            if step > 0 and step % 3 == 0 and hasattr(self.grid, 'dynamic_obstacles'):
                if self.grid.dynamic_obstacles:
                    self.grid.update_dynamic_obstacles()
                    # Re-draw the grid to show updated obstacles
                    path = path  # Keep the original path for visualization
            
            # Draw current state
            info = f"Algorithm: {algorithm_name} - Step {step+1}/{len(path)} - Pos: {pos}"
            self.draw_grid(agent.position, goal, path, info)
            
            pygame.time.delay(delay)  # Delay in milliseconds
        
        # Show final state for a bit longer
        final_info = f"Algorithm: {algorithm_name} - DELIVERY COMPLETE! - Total cost: {agent.total_cost}"
        self.draw_grid(agent.position, goal, path, final_info)
        pygame.time.delay(2000)
        
        # Wait for user to close window
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        waiting = False
        pygame.quit()

class DeliveryAgent:
    def __init__(self, grid: Grid):
        self.grid = grid
        self.position = (0, 0)
        self.path = []
        self.nodes_expanded = 0
        self.total_cost = 0
    
    def set_position(self, x: int, y: int):
        if self.grid.is_valid_position(x, y):
            self.position = (x, y)
    
    def manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def bfs(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """Breadth-First Search"""
        if start == goal:
            return [start]
        
        queue = [(start, [start])]
        visited = set([start])
        self.nodes_expanded = 0
        
        while queue:
            current, path = queue.pop(0)
            self.nodes_expanded += 1
            
            if current == goal:
                return path
            
            for nx, ny, cost in self.grid.get_neighbors(*current):
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [(nx, ny)]))
        
        return None
    
    def uniform_cost_search(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """Uniform Cost Search"""
        if start == goal:
            return [start]
        
        priority_queue = [(0, start, [start])]
        visited = set()
        self.nodes_expanded = 0
        
        while priority_queue:
            current_cost, current, path = heapq.heappop(priority_queue)
            self.nodes_expanded += 1
            
            if current == goal:
                return path
            
            if current in visited:
                continue
            visited.add(current)
            
            for nx, ny, cost in self.grid.get_neighbors(*current):
                if (nx, ny) not in visited:
                    new_cost = current_cost + cost
                    heapq.heappush(priority_queue, (new_cost, (nx, ny), path + [(nx, ny)]))
        
        return None
    
    def a_star_search(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """A* Search with Manhattan distance heuristic"""
        if start == goal:
            return [start]
        
        # Priority queue: (f_cost, g_cost, position, path)
        g_cost = {start: 0}
        f_cost = {start: self.manhattan_distance(start, goal)}
        priority_queue = [(f_cost[start], 0, start, [start])]
        visited = set()
        self.nodes_expanded = 0
        
        while priority_queue:
            current_f, current_g, current, path = heapq.heappop(priority_queue)
            self.nodes_expanded += 1
            
            if current == goal:
                return path
            
            if current in visited:
                continue
            visited.add(current)
            
            for nx, ny, cost in self.grid.get_neighbors(*current):
                neighbor = (nx, ny)
                new_g = current_g + cost
                
                if neighbor not in g_cost or new_g < g_cost[neighbor]:
                    g_cost[neighbor] = new_g
                    f_cost[neighbor] = new_g + self.manhattan_distance(neighbor, goal)
                    heapq.heappush(priority_queue, (f_cost[neighbor], new_g, neighbor, path + [neighbor]))
        
        return None
    
    def hill_climbing_replan(self, start: Tuple[int, int], goal: Tuple[int, int], max_restarts: int = 10) -> Optional[List[Tuple[int, int]]]:
        """Hill climbing with random restarts for dynamic replanning"""
        best_path = self.a_star_search(start, goal)
        if not best_path:
            return None
        
        best_cost = self.calculate_path_cost(best_path)
        
        for _ in range(max_restarts):
            # Randomly modify the grid slightly (simulating dynamic changes)
            temp_grid = copy.deepcopy(self.grid)
            
            # Randomly change some terrain costs
            for _ in range(5):  # Change 5 random cells
                x, y = random.randint(0, temp_grid.width-1), random.randint(0, temp_grid.height-1)
                new_terrain = random.choice(list(Terrain))
                temp_grid.set_terrain(x, y, new_terrain)
            
            # Try to find a new path
            temp_agent = DeliveryAgent(temp_grid)
            new_path = temp_agent.a_star_search(start, goal)
            
            if new_path:
                new_cost = self.calculate_path_cost(new_path)
                if new_cost < best_cost:
                    best_path = new_path
                    best_cost = new_cost
        
        return best_path
    
    def calculate_path_cost(self, path: List[Tuple[int, int]]) -> float:
        """Calculate the total cost of a path"""
        total_cost = 0
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i+1]
            total_cost += self.grid.get_cost(x2, y2)
        return total_cost
    
    def deliver_package(self, goal: Tuple[int, int], algorithm: str = "astar") -> bool:
        """Deliver a package to the goal using the specified algorithm"""
        print(f"Starting delivery from {self.position} to {goal} using {algorithm}")
        
        start_time = time.time()
        
        if algorithm == "bfs":
            path = self.bfs(self.position, goal)
        elif algorithm == "ucs":
            path = self.uniform_cost_search(self.position, goal)
        elif algorithm == "astar":
            path = self.a_star_search(self.position, goal)
        elif algorithm == "replan":
            path = self.hill_climbing_replan(self.position, goal)
        else:
            print(f"Unknown algorithm: {algorithm}")
            return False
        
        end_time = time.time()
        
        if not path:
            print("No path found!")
            return False
        
        self.path = path
        self.total_cost = self.calculate_path_cost(path)
        
        print(f"Path found! Cost: {self.total_cost}, Nodes expanded: {self.nodes_expanded}")
        print(f"Time taken: {end_time - start_time:.4f} seconds")
        print(f"Path length: {len(path)} steps")
        
        return True

# Map creation functions
def create_small_map() -> Grid:
    """Create a small test map"""
    grid = Grid(5, 5)
    
    # Set different terrains
    for y in range(5):
        for x in range(5):
            if (x + y) % 3 == 0:
                grid.set_terrain(x, y, Terrain.GRASS)
    
    # Add some obstacles
    grid.set_obstacle(2, 1)
    grid.set_obstacle(2, 2)
    grid.set_obstacle(2, 3)
    
    return grid

def create_medium_map() -> Grid:
    """Create a medium test map"""
    grid = Grid(10, 10)
    
    # Set different terrains
    for y in range(10):
        for x in range(10):
            if x % 4 == 0 and y % 4 == 0:
                grid.set_terrain(x, y, Terrain.WATER)
            elif (x + y) % 5 == 0:
                grid.set_terrain(x, y, Terrain.MOUNTAIN)
            elif (x * y) % 7 == 0:
                grid.set_terrain(x, y, Terrain.GRASS)
    
    # Add obstacles
    for i in range(3, 7):
        grid.set_obstacle(i, 5)
    
    return grid

def create_large_map() -> Grid:
    """Create a large test map"""
    grid = Grid(15, 15)  # Smaller for better visualization
    
    # Set different terrains in patterns
    for y in range(15):
        for x in range(15):
            if x < 5 and y < 5:
                grid.set_terrain(x, y, Terrain.GRASS)
            elif x > 10 and y > 10:
                grid.set_terrain(x, y, Terrain.MOUNTAIN)
            elif 5 < x < 12 and 5 < y < 12:
                grid.set_terrain(x, y, Terrain.WATER)
    
    # Add maze-like obstacles
    for i in range(1, 14):
        if i % 3 != 0:
            grid.set_obstacle(i, 7)
    
    return grid

def create_dynamic_map() -> Grid:
    """Create a map with dynamic obstacles"""
    grid = Grid(8, 8)
    
    # Set base terrain
    for y in range(8):
        for x in range(8):
            if (x + y) % 4 == 0:
                grid.set_terrain(x, y, Terrain.GRASS)
    
    # Add dynamic obstacles with movement patterns
    grid.add_dynamic_obstacle(3, 3, [(0, 1), (0, 1), (0, -1), (0, -1)])  # Moves up and down
    grid.add_dynamic_obstacle(5, 2, [(1, 0), (1, 0), (-1, 0), (-1, 0)])  # Moves left and right
    
    return grid

def run_pygame_demo():
    """Run a demo with Pygame visualization"""
    print("Delivery Agent Simulation - PyGame Visualization")
    print("=" * 50)
    
    # Choose map and algorithm
    print("Available maps: small, medium, large, dynamic")
    map_choice = input("Enter map choice: ").strip().lower() or "medium"
    
    print("Available algorithms: bfs, ucs, astar, replan")
    algo_choice = input("Enter algorithm choice: ").strip().lower() or "astar"
    
    # Create map
    if map_choice == "small":
        grid = create_small_map()
    elif map_choice == "medium":
        grid = create_medium_map()
    elif map_choice == "large":
        grid = create_large_map()
    elif map_choice == "dynamic":
        grid = create_dynamic_map()
    else:
        print("Invalid choice! Using medium map.")
        grid = create_medium_map()
    
    # Set start and goal
    start = (0, 0)
    goal = (grid.width-1, grid.height-1)
    
    # Create agent and find path
    agent = DeliveryAgent(grid)
    agent.set_position(*start)
    
    print(f"Finding path using {algo_choice} algorithm...")
    
    if agent.deliver_package(goal, algo_choice):
        # Create visualizer and animate
        visualizer = PygameVisualizer(grid)
        visualizer.animate_path(agent, goal, agent.path, algo_choice.upper())
    else:
        print("No path found!")
        # Still show the grid
        visualizer = PygameVisualizer(grid)
        visualizer.draw_grid(start, goal, [], "No path found!")
        pygame.time.delay(3000)
        pygame.quit()

def main():
    """Main function"""
    print("Delivery Agent Simulation")
    print("=" * 30)
    
    while True:
        print("\nOptions:")
        print("1. Run with PyGame visualization")
        print("2. Exit")
        
        choice = input("Enter your choice (1-2): ").strip()
        
        if choice == "1":
            try:
                run_pygame_demo()
            except pygame.error as e:
                print(f"Pygame error: {e}")
                print("Make sure you have a graphical environment available.")
        elif choice == "2":
            print("Goodbye!")
            break
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()