import socket
import random
import time
import heapq  # For priority queue in A* algorithm

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
immunity = 0
apple_positions = []  # Track recent apple positions

def log(message):
    print(f"[LOG] {message}")

def get_center_position(rect_coords):
    """Get center of a rectangle from its coordinates."""
    x1, y1, x2, y2 = rect_coords
    return ((x1 + x2) / 2, (y1 + y2) / 2)

def to_grid_position(pos):
    """Convert pixel coordinates to grid coordinates."""
    return (int(pos[0] // SEG_SIZE), int(pos[1] // SEG_SIZE))

def to_pixel_position(grid_pos):
    """Convert grid coordinates to pixel coordinates (center of cell)."""
    return ((grid_pos[0] * SEG_SIZE) + (SEG_SIZE // 2), 
            (grid_pos[1] * SEG_SIZE) + (SEG_SIZE // 2))

def manhattan_distance(pos1, pos2):
    """Calculate Manhattan distance between two positions."""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def get_direction_from_positions(from_pos, to_pos):
    """Determine direction from one position to another."""
    dx = to_pos[0] - from_pos[0]
    dy = to_pos[1] - from_pos[1]
    
    # Only consider significant movements (full grid cells)
    if abs(dx) >= SEG_SIZE/2 and abs(dx) > abs(dy):
        return "Right" if dx > 0 else "Left"
    elif abs(dy) >= SEG_SIZE/2:
        return "Down" if dy > 0 else "Up"
    
    # Default to current direction if no significant movement
    return current_direction

def is_valid_grid_position(pos):
    """Check if a grid position is valid (within grid boundaries)."""
    x, y = pos
    return 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT

def get_neighbors(grid_pos):
    """Get valid neighboring grid positions."""
    x, y = grid_pos
    neighbors = []
    
    # Check all four directions
    for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:  # Up, Right, Down, Left
        new_pos = (x + dx, y + dy)
        if is_valid_grid_position(new_pos):
            neighbors.append(new_pos)
    
    return neighbors

def a_star_search(start_pos, goal_pos, opponent_pos=None, has_immunity=False):
    """A* pathfinding algorithm to find optimal path."""
    # Convert to grid coordinates
    start_grid = to_grid_position(start_pos)
    goal_grid = to_grid_position(goal_pos)
    opponent_grid = to_grid_position(opponent_pos) if opponent_pos else None
    
    # If start and goal are the same, no path needed
    if start_grid == goal_grid:
        return []
    
    # Open set (priority queue: (f_score, position))
    open_set = [(manhattan_distance(start_grid, goal_grid), 0, start_grid)]
    heapq.heapify(open_set)
    
    # Closed set (visited nodes)
    closed_set = set()
    
    # Path tracking
    came_from = {}
    
    # Cost from start to each node
    g_score = {start_grid: 0}
    
    while open_set:
        # Get node with lowest f_score
        _, _, current = heapq.heappop(open_set)
        
        # If we've reached the goal
        if current == goal_grid:
            # Reconstruct path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path
        
        # Add to closed set
        closed_set.add(current)
        
        # Check all neighbors
        for neighbor in get_neighbors(current):
            # Skip if already evaluated
            if neighbor in closed_set:
                continue
            
            # Skip if would hit opponent (unless immune)
            if (not has_immunity and opponent_grid and 
                neighbor == opponent_grid):
                continue
            
            # Calculate tentative g_score
            tentative_g_score = g_score[current] + 1
            
            # Check if this path is better than any previous ones
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                # This path is better, record it
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + manhattan_distance(neighbor, goal_grid)
                
                # Add to open set
                heapq.heappush(open_set, (f_score, g_score[neighbor], neighbor))
    
    # No path found
    return []

def get_next_direction(current_pos, path):
    """Get the next direction based on the A* path."""
    if not path:
        return current_direction
    
    # Get the next position in the path
    next_grid_pos = path[0]
    next_pixel_pos = to_pixel_position(next_grid_pos)
    
    # Determine direction to that position
    return get_direction_from_positions(current_pos, next_pixel_pos)

def is_wall_collision(direction, pos):
    """Check if moving in a direction would hit a wall."""
    grid_pos = to_grid_position(pos)
    x, y = grid_pos
    
    if direction == "Up" and y <= 0:
        return True
    elif direction == "Down" and y >= GRID_HEIGHT - 1:
        return True
    elif direction == "Left" and x <= 0:
        return True
    elif direction == "Right" and x >= GRID_WIDTH - 1:
        return True
    
    return False

def process_game_state(data_str):
    """Process game state and decide next move using A* pathfinding."""
    global current_direction, immunity, apple_positions
    
    try:
        # Parse data - format: [x1, y1, x2, y2, rx1, ry1, rx2, ry2, ax, ay]
        clean_data = data_str
        if '[' in data_str and ']' in data_str:
            clean_data = data_str.split('[')[1].split(']')[0]
        
        parts = clean_data.split(',')
        if len(parts) < 10:
            return current_direction
        
        # Extract coordinates
        try:
            x1 = float(parts[0])
            y1 = float(parts[1])
            x2 = float(parts[2])
            y2 = float(parts[3])
            rx1 = float(parts[4])
            ry1 = float(parts[5])
            rx2 = float(parts[6])
            ry2 = float(parts[7])
            ax = float(parts[8])
            ay = float(parts[9])
        except ValueError:
            log("Error parsing coordinates, using default direction")
            return current_direction
        
        # Calculate centers
        yellow_pos = get_center_position((x1, y1, x2, y2))
        red_pos = get_center_position((rx1, ry1, rx2, ry2))
        apple_pos = (ax, ay)
        
        log(f"Yellow at {yellow_pos}, Red at {red_pos}, Apple at {apple_pos}")
        
        # Track apple positions
        if not apple_positions or apple_pos != apple_positions[-1]:
            apple_positions.append(apple_pos)
            if len(apple_positions) > 3:
                apple_positions = apple_positions[-3:]
        
        # Check if we have immunity
        if len(apple_positions) >= 2 and apple_positions[-2] != apple_positions[-1]:
            # If we were close to the previous apple, we might have eaten it
            if manhattan_distance(yellow_pos, apple_positions[-2]) < SEG_SIZE * 2:
                immunity = 6  # Default immunity duration
                log("Probably gained immunity")
        
        # 1. If we're about to hit a wall, emergency avoidance
        if is_wall_collision(current_direction, yellow_pos):
            log("Wall collision detected! Emergency change")
            
            # Try to find a valid direction
            for test_dir in ["Up", "Right", "Down", "Left"]:
                if not is_wall_collision(test_dir, yellow_pos):
                    log(f"Emergency direction: {test_dir}")
                    current_direction = test_dir
                    return current_direction
        
        # 2. Use A* to find path to apple
        path = a_star_search(yellow_pos, apple_pos, red_pos, has_immunity=(immunity > 0))
        
        if path:
            # Convert path to next direction
            next_direction = get_next_direction(yellow_pos, path)
            
            # Verify the direction won't cause a wall collision
            if not is_wall_collision(next_direction, yellow_pos):
                log(f"A* path found, next direction: {next_direction}")
                current_direction = next_direction
                return current_direction
            else:
                log(f"A* suggested invalid direction {next_direction}, fallback")
        else:
            log("No A* path found to apple")
        
        # 3. If we have immunity, try to attack the opponent
        if immunity > 0:
            immunity -= 1
            path_to_opponent = a_star_search(yellow_pos, red_pos, has_immunity=True)
            
            if path_to_opponent:
                next_direction = get_next_direction(yellow_pos, path_to_opponent)
                
                if not is_wall_collision(next_direction, yellow_pos):
                    log(f"Attacking opponent with immunity: {next_direction}")
                    current_direction = next_direction
                    return current_direction
        
        # 4. If no valid A* path, try to move toward the center
        center_pos = (WIDTH/2, HEIGHT/2)
        path_to_center = a_star_search(yellow_pos, center_pos, red_pos, has_immunity=(immunity > 0))
        
        if path_to_center:
            next_direction = get_next_direction(yellow_pos, path_to_center)
            
            if not is_wall_collision(next_direction, yellow_pos):
                log(f"Moving toward center: {next_direction}")
                current_direction = next_direction
                return current_direction
        
        # 5. Last resort: choose a random valid direction
        valid_directions = []
        for test_dir in ["Up", "Right", "Down", "Left"]:
            if not is_wall_collision(test_dir, yellow_pos):
                valid_directions.append(test_dir)
        
        if valid_directions:
            next_direction = random.choice(valid_directions)
            log(f"Random valid direction: {next_direction}")
            current_direction = next_direction
            return current_direction
        
        # Absolute fallback: continue in current direction
        return current_direction
    
    except Exception as e:
        log(f"Error processing state: {e}")
        return current_direction

# Main server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Yellow Snake Server listening on {HOST}:{PORT}")
    
    while True:
        client_sock, addr = s.accept()
        print(f"Connection from {addr}")
        
        try:
            while True:
                data = client_sock.recv(1024)
                if not data:
                    break
                
                start_time = time.time()
                data_str = data.decode()
                print(f"Received: {data_str}")
                
                next_move = process_game_state(data_str)
                client_sock.sendall(next_move.encode())
                
                elapsed = time.time() - start_time
                print(f"Sent: {next_move}, time: {elapsed:.4f}s")
        
        except Exception as e:
            print(f"Error: {e}")
        finally:
            client_sock.close()