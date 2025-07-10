import tkinter as tk
from tkinter import messagebox
import ipaddress
import logging
from PIL import Image, ImageTk

import Client.Backend as Backend
import Utils.GameState as GameState

TABLE_H = 675
TABLE_W = 800
TEXT_W = 100
TEXT_H = 75
HAND_H = (TABLE_H - TEXT_H) // 4

CARD_H = 96
CARD_W = 71

TABLE_COLOR = "GREEN"

class UI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Connect to Server")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        # self.wm_attributes('-transparentcolor', '#ab23ff')

        self.state = None

        self.backend = None
        self.children_widgets = []

        self.create_widgets()

        self.images = GameState.load_images()

    def create_widgets(self):
        # Server IP input
        self.clear_screen()

        self.ip_label = tk.Label(self, text="Server IP:")
        self.ip_label.grid(row=0, column=0, sticky="e", padx=5, pady=5)

        self.ip_entry = tk.Entry(self, width=40)
        self.ip_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        self.connect_button = tk.Button(self, text="Connect", command=self.connect_to_server)
        self.connect_button.grid(row=0, column=2, sticky="w", padx=5, pady=5)

        self.children_widgets = [self.ip_label, self.ip_entry, self.connect_button]

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
            self.backend = Backend.Backend(host, self.update, self.load_table)
            if self.backend.is_connected():
                logging.info("Connected to server.")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def load_table(self, player_nb):
        self.clear_screen()

        self.menubar = tk.Menu(self)
        self.servermenu = tk.Menu(self.menubar, tearoff=0)
        self.servermenu.add_command(label="Deal", command=self.deal)
        self.servermenu.add_separator()
        self.servermenu.add_command(label="Exit", command=self.on_close)
        self.menubar.add_cascade(label="Game", menu=self.servermenu)
        self.config(menu=self.menubar)

        self.table = tk.Frame(bg=TABLE_COLOR, height=TABLE_H, width=TABLE_W)
        self.table.pack(anchor="nw")

        # Table is split into 5 sections, 1 for each other player (top 2), middle is last play, next is player hand, last is card count
        # First 4 are all the same height, last is shorter
        keys = ["A", "B", "Last", "Mine", "Count"]
        self.hands = {}
        for ind, key in enumerate(keys[:-1]):
            self.hands[key] = (tk.Frame(self.table, height=HAND_H, width=(TABLE_W-TEXT_W), bg=TABLE_COLOR), tk.StringVar())
            self.hands[key][0].grid(row=ind, column=0, sticky="nw")
            tk.Label(self.table, textvariable=self.hands[key][1], bg=TABLE_COLOR).grid(row=ind, column=1)

            if (key != "Last"):
                self.build_hand(["back"] * 17, self.hands[key][0], self.hands[key][1])

        self.hands["Count"] = tk.StringVar()
        tk.Label(self.table, textvariable=self.hands["Count"], bg=TABLE_COLOR).grid(row=4, column=0, columnspan=2, sticky="nw")

        self.children_widgets = [self.menubar, self.servermenu, self.table]# + list(self.table.winfo_children())

        self.state = None

    def build_hand(self, hand, frame, count_str):
        for child in frame.winfo_children():
            child.destroy()

        delta_x = 0
        if len(hand) > 1:
            delta_x = (TABLE_W - TEXT_W - CARD_W) / (len(hand) - 1)
            if delta_x > CARD_W:
                delta_x = CARD_W

        curr_x = 0
        for card in hand:
            temp = tk.Label(frame, image=self.images[card], anchor="nw")#, bg='#ab23ff')
            temp.place(x=curr_x, y=(HAND_H-CARD_H)//2)
            curr_x += delta_x

        count_str.set(str(len(hand)))

    def update(self, state):

        self.build_hand(["back"] * state["others"][0], self.hands["A"][0], self.hands["A"][1])
        self.build_hand(["back"] * state["others"][1], self.hands["B"][0], self.hands["B"][1])

        self.build_hand(state["last_play"], self.hands["Last"][0], self.hands["Last"][1])

        if self.state == None:
            # Update whole screen
            self.state = state
            self.build_hand(state["hand"], self.hands["Mine"][0], self.hands["Mine"][1])
        else:
            # Update only diff
            temp_hand = self.state["hand"]
            self.state = state
            self.state["hand"] = []
            if temp_hand != state["hand"]:
                for card in temp_hand:
                    if card in state["hand"]:
                        self.state["hand"].append(card)

    def deal(self):
        # TODO add confirmation!
        self.backend.send_deal()

    def clear_screen(self):
        self.config(menu=None)
        for child in self.children_widgets:
            child.destroy()

        self.children_widgets = []

    def disconnect(self):
        if self.backend:
            self.backend.close()

        self.create_widgets()

    def on_close(self):
        if self.backend:
            self.backend.close()
        self.destroy()

if __name__ == "__main__":
    app = UI()
    app.mainloop()
