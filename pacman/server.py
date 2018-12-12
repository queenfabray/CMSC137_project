import pygame
from pygame.math import Vector2
import json
import queue
import threading
import socket
import pickle

# import pong.game

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

class PacmanServer(threading.Thread, socket.socket):
    BUFFER_SIZE = 8192
    DEFAULT_PORT = 10939
    COMMAND_CLIENT_CONNECT = 'pacman_connect'
    TIMEOUT = 2.0
    COMMAND_RATE = 60   # updates per second

    def __init__(self, port=None):
        threading.Thread.__init__(self, name='Server thread')
        socket.socket.__init__(self, type=socket.SOCK_DGRAM)

        self.port = self.DEFAULT_PORT if port is None else port
        # self.settimeout(self.TIMEOUT)
        self.bind(('', self.port))
        self.clients = []
        self.player_addresses = dict()
        self._current_player_to_assign = 1
        self.client_handlers = []
        self.pacman1_props = pacman_props1
        self.pacman2_props = pacman_props2
        self.pacman3_props = pacman_props3

    def run(self):
        print('Hosting at:', self.getsockname())

        print('Starting server.')

        for i in range(3):
            player_number = i + 1

            print('Waiting for client #{}'.format(player_number))
            c = self.wait_client()
            self.clients.append(c)

            print('Sending player number {} to {}'.format(player_number, c))
            self.send_player_number(c, player_number)

            # data, address = self.recvfrom(self.BUFFER_SIZE)
            # pacman_props = pickle.loads(data)
            
            # Receive the dictionary
            # if (i+1) == 1:
            #     self.pacman1_props = pacman_props
            # else:
            #     self.pacman2_props = pacman_props

        # Send all pacmansserver_address
        # self.sendto(pickle.dumps(self.pacman1_props), self.client_address)
        # self.sendto(pickle.dumps(self.pacman2_props), self.client_address)

        print('Starting game.')
        clock = pygame.time.Clock()
        seconds_passed = 0

        while True:
            # self.pong_world.update(seconds_passed=seconds_passed)
            seconds_passed = clock.tick(self.COMMAND_RATE) / 1000
        return

    def wait_client(self, return_queue=None):
        """Step 1: Wait for a client to connect."""
        data, address_info = self.recvfrom(self.BUFFER_SIZE)
        print('data:', data, 'address_info:', address_info)

        if data:
            decoded = data.decode('utf-8')
            if decoded != self.COMMAND_CLIENT_CONNECT:
                raise ValueError('Expecting "{}", but got "{}"'.format(self.COMMAND_CLIENT_CONNECT, decoded))
            if return_queue is not None:
                return_queue['client_address'] = address_info
            # print('Client address found:', address_info)
            return address_info

    def send_player_number(self, client_address, player_number):
        """Step 2: Create a client handler object to send the player number to the connected client"""
        ch = ClientHandler(self.port + self._current_player_to_assign, client_address, player_number, self)
        self.client_handlers.append(ch)
        self._current_player_to_assign += 1
        ch.start()    # Start happens later in another function...?

        self.player_addresses[player_number] = client_address

    def join(self, timeout=None):
        super().join()
        self.close()


class ClientHandler(threading.Thread, socket.socket):
    def __init__(self, port, client_address, player_number, server):
        socket.socket.__init__(self, type=socket.SOCK_DGRAM)
        threading.Thread.__init__(self, name='ClientHandler')
        self.settimeout(2)
        self.bind(('localhost', port))
        self.setDaemon(True)
        self.player_number = player_number
        self.client_address = client_address
        self.server = server

        self.send_player_number()

    def send_player_number(self):
        self.sendto(str(self.player_number).encode('utf-8'), self.client_address)

    def send_game_update(self):
        self.sendto(self.server.pong_world.locations_json().encode('utf-8'), self.client_address)

    def receive_client_command(self, retd=None):
        data, address_info = self.recvfrom(pong.common.BUFFER_SIZE)

        if data:
            decoded = data.decode('utf-8')
            try:
                cc = json.loads(decoded, object_hook=pong.common.from_json)
            except ValueError as err:
                print(err)
                raise ValueError('Expecting a JSON string from client, but got something else:', decoded)

            if retd is not None and isinstance(retd, dict):
                retd['client_command'] = cc
            return cc

    def run(self):
        while True:
            self.send_pacman()
            self.server.pacman1_props = self.receive_pacman()
            self.server.pacman2_props = self.receive_pacman()
            self.server.pacman3_props = self.receive_pacman()

    def receive_pacman(self):
        data, address = self.recvfrom(self.server.BUFFER_SIZE)
        return pickle.loads(data)
        # self.server.client_address = address[1]

    def send_pacman(self):
        self.sendto(pickle.dumps(self.server.pacman1_props), self.client_address)
        self.sendto(pickle.dumps(self.server.pacman2_props), self.client_address)
        self.sendto(pickle.dumps(self.server.pacman3_props), self.client_address)

    def join(self, timeout=None):
        super().join(timeout=2)
        self.close()
