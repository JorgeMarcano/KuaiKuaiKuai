import logging
import select
import socket
import threading
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.scrolledtext as st

####################
# Global Variables #
####################

LOCALHOST = "127.0.0.1"  # Standard loopback interface address (localhost)
HOST = socket.gethostbyname(socket.gethostname())
HOST_PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

BUFFER_SIZE = 1024

PLAYER_CAPACITY = 3
HANDSHAKE = str.encode("aok")

####################
# Class Definition #
####################

class Host:
    def __init__(self, host, port):
        try:
            # Create members for socket and handler threads
            self.__host = host
            self.__port = port
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__socket.bind((host, port))
            self.__socket.listen(PLAYER_CAPACITY)
            self.__conns = [None] * PLAYER_CAPACITY
            self.__active_conns = 0
            self.__active_conns_str = tk.StringVar()
            self.__active_conns_str.set(self.__active_conns)
            self.__addrs = [None] * PLAYER_CAPACITY
            self.__threads = [None] * PLAYER_CAPACITY
            self.__stop_events = [threading.Event() for _ in range(PLAYER_CAPACITY)]

        except Exception as e:
            raise e

    @property
    def active_players(self):
        return self.__active_conns_str

    def run(self):
        logging.info(f"Server started on {self.__host}")

        # Start player handlers
        for i in range(PLAYER_CAPACITY):
            self.open_connection(i)

    def open_connection(self, index):
        self.__threads[index] = threading.Thread(target=self.daemon, args=(index,), daemon=True)
        self.__threads[index].start()

    def close_connection(self, index):
        try:
            self.__conns[index].shutdown(socket.SHUT_RDWR)
            self.__conns[index].close()
            self.__conns[index] = None
            self.__active_conns -= 1
            self.__active_conns_str.set(self.__active_conns)
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
        self.__active_conns_str.set(self.__active_conns)
        self.__conns[index].setblocking(False)

        logging.info(f"Connected to {self.__addrs[index][0]}:{str(self.__addrs[index][1])} as player {index + 1}")
        logging.info(f"Connected to {self.__active_conns}/{PLAYER_CAPACITY} Players")

        # Notify the client who they are
        # self.__conns[index].sendall(str.encode(f"You are player {index + 1}"))
        self.__conns[index].sendall(str.encode(f"12;{index}"))

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

                    command = data.decode()

                    logging.info(f"Received message from player {index}: {command}")

                    # TODO, check for validity

                    # Propgate move to each player
                    for __conn in (__conn for __conn in self.__conns if __conn is not None):
                        __conn.sendall(data)

        except ConnectionResetError as e:
            logging.warning(f"Client {self.__addrs[index][0]}:{str(self.__addrs[index][1])} forcefully disconnected")

        # Client has closed the connection, close server-side connection
        self.close_connection(index)

        # Reopen the connection
        self.open_connection(index)

# Class to redirect log output to a tkinter text widget
class TextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        log_message = self.format(record)
        self.text_widget.after(0, self.append_text, log_message)

    def append_text(self, log_message):
        self.text_widget.insert(tk.END, log_message + "\n")
        self.text_widget.yview(tk.END)  # Auto-scroll to the latest log

#################
# Sample Server #
#################

def runServerGUI(host=HOST, port=HOST_PORT):
    window = tk.Tk()

    window.title("KuaiKuaiKuai Kyaaaaaaa!")

    server = Host(host, port)

    # Configure grid layout
    window.columnconfigure(1, weight=1)  # Allow second column to grow
    window.rowconfigure(2, weight=1)     # Allow third row to grow

    # Add IP information
    ttk.Label(window, text="Server IP:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    ip_str = tk.StringVar(value=HOST)
    ttk.Entry(window, textvariable=ip_str, state="readonly", justify="center").grid(row=0, column=1, sticky="w", padx=5, pady=5)

    # Show number of active connected players
    ttk.Label(window, text="Connected Players:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    ttk.Entry(window, textvariable=server.active_players, state="readonly", justify="center").grid(row=1, column=1, sticky="w", padx=5, pady=5)

    # Add log for server events
    text_log = st.ScrolledText(window)
    text_log.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

    # Add close menu button
    exit_button = ttk.Button(window, text="Close Server", command=window.destroy)
    exit_button.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

    # Add logging to the text_log widget
    text_handler = TextHandler(text_log)
    text_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    # Set up the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Ensure all levels are logged
    root_logger.handlers.clear()  # Remove any default handlers
    root_logger.addHandler(text_handler)

    server.run()

    window.mainloop()

if __name__ == "__main__":
    runServerGUI()
