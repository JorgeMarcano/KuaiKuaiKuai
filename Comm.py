import socket

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

class Host:
    def __init__(self, host, port):
        try:
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__socket.bind((HOST, PORT))
            self.__socket.listen()
            self.__conns = []
            self.__addrs = []

            for i in range(2):
                self.__conns[i], self.__addrs[i] = self.__socket.accept()
            
            print(f"Connected by {' & '.join(self.__addrs)}")
        except Exception as e:
            raise e

    def close(self):
        self.__conn.close()
        self.__socket.close()

    def deamon(self):
        while True:
            data = self.__conn.recv(1024)
            if not data:
                break
            self.__conn.sendall(data)