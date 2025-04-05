from tkinter import Tk, Canvas
import random

WIDTH = 800
HEIGHT = 600
SEG_SIZE = 20
IN_GAME = True
GAME_MODE = 0

def create_apple():
    global APPLE, apple_posx, apple_posy
    apple_posx = SEG_SIZE * random.randint(1, (WIDTH - SEG_SIZE) / SEG_SIZE)
    apple_posy = SEG_SIZE * random.randint(1, (HEIGHT - SEG_SIZE) / SEG_SIZE)
    APPLE = c.create_oval(apple_posx, apple_posy,
                          apple_posx + SEG_SIZE, apple_posy + SEG_SIZE,
                          fill="red")
    
SEG_SIZE

(WIDTH - SEG_SIZE) / SEG_SIZE

def create_apple_reachable(period, x1, y1, x2, y2):
    global APPLE, apple_posx, apple_posy
    
    attempts = 0
    while attempts == 0 or (
        abs(apple_posx - x1) % period == 0 and
        abs(apple_posx - x2) % period == 0 
    ):
        apple_posx = SEG_SIZE * random.randint(1, (WIDTH - SEG_SIZE) / SEG_SIZE)
        attempts += 1
        if 1000 < attempts:
            break
        
    attempts = 0
    while attempts == 0 or (
        abs(apple_posy - y1) % period == 0 and
        abs(apple_posy - y2) % period == 0
    ):
        apple_posy = SEG_SIZE * random.randint(1, (HEIGHT - SEG_SIZE) / SEG_SIZE)
        attempts += 1
        if 1000 < attempts:
            break
        
    APPLE = c.create_oval(apple_posx, apple_posy,
                              apple_posx + SEG_SIZE, apple_posy + SEG_SIZE,
                              fill="red")
    
#Snake object class¶

class Segment(object):
    def __init__(self, x, y, color=None):
        if not color:
            self.instance = c.create_rectangle(x, y, x + SEG_SIZE, y + SEG_SIZE, fill="white")
        else:
            self.instance = c.create_rectangle(x, y, x + SEG_SIZE, y + SEG_SIZE, fill=color)

class Snake(object):
    def __init__(self, segments, color=None):
        self.segments = segments
        self.color = color
        # Possible directions of movement
        self.mapping = {"Down": (0, 1), "Right": (1, 0),
                        "Up": (0, -1), "Left": (-1, 0)}
        # Initial snake movement direction
        self.vector = self.mapping["Right"]

    # Snake movement
    def move(self):
        for index in range(len(self.segments) - 1):
            segment = self.segments[index].instance
            x1, y1, x2, y2 = c.coords(self.segments[index + 1].instance)
            c.coords(segment, x1, y1, x2, y2)

        x1, y1, x2, y2 = c.coords(self.segments[-2].instance)
        c.coords(self.segments[-1].instance,
                 x1 + self.vector[0] * SEG_SIZE, y1 + self.vector[1] * SEG_SIZE,
                 x2 + self.vector[0] * SEG_SIZE, y2 + self.vector[1] * SEG_SIZE)

    # Snake getting fatter: Adding a segment to the snake body
    def add_segment(self, color=None):
        last_seg = c.coords(self.segments[0].instance)
        x = last_seg[2] - SEG_SIZE
        y = last_seg[3] - SEG_SIZE
        self.segments.insert(0, Segment(x, y, color))

    # Change of direction initiated by keyboard
    def change_direction(self, event):
        if event.keysym in self.mapping:
            self.vector = self.mapping[event.keysym]
            
    # Change of direction initiated by AI
    def change_direction_ai(self, direction):
        if direction in self.mapping:
            #print("changing direction to:", direction)
            self.vector = self.mapping[direction]

    def reset_snake(self):
        for segment in self.segments:
            c.delete(segment.instance)

#Game states
#A snake is made from many colored scales (body segments). We start life as a baby snake with 3 segments:

