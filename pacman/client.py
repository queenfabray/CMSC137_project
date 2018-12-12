import json
import random
import threading
import socket
import pickle
import time

pacman_props1 = {
    "image": 'right',
    "x": 416,
    "y": 544,
    "direction": 'right',
    "life": 3,
    "score": 0,
    "can_eat": False
}

pacman_props2 = {
    "image": 'right',
    "x": 390,
    "y": 544,
    "direction": 'right',
    "life": 3,
    "score": 0,
    "can_eat": False
}

pacman_props3 = {
    "image": 'right',
    "x": 450,
    "y": 544,
    "direction": 'right',
    "life": 3,
    "score": 0,
    "can_eat": False
}

class ServerHandler(socket.socket, threading.Thread):
    BUFFER_SIZE = 8192
    COMMAND_CLIENT_CONNECT = 'pacman_connect'

    def __init__(self, bind_address, server_address, pacman_props, ghost_group):
        socket.socket.__init__(self, type=socket.SOCK_DGRAM)
        threading.Thread.__init__(self)
        self.settimeout(2)
        self.setDaemon(True)
        self.bind(bind_address)
        self.server_address = server_address
        self.player_number = -1
        self.ghost_group = ghost_group
        self.client_address = bind_address[1]
        self.pacman1_props = pacman_props1
        self.pacman2_props = pacman_props2
        self.pacman3_props = pacman_props3

    def run(self):
        self.connect()
        self.player_number = self.receive_player_number()

        # if (self.player_number != -1):
        #     # Send pacman group
        #     if self.player_number == 1:
        #         self.sendto(pickle.dumps(self.pacman1_props), self.server_address)

        #     else:
        #         self.sendto(pickle.dumps(self.pacman1_props), self.server_address)

        # data, address = self.recvfrom(self.BUFFER_SIZE)
        # self.pacman_groups = pickle.loads(data)
        # self.client_address = address[1]

        # Receive all pacmans
        # pacman1_props = self.receive_pacman()
        # pacman2_props = self.receive_pacman()

        # data, address = self.recvfrom(self.BUFFER_SIZE)
        # self.players_all_in = pickle.loads(data)

        # while True:
        #     self.pacman1_props = self.receive_pacman()
        #     self.pacman2_props = self.receive_pacman()
        #     self.send_pacman()

    def __del__(self):
        self.close()

    def connect(self):
        self.sendto(self.COMMAND_CLIENT_CONNECT.encode('utf-8'), self.server_address)
        return

    def receive_pacman(self):
        data, address = self.recvfrom(self.BUFFER_SIZE)
        return pickle.loads(data)

    def send_pacman(self):
        self.sendto(pickle.dumps(self.pacman1_props), self.server_address)
        self.sendto(pickle.dumps(self.pacman2_props), self.server_address)
        self.sendto(pickle.dumps(self.pacman3_props), self.server_address)

    def receive_player_number(self, return_dict=None):
        data, address = self.recvfrom(self.BUFFER_SIZE)

        if data is None:
            return -1

        decoded = data.decode('utf-8')

        try:
            player_number = int(decoded)
            print('player_number', player_number)
        except ValueError as err:
            raise ValueError(err + ' Should have received an integer!')

        if return_dict is not None and isinstance(return_dict, dict):
            return_dict['player_number'] = player_number

        # OVERWRITE self.server_address to the one received, since that will be address of the client handler
        self.server_address = address

        return player_number

    def receive_game_update_json(self, return_dict=None):
        data, address = self.recvfrom(self.BUFFER_SIZE)
        if data is None:
            raise ValueError('Unable to receive game update!')
            return -1

        decoded_json = data.decode('utf-8')

        try:
            # pong_update = json.loads(decoded_json, object_hook=pong.common.from_json)
            pass
        except json.JSONDecodeError as err:
            raise json.JSONDecodeError(err + ' Not a JSON string!')
            
        if return_dict is not None and isinstance(return_dict, dict):
            return_dict['game_update_json'] = decoded_json

        return decoded_json

    def send_client_command(self):
        # self.sendto(pongserver.server.PongServer.COMMAND_CLIENT_CONNECT.encode('utf-8'), self.server_address)
        if self.client_command is None:
            print('Unable to send client command: None!')
            return
        self.sendto(self.client_command.json().encode('utf-8'), self.server_address)
        return