#!/usr/bin/env python3
import socket
from time import sleep
import player_pb2, tcp_packet_pb2
from google.protobuf.internal import encoder

NUM_OF_TESTS = 5
SERVER = '202.92.144.45'
PORT = 80

tcp_packet = tcp_packet_pb2.TcpPacket

def send_over_socket(sock, message):
    delimiter = encoder._VarintBytes(len(message))
    message = delimiter + message
    msg_len = len(message)
    total_sent = 0

    while total_sent < msg_len:
        sent = sock.send(message[total_sent:])
        if sent == 0:
            raise RuntimeError('Socket connection broken')
        total_sent = total_sent + sent


def main():

    # Connect over tcp_packet_pb2 socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER, PORT))

    lobby = tcp_packet.CreateLobbyPacket()
    lobby.type = tcp_packet.CREATE_LOBBY
    lobby.max_players = 3

    lobby_id = sock.send(lobby.SerializeToString())
    lobby_id = str(lobby_id)
    print(lobby_id)

    p1 = player_pb2.Player()
    p1.name = raw_input("Enter name: ")

    host = tcp_packet.ConnectPacket()
    host.type = tcp_packet.CONNECT
    # host.player = p1
    host.lobby_id = lobby_id
    host.update = tcp_packet.ConnectPacket.NEW

    chat = tcp_packet.ChatPacket()
    chat.type = tcp_packet.CHAT
    # chat.player = p1

    while True:
        chat.message = raw_input("Enter message: ")
        sock.send(chat.SerializeToString())

    # send_over_socket(sock, lobby.SerializeToString())

    # for i in range(NUM_OF_TESTS):

    #     print('Starting test {}'.format(i))

    #     player = player_pb2.Player()


    #     command = message_pb2.Command()
    #     command.type = message_pb2.Command.START_TEST
    #     command.name = 'Test Case {}'.format(i)
    #     command.data = 'Test Data'

    #     send_over_socket(sock, command.SerializeToString())
    #     sleep(2)

    # command = message_pb2.Command()
    # command.type = message_pb2.Command.SHUTDOWN
    # command.name = 'Shutting down'.format(i)
    # send_over_socket(sock, command.SerializeToString())


if __name__ == '__main__':
    main()