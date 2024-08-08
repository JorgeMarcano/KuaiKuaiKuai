import socket
import ipaddress

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
HOST_PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

HANDSHAKE = str.encode("aok")

class Client:
    def __init__(self, host, port):
        try:
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__socket.connect((host, port))
            
            print(f"Connected to {self.__socket.getsockname()[0]}")
        except Exception as e:
            raise e

    def close(self):
        self.__socket.close()

    def send(self, message):
        self.__socket.sendall(message)
        data = self.__socket.recv(1024)

        return data

# Get Server IP
host = None
while host == None:  
    try:
        host = input("Enter server IP:")
        ipaddress.ip_address(host)
    except ValueError:
        print('address/netmask is invalid: %s' % host)
        host = None
    except:
        print('Usage : %s  ip' % host)
        host = None


client = Client(host, HOST_PORT)

print(client.send(str.encode("Test")).decode())