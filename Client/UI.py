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
HAND_W = (TABLE_W-TEXT_W)

CARD_H = 96
CARD_W = 71
CARD_Y = (HAND_H-CARD_H)//2

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

        self.selected_cards = []

        self.ui_create_widgets()

        self.images = GameState.load_images()
        self.dummy_img = tk.PhotoImage()

    def ui_create_widgets(self):
        # Server IP input
        self.ui_clear_screen()

        self.ip_label = tk.Label(self, text="Server IP:")
        self.ip_label.grid(row=0, column=0, sticky="e", padx=5, pady=5)

        self.ip_entry = tk.Entry(self, width=40)
        self.ip_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        self.connect_button = tk.Button(self, text="Connect", command=self.sv_connect_to_server)
        self.connect_button.grid(row=0, column=2, sticky="w", padx=5, pady=5)

        self.children_widgets = [self.ip_label, self.ip_entry, self.connect_button]

    def sv_connect_to_server(self):
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
            self.backend = Backend.Backend(host, self.ui_update, self.ui_load_table)
            if self.backend.is_connected():
                logging.info("Connected to server.")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def ui_create_menu(self):
        self.menubar = tk.Menu(self)

        self.servermenu = tk.Menu(self.menubar, tearoff=0)
        self.servermenu.add_command(label="Deal", command=self.deal)
        self.servermenu.add_separator()
        self.servermenu.add_command(label="Disconnect", command=self.disconnect)
        self.servermenu.add_command(label="Exit", command=self.on_close)
        self.menubar.add_cascade(label="Game", menu=self.servermenu)

        self.viewmenu = tk.Menu(self.menubar, tearoff=0)
        self.viewmenu.add_command(label="Set Alias", command=self.set_alias)
        self.menubar.add_cascade(label="View", menu=self.viewmenu)

        self.settingmenu = tk.Menu(self.menubar, tearoff=0)
        self.settingmenu.add_command(label="Sort by Number", command=lambda: self.sort_cards("number"))
        self.settingmenu.add_command(label="Sort by Suit", command=lambda: self.sort_cards("suit"))
        self.menubar.add_cascade(label="Setting", menu=self.settingmenu)

        self.config(menu=self.menubar)

        self.children_widgets.append(self.menubar)
        self.children_widgets.append(self.servermenu)
        self.children_widgets.append(self.settingmenu)
        self.children_widgets.append(self.viewmenu)

    def ui_load_table(self, player_nb):
        # Change title
        self.title(f"Connected to {self.ip_entry.get()}")
        # Clear screen
        self.ui_clear_screen()
        # Create Menu Bar
        self.ui_create_menu()

        self.table = tk.Frame(bg=TABLE_COLOR, height=TABLE_H, width=TABLE_W)
        self.table.pack(anchor="nw")

        # Table is split into 5 sections, 1 for each other player (top 2), middle is last play, next is player hand, last is card count
        # First 4 are all the same height, last is shorter
        keys = ["A", "B", "Last", "Mine", "Count"]
        self.hands = {}
        for ind, key in enumerate(keys[:-1]):
            self.hands[key] = (tk.Frame(self.table, height=HAND_H, width=HAND_W, bg=TABLE_COLOR), tk.StringVar())
            self.hands[key][0].grid(row=ind, column=0, sticky="nw")

            if (key != "Last"):
                self.game_build_hand(["back"] * 17, self.hands[key][0], self.hands[key][1])
                tk.Label(self.table, textvariable=self.hands[key][1], bg=TABLE_COLOR).grid(row=ind, column=1, sticky="e")
            else:
                self.play_btn = tk.Button(self.table, text="Play", image=self.dummy_img, compound="c", command=self.play_selected, width=TEXT_W, height=HAND_H, state="disabled")
                self.play_btn.grid(row=ind, column=1, sticky="e")

        self.hands["Count"] = tk.StringVar()
        tk.Label(self.table, textvariable=self.hands["Count"], bg=TABLE_COLOR).grid(row=4, column=0, columnspan=2, sticky="nw")

        # Save Children
        self.children_widgets.append(self.table)# + list(self.table.winfo_children())

        # Clear Game State
        self.state = None

    def game_build_hand(self, hand, frame, count_str, onclick=None):
        for child in frame.winfo_children():
            child.destroy()

        delta_x = 0
        curr_x = 0
        if len(hand) > 1:
            delta_x = (TABLE_W - TEXT_W - CARD_W) / (len(hand) - 1)

            if delta_x > CARD_W:
                delta_x = CARD_W
                total_x = delta_x * len(hand)
                curr_x = (HAND_W - total_x) // 2

        for card in hand:
            temp = tk.Label(frame, image=self.images[card], anchor="nw", highlightbackground="orange", highlightcolor="orange", highlightthickness=0)#, bg='#ab23ff')
            temp.place(x=curr_x, y=(HAND_H-CARD_H)//2)
            curr_x += delta_x

            if onclick != None:
                temp.bind("<Button-1>", lambda e, card=card: onclick(e, card))

            if card in self.selected_cards:
                widget.config(highlightthickness=4)
                widget.place(y=0)

        count_str.set(str(len(hand)))

    def ui_update(self, state, force=False):
        # Update the number of ocards of the other people
        self.game_build_hand(["back"] * state["others"][0], self.hands["A"][0], self.hands["A"][1])
        self.game_build_hand(["back"] * state["others"][1], self.hands["B"][0], self.hands["B"][1])

        # Update Last Play
        self.game_build_hand(state["last_play"], self.hands["Last"][0], self.hands["Last"][1])

        if self.state == None or force:
            # Update whole screen
            self.state = state
            # Update hand
            self.game_build_hand(state["hand"], self.hands["Mine"][0], self.hands["Mine"][1], onclick=self.on_card_click)
        else:
            # Update only diff
            temp_hand = self.state["hand"]
            self.state = state.copy()
            self.state["hand"] = []
            if set(temp_hand) != set(state["hand"]):
                for card in temp_hand:
                    if card in state["hand"]:
                        self.state["hand"].append(card)
                    if (card in self.selected_cards) and not (card in state["hand"]):
                        self.selected_cards.remove(card)

                # Update hand
                self.game_build_hand(state["hand"], self.hands["Mine"][0], self.hands["Mine"][1], onclick=self.on_card_click)

        # If it is our turn, enable button
        if self.state["current_player"] == self.backend.player_nb:
            self.play_btn.config(state="normal")
        else:
            self.play_btn.config(state="disabled")

    def deal(self):
        # TODO add confirmation!
        self.backend.send_deal()

    def ui_clear_screen(self):
        self.config(menu=None)
        for child in self.children_widgets:
            child.destroy()

        self.children_widgets = []
        self.selected_cards = []

    def on_card_click(self, event, card):
        widget = event.widget

        if card in self.selected_cards:
            # Unselect Card
            widget.config(highlightthickness=0)
            widget.place(y=CARD_Y)

            self.selected_cards.remove(card)
        else:
            # Select Card
            widget.config(highlightthickness=4)
            widget.place(y=0)

            self.selected_cards.append(card)

    def sort_cards(self, type):
        if type == "number":
            print(self.state["hand"])
            self.state["hand"].sort()

        elif type == "suit":
            pass

        self.ui_update(self.state)

    def play_selected(self):
        self.backend.play_hand(self.selected_cards)

    def set_alias(self):
        self.alias = tk.simpledialog.askstring(title="Your Alias", prompt="What's your Name?:")
        self.backend.set_alias(self.alias)

    def disconnect(self):
        if self.backend:
            self.backend.close()

        self.ui_create_widgets()

    def on_close(self):
        if self.backend:
            self.backend.close()
        self.destroy()

if __name__ == "__main__":
    app = UI()
    app.mainloop()
