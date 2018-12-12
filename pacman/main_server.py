import server
from collections import namedtuple

PacmanProps = namedtuple("PacmanProps", "image x y direction life score can_eat")

def main():
    port = server.PacmanServer.DEFAULT_PORT
    game_server = server.PacmanServer(port)
    game_server.start()

if __name__ == '__main__':
    main()