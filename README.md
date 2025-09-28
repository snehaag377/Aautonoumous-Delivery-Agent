Delivery Agent Simulation
A comprehensive pathfinding simulation with multiple search algorithms and Pygame visualization. This project demonstrates various AI search techniques for package delivery in different terrain environments.

Features
🗺️ Map Types
Small Map (5x5): Simple grid with basic obstacles

Medium Map (10x10): Varied terrain patterns and obstacles

Large Map (15x15): Complex maze-like structure

Dynamic Map: Moving obstacles that change positions

🔍 Search Algorithms
BFS (Breadth-First Search): Finds shortest path by steps

UCS (Uniform Cost Search): Finds lowest-cost path

A* (A-Star Search): Most efficient with heuristic guidance

Replan: Adaptive algorithm for dynamic environments

🎮 Visualization
Real-time path animation

Color-coded terrain types

Dynamic obstacle movement

Cost display on each cell

Step-by-step execution tracking

Installation
Prerequisites
Python 3.7+

Pygame library

Usage
Running the Simulation
Execute the main script

Choose option 1 for PyGame visualization

Select map type (1-4):

1: Small map

2: Medium map

3: Large map

4: Dynamic map

Select algorithm (1-4):

1: BFS

2: UCS

3: A*

4: Replan

Controls During Animation
ESC: Exit simulation

Close Window: Quit application

Animation runs automatically with configurable delays

Algorithm Comparison
BFS (Breadth-First Search)
Pros: Guarantees shortest path by steps

Cons: Ignores terrain costs

Best for: Simple grids without cost considerations

UCS (Uniform Cost Search)
Pros: Finds lowest-cost path

Cons: Slower than BFS

Best for: Cost-sensitive applications

A* (A-Star Search)
Pros: Most efficient, combines cost + heuristic

Cons: Requires admissible heuristic

Best for: Most practical applications

Replan (Hill Climbing)
Pros: Adapts to changing environments

Cons: May not find optimal solution

Best for: Dynamic obstacle scenarios

DeliveryAgent/
├── Grid Class          # Manages terrain and obstacles
├── Cell Class          # Individual grid cell properties
├── DeliveryAgent Class # Implements search algorithms
├── PygameVisualizer    # Handles visualization
└── Map Creators        # Predefined map configurations

Key Classes
Grid: Manages the game world with terrain and obstacles

set_terrain(): Configure cell terrain types

set_obstacle(): Add permanent/dynamic obstacles

update_dynamic_obstacles(): Move dynamic obstacles

DeliveryAgent: Implements pathfinding algorithms

bfs(): Breadth-first search implementation

uniform_cost_search(): Cost-based search

a_star_search(): Heuristic-guided search

hill_climbing_replan(): Adaptive search

PygameVisualizer: Handles graphics and animation

draw_grid(): Render the game world

animate_path(): Show agent movement

Future Enhancements
Potential improvements:

Multiple agents with interactions

More search algorithms (IDA, D Lite)

Improved dynamic obstacle handling

Performance benchmarking suite

Save/load map configurations

License
This project is for educational purposes. Feel free to modify and extend for learning AI pathfinding concepts.

Contributing
Suggestions and improvements welcome! Focus areas:

Algorithm efficiency

Visualization enhancements

Additional map types

Performance optimization

