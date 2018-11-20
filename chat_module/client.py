#!/usr/bin/env python3
import socket
from time import sleep
import player_pb2, tcp_packet_pb2
from google.protobuf.internal import encoder

NUM_OF_TESTS = 5
SERVER = '202.92.144.45'
PORT = 80

tcp_packet = tcp_packet_pb2.TcpPacket

def connect_to_server(client, lobby_id):

    connect_packet = tcp_packet.ConnectPacket()
    connect_packet.type = tcp_packet.CONNECT
    connect_packet.player.name = client.name
    connect_packet.lobby_id = lobby_id
    connect_packet.update = tcp_packet.ConnectPacket.NEW

def send_to_server(sock, packet):

    # Serialize packet first before sending to server
    return sock.send(packet.SerializeToString()) # returns max no.

def main():

    lobby_id = "AB2L" # custom lobby

    # Socket to be used
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER, PORT))

    player_list_packet = tcp_packet.PlayerListPacket()
    player_list_packet.type = tcp_packet.PLAYER_LIST

    send_to_server(sock, player_list_packet)

    player_list = player_list_packet.player_list
    no_of_players = len(player_list)

    # ----------If custom lobby won't be used --------
    # if no_of_players == 0:
    #     # Send a lobby packet
    #     lobby_packet = tcp_packet.CreateLobbyPacket()
    #     lobby_packet.type = tcp_packet.CREATE_LOBBY
    #     lobby_packet.max_players = 3

    #     lobby_id = send_to_server(sock, lobby_packet) # returns lobby id
    #     lobby_id = str(lobby_id)

    #     print("Lobby id: " + lobby_id)
    #     print("Server can hold up to " + str(lobby_packet.max_players) + " players.")

    # if lobby_id == -1:
    #     print("No lobby has been created.")
        # return

    # Create a client ('host' is just the first player to connect)
    name = raw_input("Enter name: ")
    client = player_pb2.Player()
    client.name = name

    # Connect now the client to server
    connect_to_server(client, lobby_id)

    # Create chat packet
    chat_packet = tcp_packet.ChatPacket()
    chat_packet.type = tcp_packet.CHAT
    chat_packet.player.name = client.name

    while True:
        received = sock.recv(1024)
        print(received)

        message = raw_input(name + ": ")
        chat_packet.message = message

        send_to_server(sock, chat_packet)

        if(message == "bye"):
            print(player_list)
            disconnect_packet = tcp_packet.DisconnectPacket()
            disconnect_packet.player.name = name
            disconnect_packet.update = tcp_packet.DisconnectPacket.NORMAL

            return

    sock.close()

if __name__ == '__main__':
    main()