def create_snake(color = None):
    if not color:
        # creating snake segments
        segments = [Segment(SEG_SIZE, SEG_SIZE),
                    Segment(SEG_SIZE*2, SEG_SIZE),
                    Segment(SEG_SIZE*3, SEG_SIZE)]
        return Snake(segments)
    
    else:
        # creating snake segments with color at random locations
        posx = SEG_SIZE * random.randint(1, (WIDTH - SEG_SIZE) / SEG_SIZE)
        posy = SEG_SIZE * random.randint(1, (HEIGHT - SEG_SIZE) / SEG_SIZE)
        segments = [Segment(posx, posy, color),
                    Segment(posx + SEG_SIZE, posy, color),
                    Segment(posx + SEG_SIZE*2, posy, color)]
        return Snake(segments, color)

#Single user game mode:

def start_game():
    global s
    create_apple()
    s = create_snake()
    
    # Keystroke Response
    c.bind("<KeyPress>", s.change_direction)
    main()

#Dueling snakes simulation mode:

def start_game2():
    global r_s, y_s
    create_apple()
    r_s = create_snake('red')
    y_s = create_snake('yellow')
    
    # Keystroke Response: Even in sim mode, user
    # could jointly change snakes movement direction
    c.bind("<KeyPress>", r_s.change_direction)
    c.bind("<KeyPress>", y_s.change_direction)
    main()

#Using remote servers to control each snake's movements

def start_game3():
    global r_s, y_s
    create_apple()
    r_s = create_snake('red')
    y_s = create_snake('yellow')
    
    # Keystroke Response: Even in sim mode, user
    # could jointly change snakes movement direction
    #c.bind("<KeyPress>", r_s.change_direction)
    #c.bind("<KeyPress>", y_s.change_direction)
    main()

def set_state(item, state):
    c.itemconfigure(item, state=state)

#The user selected one-person (single snake) game with keyboard actions:
def clicked(event):
    global GAME_MODE
    
    s.reset_snake()
    IN_GAME = True
    GAME_MODE = 1
    c.delete(APPLE)
    
    c.itemconfigure(play_text, state='hidden')
    c.itemconfigure(simulate_text, state='hidden')
    c.itemconfigure(game_over_text, state='hidden')
    c.itemconfigure(remote_simulate_text, state='hidden')
    start_game()

#The user selected local dueling snakes AI mode:
def clicked2(event):
    global GAME_MODE
    
    r_s.reset_snake()
    y_s.reset_snake()
    IN_GAME = True
    GAME_MODE = 2
    c.delete(APPLE)
    
    c.itemconfigure(play_text, state='hidden')
    c.itemconfigure(simulate_text, state='hidden')
    c.itemconfigure(game_over_text, state='hidden')
    c.itemconfigure(remote_simulate_text, state='hidden')
    start_game2()

#The user selected remote servers dueling snakes AI mode (need to run the two servers, first):
def clicked3(event):
    global GAME_MODE
    
    r_s.reset_snake()
    y_s.reset_snake()
    IN_GAME = True
    GAME_MODE = 3
    c.delete(APPLE)
    
    c.itemconfigure(play_text, state='hidden')
    c.itemconfigure(simulate_text, state='hidden')
    c.itemconfigure(game_over_text, state='hidden')
    c.itemconfigure(remote_simulate_text, state='hidden')
    start_game3()


#Gameplay
#For both single-user and AI mode:

str([12, 13])
from ast import literal_eval
s = "[1,[2,3,4],5]"
print(literal_eval(s))

b'Up'.decode('ascii')

# Game variables
# Each snake movement by one pixel is called a game heartbeat.

# Game dice for immunity heartbeats: When a snake eats an apple, it gains an immunity for x heartbeats where the opponent snake cannot kill it. Also, snakes are queried for movement every y heartbeats (otherwise the snake keeps going straight). x and y are decided by throwing dice at the beginning of a game.

# Remote snake server coordinates.

game_heartbeats = 0
snake_immunity_period, game_period = 6, 1
yellow_immunity, red_immunity = 0, 0
yellow_snake_ip, red_snake_ip = "127.0.0.1", "127.0.0.1"
yellow_snake_port, red_snake_port = 5001, 5002

