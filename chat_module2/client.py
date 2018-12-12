#!/usr/bin/env python3
import socket, select, sys
from time import sleep
import player_pb2, tcp_packet_pb2

NUM_OF_TESTS = 5
SERVER = '202.92.144.45'
PORT = 80
BUFFER = 1024

tcp_packet = tcp_packet_pb2.TcpPacket()

CONNECTION_LIST = []
# class recvThread(threading.Thread):

#     def __init__(self, sock, chat_packet):

#         threading.Thread.__init__(self)
#         self.chat_packet = chat_packet
#         self.sock = sock

#     def run(self):

#         while True:
#             self.sock.recv(1024)

def send_and_receive(sock, packet):

    # Serialize packet first before sending to server
    sock.sendall(packet.SerializeToString())
    sock.recv(BUFFER)

    return packet

def send_msg(sock, chat_packet, client):

    while True:
        message = raw_input(client.name + ": ")

        chat_packet.type = tcp_packet.CHAT
        chat_packet.player.CopyFrom(client)
        chat_packet.message = message

        # Serialize packet first before sending to server
        sock.sendall(chat_packet.SerializeToString())

        sender = chat_packet.player.name
        message = chat_packet.message

        if message == "bye":
            disconnect_packet = tcp_packet.DisconnectPacket()
            disconnect_packet.type = tcp_packet.DISCONNECT
            disconnect_packet.player.name = name
            disconnect_packet.update = tcp_packet.DisconnectPacket.NORMAL

            disconnect_packet = send_and_receive(sock, disconnect_packet);

            print("You have disconnected")
            return

        if message and sender != client.name:
            print(sender + ": " + message)

def receive_msg(sock):

    while True:
        data = sock.recv(BUFFER)
        print(data)


def connect_to_server(client, lobby_id, sock):

    connect_packet = tcp_packet.ConnectPacket()
    connect_packet.type = tcp_packet.CONNECT
    connect_packet.player.CopyFrom(client)
    connect_packet.lobby_id = lobby_id
    # connect_packet.update = tcp_packet.ConnectPacket.NEW

    return send_and_receive(sock, connect_packet)

# Function to broadcast chat messages to all connected clients
def broadcast_data (sock, message):
    #Do not send the message to master socket and the client who has send us the message
    for socket in CONNECTION_LIST:
        if socket != server_socket and socket != sock :
            try :
                socket.send(message)
            except :
                # broken socket connection may be, chat client pressed ctrl+c for example
                socket.close()
                CONNECTION_LIST.remove(socket)

def main():

    lobby_id = "AB2L" # custom lobby

    # Socket to be used
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER, PORT))

    # CONNECTION_LIST.append(server_socket)

    while True:
        sockets_list = [sys.stdin, sock] 

        read_sockets, write_sockets, error_sockets = select.select(sockets_list,[],[])

        for socks in read_sockets:
            
            if socks == server: 
                message = socks.recv(2048) 
                print message 
            else: 
                message = sys.stdin.readline() 
                server.send(message) 
                sys.stdout.write("<You>") 
                sys.stdout.write(message) 
                sys.stdout.flush() 
    #     # CONNECTION_LIST = [sys.stdin, server_socket]


    #     for sock in read_sockets:

    #         if sock == server_socket:
    #             # New connection received through the server socket
    #             sockfd, addr = server_socket.accept()
    #             CONNECTION_LIST.append(sockfd)

    #             broadcast_data(sockfd, "[%s:%s] entered room\n" % addr)

    #         # Some incoming message from a client
    #         else:
    #             # Data recieved from client, process it
    #             try:
    #                 data = sock.recv(BUFFER)
    #                 if data:
    #                     broadcast_data(sock, "\r" + '<' + str(sock.getpeername()) + '> ' + data)                
                
    #             except:
    #                 broadcast_data(sock, "Client (%s, %s) is offline" % addr)
    #                 print "Client (%s, %s) is offline" % addr
    #                 sock.close()
    #                 CONNECTION_LIST.remove(sock)
    #                 continue

    server_socket.close()

    # # Create a client ('host' is just the first player to connect)
    # name = raw_input("Enter name: ")
    # client = player_pb2.Player()
    # client.name = name
    # client.id = "-1"

    # # Connect now the client to server
    # connect_packet = connect_to_server(client, lobby_id, sock)

    # player_list_packet = tcp_packet.PlayerListPacket()
    # player_list_packet.type = tcp_packet.PLAYER_LIST
    # player_list_packet = send_and_receive(sock, player_list_packet)
    
    # ----------If custom lobby won't be used --------
    # if no_of_players == 0:
    #     # Send a lobby packet
        # lobby_packet = tcp_packet.CreateLobbyPacket()
        # lobby_packet.type = tcp_packet.CREATE_LOBBY
        # lobby_packet.max_players = 3

        # lobby_id = send_and_receive(sock, lobby_packet) # returns lobby id
        # lobby_id = str(lobby_id)

        # print("Lobby id: " + lobby_id)
        # print("Server can hold up to " + str(lobby_packet.max_players) + " players.")

    # if lobby_id == -1:
    #     print("No lobby has been created.")
        # returnthreading

    # Create chat packet
    # chat_packet = tcp_packet.ChatPacket()


    # if(message == "bye"):
    #    

    # sock.close()

if __name__ == '__main__':
    main()