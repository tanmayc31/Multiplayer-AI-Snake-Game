import socket
import random
from ast import literal_eval
import time

"""
Yellow Snake Server - Advanced AI Implementation
This server controls a yellow snake in a competitive snake game using TCP sockets.

Key strategies implemented:
1. A* pathfinding to efficiently navigate to apples
2. Opponent tracking to predict movement patterns
3. Defensive maneuvers to avoid collisions
4. Offensive encirclement tactics when immune
5. Wall avoidance and edge navigation
"""

# Game constants
WIDTH = 800
HEIGHT = 600
SEG_SIZE = 20
MAX_X = WIDTH // SEG_SIZE
MAX_Y = HEIGHT // SEG_SIZE
DIRECTIONS = ["Up", "Down", "Left", "Right"]

# Server configuration
HOST = '0.0.0.0'  # Listen on all available interfaces
PORT = 5001       # Port to listen on for yellow snake

# Game state tracking
opponent_positions = []
my_previous_heads = []
my_immunity = 0  # Track immunity status
opponent_immunity = 0  # Track opponent's immunity status
previous_apple_pos = None
growth_count = 5  # Start with 5 segments (baby snake)

def manhattan_distance(pos1, pos2):
    """Calculate Manhattan distance between two positions."""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def is_valid_move(current_pos, direction):
    """Check if a move is valid (won't hit wall)."""
    x, y = current_pos
    if direction == "Up": y -= 1
    elif direction == "Down": y += 1
    elif direction == "Left": x -= 1
    elif direction == "Right": x += 1
    
    # Check boundary conditions
    if x < 0 or x >= MAX_X or y < 0 or y >= MAX_Y:
        return False
    return True

def estimate_opponent_body(head_pos, growth):
    """Estimate opponent's body positions based on their head and growth."""
    # This is a simplified estimation - in a real scenario we would track 
    # the opponent's movements more precisely
    body_positions = [head_pos]
    direction_preferences = ["Left", "Down", "Right", "Up"]  # Default preference
    
    # Try to add body segments based on growth and previous observed positions
    x, y = head_pos
    for i in range(growth):
        # Simple body extension in one of the directions
        for direction in direction_preferences:
            new_x, new_y = x, y
            if direction == "Left": new_x -= 1
            elif direction == "Right": new_x += 1
            elif direction == "Up": new_y -= 1
            elif direction == "Down": new_y += 1
            
            # Check if this position is valid
            if 0 <= new_x < MAX_X and 0 <= new_y < MAX_Y:
                body_positions.append((new_x, new_y))
                x, y = new_x, new_y
                break
    
    return body_positions

def a_star_search(start, goal, opponent_body):
    """A* algorithm for pathfinding to the apple or another goal."""
    open_set = {start}
    closed_set = set()
    
    # g_score is the cost of the cheapest path from start to current node
    g_score = {start: 0}
    
    # f_score is the estimated total cost from start to goal through y
    f_score = {start: manhattan_distance(start, goal)}
    
    # For reconstructing the path
    came_from = {}
    
    while open_set:
        # Find node in open_set with lowest f_score
        current = min(open_set, key=lambda pos: f_score.get(pos, float('inf')))
        
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
        
        # Check all four possible moves
        x, y = current
        neighbors = [
            ((x, y-1), "Up"),
            ((x, y+1), "Down"),
            ((x-1, y), "Left"),
            ((x+1, y), "Right")
        ]
        
        for neighbor, _ in neighbors:
            if (not (0 <= neighbor[0] < MAX_X and 0 <= neighbor[1] < MAX_Y) or 
                neighbor in closed_set or
                neighbor in opponent_body):
                continue
            
            tentative_g_score = g_score[current] + 1
            
            if neighbor not in open_set:
                open_set.add(neighbor)
            elif tentative_g_score >= g_score.get(neighbor, float('inf')):
                continue
            
            came_from[neighbor] = current
            g_score[neighbor] = tentative_g_score
            f_score[neighbor] = g_score[neighbor] + manhattan_distance(neighbor, goal)
    
    return None  # No path found

def choose_direction(current_pos, next_pos):
    """Convert a position change to a direction."""
    x1, y1 = current_pos
    x2, y2 = next_pos
    
    if x1 < x2: return "Right"
    if x1 > x2: return "Left"
    if y1 < y2: return "Down"
    if y1 > y2: return "Up"
    return "Straight"  # Default if no clear direction