# Client code: Calling a TCP socket server
# We prototype TCP sockets. What you call in this notebook to contact a snake server, using TCP sockets:

import socket

#host = '10.110.79.140'  # The server's IP address
#port = 12345        # The same port as used by the server
def call_snake_server(host, port, game_state):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        #s.sendall(b'Hello, server')
        s.sendall(game_state)
        data = s.recv(1024)
    
    return repr(data)

# Server code: The TCP socker server code
# What the TCP socket server runs:

import socket
HOST = '0.0.0.0' # listen on all available interfaces
PORT = 5001      # port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server listening on {HOST}:{PORT}")
    while True:
        # Accept new connections in an infinite loop.
        client_sock, client_addr = s.accept()
        print('New connection from', client_addr)

        while True:
            data = client_sock.recv(1024)
            if data:
                print(f"Received: {data.decode()}")
                data_to_proxy = f"Hi {data}"
                client_sock.sendall(data_to_proxy.encode())
            else:
                break
                
        client_sock.close()

# Snake game server
# Encoding snake positions:

str((10,20,30,40,50,60,70,80,90,99))[1:-1].encode('utf-8')

c = Canvas(root, width=WIDTH, height=HEIGHT, bg="#003300")
create_apple()
rs = create_snake('red')
ys = create_snake('yellow')

yellow_head_coords = c.coords(ys.segments[-1].instance)
red_head_coords = c.coords(rs.segments[-1].instance)

# Yellow snake
yx1, yy1, yx2, yy2 = yellow_head_coords

# Red snake
rx1, ry1, rx2, ry2 = red_head_coords

# report initial snake positions
if game_heartbeats == 0:
    print("yellow snake starts at", yellow_head_coords)
    print("red snake starts at", red_head_coords)

# game info
game_info = yellow_head_coords + red_head_coords + [apple_posx, apple_posy]
game_info

b = str(game_info)[1:-1].encode('utf-8')
b

# This runs the snake game in this jupyter notebook:

import random
#import requests -REST calls, too slow!
#from sockets.python3.client import Client -Websockets, too complex!
import socket #TCP sockets, just right!

