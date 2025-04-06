import socket
from ast import literal_eval
import random

HOST = '0.0.0.0' # Listen on all available interfaces
PORT = 5001      # Port to listen on for yellow snakes (non-privileged ports are > 1023)

WIDTH = 800
HEIGHT = 600
SEG_SIZE = 20

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
				x1, y1, x2, y2, rx1, ry1, rx2, ry2, ax, ay = literal_eval(data.decode())
				print(x1,y1,x2,y2, "red:", rx1, ry1, rx2, ry2, "apple:", ax, ay)
				
				# Fixing collisions with field edges (or obstacles) for sim
				# (in real game, snake hitting obstacles dies!)
				print("fixing collisions...")
				if max(x1,x2) >= WIDTH - SEG_SIZE:
					#print("yellow snake, right wall")
					data_to_proxy = "Left"
            
				elif min(x1,x2) <= SEG_SIZE:
					#print("yellow snake, left wall")
					data_to_proxy = "Right"
            
				elif max(y1,y2) >= HEIGHT - SEG_SIZE:
					#print("yellow snake, top edge")
					data_to_proxy = "Up"
					
				elif min(y1,y2) <= SEG_SIZE:
					#print("yellow snake, bottom edge")
					data_to_proxy = "Down"
            
				else:
					# occasional random movements
					print("occasional random movements...")
					if random.randint(1,10) == 1:
						direction = random.randint(1,4)
						if direction == 1:
							#print("returning Up...")
							data_to_proxy = "Up"
						elif direction == 2:
							#print("returning Down...")
							data_to_proxy = "Down"
						elif direction == 3:
							#print("returning Right...")
							data_to_proxy = "Right"
						else:
							#print("returning Left...")
							data_to_proxy = "Left"
					else:
						data_to_proxy = "Straight"
		
				client_sock.sendall(data_to_proxy.encode())
				
			else:
				break

		client_sock.close()
	s.close()