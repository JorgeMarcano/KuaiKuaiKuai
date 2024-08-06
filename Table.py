import random
import time
from tkinter import *
from PIL import Image, ImageTk

class Card:
    __values = ("01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13")
    __suits = ("c", "s", "d", "h")

    def __init__(self, value, suit, cardImage=None):
        self.__value = value
        self.__suit = suit
        
        self.__cardImage = cardImage
        if cardImage == None:
            ImageTk.PhotoImage(Image.open("cardset-standard/"+value+suit+".gif"))

    @property
    def value(self):
        return self.__value

    @property
    def suit(self):
        return self.__suit

    @property
    def cardImage(self):
        return self.__cardImage

    @property
    def sv(self):
        return (self.__value, self.__suit)

    @staticmethod
    def fresh_deck():
        cards = []
        for v in Card.__values:
            for s in Card.__suits:
                # Only 3 Aces
                if (v == "01" and s == "c"):
                    continue
                # Onlye one 2
                if (v == "02" and s != "h"):
                    continue

                cards.append(Card(v, s))

        random.shuffle(cards)
        return cards

    def __eq__(self, other):
        return ((self.__suit == other.suit()) and (self.__value == other.value()))

class Pile:
    def __init__(self, cards=None, visible=None):
        self.__cards = cards if cards != None else []
        self.__visible = visible if visible != None else False

    def add_cards(self, cards):
        for card in cards:
            if not (card is Card):
                raise Exception

            if not (card in self.__cards):
                self.__cards.append(card)

    def remove_cards(self, cards):
        for card in cards:
            if not (card is Card):
                raise Exception

            if not (card in self.__cards):
                raise Exception

            self.__cards.remove(card)

    @property
    def cards(self):
        return self.__cards

    @property
    def visible(self):
        return self.__visible

    @visible.setter
    def visible(self, value):
        self.__visible = value

    def compile(self):
        return Pile.compile_set(self.__cards)

    @staticmethod
    def compile_set(cards):
        deck_list = []

        for card in cards:
            deck_list.append(card.sv)

        return deck_list

class Table:
    def __init__(self):
        self.__player_hands = [Pile() for i in range(3)]
        self.__player_played = [Pile() for i in range(3)]
        self.__discard = Pile()
        self.__deck = []

    def new(self, deck=None):
        self.__deck = deck if deck != None else Card.fresh_deck()

        for index, player in enumerate(self.__player_piles):
            player.add_cards(deck[index::3])

    def load(self, deck_list):
        deck = []
        for (v, s) in deck_list:
            deck.append(Card(v, s))

        self.new(deck)

    def compile(self):
        deck_list = []

        for card in self.__deck:
            deck_list.append(card.sv)

        return deck_list

    @staticmethod
    def export_pile(pile_list):
        outputStr = ",".join([f"{i}-{j}" for i, j in pile_list])
        return f"S:{outputStr}:E"

    @staticmethod
    def import_pile(sentence):
        sections = sentence.split(":")
        if len(sections) != 3 or sections[-1] != "E" or sections[0] != "S":
            raise Exception

        card_list = sections[1].split(",")
        card_list = [card.split("-") for card in card_list]
        
        return [(i, j) for i, j in card_list]