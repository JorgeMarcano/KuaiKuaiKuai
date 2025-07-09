import tkinter as tk
from tkinter import messagebox
import tkinter.scrolledtext as st
import ipaddress
import logging

import Backend

class UI(tk.Tk):
    def __init__(self):
        super().init()

        self.title("Client GUI")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.backend = None

        self.create_widgets()

    def create_widgets(self):
        # Server IP input
        self.ip_label = tk.Label(self, text="Server IP:")
        self.ip_label.grid(row=0, column=0, sticky="e", padx=5, pady=5)

        self.ip_entry = tk.Entry(self, width=40)
        self.ip_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        self.connect_button = tk.Button(self, text="Connect", command=self.connect_to_server)
        self.connect_button.grid(row=0, column=2, sticky="w", padx=5, pady=5)

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
            self.backend = Backend.Backend(host)
            if self.backend.is_connected():
                self.log_message("Connected to server.")
                self.load_table()
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def load_table(self):
        # TODO: once connected to server, clear window and load game board
        pass
