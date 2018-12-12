import pygame
import time
import random
import os

from pygame.locals import *
from collections import namedtuple
from generate_map import create_map, draw_map
from node_position import node_position
from coins import create_coins, place_coins
from math import sqrt
from random import randint as rand
from random import randrange

import pygameMenu
from pygameMenu.locals import *

import client
# import pong
# import pong.entities

# LOCAL_ADDRESS = ('localhost', 10400)
# SERVER_ADDRESS = ('localhost', pongserver.server.PongServer.DEFAULT_PORT)

# address = input('Server address (host:port) = ')
# host, port = address.split(':')
# port = int(port)


# ------------------------------------------------------

SERVER_ADDRESS = ("0.0.0.0", 10939)

pygame.init()
pygame.mixer.init()

channel = pygame.mixer.Channel(0)
dying = pygame.mixer.Sound('audio/pacman_death.wav')
chomp = pygame.mixer.Sound('audio/pacman_chomp.wav')
ready = pygame.mixer.Sound('audio/pacman_beginning.wav')

block_size = 32

GAME_RES = WIDTH, HEIGHT = 28 * block_size, 31 * block_size
FPS = 60
GAME_TITLE = 'PACMAN'

window = pygame.display.set_mode(GAME_RES, HWACCEL|HWSURFACE|DOUBLEBUF)
pygame.display.set_caption(GAME_TITLE)
clock = pygame.time.Clock()

# Game Values
background_color = (150, 150, 150) # RGB value
speed = 2
non_touching_position = (32, 32)


class Pacman(pygame.sprite.Sprite):
    """The class of the main character"""

    def __init__(self, images, x, y, speed, life_pos, life_image):
        pygame.sprite.Sprite.__init__(self)
        self.images = images
        self.image = self.images['right']
        self.rect = self.image.get_rect()
        self.start_x = x
        self.start_y = y
        self.rect.x = self.start_x
        self.rect.y = self.start_y
        self.speed = speed
        self.direction = ""
        self.new_direction = random.choice(["left", "right"])
        self.life_image = life_image
        self.rect_life = self.life_image.get_rect()
        self.life = 3
        self.life_pos = life_pos
        self.score = 0
        self.can_eat = False
        self.counter = 0

    def touch_node(self):   #detect collision between PyMan and nodes
        if (self.rect.x, self.rect.y) in node_list:
            return True

    def wall_collide(self): #detect if PyMan is colliding with a wall
        if pygame.sprite.spritecollide(self, wall_group, False) != []:
            return True

    def position(self, non_touching_position):  #return the position of PyMan
        if pygame.sprite.spritecollide(self, wall_group, False) == []:
            return (self.rect.x, self.rect.y)
        else:
            self.rect.x  = non_touching_position[0]
            self.rect.y = non_touching_position[1]
            return non_touching_position

    def move(self):  #give PyMan the ability to move
        self.teleport()

        if self.direction == "up":
            self.rect.y += self.speed * -1
            self.image = self.images['up']
        if self.direction == "down":
            self.rect.y += self.speed * 1
            self.image = self.images['down']
        if self.direction == "right":
            self.rect.x += self.speed * 1
            self.image = self.images['right']
        if self.direction == "left":
            self.rect.x += self.speed * -1
            self.image = self.images['left']

        # Change mouth
        if self.counter >= 15:
            self.image = self.images['c']

        if self.counter > 16:
            self.counter = 0

        self.counter += 1

    def teleport(self):     #allow PyMan to teleport when he's outside the map
        if self.rect.x < -self.rect.width:
            self.rect.x = WIDTH
        if self.rect.x > WIDTH:
            self.rect.x = -self.rect.width

    def check_if_touch(self):
        if pygame.sprite.spritecollide(self, ghost_group, False) != []:

            self.image = self.images['c']
            pygame.display.update()

            # for i in range(1, 7):
            #     self.image = self.images[''+str(i)]

            if self.can_eat == True:
                pygame.sprite.spritecollide(self, ghost_group, True)[0].restart()
                self.score += 150
            else:
                self.restart()

    def restart(self): #restart the game
        # channel.play(dying, -1)

        # global ghost_group, game_over_image
        self.life -= 1
        self.image = self.images['c']

        if self.life <= 0:
            self.speed = 0

            for ghosts in ghost_group:
                ghosts.speed = 0

            game_over_rect = game_over_image.get_rect()
            
            window.blit(game_over_image,
                        (WIDTH / 2 - game_over_rect.width / 2,
                         HEIGHT / 2 - game_over_rect.height / 2))

        else:
            time.sleep(0.5)
            self.rect.x = self.start_x
            self.rect.y = self.start_y
            self.direction = random.choice(["left", "right"])

            for ghosts in ghost_group:
                ghosts.rect.x =  ghosts.start_x
                ghosts.rect.y = ghosts.start_y
                ghosts.in_home = True
                ghosts.direction = random.choice(["left", "right"])
            time.sleep(0.5)

        pygame.mixer.pause()

    def life_display(self): #display the ammount of life
        c = 0
        for life in range(self.life):
            if c < 3:
                window.blit(self.life_image,
                            (self.life_pos[0] + self.rect_life.width * life + 1,
                            self.life_pos[1]))
            c += 1

    def get_points(self, screen): #calculate points for PyMan
        global small_coin_list, big_coin_list

        if pygame.sprite.spritecollide(self, small_coin_group, True) != []:
            # channel.play(chomp, -1)

            self.score += 10
            small_coin_list = small_coin_list[0:-1]

        if pygame.sprite.spritecollide(self, big_coin_group, True) != []:
            # channel.play(chomp, -1)
            # self.can_eat = True
            self.score += 150
            big_coin_list = big_coin_list[0:-1]

        pygame.font.init()
        myfont = pygame.font.SysFont('emulogic.ttf', 40)
        textsurface = myfont.render(str(self.score), False, (255, 255, 0))
        screen.blit(textsurface,(32,
                                 self.life_pos[1] + 220))

