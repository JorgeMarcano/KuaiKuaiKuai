import ipaddress
import logging
import select
import socket
import threading

####################
# Global Variables #
####################

LOCALHOST = "127.0.0.1"  # Standard loopback interface address (localhost)
HOST_PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

BUFFER_SIZE = 1024

HANDSHAKE = str.encode("aok")

logging.basicConfig(level=logging.DEBUG)

####################
# Class Definition #
####################

class Client:
    def __init__(self, host, port, callback = None):
        try:
            # Create members for socket, read data buffer, and callback
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__buffer = [0] * BUFFER_SIZE
            self.__buffer_full = False
            self.__callback = callback
            self.__thread = None
            self.__stop_event = threading.Event()
            
            # Connect to server
            self.__socket.connect((host, port))
            logging.info(f"Connected to {self.__socket.getsockname()[0]}")

            # Listen for server activity on another thread
            self.__thread = threading.Thread(target=self.daemon, daemon=True)
            self.__thread.start()

        except ConnectionRefusedError as e:
            logging.error(f"Machine at {host} refused connecton")
            self.__socket = None

        except Exception as e:
            raise e

    def close(self):
        # Stop daemon thread
        self.__stop_event.set()
        self.__thread.join()

        self.close_socket()

    def close_socket(self):
        try:
            self.__socket.shutdown(socket.SHUT_RDWR)
            self.__socket.close()
        except (OSError, AttributeError):
            # Ignore errors if the socket is already closed
            pass
        finally:
            self.__socket = None
            logging.info("Client socket has been closed")

    def daemon(self):
        self.__socket.setblocking(False)
        try:
            while True:
                if self.__stop_event.is_set():
                    return

                readable, _, _ = select.select([self.__socket], [], [], 1)

                if readable:
                    # Listen for moves from server
                    self.__buffer = self.__socket.recv(BUFFER_SIZE)
                    self.__buffer_full = True

                    if not self.__buffer:
                        break

                    logging.info(f"Received data: {self.__buffer.decode()}")

                    # The callback is called whenever the client receives data
                    if self.__callback:
                        self.__callback(self)

        except ConnectionResetError:
            logging.warning(f"The server forcefully disconnected")

        # Server has closed the connection, close client-side connection
        logging.info(f"Closing connection due to server disconnect")
        self.close_socket()

    def send(self, message):
        self.__socket.sendall(message)

    def is_connected(self):
        return self.__socket and self.__socket.fileno() != -1
    
    def is_buffer_full(self):
        return self.__buffer_full == True

    def read_buffer(self):
        self.__buffer_full = False
        return self.__buffer.decode()

#################
# Sample Client #
#################

import msvcrt # used to check is sys.stdin has pending inputs

####################
# Helper Functions #
####################

# Get Server IP using console
def get_host_IP_from_user():
    host = None
    while host == None:  
        try:
            host = input("Enter server IP:")
            ipaddress.ip_address(host)
        except ValueError:
            logging.error('address/netmask is invalid: %s' % host)
            host = None
        except:
            logging.error('Usage : %s  ip' % host)
            host = None
    
    return host

# Simple callback that prints the data received from the server in reverse
def sample_callback(client):
    print(f"Callback Output: {client.read_buffer()[::-1]}")

#############
# Main loop #
#############

while True:
    # Establish connection with server
    while True:
        host = get_host_IP_from_user()
        client = Client(host, HOST_PORT, sample_callback)

        if client.is_connected():
            break

    # Run Client
    print(f"Type messages and press enter to send them to the server (type \"end\" to close client)")
    while True:

        # Read user input if available
        if msvcrt.kbhit():
            user_input = input()
            if user_input == "end" or not client.is_connected():
                client.close()
                break

            client.send(str.encode(user_input))

        # Exit if the server was closed
        if not client.is_connected():
            break

    if input("Reconnect to server? (y/n): ").lower() == 'n':
        break
