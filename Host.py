import logging
import socket
import threading

LOCALHOST = "127.0.0.1"  # Standard loopback interface address (localhost)
HOST = socket.gethostbyname(socket.gethostname())
HOST_PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

BUFFER_SIZE = 1024

PLAYER_CAPACITY = 2
HANDSHAKE = str.encode("aok")

logging.basicConfig(level=logging.DEBUG)

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

            logging.info(f"Server started on {host}")

            # Start player handlers
            for i in range(PLAYER_CAPACITY):
                self.open_connection(i)
            
            # Wait for enough players to connect
            logging.info(f"Waiting for Players...")
            while self.__active_conns < PLAYER_CAPACITY:
                continue
            
            logging.info("Connected by " + ' & '.join([(i[0]+":"+str(i[1])) for i in self.__addrs]))

        except Exception as e:
            raise e

    def open_connection(self, index):
        self.__threads[index] = threading.Thread(target=self.daemon, args=(index,), daemon=True)
        self.__threads[index].start()

    def close_connection(self, index):
        try:
            self.__conns[index].shutdown(socket.SHUT_RDWR)
            self.__conns[index].close()
            self.__conns[index] = None
            self.__active_conns -= 1
            logging.info(f"Disconnected from player {index + 1}")
            logging.info(f"Connected to {self.__active_conns}/{PLAYER_CAPACITY} Players")
        except:
            logging.warning("Closing a connection failed")

    def close(self):
        try:
            self.__socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            # Ignore error if the socket is already closed
            pass
        finally:
            self.__socket.close()
            self.__socket = None
            logging.info("Server socket has been closed")

    def daemon(self, index):
        # Establish connection with client
        self.__conns[index], self.__addrs[index] = self.__socket.accept()
        self.__active_conns += 1
        logging.info(f"Connected to {self.__addrs[index][0]}:{str(self.__addrs[index][1])} as player {index + 1}")
        logging.info(f"Connected to {self.__active_conns}/{PLAYER_CAPACITY} Players")

        try:
            while True:
                # Listen for move
                data = self.__conns[index].recv(BUFFER_SIZE)
                if not data:
                    break

                logging.info(f"Received message from player {index + 1}: {data.decode()}")

                # Propgate move to each player
                for __conn in (__conn for __conn in self.__conns if __conn is not None):
                    __conn.sendall(data)
        except ConnectionResetError as e:
            logging.warning(f"Client {self.__addrs[index][0]}:{str(self.__addrs[index][1])} forcefully disconnected")

        # Client has closed the connection, close server-side connection
        self.close_connection(index)

        # Reopen the connection
        self.open_connection(index)

server = Host(HOST, HOST_PORT)

logging.info("Server is active! Type \"end\" to Deactivate server...")

while True:
    user_input = input()
    if user_input == "end":
        break

server.close()
