import socket
import threading

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
HOST_PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

PLAYER_CAPACITY = 2
HANDSHAKE = str.encode("aok")

class Host:
    def __init__(self, host, port):
        try:
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__socket.bind((host, port))
            self.__socket.listen(PLAYER_CAPACITY)
            self.__conns = [None] * PLAYER_CAPACITY
            self.__active_conns = 0
            self.__addrs = [None] * PLAYER_CAPACITY
            self.__threads = [None] * PLAYER_CAPACITY

            print(f"Server started on {host}")

            # Start player handlers
            for i in range(PLAYER_CAPACITY):
                self.open_connection(i)
            
            # Wait for enough players to connect
            print(f"Waiting for Players...", end="\r")
            while self.__active_conns < PLAYER_CAPACITY:
                print(f"Connected to {self.__active_conns}/{PLAYER_CAPACITY} Players", end="\r")
            
            print("Connected by " + ' & '.join([(i[0]+":"+str(i[1])) for i in self.__addrs]))

        except Exception as e:
            raise e

    def open_connection(self, index):
        self.__conns[index], self.__addrs[index] = self.__socket.accept()
        self.__threads[index] = threading.Thread(target=self.daemon, args=(index,), daemon=True)
        self.__threads[index].start()
        self.__active_conns += 1


    def close(self):
        self.__socket.close()

    def daemon(self, index):
        while True:
            # Listen for move
            data = self.__conns[index].recv(1024)
            if not data:
                break

            # Propgate move to each player
            for __conn in (__conn for __conn in self.__conns if __conn is not None):
                __conn.sendall(data)

        # Client has closed the connection, close server-side connection and repoen
        self.__conns[index].close()
        self.__conns[index] = None
        self.__active_conns -= 1
        self.open_connection(index)

server = Host(HOST, HOST_PORT)

_ = input("Server is active! Press enter to Deactivate server...")

server.close()
