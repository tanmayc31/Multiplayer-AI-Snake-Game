import socket
import random
import time
import heapq  # For priority queue in A* algorithm
from ast import literal_eval

# Server configuration
HOST = '0.0.0.0'
PORT = 5001

# Game constants
WIDTH = 800
HEIGHT = 600
SEG_SIZE = 20
GRID_WIDTH = WIDTH // SEG_SIZE
GRID_HEIGHT = HEIGHT // SEG_SIZE

# Game state
current_direction = "Right"
yellow_immunity = 0
immunity_period = 6
apple_pos = None
yellow_head_pos = None
red_head_pos = None
yellow_length = 3
red_length = 3

# Directions and their vector values (grid-based)
directions = {
    "Up": (0, -1),
    "Down": (0, 1),
    "Left": (-1, 0),
    "Right": (1, 0)
}

# Opposite directions lookup
opposite_directions = {
    "Up": "Down",
    "Down": "Up",
    "Left": "Right",
    "Right": "Left"
}

def get_center_position(rect_coords):
    """Get center of a rectangle from its coordinates."""
    x1, y1, x2, y2 = rect_coords
    return ((x1 + x2) / 2, (y1 + y2) / 2)

def get_grid_position(center_pos):
    """Convert center position to grid coordinates."""
    x, y = center_pos
    return (int(x // SEG_SIZE), int(y // SEG_SIZE))

def manhattan_distance(pos1, pos2):
    """Calculate Manhattan distance between two positions."""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def is_position_valid(pos):
    """Check if a position is valid (within grid boundaries)."""
    x, y = pos
    return 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT

def is_position_safe(pos, opponent_pos=None, has_immunity=False):
    """Check if a position is safe (not hitting walls or opponent)."""
    if not is_position_valid(pos):
        return False
    
    # If we have immunity, we don't need to worry about hitting the opponent
    if has_immunity:
        return True
    
    # Check if we would hit the opponent
    if opponent_pos and manhattan_distance(pos, opponent_pos) < 2:
        return False
    
    return True

def get_next_position(current_pos, direction):
    """Get the next position if moving in the specified direction."""
    dx, dy = directions[direction]
    return (current_pos[0] + dx, current_pos[1] + dy)

def a_star_search(start, goal, opponent_pos=None, has_immunity=False):
    """A* search algorithm to find the optimal path."""
    # Priority queue for open nodes
    open_set = {start}
    closed_set = set()
    
    # Previous node in optimal path
    came_from = {}
    
    # Cost from start to current node
    g_score = {start: 0}
    
    # Estimated total cost from start to goal
    f_score = {start: manhattan_distance(start, goal)}
    
    while open_set:
        # Find node with lowest f_score
        current = min(open_set, key=lambda pos: f_score.get(pos, float('inf')))
        
        # If we've reached the goal
        if current == goal:
            # Reconstruct path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path
        
        open_set.remove(current)
        closed_set.add(current)
        
        # Check all adjacent nodes
        for direction, (dx, dy) in directions.items():
            neighbor = (current[0] + dx, current[1] + dy)
            
            # Skip if already evaluated or not valid
            if neighbor in closed_set or not is_position_safe(neighbor, opponent_pos, has_immunity):
                continue
            
            # Tentative g_score
            tentative_g_score = g_score[current] + 1
            
            if neighbor not in open_set:
                open_set.add(neighbor)
            elif tentative_g_score >= g_score.get(neighbor, float('inf')):
                # This is not a better path
                continue
            
            # This path is the best so far
            came_from[neighbor] = current
            g_score[neighbor] = tentative_g_score
            f_score[neighbor] = g_score[neighbor] + manhattan_distance(neighbor, goal)
    
    # No path found
    return []

def get_safe_directions(current_pos, opponent_pos=None, has_immunity=False):
    """Get list of safe directions to move in."""
    safe_dirs = []
    
    for direction in directions:
        next_pos = get_next_position(current_pos, direction)
        if is_position_safe(next_pos, opponent_pos, has_immunity):
            safe_dirs.append(direction)
    
    return safe_dirs

def calculate_intercept_point(my_pos, opponent_pos, apple_pos):
    """Calculate a point to intercept opponent on way to apple."""
    # If opponent is closer to apple, try to intercept
    my_dist_to_apple = manhattan_distance(my_pos, apple_pos)
    opp_dist_to_apple = manhattan_distance(opponent_pos, apple_pos)
    
    if opp_dist_to_apple < my_dist_to_apple:
        # Calculate a point between opponent and apple
        intercept_x = (opponent_pos[0] + apple_pos[0]) // 2
        intercept_y = (opponent_pos[1] + apple_pos[1]) // 2
        return (intercept_x, intercept_y)
    
    return None

def decide_move(yellow_pos, red_pos, apple_pos, has_immunity=False):
    """Decide the next move based on current game state."""
    global current_direction
    
    # Convert to grid positions
    yellow_grid = get_grid_position(yellow_pos)
    red_grid = get_grid_position(red_pos)
    apple_grid = get_grid_position(apple_pos) if apple_pos else None
    
    # First, check safe directions to avoid immediate death
    safe_directions = get_safe_directions(yellow_grid, red_grid, has_immunity)
    
    if not safe_directions:
        print("WARNING: No safe directions available!")
        # Emergency move: try to avoid walls at least
        for direction in directions:
            next_pos = get_next_position(yellow_grid, direction)
            if is_position_valid(next_pos):
                return direction
        return current_direction  # As a last resort
    
    # Strategy 1: If we have immunity, go after the opponent
    if has_immunity:
        print("ATTACK MODE: We have immunity!")
        path = a_star_search(yellow_grid, red_grid, has_immunity=True)
        if path and len(path) > 0:
            next_pos = path[0]
            for direction, (dx, dy) in directions.items():
                if (yellow_grid[0] + dx, yellow_grid[1] + dy) == next_pos:
                    return direction
    
    # Strategy 2: If there's an apple, decide whether to go for it
    if apple_grid:
        # Calculate distances
        yellow_to_apple = manhattan_distance(yellow_grid, apple_grid)
        red_to_apple = manhattan_distance(red_grid, apple_grid)
        
        # If we're closer to the apple than opponent, go for it
        if yellow_to_apple <= red_to_apple:
            print(f"APPLE STRATEGY: Going for apple at {apple_grid}")
            path = a_star_search(yellow_grid, apple_grid, red_grid, has_immunity)
            if path and len(path) > 0:
                next_pos = path[0]
                for direction, (dx, dy) in directions.items():
                    if (yellow_grid[0] + dx, yellow_grid[1] + dy) == next_pos:
                        return direction
        else:
            # If opponent is closer, try to intercept them
            intercept_point = calculate_intercept_point(yellow_grid, red_grid, apple_grid)
            if intercept_point:
                print(f"INTERCEPT STRATEGY: Intercepting at {intercept_point}")
                path = a_star_search(yellow_grid, intercept_point, red_grid, has_immunity)
                if path and len(path) > 0:
                    next_pos = path[0]
                    for direction, (dx, dy) in directions.items():
                        if (yellow_grid[0] + dx, yellow_grid[1] + dy) == next_pos:
                            return direction
    
    # Strategy 3: If we're close to opponent and longer, try to encircle them
    if manhattan_distance(yellow_grid, red_grid) < 10 and yellow_length > red_length:
        print("ENCIRCLE STRATEGY: Trying to trap opponent")
        # Try to find a position that blocks opponent
        for direction, (dx, dy) in directions.items():
            # Look for a position that gets us closer to opponent without colliding
            test_pos = (yellow_grid[0] + dx, yellow_grid[1] + dy)
            if is_position_safe(test_pos, red_grid, has_immunity) and manhattan_distance(test_pos, red_grid) < manhattan_distance(yellow_grid, red_grid):
                return direction
    
    # Strategy 4: If no specific strategy, continue moving safely
    # Prefer continuing in same direction if safe
    if current_direction in safe_directions:
        return current_direction
    
    # Avoid reversing direction if possible
    opposite = opposite_directions.get(current_direction)
    forward_directions = [d for d in safe_directions if d != opposite]
    if forward_directions:
        return random.choice(forward_directions)
    
    # If all else fails, choose any safe direction
    return random.choice(safe_directions)

def process_game_state(data):
    """Process the game state and decide the next move."""
    global current_direction, yellow_immunity, apple_pos, yellow_head_pos, red_head_pos, yellow_length, red_length
    
    try:
        # Parse data: yellow head, red head, apple
        yx1, yy1, yx2, yy2, x1, y1, x2, y2, ax, ay = literal_eval(data)
        
        # Get center positions
        yellow_center = get_center_position((yx1, yy1, yx2, yy2))
        red_center = get_center_position((x1, y1, x2, y2))
        current_apple_pos = (ax, ay) if ax is not None and ay is not None else None
        
        # Check if an apple was eaten
        if apple_pos and apple_pos != current_apple_pos:
            # If the apple was at our previous position, we ate it
            if manhattan_distance(yellow_center, apple_pos) < SEG_SIZE:
                yellow_length += 1
                yellow_immunity = immunity_period
                print(f"We ate an apple! Length: {yellow_length}, Immunity: {yellow_immunity}")
            # If the apple was at opponent's position, they ate it
            elif manhattan_distance(red_center, apple_pos) < SEG_SIZE:
                red_length += 1
                print(f"Opponent ate an apple! Their length: {red_length}")
        
        # Update current positions
        apple_pos = current_apple_pos
        yellow_head_pos = yellow_center
        red_head_pos = red_center
        
        # Decide next move
        next_move = decide_move(yellow_center, red_center, current_apple_pos, has_immunity=(yellow_immunity > 0))
        
        # Update current direction
        if next_move != "Straight":
            current_direction = next_move
        
        # Decrease immunity counter if active
        if yellow_immunity > 0:
            yellow_immunity -= 1
        
        return next_move
        
    except Exception as e:
        print(f"Error processing game state: {e}")
        return current_direction  # Fallback to current direction

# Main server loop
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Yellow Snake Server listening on {HOST}:{PORT}")
    
    while True:
        # Accept new connections
        client_sock, client_addr = s.accept()
        print(f'New connection from {client_addr}')
        
        try:
            while True:
                data = client_sock.recv(1024)
                if not data:
                    break
                
                start_time = time.time()
                decoded_data = data.decode()
                print(f"Received: {decoded_data}")
                
                # Process game state and determine next move
                next_move = process_game_state(decoded_data)
                
                # Send the move back
                client_sock.sendall(next_move.encode())
                
                # Performance monitoring
                elapsed = time.time() - start_time
                print(f"Response: {next_move}, time: {elapsed:.4f}s")
                if elapsed > 0.8:
                    print("WARNING: Response time approaching 1 second limit!")
                
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_sock.close()