def main():
    global GAME_MODE, IN_GAME, APPLE, apple_posx, apple_posy
    global game_heartbeats, snake_immunity_period, game_period, yellow_immunity, red_immunity
    
    # single user with keyboard actions
    if GAME_MODE == 1:
        s.move()
        head_coords = c.coords(s.segments[-1].instance)
        x1, y1, x2, y2 = head_coords
        
        # Checking for collisions with field edges
        if x2 > WIDTH or x1 < 0 or y1 < 0 or y2 > HEIGHT:
            IN_GAME = False
            GAME_MODE = 0
            
        # eating apples, getting fatter!
        elif head_coords == c.coords(APPLE):
            s.add_segment()
            c.delete(APPLE)
            create_apple()
            
        # A snake eating itself
        else:
            for index in range(len(s.segments) - 1):
                if head_coords == c.coords(s.segments[index].instance):
                    IN_GAME = False
                    GAME_MODE = 0
                    
        root.after(100, main)
        
    # sim mode: dueling snakes with local AI actions
    elif GAME_MODE == 2:
        y_s.move()
        r_s.move()
        yellow_head_coords = c.coords(y_s.segments[-1].instance)
        red_head_coords = c.coords(r_s.segments[-1].instance)
        
        # Yellow snake
        x1, y1, x2, y2 = yellow_head_coords
        
        # Fixing collisions with field edges (or obstacles) for sim
        # (in real game, snake hitting obstacles dies!)
        if max(x1,x2) >= WIDTH - 20:
            #print("yellow snake, right wall:", red_head_coords)
            y_s.change_direction_ai("Left")
            
        if min(x1,x2) <= 20:
            #print("yellow snake, left wall:", red_head_coords)
            y_s.change_direction_ai("Right")
            
        if max(y1,y2) >= HEIGHT - 20:
            #print("yellow snake, top edge:", red_head_coords)
            y_s.change_direction_ai("Up")
            
        if min(y1,y2) <= 20:
            #print("yellow snake, bottom edge:", red_head_coords)
            y_s.change_direction_ai("Down")
            
        # occasional random movements and get fatter
        if random.randint(1,10) == 1:
            if random.randint(1,5) == 1:
                y_s.add_segment()
            direction = random.randint(1,4)
            if direction == 1:
                y_s.change_direction_ai("Up")
            elif direction == 2:
                y_s.change_direction_ai("Down")
            elif direction == 3:
                y_s.change_direction_ai("Right")
            else:
                y_s.change_direction_ai("Left")
                    
                    
        # Red snake
        x1, y1, x2, y2 = red_head_coords
        
        # Fixing collisions with field edges (or obstacles) for sim
        # (in real game, snake hitting obstacles dies!)
        #if x2 >= WIDTH-20 or x1 <= 20 or y1 <= 20 or y2 >= HEIGHT-20:
        if max(x1,x2) >= WIDTH - 20:
            #print("red snake, right wall:", red_head_coords)
            r_s.change_direction_ai("Left")
            
        if min(x1,x2) <= 20:
            #print("red snake, left wall:", red_head_coords)
            r_s.change_direction_ai("Right")
            
        if max(y1,y2) >= HEIGHT - 20:
            #print("red snake, top edge:", red_head_coords)
            r_s.change_direction_ai("Up")
            
        if min(y1,y2) <= 20:
            #print("red snake, bottom edge:", red_head_coords)
            r_s.change_direction_ai("Down")
                
            
            # This should help us survive, but now we are actually
            # slithering along the edges!
            #IN_GAME = False
            
        # occasional random movements and get fatter
        if random.randint(1,10) == 1:
            if random.randint(1,5) == 1:
                r_s.add_segment()
            direction = random.randint(1,4)
            if direction == 1:
                r_s.change_direction_ai("Up")
            elif direction == 2:
                r_s.change_direction_ai("Down")
            elif direction == 3:
                r_s.change_direction_ai("Right")
            else:
                r_s.change_direction_ai("Left")    
            
        # eating apples, getting fatter!
        elif yellow_head_coords == c.coords(APPLE):
            y_s.add_segment()
            c.delete(APPLE)
            create_apple()
        elif red_head_coords == c.coords(APPLE):
            r_s.add_segment()
            c.delete(APPLE)
            create_apple()
            
        # Snakes eating each other (or itself)
        else:
            # yellow snake eating itself
            #for index in range(len(y_s.segments) - 1):
            #    if yellow_head_coords == c.coords(y_s.segments[index].instance):
            #        print("yellow snake ate itself!")
            #        IN_GAME = False
            #        GAME_MODE = 0
                    
            # red snake eating itself
            #for index in range(len(r_s.segments) - 1):
            #    if red_head_coords == c.coords(r_s.segments[index].instance):
            #        print("red snake ate itself!")
            #        IN_GAME = False
            #        GAME_MODE = 0
                    
            # Yellow snake kills red snake
            for index in range(len(y_s.segments) - 1):
                if red_head_coords == c.coords(y_s.segments[index].instance):
                    print("yellow snake killed red snake!")
                    IN_GAME = False
                    GAME_MODE = 0
                    
            # Red snake kills yellow snake
            for index in range(len(r_s.segments) - 1):
                if yellow_head_coords == c.coords(r_s.segments[index].instance):
                    print("red snake killed yellow snake!")
                    IN_GAME = False
                    GAME_MODE = 0
        
        root.after(100, main)
        
        
    # Remote mode: dueling snakes with remote game servers AI actions
    elif GAME_MODE == 3:
        y_s.move()
        r_s.move()
        yellow_head_coords = c.coords(y_s.segments[-1].instance)
        red_head_coords = c.coords(r_s.segments[-1].instance)
        
        # Yellow snake
        yx1, yy1, yx2, yy2 = yellow_head_coords
        
        # Red snake
        rx1, ry1, rx2, ry2 = red_head_coords
        
        # report initial snake positions
        if game_heartbeats == 0:
            print("yellow snake starts at", yellow_head_coords)
            print("red snake starts at", red_head_coords)
        
        # game info
        game_info = yellow_head_coords + red_head_coords + [apple_posx, apple_posy]
        
        # query snake servers every game_period heartbeats for any change of direction
        if game_heartbeats % game_period == 0:
            
            #
            # Get command from remote yellow server
            #
            
            # First attempt: using requests library
            #url = "http://localhost:5001/api/snake"
            #data = {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
            #response = requests.post(url, json=data)
            #if response.status_code == 200:
            #    print("Yellow r/u/d POST request successful! ")
            #    print(response.json())
            #elif response.status_code == 201:
            #    print("Yellow c POST request successful!")
            #    print(response.json())
            #else:
            #    print(f"Yellow POST request failed with status code: {response.status_code}")
            #    print(response.text)

            # Second attempt: Using Websockets (pip install sockets)
            #client = Client()
            #response, addr = client.poll_server("Hello world", server=('localhost', 5001))
            #response, addr = client.poll_server(str(yellow_head_coords), server=('localhost', 5001))
            #response, addr = client.poll_server(str(game_info), server=('localhost', 5001))
            
            # ngrok test
            #response, addr = client.poll_server(
            #    str(game_info), 
            #    server=('https://aaae-155-33-129-31.ngrok-free.app', 80)
            #)
            
            #print(response, addr)
            #direction = response.decode('ascii')
            
            # Third attempt: Using TCP sockets (import socket)
            b = str(game_info)[1:-1].encode('utf-8')
            direction = call_snake_server(yellow_snake_ip, yellow_snake_port, b)[2:-1]
            if direction != "Straight":
                y_s.change_direction_ai(direction)
                print("yellow snake turned", direction)

            #
            # Get command from remote red server
            #
            
            # First attempt: requests library
            #url = "http://localhost:5002/api/snake"
            #data = {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
            #response = requests.post(url, json=data)
            #if response.status_code == 200:
            #    print("Red r/u/d POST request successful! ")
            #    print(response.json())
            #elif response.status_code == 201:
            #    print("Red c POST request successful!")
            #    print(response.json())
            #else:
            #    print(f"Red POST request failed with status code: {response.status_code}")
            #    print(response.text)

            # Second attempt: Using Websockets
            #client = Client()
            #response, addr = client.poll_server("Hello world", server=('localhost', 5002))
            #response, addr = client.poll_server(str(red_head_coords), server=('localhost', 5002))
            #response, addr = client.poll_server(str(game_info), server=('localhost', 5002))
            
            # nginx web server
            #response, addr = client.poll_server(str(game_info), 
            #                                    server=('http://10.110.79.140', 5002))
            
            #print(response, addr)
            #direction = response.decode('ascii')
            
            # Third attempt: Using TCP sockets
            direction = call_snake_server(red_snake_ip, red_snake_port, b)[2:-1]
            if direction != "Straight":
                r_s.change_direction_ai(direction)
                print("red snake turned", direction)
            
            
        # snakes occasional get fatter: 
        # NOTE: This won't happen during official games,
        # This is only to make the simulation more interesting.
        if random.randint(1,15) == 1:
            y_s.add_segment("yellow")
            
        if random.randint(1,15) == 1:
            r_s.add_segment("red")
            
            
        # eating apples, definitely get fatter!
        # If both snakes reach apple at the same time, yellow snake wins
        if yellow_head_coords == c.coords(APPLE):
            y_s.add_segment("yellow")
            yellow_immunity += snake_immunity_period + 1
            c.delete(APPLE)
            #create_apple()
            create_apple_reachable(game_period, red_head_coords[0], red_head_coords[1],
                                             yellow_head_coords[0], yellow_head_coords[1])
            
        elif red_head_coords == c.coords(APPLE):
            r_s.add_segment("red")
            red_immunity += snake_immunity_period + 1
            c.delete(APPLE)
            #create_apple()
            create_apple_reachable(game_period, red_head_coords[0], red_head_coords[1],
                                             yellow_head_coords[0], yellow_head_coords[1])
            

        #    
        # Snakes eating each other (or themselves): Commented out
        #

        # yellow snake eating itself
        #for index in range(len(y_s.segments) - 1):
        #    if yellow_head_coords == c.coords(y_s.segments[index].instance):
        #        print("yellow snake ate itself!")
        #        IN_GAME = False
        #        GAME_MODE = 0

        # red snake eating itself
        #for index in range(len(r_s.segments) - 1):
        #    if red_head_coords == c.coords(r_s.segments[index].instance):
        #        print("red snake ate itself!")
        #        IN_GAME = False
        #        GAME_MODE = 0

        # Yellow snake kills red snake
        if 0 == red_immunity:
            for index in range(len(y_s.segments) - 1):
                if red_head_coords == c.coords(y_s.segments[index].instance):
                    print("Yellow snake killed red snake after", game_heartbeats, "game heartbeats!")
                    IN_GAME = False
                    GAME_MODE = 0

        # Red snake kills yellow snake
        if 0 == yellow_immunity:
            for index in range(len(r_s.segments) - 1):
                if yellow_head_coords == c.coords(r_s.segments[index].instance):
                    print("Red snake killed yellow snake after", game_heartbeats, "game heartbeats!")
                    IN_GAME = False
                    GAME_MODE = 0
        
        
        # game state variables
        if 0 < yellow_immunity:
            yellow_immunity -= 1
        if 0 < red_immunity:
            red_immunity -= 1
        game_heartbeats += 1
        root.after(150, main)
        
        
    # if crash, end game
    else:
        set_state(play_text, 'normal')
        set_state(simulate_text, 'normal')
        set_state(game_over_text, 'normal')
        set_state(remote_simulate_text, 'normal')
        game_heartbeats = 0
        yellow_immunity = 0
        red_immunity = 0