directions = ['right', 'up', 'left', 'down']
pacman_images = {}

# Insert first the closed pacman
pyman_image_c = pygame.image.load("image/pacman/pacmanc.png")
pyman_image_c = pygame.transform.scale(pyman_image_c, (block_size - 2, block_size - 2))
pacman_images['c'] = pyman_image_c

for i in range(1, 7):
    pacman_image = pygame.image.load("image/pacman/pdying" + str(i) + ".png")
    pacman_image = pygame.transform.scale(pacman_image, (block_size - 2, block_size - 2))
    pacman_images[''+str(i)] = pacman_image

    pyman_image_r = pygame.image.load("image/pacman/pacmanr.png")
    pyman_image_r = pygame.transform.scale(pyman_image_r, (block_size - 2, block_size - 2))

    pacman_image = pyman_image_r # used for rotation

for i in range(4):
    pacman_images[directions[i]] = pacman_image
    pacman_image = pygame.transform.rotate(pacman_image, 90)

    life_image = pygame.image.load("image/life.png")
    life_image = pygame.transform.scale(life_image,
                                    (block_size + block_size // 2,
                                    block_size + block_size // 2))

pacman1 = Pacman(pacman_images, #create PyMan instance
                  block_size * 13,
                  block_size * 17,
                  speed,
                  [0, HEIGHT / 2 - 5 * block_size],
                  life_image)

pacman2 = Pacman(pacman_images, #create PyMan instance
                  block_size * 16,
                  block_size * 20,
                  speed,
                  [0, HEIGHT / 2 - 5 * block_size],
                  life_image)

pacman3 = Pacman(pacman_images, #create PyMan instance
                  block_size * 16,
                  block_size * 20,
                  speed,
                  [0, HEIGHT / 2 - 5 * block_size],
                  life_image)

pacman = pacman1

pacman_group1 = pygame.sprite.Group(pacman1)
pacman_group2 = pygame.sprite.Group(pacman2)
pacman_group3 = pygame.sprite.Group(pacman3)

game_over_width = WIDTH
game_over_image = pygame.image.load("image/game_over.png")
game_over_image = pygame.transform.scale(game_over_image,
                                    (game_over_width,
                                    int(game_over_width / 1.7777)))

game_win_width = WIDTH
game_win_image = pygame.image.load("image/game_win.png")
game_win_image = pygame.transform.scale(game_win_image,
                                    (game_win_width,
                                    int(game_win_width / 1.7777)))

class Ghost(pygame.sprite.Sprite):
    """The class for the 4 ghosts"""
    def __init__(self, images, x, y, speed):
        pygame.sprite.Sprite.__init__(self)
        self.images = images
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.start_x = x
        self.start_y = y
        self.rect.x = self.start_x
        self.rect.y = self.start_y
        self.speed = speed
        self.last_node = (x, y)
        self.in_home = True
        self.direction = random.choice(["left", "right"])
        self.counter = 0

    def refresh_direction(self, pacman_rect, node_list):
        if (self.rect.x, self.rect.y) in node_list:
            directions = ["right", "left", "up", "down"]
            if self.direction == "right":
                directions.remove("left")
            elif self.direction == "left":
                directions.remove("right")
            elif self.direction == "up":
                directions.remove("down")
            elif self.direction == "down":
                directions.remove("up")

            if self.collide_wall("right"):
                directions.remove("right")
            if self.collide_wall("left"):
                directions.remove("left")
            if self.collide_wall("up"):
                directions.remove("up")
            if self.collide_wall("down"):
                directions.remove("down")

            pacman_relative_pos = []
            if pacman_rect[0] > self.rect.x:
                pacman_relative_pos.append("right")
            elif pacman_rect[0] < self.rect.x:
                pacman_relative_pos.append("left")
            if pacman_rect[1] > self.rect.y:
                pacman_relative_pos.append("down")
            elif pacman_rect[1] < self.rect.y:
                pacman_relative_pos.append("up")

            new_possible_directions = [value for value in directions if value in pacman_relative_pos]
            new_possible_directions = directions if new_possible_directions == [] else new_possible_directions

            direct_sight_bool, direct_sight_direction = self.direct_sight(pacman_rect)

            if direct_sight_bool:
                new_possible_directions = [value for value in directions if value in direct_sight_direction]
                new_possible_directions = directions if new_possible_directions == [] else new_possible_directions

            self.direction = random.choice(new_possible_directions)

    #give the ghost the ability to move
    def move(self):
        curr_index = 0

        if self.in_home == True:
            self.go_out_home()

        else:
            self.refresh_direction([pacman.rect[0], pacman.rect[1]], node_list)

            if self.direction == "right":
                self.rect.x += self.speed
                self.image = self.images[0]
                curr_index = 0

            if self.direction == "left":
                self.rect.x -= self.speed
                self.image = self.images[4]
                curr_index = 4

            if self.direction == "down":
                self.rect.y += self.speed
                self.image = self.images[6]
                curr_index = 6

            if self.direction == "up":
                self.rect.y -= self.speed
                self.image = self.images[2]
                curr_index = 2

            if self.rect.x < -self.rect.width:
                self.rect.x = WIDTH

            # Change ghost's feet position
            if self.counter >= 15:
                self.image = self.images[curr_index+1]

            if self.counter >= 16:
                self.counter = 0

            self.counter += 1

    def direct_sight(self, pacman_rect):
        pacman_directions = []
        if self.rect.x == pacman_rect[0]:
            if self.rect.y > pacman_rect[1]:
                pacman_directions.append("up")
            else:
                pacman_directions.append("down")
        if self.rect.y == pacman_rect[1]:
            if self.rect.x > pacman_rect[0]:
                pacman_directions.append("left")
            else:
                pacman_directions.append("right")
        if [self.rect.x, self.rect.y] != pacman_rect:
            return [False, pacman_directions]
        return [True, pacman_directions]

    def go_out_home(self): #allow the ghost to get out of the little house

        if not (self.rect.x == block_size * 13 or \
                self.rect.x == block_size * 14):
            if self.rect.x < block_size * 13:
                self.rect.x += self.speed
            else:
                self.rect.x -= self.speed
        else:
            if self.rect.y > block_size * 11:
                self.rect.y -= self.speed
            else:
                self.in_home = False

    #refresh the last node position
    def refresh_last_node(self, node_list):
        for node in node_list:
            if node == (self.rect.x, self.rect.y):
                self.last_node = node
                return None

    #detect if there is a wall in front of the ghost
    def collide_wall(self, direction):
        global block_size, wall_position
        if direction == "up":
            if (self.rect.x, self.rect.y - block_size) in wall_position:
                return True
        elif direction == "down":
            if (self.rect.x, self.rect.y + block_size) in wall_position:
                return True
        elif direction == "left":
            if (self.rect.x - block_size, self.rect.y) in wall_position:
                return True
            if (self.rect.x, self.rect.y) == (block_size * 6, block_size * 14):
                return True
        elif direction == "right":
            if (self.rect.x + block_size, self.rect.y) in wall_position:
                return True
            if (self.rect.x, self.rect.y) == (block_size * 21, block_size * 14):
                return True
        return False

ghost_colors = ['cian', 'pink', 'orange', 'red']
all_ghost_list = []

#function that find the distance between point a and b
def distance(a, b):
    delta_x = a[0] - b[0]
    delta_y = a[1] - b[1]
    return sqrt(delta_x ** 2 + delta_y ** 2)

def updatePacman(pacman, props):
    pacman.image = pacman.images[props['image']]
    pacman.rect.x = props['x']
    pacman.rect.y = props['y']
    pacman.direction = props['direction']
    pacman.life = props['life']
    pacman.score = props['score']
    pacman.can_eat = props['can_eat']

def updateProps(props, pacman):
    props['image'] = pacman.direction
    props['x'] = pacman.rect.x
    props['y'] = pacman.rect.y
    props['direction'] = pacman.direction
    props['life'] = pacman.life
    props['score'] = pacman.score
    props['can_eat'] = pacman.can_eat

    return props

for i in range(4):
    ghost_list = []

    for j in range(4):
        for k in range(1, 3):
            ghost_image = pygame.image.load("image/ghost/" + str(ghost_colors[i]) + "-" + str(directions[j]) + str(k) + ".png")
            ghost_image = pygame.transform.scale(ghost_image, (block_size, block_size))

            ghost_list.append(ghost_image)

    all_ghost_list.append(ghost_list)

# create four Ghost instances
ghost_instances = []

for i in range(4):
    ghost = Ghost(all_ghost_list[i],
               block_size * 12 - block_size / 2 + 4*i,
               block_size * 15 - block_size / 2 - 4*i,
               speed)

    ghost_instances.append(ghost)

ghost_group = pygame.sprite.Group(ghost_instances)

# acquiring map images
map_image = "image/PixelMap.png"
map_bg = "image/PacmanLevel-1.png"

#a dictionary used for the creation of the map
dict_map = {
    (0, 0, 0):  ("image/trasparente.png", True), # wall
    (255, 255, 255): ("image/trasparente.png", False), # bg
    (0, 255, 0): ("image/trasparente.png", False), # node
    (0, 0, 255): ("image/trasparente.png", False) # sponsor
}

#creating the map
map = create_map(map_image, dict_map, block_size, WIDTH) #create the map
wall_array = []
for blocks in map:
    if blocks.wall == True:
        wall_array.append(blocks)

wall_group = pygame.sprite.Group(wall_array)
wall_position = []
for walls in wall_array:
    wall_position.append((walls.rect.x, walls.rect.y))


dict_coin = {
    (255, 0, 0): ("image/BigJim.png", "big"),
    (255, 255, 0): ("image/SmallJim.png", "small")
}

coinmap_image = "image/CoinMap.png"
coins_map = create_coins(coinmap_image, dict_coin, block_size, WIDTH)
small_coin_list = []
big_coin_list = []

for coin in coins_map:
    if coin.type == "small":
        small_coin_list.append(coin)
    elif coin.type == "big":
        big_coin_list.append(coin)

small_coin_group = pygame.sprite.Group(small_coin_list)
big_coin_group = pygame.sprite.Group(big_coin_list)

#creating a list of the node(crossings) of the map
node_list = node_position(map_image, (0, 255, 0), block_size, WIDTH)
# End of Game Values


# -------------------GAME MENU--------------------------
ABOUT = ['Pacman Multiplayer',
         'Authors: Johnnedel Pagsinohin',
         '         Mariqueen Tenedero',
         '         Francisco Hernandez',
         PYGAMEMENU_TEXT_NEWLINE,
         'CMSC 137 Project AB-2L',
         '2018']

MECHANICS = ['Pacman Multiplayer',
             'The game can be played by up to 4 players. The goal is to',
             'eat as many pellets, but... be sure not to touch the',
             'ghosts. The player who will be left standing',
             '(and eating) will be crowned as victor.',
             PYGAMEMENU_TEXT_NEWLINE,
             'So basically, avoid the ghosts, don\'t mind the score.']


COLOR_BACKGROUND = (128, 0, 128)
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
FPS = 60.0
MENU_BACKGROUND_COLOR = (228, 55, 36)
WINDOW_SIZE = GAME_RES

# -----------------------------------------------------------------------------
# Init pygame
# pygame.init()
os.environ['SDL_VIDEO_CENTERED'] = '1'

# Create pygame screen and objects
surface = pygame.display.set_mode(WINDOW_SIZE)
# pygame.display.set_caption('PygameMenu example 2')
clock = pygame.time.Clock()
dt = 1 / FPS

# Global variables
DIFFICULTY = ['EASY']


# -----------------------------------------------------------------------------

def change_difficulty(d):
    """
    Change difficulty of the game.
    
    :return: 
    """
    print ('Selected difficulty: {0}'.format(d))
    DIFFICULTY[0] = d


def random_color():
    """
    Return random color.
    
    :return: Color tuple
    """
    return randrange(0, 255), randrange(0, 255), randrange(0, 255)


def play_function(difficulty, font):
    global pacman, non_touching_position
    """
    Main game function
    
    :param difficulty: Difficulty of the game
    :param font: Pygame font
    :return: None
    """
    difficulty = difficulty[0]
    assert isinstance(difficulty, str)

    if difficulty == 'EASY':
        f = font.render('Playing as baby', 1, COLOR_WHITE)
    elif difficulty == 'MEDIUM':
        f = font.render('Playing as normie', 1, COLOR_WHITE)
    elif difficulty == 'HARD':
        f = font.render('Playing as god', 1, COLOR_WHITE)
    else:
        raise Exception('Unknown difficulty {0}'.format(difficulty))

    # Reset main menu and disable
    # You also can set another menu, like a 'pause menu', or just use the same
    # main_menu as the menu that will check all your input.
    main_menu.disable()
    main_menu.reset(1)

    # Game loop
    channel.play(ready, 0)
    game_ended = False

    pacman_props = {
        "image": pacman.new_direction,
        "x": pacman.start_x,
        "y": pacman.start_y,
        "direction": pacman.direction,
        "life": pacman.life,
        "score": pacman.score,
        "can_eat": pacman.can_eat
    }

    # Randomly generate the address for this client
    local_address = ('localhost', random.randint(10000, 20000))

    svh = client.ServerHandler(local_address,
                              SERVER_ADDRESS,
                              pacman_props,
                              ghost_group,)
    svh.start()

    while svh.player_number == -1:
        pass

    player_number = svh.player_number

    if player_number == 1:
        pacman = pacman1

    elif player_number == 2:
        pacman = pacman2

    else:
        pacman = pacman3

    while not game_ended:
    # for i in range(6):

        svh.pacman1_props = svh.receive_pacman()
        svh.pacman2_props = svh.receive_pacman()
        svh.pacman3_props = svh.receive_pacman()
        # print(svh.pacman1_props['score'])
        updatePacman(pacman1, svh.pacman1_props)
        updatePacman(pacman2, svh.pacman2_props)
        updatePacman(pacman3, svh.pacman3_props)

        # Event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                game_ended  = True
                break
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    game_ended  = True
                    break

        keys_pressed = pygame.key.get_pressed()

        #detect if any key is pressed
        if keys_pressed[K_s] or keys_pressed[K_DOWN]:
            pacman.new_direction = "down"
        if keys_pressed[K_w] or keys_pressed[K_UP]:
            pacman.new_direction = "up"
        if keys_pressed[K_a] or keys_pressed[K_LEFT]:
            pacman.new_direction = "left"
        if keys_pressed[K_d] or keys_pressed[K_RIGHT]:
            pacman.new_direction = "right"
        

        #allow PyMan to move only if it's on a node or the movement is opposite
        if not pacman.wall_collide():
            if (pacman.touch_node() or
                pacman.direction == "down" and pacman.new_direction == "up" or
                pacman.direction == "up" and pacman.new_direction == "down" or
                pacman.direction == "left" and pacman.new_direction == "right" or
                pacman.direction == "right" and pacman.new_direction == "left"):
                pacman.direction = pacman.new_direction
        else:   #allow PyMan to get out of the wall...
            pacman.direction = pacman.new_direction

        #getting the position that is not touching the wall
        non_touching_position = pacman.position(non_touching_position)

        for ghosts in ghost_group:
            ghosts.refresh_last_node(node_list)
            ghosts.move()

        pacman.check_if_touch()
        pacman.move()

        # if player_number == 1:
        #     pacman1 = pacman

        # else:
        #     pacman2 = pacman

        if player_number == 1:
            svh.pacman1_props = updateProps(svh.pacman1_props, pacman)
            svh.pacman2_props = updateProps(svh.pacman2_props, pacman2)
            svh.pacman3_props = updateProps(svh.pacman3_props, pacman3)

        elif player_number == 2:
            svh.pacman2_props = updateProps(svh.pacman2_props, pacman)
            svh.pacman1_props = updateProps(svh.pacman1_props, pacman1)
            svh.pacman3_props = updateProps(svh.pacman3_props, pacman3)

        else:
            svh.pacman3_props = updateProps(svh.pacman3_props, pacman)
            svh.pacman1_props = updateProps(svh.pacman1_props, pacman1)
            svh.pacman2_props = updateProps(svh.pacman2_props, pacman2)

        svh.send_pacman()

        # Display update
        draw_map(map, map_bg, window)
        place_coins(big_coin_group, window)
        place_coins(small_coin_group, window)

        pacman_group1.draw(window)
        pacman_group2.draw(window)
        pacman_group3.draw(window)

        ghost_group.draw(window)

        pacman1.life_display()
        pacman2.life_display()
        pacman3.life_display()

        pacman1.get_points(window)
        pacman2.get_points(window)
        pacman3.get_points(window)

        pacman_group1.update()
        pacman_group2.update()
        pacman_group3.update()

        # if player_number == 1:
        #     svh.pacman1_props['score'] = pacman.score

        # elif player_number == 2:
        #     svh.pacman2_props['score'] = pacman.score
        # else:
        #     svh.pacman3_props['score'] = pacman.score

        if big_coin_list == [] and small_coin_list == []:
            pacman.speed = 0
            for ghosts in ghost_group:
                ghosts.speed = 0
                game_win_rect = game_over_image.get_rect()
                window.blit(game_win_image,
                (WIDTH / 2 - game_win_rect.width / 2,
                HEIGHT / 2 - game_win_rect.height / 2))

        if pacman.life == 0:
            f = font.render('GAME OVER', 1, COLOR_WHITE)
            # Draw random color and text
            bg_color = random_color()
            f_width = f.get_size()[0]

            window.fill(bg_color)
            window.blit(f, ((WINDOW_SIZE[0] - f_width) / 2, WINDOW_SIZE[1] / 2))

            pygame.display.update()

            time.sleep(3)
            break

        pygame.display.update()
        clock.tick(FPS)

        # Pass events to main_menu
        main_menu.mainloop(pygame.event.get())

        # Continue playing
        pygame.display.flip()


def main_background():
    """
    Function used by menus, draw on background while menu is active.
    
    :return: None
    """
    surface.fill(COLOR_BACKGROUND)


# -----------------------------------------------------------------------------
# PLAY MENU
play_menu = pygameMenu.Menu(surface,
                            bgfun=main_background,
                            color_selected=COLOR_WHITE,
                            font=pygameMenu.fonts.FONT_BEBAS,
                            font_color=COLOR_BLACK,
                            font_size=30,
                            menu_alpha=100,
                            menu_color=MENU_BACKGROUND_COLOR,
                            menu_height=int(WINDOW_SIZE[1] * 0.6),
                            menu_width=int(WINDOW_SIZE[0] * 0.6),
                            onclose=PYGAME_MENU_DISABLE_CLOSE,
                            option_shadow=False,
                            title='Play menu',
                            window_height=GAME_RES[1],
                            window_width=GAME_RES[0]
                            )
# When pressing return -> play(DIFFICULTY[0], font)
play_menu.add_option('Start', play_function, DIFFICULTY,
                     pygame.font.Font(pygameMenu.fonts.FONT_FRANCHISE, 30))
play_menu.add_selector('Select difficulty', [('Easy', 'EASY'),
                                             ('Medium', 'MEDIUM'),
                                             ('Hard', 'HARD')],
                       onreturn=None,
                       onchange=change_difficulty)
play_menu.add_option('Return to main menu', PYGAME_MENU_BACK)

# MECHANICS
mechanics_menu = pygameMenu.TextMenu(surface,
                                 bgfun=main_background,
                                 color_selected=COLOR_WHITE,
                                 font=pygameMenu.fonts.FONT_BEBAS,
                                 font_color=COLOR_BLACK,
                                 font_size_title=30,
                                 font_title=pygameMenu.fonts.FONT_8BIT,
                                 menu_color=MENU_BACKGROUND_COLOR,
                                 menu_color_title=COLOR_WHITE,
                                 menu_height=int(WINDOW_SIZE[1] * 0.6),
                                 menu_width=int(WINDOW_SIZE[0] * 0.6),
                                 onclose=PYGAME_MENU_DISABLE_CLOSE,
                                 option_shadow=False,
                                 text_color=COLOR_BLACK,
                                 text_fontsize=20,
                                 title='About',
                                 window_height=WINDOW_SIZE[1],
                                 window_width=WINDOW_SIZE[0]
                                 )

for m in MECHANICS:
    mechanics_menu.add_line(m)

mechanics_menu.add_line(PYGAMEMENU_TEXT_NEWLINE)
mechanics_menu.add_option('Return to menu', PYGAME_MENU_BACK)
# ABOUT MENU
about_menu = pygameMenu.TextMenu(surface,
                                 bgfun=main_background,
                                 color_selected=COLOR_WHITE,
                                 font=pygameMenu.fonts.FONT_BEBAS,
                                 font_color=COLOR_BLACK,
                                 font_size_title=30,
                                 font_title=pygameMenu.fonts.FONT_8BIT,
                                 menu_color=MENU_BACKGROUND_COLOR,
                                 menu_color_title=COLOR_WHITE,
                                 menu_height=int(WINDOW_SIZE[1] * 0.6),
                                 menu_width=int(WINDOW_SIZE[0] * 0.6),
                                 onclose=PYGAME_MENU_DISABLE_CLOSE,
                                 option_shadow=False,
                                 text_color=COLOR_BLACK,
                                 text_fontsize=20,
                                 title='About',
                                 window_height=WINDOW_SIZE[1],
                                 window_width=WINDOW_SIZE[0]
                                 )
for m in ABOUT:
    about_menu.add_line(m)

about_menu.add_line(PYGAMEMENU_TEXT_NEWLINE)
about_menu.add_option('Return to menu', PYGAME_MENU_BACK)

# MAIN MENU
main_menu = pygameMenu.Menu(surface,
                            bgfun=main_background,
                            color_selected=COLOR_WHITE,
                            font=pygameMenu.fonts.FONT_BEBAS,
                            font_color=COLOR_BLACK,
                            font_size=30,
                            menu_alpha=100,
                            menu_color=MENU_BACKGROUND_COLOR,
                            menu_height=int(WINDOW_SIZE[1] * 0.6),
                            menu_width=int(WINDOW_SIZE[0] * 0.6),
                            onclose=PYGAME_MENU_DISABLE_CLOSE,
                            option_shadow=False,
                            title='Main menu',
                            window_height=GAME_RES[1],
                            window_width=GAME_RES[0]
                            )
main_menu.add_option('Play', play_menu)
main_menu.add_option('About', about_menu)
main_menu.add_option('Mechanics', mechanics_menu)
main_menu.add_option('Quit', PYGAME_MENU_EXIT)

# -----------------------------------------------------------------------------

def handle_event(event):
    return

def draw_graphics():
    return

while True:

    # Tick
    clock.tick(60)

    # Application events
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT:
            exit()

    # Main menu
    main_menu.mainloop(events)

    # Flip surface
    # pygame.display.flip()