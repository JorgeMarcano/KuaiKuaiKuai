import ipaddress
import logging
import select
import socket
import threading
import tkinter as tk
from tkinter import messagebox
import tkinter.scrolledtext as st

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

class ClientGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Client GUI")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.client = None
        self.host_port = 65432  # Default port

        self.create_widgets()

    def create_widgets(self):

        # Configure grid layout
        self.columnconfigure(2, weight=5)  # Allow third column to grow
        self.rowconfigure(2, weight=1)     # Allow third row to grow

        # Server IP input
        self.ip_label = tk.Label(self, text="Server IP:")
        self.ip_label.grid(row=0, column=0, sticky="e", padx=5, pady=5)

        self.ip_entry = tk.Entry(self, width=40)
        self.ip_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        self.connect_button = tk.Button(self, text="Connect", command=self.connect_to_server)
        self.connect_button.grid(row=0, column=2, sticky="w", padx=5, pady=5)

        # Message input
        self.message_entry = tk.Entry(self, width=40)
        self.message_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        self.send_button = tk.Button(self, text="Send", command=self.send_message, state="disabled")
        self.send_button.grid(row=1, column=2, sticky="w", padx=5, pady=5)

        # Output display
        self.output_text = st.ScrolledText(self)
        self.output_text.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)

        # Disconnect button
        self.disconnect_button = tk.Button(self, text="Disconnect", command=self.disconnect, state="disabled")
        self.disconnect_button.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

    def connect_to_server(self):
        host = self.ip_entry.get()
        if not host:
            messagebox.showerror("Error", "Please enter the server IP.")
            return
        
        try:
            # Validate the IP address
            ipaddress.ip_address(host)
        except ValueError:
            messagebox.showerror("Error", "Invalid IP address format. Please enter a valid IP.")
            return

        try:
            self.client = Client(host, self.host_port, self.message_callback)
            if self.client.is_connected():
                self.log_message("Connected to server.")
                self.enable_controls(True)
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def message_callback(self, client):
        # Callback to process received data from the server.
        data = client.read_buffer()
        self.log_message(f"Server: {data}")

    def send_message(self):
        if self.client and self.client.is_connected():
            message = self.message_entry.get()
            if message:
                if message.lower() == "end":
                    self.disconnect()
                    return
                self.client.send(str.encode(message))
                self.message_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Not Connected", "Connect to the server first.")

    def disconnect(self):
        if self.client:
            self.client.close()
            self.log_message("Disconnected from server.")
            self.enable_controls(False)

    def log_message(self, message):
        self.output_text.configure(state="normal")
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.configure(state="disabled")

    def enable_controls(self, connected):
        # Enable or disable controls based on the connection status.
        state = "normal" if connected else "disabled"
        self.send_button.configure(state=state)
        self.disconnect_button.configure(state=state)
        self.connect_button.configure(state="disabled" if connected else "normal")
        self.message_entry.configure(state=state)

    def on_close(self):
        if self.client:
            self.client.close()
        self.destroy()


if __name__ == "__main__":
    app = ClientGUI()
    app.mainloop()

