import csv
import pygame
pygame.init()

#TODO: Create a venv

#game variables
clock = pygame.time.Clock()
fps = 60
scroll = [0, 0]
tile_size = 50 # 1, 2, 4, 5, 8, 16, 20, 25, 32, 40, 50, 80, 100, 160, 200, 400, 800
screen_dimensions = screen_width, screen_height = 1000, 800
screen = pygame.display.set_mode(screen_dimensions)
pygame.display.set_caption('Platformer')

bg_img = pygame.image.load('img/BG/BG.png').convert_alpha()
bg_img = pygame.transform.scale(bg_img, screen_dimensions)


#TODO: Take off Godmode
godMode = True

#load in level func
def load_level(file):
    global world
    with open(file, "r") as f:
        data = csv.reader(f)
        data = [row for row in data]
    world = World(data)

#scaling func
def scale_surface(surf, scale):
    width = round(surf.get_width() * scale)
    height = round(surf.get_height() * scale)
    return pygame.transform.smoothscale(surf, (width, height))


#player class
class Player():
    def __init__(self, x, y):
        self.images_jump_start_right = []
        self.images_jump_start_left = []
        self.images_idle_right = []
        self.images_idle_left = []
        self.images_run_right = []
        self.images_walk_left = []

        self.idle_index = 0
        self.index = 0
        self.counter = 0
        self.wait = 0

        #load images
        for n in range(0, 10):
            img_right = pygame.image.load(f'img/Character animations/Jump Start/Jump Start_{n}.png').convert_alpha()
            img_right = scale_surface(img_right, 0.2)
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_jump_start_right.append(img_right)
            self.images_jump_start_left.append(img_left)
        for n in range(0, 12):
            img_right = pygame.image.load(f'img/Character animations/Idle/Idle_{n}.png').convert_alpha()
            img_right = scale_surface(img_right, 0.2)
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_idle_right.append(img_right)
            self.images_idle_left.append(img_left)
        for n in range(0, 16):
            img_right = pygame.image.load(f'img/Character animations/Walk/Walk_{n}.png').convert_alpha()
            img_right = scale_surface(img_right, 0.2)
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_run_right.append(img_right)
            self.images_walk_left.append(img_left)

        #player setup
        self.image = self.images_idle_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        self.vel_y = 0
        self.jumped = False
        self.direction = 'right'

    def animate(self):
        jump_countdown = 3
        walk_countdown = 3
        idle_countdown = 4

        #handle animations
        if self.jumped:
            self.wait = 0
            if self.counter > jump_countdown:
                self.counter = 0
                self.index += 1

                if self.image == self.images_jump_start_left[-1] or self.image == self.images_jump_start_right[-1]:
                    last = True
                else:
                    last = False

                if not last:
                    if self.index >= len(self.images_jump_start_right):
                        self.index = 0
                    if self.direction == 'right':
                        self.image = self.images_jump_start_right[self.index]
                    if self.direction == 'left':
                        self.image = self.images_jump_start_left[self.index]
                else:
                    self.index = -1
        else:
            if self.moving == False:
                if self.idle_index+1 >= len(self.images_idle_right):
                    self.wait = 0
                    self.idle_index = 0
                if self.wait > idle_countdown:
                    self.wait = 0
                    self.idle_index += 1
                if self.direction == 'right':
                    self.image = self.images_idle_right[self.idle_index]
                if self.direction == 'left':
                    self.image = self.images_idle_left[self.idle_index]
                self.wait += 1
            elif self.moving:
                self.wait = 0
                if self.counter > walk_countdown:
                    self.counter = 0    
                    self.index += 1
                    if self.index >= len(self.images_run_right):
                        self.index = 0
                    if self.direction == 'right':
                        self.image = self.images_run_right[self.index]
                    if self.direction == 'left':
                        self.image = self.images_walk_left[self.index]

    def update(self):
        dx = 0
        dy = 0
        self.moving = False

        # keyboard input
        key = pygame.key.get_pressed()
        if not godMode: #TODO:TAKE OUT GODMODE
            if key[pygame.K_SPACE] and self.jumped == False:
                self.vel_y = -20
                self.jumped = True

            if key[pygame.K_a] or key[pygame.K_LEFT]:
                dx -= 5
                self.counter += 1
                self.direction = 'left'
                self.moving = True

            if key[pygame.K_d] or key[pygame.K_RIGHT]:
                dx += 5
                self.counter += 1
                self.direction = 'right'
                self.moving = True
        else:
            if key[pygame.K_SPACE] or key[pygame.K_UP] or key[pygame.K_w]:
                dy -= 5
            if key[pygame.K_LEFT] or key[pygame.K_a]:
                dx -= 5
            if key[pygame.K_RIGHT] or key[pygame.K_d]:
                dx += 5
            if key[pygame.K_DOWN] or key[pygame.K_s]:
                dy += 5

        self.animate()
        
        if not godMode: #TODO: TAKE GODMODE OUT
            # add gravity
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

        # check collision
        for tile in world.tiles:
            if tile[2] == True:
                #check collision in x-axis
                if self.direction == 'right':
                    if tile[1].colliderect(self.rect.x + 5, self.rect.y, self.width, self.height):
                        dx = 0
                else:
                    if tile[1].colliderect(self.rect.x - 5, self.rect.y, self.width, self.height):
                        dx = 0
                #check collision in y-axis
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #check if player is below ground
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    #check if player is on ground
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.jumped = False

        # update player coords
        self.rect.x += dx
        self.rect.y += dy

    def draw(self):
        # draw player onto screen
        if self.image in self.images_jump_start_right or self.image in self.images_jump_start_left:
            if self.direction == 'left':
                screen.blit(self.image, (player.rect.x - 55 - scroll[0], player.rect.y - scroll[1] - 50))
            
            if self.direction == 'right':
                screen.blit(self.image, (player.rect.x - 20 - scroll[0], player.rect.y - scroll[1] - 50))
        else:
            screen.blit(self.image, (player.rect.x - scroll[0], player.rect.y - scroll[1]))