def get_safe_direction(head_pos, opponent_head, opponent_body, apple_pos):
    """Get a safe direction that avoids walls and opponent."""
    global my_immunity, opponent_immunity, growth_count, previous_apple_pos, my_previous_heads
    
    # Convert pixel coordinates to grid positions
    head_grid_x, head_grid_y = head_pos[0] // SEG_SIZE, head_pos[1] // SEG_SIZE
    head_grid_pos = (head_grid_x, head_grid_y)
    
    opponent_grid_x, opponent_grid_y = opponent_head[0] // SEG_SIZE, opponent_head[1] // SEG_SIZE
    opponent_grid_pos = (opponent_grid_x, opponent_grid_y)
    
    apple_grid_x, apple_grid_y = apple_pos[0] // SEG_SIZE, apple_pos[1] // SEG_SIZE
    apple_grid_pos = (apple_grid_x, apple_grid_y)
    
    # Track my previous head positions for body estimation
    my_previous_heads.append(head_grid_pos)
    if len(my_previous_heads) > growth_count:
        my_previous_heads = my_previous_heads[-growth_count:]
    
    # Check if we just ate an apple
    if previous_apple_pos and head_grid_pos == previous_apple_pos:
        my_immunity = 6  # Set immunity based on game rules (typically 1-6 heartbeats)
        growth_count += 1  # We've grown by eating an apple
    
    # Check if opponent just ate an apple
    if previous_apple_pos and opponent_grid_pos == previous_apple_pos:
        opponent_immunity = 6  # Assume same immunity period
        
    # Update apple position for next check
    previous_apple_pos = apple_grid_pos
    
    # Update immunity counters
    if my_immunity > 0:
        my_immunity -= 1
    if opponent_immunity > 0:
        opponent_immunity -= 1
    
    # Estimate opponent's body
    estimated_opponent_body = estimate_opponent_body(opponent_grid_pos, growth_count)
    
    # STRATEGY SELECTION
    # If we're immune, we can be more aggressive
    if my_immunity > 0:
        # Try to intercept or encircle the opponent
        path_to_opponent = a_star_search(head_grid_pos, opponent_grid_pos, [])
        if path_to_opponent and len(path_to_opponent) > 0:
            return choose_direction(head_grid_pos, path_to_opponent[0])
    
    # If not immune, prioritize apple collection while staying safe
    path_to_apple = a_star_search(head_grid_pos, apple_grid_pos, estimated_opponent_body)
    
    # If we found a path to the apple, follow it
    if path_to_apple and len(path_to_apple) > 0:
        return choose_direction(head_grid_pos, path_to_apple[0])
    
    # If no path to apple, enter defensive mode
    # Find directions that don't result in collisions
    safe_directions = []
    for direction in DIRECTIONS:
        next_x, next_y = head_grid_x, head_grid_y
        
        if direction == "Up": next_y -= 1
        elif direction == "Down": next_y += 1
        elif direction == "Left": next_x -= 1
        elif direction == "Right": next_x += 1
        
        # Check if this move is safe (no walls, no opponent body)
        if (0 <= next_x < MAX_X and 0 <= next_y < MAX_Y and 
            (next_x, next_y) not in estimated_opponent_body):
            safe_directions.append(direction)
    
    # If we have safe directions, pick the one furthest from opponent if not immune
    if safe_directions:
        if not my_immunity:
            # Pick direction that maximizes distance from opponent
            return max(safe_directions, 
                      key=lambda d: manhattan_distance(
                          (head_grid_x + (1 if d == "Right" else -1 if d == "Left" else 0),
                           head_grid_y + (1 if d == "Down" else -1 if d == "Up" else 0)),
                          opponent_grid_pos))
        else:
            # If immune, pick direction that minimizes distance to apple
            return min(safe_directions,
                      key=lambda d: manhattan_distance(
                          (head_grid_x + (1 if d == "Right" else -1 if d == "Left" else 0),
                           head_grid_y + (1 if d == "Down" else -1 if d == "Up" else 0)),
                          apple_grid_pos))
    
    # Last resort - try to go in a direction that's valid (won't hit wall)
    for direction in DIRECTIONS:
        if is_valid_move(head_grid_pos, direction):
            return direction
    
    # If all else fails, go straight
    return "Straight"

def determine_move(game_state):
    """Determine the next move based on the current game state."""
    try:
        # Parse the game state
        # Format: yellow_x1, yellow_y1, yellow_x2, yellow_y2, red_x1, red_y1, red_x2, red_y2, apple_x, apple_y
        yx1, yy1, yx2, yy2, rx1, ry1, rx2, ry2, ax, ay = literal_eval(game_state)
        
        # Yellow snake head coordinates
        yellow_head = (yx2, yy2)
        
        # Red snake head coordinates
        red_head = (rx2, ry2)
        
        # Apple coordinates
        apple_pos = (ax, ay)
        
        # Track opponent's position
        opponent_positions.append(red_head)
        if len(opponent_positions) > 10:  # Keep only the last 10 positions
            opponent_positions.pop(0)
        
        # Determine the best move
        return get_safe_direction(yellow_head, red_head, opponent_positions, apple_pos)
    
    except Exception as e:
        print(f"Error determining move: {e}")
        # Default to a random but safe move
        return random.choice(["Up", "Down", "Left", "Right"])

def main():
    """Main server function to receive game state and respond with a move."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Yellow Snake Server listening on {HOST}:{PORT}")
        
        while True:
            client_sock, client_addr = s.accept()
            print(f'New connection from {client_addr}')
            
            while True:
                try:
                    data = client_sock.recv(1024)
                    if not data:
                        break
                    
                    game_state = data.decode()
                    print(f"Received game state: {game_state}")
                    
                    # Determine the next move
                    start_time = time.time()
                    direction = determine_move(game_state)
                    end_time = time.time()
                    
                    # Log the decision and time taken
                    print(f"Chosen direction: {direction} (took {end_time - start_time:.4f}s)")
                    
                    # Send the response
                    client_sock.sendall(direction.encode())
                    
                except Exception as e:
                    print(f"Error in game loop: {e}")
                    # Try to recover by sending a safe response
                    try:
                        client_sock.sendall("Straight".encode())
                    except:
                        break
            
            client_sock.close()
            print(f"Connection closed with {client_addr}")

if __name__ == "__main__":
    main()