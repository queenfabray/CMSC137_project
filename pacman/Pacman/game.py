import pygame
import time
import random

from pygame.locals import *
from generate_map import create_map, draw_map
from node_position import node_position
from math import sqrt
from coins import create_coins, place_coins
from random import randint as rand

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
        self.start_x = xclass Pacman(pygame.sprite.Sprite):
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
        self.new_direction = self.direction
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
        self.start_y = y
        self.rect.x = self.start_x
        self.rect.y = self.start_y
        self.speed = speed
        self.direction = ""
        self.new_direction = self.direction
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
pyman_image_c = pygame.image.load("./image/pacman/pacmanc.png")
pyman_image_c = pygame.transform.scale(pyman_image_c, (block_size - 2, block_size - 2))
pacman_images['c'] = pyman_image_c

for i in range(1, 7):
    pacman_image = pygame.image.load("./image/pacman/pdying" + str(i) + ".png")
    pacman_image = pygame.transform.scale(pacman_image, (block_size - 2, block_size - 2))
    pacman_images[''+str(i)] = pacman_image

pyman_image_r = pygame.image.load("./image/pacman/pacmanr.png")
pyman_image_r = pygame.transform.scale(pyman_image_r, (block_size - 2, block_size - 2))

pacman_image = pyman_image_r # used for rotation

for i in range(4):
    pacman_images[directions[i]] = pacman_image
    pacman_image = pygame.transform.rotate(pacman_image, 90)

life_image = pygame.image.load("./image/life.png")
life_image = pygame.transform.scale(life_image,
                                    (block_size + block_size // 2,
                                    block_size + block_size // 2))

pacman = Pacman(pacman_images, #create PyMan instance
              block_size * 13,
              block_size * 17,
              speed,
              [0, HEIGHT / 2 - 5 * block_size],
              life_image)

pyman_group = pygame.sprite.Group(pacman)

game_over_width = WIDTH
game_over_image = pygame.image.load("./image/game_over.png")
game_over_image = pygame.transform.scale(game_over_image,
                                        (game_over_width,
                                        int(game_over_width / 1.7777)))

game_win_width = WIDTH
game_win_image = pygame.image.load("./image/game_win.png")
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

for i in range(4):
    ghost_list = []

    for j in range(4):
        for k in range(1, 3):
            ghost_image = pygame.image.load("./image/ghost/" + str(ghost_colors[i]) + "-" + str(directions[j]) + str(k) + ".png")
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
map_image = "./image/PixelMap.png"
map_bg = "./image/PacmanLevel-1.png"

#a dictionary used for the creation of the map
dict_map = {
    (0, 0, 0):  ("./image/trasparente.png", True), # wall
    (255, 255, 255): ("./image/trasparente.png", False), # bg
    (0, 255, 0): ("./image/trasparente.png", False), # node
    (0, 0, 255): ("./image/trasparente.png", False) # sponsor
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
    (255, 0, 0): ("./image/BigJim.png", "big"),
    (255, 255, 0): ("./image/SmallJim.png", "small")
}

coinmap_image = "./image/CoinMap.png"
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

# Game loop
channel.play(ready, 0)
game_ended = False

while not game_ended:

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

    # Display update
    draw_map(map, map_bg, window)
    place_coins(big_coin_group, window)
    place_coins(small_coin_group, window)
    pyman_group.draw(window)
    ghost_group.draw(window)

    pacman.life_display()
    pacman.get_points(window)

    if big_coin_list == [] and small_coin_list == []:
        pacman.speed = 0
        for ghosts in ghost_group:
            ghosts.speed = 0
            game_win_rect = game_over_image.get_rect()
            window.blit(game_win_image,
            (WIDTH / 2 - game_win_rect.width / 2,
            HEIGHT / 2 - game_win_rect.height / 2))

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
exit(0)