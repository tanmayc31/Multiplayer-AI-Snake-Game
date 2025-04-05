# Test server with Python3:
from socket.python3.server import Server # type: ignore
class MyServer(Server):
    def act_on(self, data, addr):
        # Do something with data (in bytes) and return a string.
        return data.decode()
server = MyServer(listening_address=('127.0.0.1', 11113))
server.listen()