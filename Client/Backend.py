import Utils.GameState as GameState
import Client.Client as Client

import socket
import threading
import logging

HOST_PORT = 65432

class Backend():
    def __init__(self, server_ip, update_ui, on_start):
        self.player_nb = -1 # Currently no number

        # Callback for when there is UI to update
        self.update_ui = update_ui
        # Callback for when there is a new connection
        self.on_start = on_start

        # Make new Game state instance (with no player nb yet)
        self.game = GameState.Game(-1)

        # Connect to server
        self.client = Client.Client(server_ip, HOST_PORT, self.server_event)

    def is_connected(self):
        # Feedthrough the client's
        return self.client.is_connected()

    def play_hand(self, cards):
        # Verify that the play is valid, if so, send to server
        if (self.game.verify_play(self.player_nb, cards)):
            # Send play to server
            self.client.send(self.game.pack_play(self.player_nb, cards))

    def server_event(self):
        # Sends play from server to UI, saved in buffer
        message = self.client.read_buffer()

        # First part is the key, specifying what command was sent
        unpack = message.split(";")
        if len(unpack) < 2:
            logging.error("Message from Server invalid")

        key = unpack[0]
        is_on_start = False
        is_update = False

        try:
            key = int(key)

            # If key is between 0 and 2 inclusive, it is a play by that player
            if key >= 0 and key <= 2:
                cards = unpack[1].split(",")
                self.game.do_play(key, cards)
                # Raise update UI event!
                is_update = True

            # If key is -1, it is an error
            elif key == -1:
                logging.error(f"Server Error: {unpack[1]}")

            # If key is 10, it is a new deal
            elif key == 10:
                self.game.unpack_game(";".join(unpack[1:]))
                # Raise update UI event!
                is_update = True

            # If key is 11, it is a win event
            elif key == 11:
                # TODO: This!
                pass

            # If key is 12, it is identifier
            elif key == 12:
                # Save the player nb
                self.player_nb = int(unpack[1])
                self.game.player_nb = self.player_nb
                logging.info(f"You are player {self.player_nb}")
                print(f"You are player {self.player_nb}")
                # Raise a new Connection event!
                is_on_start = True

            # If key is 13, it is alias
            elif key == 13:
                alias_player = int(unpack[1])
                alias = unpack[2]
                self.game.set_alias(alias_player, alias)

            # Invalid Key
            else:
                raise Exception()

        except Exception as e:
            logging.error(f"Event Key invalid from server: {key}")
            raise e

        # If any event was raised, send to UI
        if is_on_start:
            self.on_start(self.player_nb)
        if is_update:
            self.update_ui(self.give_state())

    def send_deal(self):
        # TODO: Make server deal instead of local player
        self.game.initialize()
        msg = "10;" + self.game.pack_game()
        self.client.send(msg)

    def give_state(self):
        # Gives up to date state of the board to UI
        return self.game.give_player_state(self.player_nb)

    def set_alias(self, alias):
        self.client.send(f"13;{self.player_nb};{alias}")

    def close(self):
        if self.client:
            self.client.close()
