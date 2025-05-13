from PIL import Image, ImageTk

class Card:
    values = ("01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13")
    suits = ("c", "s", "d", "h")

    def __init__(self, value, suit, x, y, cardImage=None):
        self.__value = value
        self.__suit = suit

        self.__x = x
        self.__y = y

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
    def card_image(self):
        return self.__cardImage

    @property
    def sv(self):
        return (self.__value, self.__suit)

    @property
    def coord(self):
        return (self.__x, self.__y)

    @coord.setter
    def coord(self, coords):
        self.__x, self.__y = coords

    def __eq__(self, other):
        return ((self.__suit == other.suit) and (self.__value == other.value))

    def __lt__(self, other):
        if (self.value < other.value):
            return True
        if (self.value > other.value):
            return False
        
        return (self.__suit < other.suit)

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

    def remove_cards(self, cards=None):
        if cards == None:
            self.__cards = []

        for card in cards:
            if not (card is Card):
                raise Exception

            if not (card in self.__cards):
                raise Exception

            self.__cards.remove(card)

    def order_cards(self, startX, startY, deltaX, deltaY):
        #cards should be ordered by number first and suit second
        self.__cards.sort()
        self.__cards.reverse()
        x = startX
        y = startY

        for card in self.__cards:
            card.coord = (x, y)
            x += deltaX
            y += deltaY

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
        self.__deck = {}

        for v in Card.values:
            for s in Card.suits:
                # Only 3 Aces
                if (v == "01" and s == "c"):
                    continue
                # Only one 2
                if (v == "02" and s != "h"):
                    continue

                self.__deck[(v, s)] = Card(v, s, 0, 0)

    def find_card(self, value, suit):
        try:
            return self.__deck[(value, suit)]
        except KeyError:
            return None

    def play_cards(self, player, cards):
        if player > 2:
            return

        card_list = [self.find_card(value, suit) for (value, suit) in cards]
        self.__player_hands[player].remove_cards(card_list)
        self.__player_played[player].add_cards(card_list)

    def discard(self, player):
        if player > 2:
            return

        self.__discard.add_cards(self.__player_played[player].cards)
        self.__player_played[player].remove_cards()

    def deal(self, cards):
        # cards are listed as such, [1,2,3,1,2,3,1,2,3,...]

        card_list = [self.find_card(value, suit) for (value, suit) in cards]
        self.__discard.remove_cards()
        for i in range(3):
            self.__player_hands[i].remove_cards()
            self.__player_played[i].remove_cards()
            self.__player_hands[i].add_cards(card_list[i::3])

    def get_coords(self):
        return [card.coord for card in self.__deck]