#world class
class World():
    def __init__(self, data):
        #load images
        self.tiles = []
        self.tile_ids = {'Tiles':
                            [
                                {
                                    'id':0,
                                    'desc':'mud block, right',
                                    'img':pygame.image.load('img/Tiles/0.png').convert_alpha()
                                }, {
                                    'id':1,
                                    'desc':'floating grass block, left',
                                    'img':pygame.image.load('img/Tiles/1.png').convert_alpha()
                                }, {
                                    'id':2,
                                    'desc':'floating grass block, mid',
                                    'img':pygame.image.load('img/Tiles/2.png').convert_alpha()
                                }, {
                                    'id':3,
                                    'desc':'floating grass block, right',
                                    'img':pygame.image.load('img/Tiles/3.png').convert_alpha()
                                }, {
                                    'id':4,
                                    'desc':'floating mud',
                                    'img':pygame.image.load('img/Tiles/4.png').convert_alpha()
                                }, {
                                    'id':5,
                                    'desc':'floating mud, left corner',
                                    'img':pygame.image.load('img/Tiles/5.png').convert_alpha()
                                }, {
                                    'id':6,
                                    'desc':'floating mud, right corner',
                                    'img':pygame.image.load('img/Tiles/6.png').convert_alpha()
                                }, {
                                    'id':7,
                                    'desc':'plain grass block',
                                    'img':pygame.image.load('img/Tiles/7.png').convert_alpha()
                                }, {
                                    'id':8,
                                    'desc':'grass block, left',
                                    'img':pygame.image.load('img/Tiles/8.png').convert_alpha()
                                }, {
                                    'id':9,
                                    'desc':'grass block, right',
                                    'img':pygame.image.load('img/Tiles/9.png').convert_alpha()
                                }, {
                                    'id':10,
                                    'desc':'grass, left',
                                    'img':pygame.image.load('img/Tiles/10.png').convert_alpha()
                                }, {
                                    'id':11,
                                    'desc':'grass, right',
                                    'img':pygame.image.load('img/Tiles/11.png').convert_alpha()
                                }, {
                                    'id':12,
                                    'desc':'mud block, left',
                                    'img':pygame.image.load('img/Tiles/12.png').convert_alpha()
                                }, {
                                    'id':13,
                                    'desc':'mud with light in left corner',
                                    'img':pygame.image.load('img/Tiles/13.png').convert_alpha()
                                }, {
                                    'id':14,
                                    'desc':'mud with light in right corner',
                                    'img':pygame.image.load('img/Tiles/14.png').convert_alpha()
                                }, {
                                    'id':15,
                                    'desc':'deep mud block',
                                    'img':pygame.image.load('img/Tiles/15.png').convert_alpha()
                                }, {
                                    'id':16,
                                    'desc':'water',
                                    'img':pygame.image.load('img/Tiles/16.png').convert_alpha()
                                }, {
                                    'id':17,
                                    'desc':'waves',
                                    'img':pygame.image.load('img/Tiles/17.png').convert_alpha()
                                }, 
                            ],

                        'Objects':
                            [
                                {
                                    'id':18,
                                    'desc':'Bush, variant #1',
                                    'img':pygame.image.load('img/Objects/18.png').convert_alpha()
                                }, {
                                    'id':19,
                                    'desc':'Bush, variant #2',
                                    'img':pygame.image.load('img/Objects/19.png').convert_alpha()
                                }, {
                                    'id':20,
                                    'desc':'Bush, variant #3',
                                            'img':pygame.image.load('img/Objects/20.png').convert_alpha()
                                        }, {
                                            'id':21,
                                            'desc':'Bush, variant #4',
                                            'img':pygame.image.load('img/Objects/21.png').convert_alpha()
                                        }, {
                                            'id':22,
                                            'desc':'Crate',
                                            'img':pygame.image.load('img/Objects/22.png').convert_alpha()
                                        }, {
                                            'id':23,
                                            'desc':'Mushroom, variant #1',
                                            'img':pygame.image.load('img/Objects/23.png').convert_alpha()
                                        }, {
                                            'id':24,
                                            'desc':'Mushroom, variant #2',
                                            'img':pygame.image.load('img/Objects/24.png').convert_alpha()
                                        }, {
                                            'id':25,
                                            'desc':'Sign, variant #1',
                                            'img':pygame.image.load('img/Objects/25.png').convert_alpha()
                                        }, {
                                            'id':26,
                                            'desc':'Sign, variant #2',
                                            'img':pygame.image.load('img/Objects/26.png').convert_alpha()
                                        }, {
                                            'id':27,
                                            'desc':'Stone',
                                            'img':pygame.image.load('img/Objects/27.png').convert_alpha()
                                        }, {
                                            'id':28,
                                            'desc':'Tree, variant #3',
                                            'img':pygame.image.load('img/Objects/28.png').convert_alpha()
                                        }, {
                                            'id':29,
                                            'desc':'Tree, variant #2',
                                            'img':pygame.image.load('img/Objects/29.png').convert_alpha()
                                        }, {
                                            'id':30,
                                            'desc':'Tree, variant #3',
                                            'img':pygame.image.load('img/Objects/30.png').convert_alpha()
                                        }
                                    ]
                                }

        #char to tile conversion
        row_count = 0
        for row in data:
            col_count = 0
            for c in row:
                c = int(c)
                if c >= 0:
                    img = pygame.transform.scale(self.tile_ids['Tiles'][c]['img'], (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect, True)
                    self.tiles.append(tile)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tiles:
            screen.blit(tile[0], (tile[1][0] - scroll[0], tile[1][1] - scroll[1]))


# load level
load_level('Levels/level_1.csv')

# set player start location
startx, starty = 150, 500#world.tiles[0][1][1], #world.tiles[-1][1][1]
player = Player(startx, starty)

run = True
while run:

    # handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g:
                if not godMode: #TODO: TAKE GODMODE OUT
                    godMode = True
                else:
                    godMode = False

    # draw bg
    screen.blit(bg_img, (0, 0))

    # change scroll vals
    if player.rect.x > 400 or player.rect.x < 400:
        scroll[0] = player.rect.x - 400
    if player.rect.y > 700:
        scroll[1] = player.rect.y - 100
    if player.rect.y < 100:
        scroll[1] = player.rect.y - 100

    # update player
    player.update()

    border_right = len(world.tiles)*tile_size + tile_size
    border_right = border_right/5.25157232704403
    if player.rect.left < 0:
        player.rect.left = 0
    elif player.rect.right > border_right:
        player.rect.right = border_right

    # draw tiles
    world.draw()

    # draw player
    player.draw()

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()