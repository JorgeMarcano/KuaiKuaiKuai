import logging
import select
import socket
import threading

####################
# Global Variables #
####################

LOCALHOST = "127.0.0.1"  # Standard loopback interface address (localhost)
HOST = socket.gethostbyname(socket.gethostname())
HOST_PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

BUFFER_SIZE = 1024

PLAYER_CAPACITY = 2
HANDSHAKE = str.encode("aok")

logging.basicConfig(level=logging.DEBUG)

####################
# Class Definition #
####################

class Host:
    def __init__(self, host, port):
        try:
            # Create members for socket and handler threads
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__socket.bind((host, port))
            self.__socket.listen(PLAYER_CAPACITY)
            self.__conns = [None] * PLAYER_CAPACITY
            self.__active_conns = 0
            self.__addrs = [None] * PLAYER_CAPACITY
            self.__threads = [None] * PLAYER_CAPACITY
            self.__stop_events = [threading.Event() for _ in range(PLAYER_CAPACITY)]

            logging.info(f"Server started on {host}")

            # Start player handlers
            for i in range(PLAYER_CAPACITY):
                self.open_connection(i)
            
            # Wait for enough players to connect
            logging.info(f"Waiting for Players...")
            while self.__active_conns < PLAYER_CAPACITY:
                continue
            
            logging.info("Connected to " + ' & '.join([(i[0]+":"+str(i[1])) for i in self.__addrs]))

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

        # Close all open threads
        for i in range(PLAYER_CAPACITY):
            if self.__conns[i] is not None:
                self.__stop_events[i].set()
                self.__threads[i].join()
                self.close_connection(i)

        try:
            self.__socket.shutdown(socket.SHUT_RDWR)
            self.__socket.close()
        except (OSError, AttributeError):
            # Ignore errors if the socket is already closed
            pass
        finally:
            self.__socket = None
            logging.info("Server socket has been closed")

    def daemon(self, index):
        # Establish connection with client
        logging.info(f"Attempting connection for player {index + 1}")
        self.__conns[index], self.__addrs[index] = self.__socket.accept()
        self.__active_conns += 1
        self.__conns[index].setblocking(False)

        logging.info(f"Connected to {self.__addrs[index][0]}:{str(self.__addrs[index][1])} as player {index + 1}")
        logging.info(f"Connected to {self.__active_conns}/{PLAYER_CAPACITY} Players")

        try:
            while True:
                if self.__stop_events[index].is_set():
                    return
                
                readable, _, _ = select.select([self.__conns[index]], [], [], 1)

                if readable:
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

#################
# Sample Server #
#################

server = Host(HOST, HOST_PORT)

logging.info("Server is active! Type \"end\" to Deactivate server...")

while True:
    user_input = input()
    if user_input == "end":
        break

server.close()