# Game grid

# Window setup
root = Tk()
root.title("PSA INFO 6205 Snake game")

c = Canvas(root, width=WIDTH, height=HEIGHT, bg="#003300")
c.grid()

# Text on screen
c.focus_set()
game_over_text = c.create_text(WIDTH/2, HEIGHT/2, text="Game over!",
                               font='Arial 20', fill='red',
                               state='hidden')
play_text = c.create_text(WIDTH/2, HEIGHT - HEIGHT/3,
                             font='Arial 20',
                             fill='white',
                             text="Click here to play single-user game",
                             state='hidden')
simulate_text = c.create_text(WIDTH/2, HEIGHT-HEIGHT/4,
                             font='Arial 20',
                             fill='yellow',
                             text="Click here to simulate dueling snakes",
                             state='hidden')
remote_simulate_text = c.create_text(WIDTH/2, HEIGHT- HEIGHT/5,
                             font='Arial 20',
                             fill='red',
                             text="Click here to simulate dueling snakes with remote servers",
                             state='hidden')

c.tag_bind(play_text, "<Button-1>", clicked)
c.tag_bind(simulate_text, "<Button-1>", clicked2)
c.tag_bind(remote_simulate_text, "<Button-1>", clicked3)

# Play Game
# To play the game, run all cells above with the jupyter menu Cell | Run all Above, then run one of the three cells below (not all three!) and select the mode you picked. The game will start.

# If you picked the remote servers dueling snakes AI mode, don't forget to start both servers, first.

# The dueling snakes simulation game is programmed so that snakes will automatically avoid obstacles and randomly change directions, getting fatter and fatter in order to become more and more lethal.

# To stop the game, close the game window. To restart another game, choose Kernel | Restart Kernel from jupyter menu above, then, again, rerun all cells above and pick one of the three cells below.

# A Window will appear. Select your game mode.

# The output of the cell below will let you know which snake won.





# AI mode with remote game servers
# Please pick remote servers option from screen menu.

# Before you run the cell below, start the remote servers from the last section below...

# Then, test your yellow snake server with this code:

# call_snake_server('127.0.0.1', 5001, b'10,20,30,40,50,60,70,80,90,99')[2:-1]
# If no errors, then run the game loop:

start_game3()
root.mainloop()

