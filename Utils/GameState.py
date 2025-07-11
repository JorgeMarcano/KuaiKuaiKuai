import random
import logging
from PIL import Image, ImageTk

list_of_suits = ["c", "s", "d", "h"]
list_of_values = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13"]

list_of_cards = []
for suit in list_of_suits:
    for value in list_of_values:
        list_of_cards.append(value+suit)

def load_images():
    images = {}
    for card in list_of_cards:
        images[card] = ImageTk.PhotoImage(Image.open("cardset-standard/"+card+".gif"))

    images["back"] = ImageTk.PhotoImage(Image.open("cardset-standard/back192.gif"))

    return images

class Game():
    def __init__(self, player_nb):
        # player_nb goes from 0 to 2, -1 for server to ignore
        self.payer_nb = player_nb

        self.current_player = -1
        self.deck_pile = []
        self.discard_pile = []
        self.last_play = []

        self.player_piles = [[] for i in range(3)]

        self.player_alias = [f"Player {i}" for i in range(3)]

    def initialize(self):
        # Choose a random player
        self.current_player = random.randint(0, 2)

        # Randomly shuffle the deck
        self.deck_pile = list_of_cards[:]
        random.shuffle(self.deck_pile)

        # Empty the discard pile
        self.discard_pile = []
        self.last_play = []

        # Deal out the cards
        for player in range(3):
            self.player_piles[player] = self.deck_pile[:17]
            self.deck_pile = self.deck_pile[17:]

    def pack_game(self):
        pack = ""

        # Start with current player
        pack += str(self.current_player) + ";"
        # Add cards in deck
        pack += ",".join(self.deck_pile) + ";"
        # Add cards in discard
        pack += ",".join(self.discard_pile) + ";"
        # Add players hands
        pack += ";".join([",".join(i) for i in self.player_piles])

        return pack

    def unpack_game(self, pack):
        # Reverse of pack
        piles = pack.split(";")

        if len(piles) != 6:
            logging.error("Invalid packing!")
            return

        self.current_player = int(piles[0])
        self.deck_pile = piles[1].split(',')
        self.discard_pile = piles[2].split(',')
        for i in range(3):
            self.player_piles[i] = piles[3+i].split(',')

    def verify_play(self, player, cards):
        if self.current_player != player:
            logging.error("Wrong player!")
            return False

        if len(cards) == 0:
            logging.error("Empty cards!")
            return False

        # TODO: do rest of checking!
        for card in cards:
            if card not in self.player_piles[player]:
                logging.error("Not valid card!")
                return False

        return True

    def do_play(self, player, cards):
        if not self.verify_play(player, cards):
            logging.error("Illegal play!")
            return False

        for card in self.last_play:
            self.discard_pile.append(card)

        self.last_play = cards[:]

        for card in cards:
            self.player_piles[player].remove(card)

        self.current_player += 1
        self.current_player %= 3

        return True

    def pack_play(self, player, cards):
        pack = ""
        pack += str(player) + ";"
        pack += ",".join(cards)

        return pack

    def give_player_state(self, player):
        state = {}

        state["hand"] = self.player_piles[player][:]
        state["hand"].sort()

        state["others"] = []
        for i in range(3):
            if i != player:
                state["others"].append(len(self.player_piles[i]))

        state["discard"] = self.discard_pile[:]
        state["last_play"] = self.last_play[:]

        state["current_player"] = self.current_player

        return state

    def set_alias(self, player, alias):
        if player >= 0 and player <=2:
            self.player_alias[player] = alias
