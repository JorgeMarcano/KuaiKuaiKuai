import KuaiKuaiKuai.Utils.GameState as GameState
import Client

import socket
import threading
import logging

HOST_PORT = 65432

class Backend(GameState.Game):
    def __init__(self, server_ip):
        self.player_nb = -1
        # Connect to server
        self.client = Client.Client(server_ip, HOST_PORT, self.server_event)

        # Await server welcome message (including player ID) TODO
        while (self.player_nb == -1):
            continue

        super().__init__(player_nb)
        pass

    def is_connected(self):
        return self.client.is_connected()

    def play_hand(self, cards):
        # Sends play from UI to server TODO
        pass

    def server_event(self):
        # Sends play from server to UI, saved in buffer TODO
        pass

    def give_state(self):
        # Gives up to date state of the board to UI
        return self.give_player_state(self.player_nb)
