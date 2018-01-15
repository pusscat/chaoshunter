import pygame
import layouts
import time
from enum import Enum

TILESIZE = 32
MOBSIZE = 16
MAPZISE  = 10
bgTiles = []
heroTiles = []
enemyTiles = []

level = 0
lives = 3
score = 0
screen = None

WHITE  = ( 255, 255, 255)
BLUE   = (   0,   0, 255)
GREEN  = (   0, 255,   0)
RED    = ( 255,   0,   0)
PURPLE = ( 255,   0, 255)

def load_tile_table(filename, width, height):
    image = pygame.image.load(filename).convert()
    image_width, image_height = image.get_size()
    tile_table = []
    for tile_y in range(0, image_height/height):
        for tile_x in range(0, image_width/width):
            rect = (tile_x*width, tile_y*height, width, height)
            tile_table.append(image.subsurface(rect))
    return tile_table

class Level():
    def __init__(self, lvlCode, player, enemies):
        self.lvlCode = lvlCode
        self.player = player
        self.enemies = enemies
        self.walls = []

    def DrawBG(self):
        global bgTiles
        global heroTiles
        global enemyTiles
        global TILESIZE
        global screen

        x = 0
        y = 0
        
        image = pygame.Surface((10*TILESIZE, 10*TILESIZE))

        for char in self.lvlCode:
            tile = int(char)
            if tile == 0:
                y += 1
                x = 0
            else:
                screen.blit(bgTiles[tile-1], (x*TILESIZE, y*TILESIZE))
                x += 1

class Orientation(Enum):
    North = 0
    South = 1
    East = 2
    West = 3

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color):
        """ Constructor function """

        # Call the parent's constructor
        pygame.sprite.Sprite.__init__(self)

        # Make a BLUE wall, of the size specified in the parameters
        self.image = pygame.Surface([width, height])
        #self.image.fill(color)

        # Make our top-left corner the passed-in location.
        self.rect = self.image.get_rect()
        self.rect.y = y
        self.rect.x = x


class Enemy(pygame.sprite.Sprite):
    def __init__(self, position):
        pygame.sprite.Sprite.__init__(self)

        global MOBSIZE
        self.image = pygame.Surface([MOBSIZE, MOBSIZE])

        global TILESIZE
        self.rect = self.image.get_rect()
        self.rect.x = position[0]*TILESIZE
        self.rect.y = position[1]*TILESIZE
        self.orient = Orientation.East
        self.change_x = 0
        self.change_y = 0

        self.life = 1

    def move(self, level, player):
        pass

    def hit(self):
        print "hit!"
        self.life = self.life - 1
        if self.life == 0:
            self.image = pygame.Surface([0, 0])
            self.rect.x = 0
            self.rect.y = 0

class Player(pygame.sprite.Sprite):
    """ This class represents the bar at the bottom that the player controls """

    # Set speed vector
    change_x = 0
    change_y = 0

    def __init__(self, position):
        """ Constructor function """

        # Call the parent's constructor
        pygame.sprite.Sprite.__init__(self)

        # Set height, width
        global MOBSIZE
        self.image = pygame.Surface([MOBSIZE, MOBSIZE])

        # Make our top-left corner the passed-in location.
        global TILESIZE
        self.rect = self.image.get_rect()
        self.rect.x = position[0]*TILESIZE
        self.rect.y = position[1]*TILESIZE
        self.orient = Orientation.East
        self.change_x = 0
        self.change_y = 0

        self.life = 1


    def attack(self):
        # shoot a bullet in the direction you are facing
        pass

    def changespeed(self, x, y):
        """ Change the speed of the player. Called with a keypress. """
        self.change_x += x
        self.change_y += y

    def SetOrient(self, orient):
        self.orient = orient

    def move(self, level, enemies):
        """ Find a new position for the player """

        # Move left/righ
        orig = self.rect.x
        self.rect.x += self.change_x

        # Did this update cause us to hit a wall?
        block_hit_list = pygame.sprite.spritecollide(self, level.walls, False)
        enemy_hit_list = pygame.sprite.spritecollide(self, enemies, False)
        block_hit_list = block_hit_list + enemy_hit_list

        self.life = self.life-len(enemy_hit_list)
        print "life: %d" % self.life
        if self.life < 0:
            self.image.fill(BLACK)

        for block in block_hit_list:
            # If we are moving right, set our right side to the left side of
            # the item we hit
            self.rect.x = orig

        # Move up/down
        orig = self.rect.y
        self.rect.y += self.change_y

        # Check and see if we hit anything
        block_hit_list = pygame.sprite.spritecollide(self, level.walls, False)
        for block in block_hit_list:
            self.rect.y = orig
            # Reset our position based on the top/bottom of the object.
            #if self.change_y > 0:
            #    self.rect.bottom = block.rect.top
            #else:
            #    self.rect.top = block.rect.bottom

        #for enemy in pygame.sprite.spritecollide(self.sword, enemies, False):
         #   enemy.hit()


def LoadLevels():
    levels = []

    for level in layouts.levels:
        levels.append(Level(level[0], level[1], level[2]))

    return levels

def DrawLevel(level, levels):
    # snazzy tile flying opening here
    pass

def DrawMob(mob, tileSet):
    SLEFT   = 0
    SRIGHT  = 1
    WLEFT   = 2
    WRIGHT  = 3

    tileNum = 0
    # standing animation
    if mob.orient == Orientation.East:
        tileNum = SRIGHT
    else:
        tileNum = SLEFT

    if pygame.time.get_ticks() % 2 != 0:
        if mob.change_x != 0 or mob.change_y != 0:
            # walking animation
            if mob.orient == Orientation.East:
                tileNum = WRIGHT
            else:
                tileNum = WLEFT

    tile = tileSet[tileNum]

    global screen
    screen.blit(tile, (mob.rect.x, mob.rect.y))
    
def RunLevel(level, levels):
    clock = pygame.time.Clock()
    
    player = Player(levels[level].player)
    movingsprites = pygame.sprite.Group()
    movingsprites.add(player)

    enemies = []
    for enemySpot in levels[level].enemies:
        enemy = Enemy(enemySpot)
        enemies.append(enemy)
        movingsprites.add(enemy)

    done = False

    while not done:
        # process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.SetOrient(Orientation.West)
                    player.changespeed(-5, 0)
                if event.key == pygame.K_RIGHT:
                    player.SetOrient(Orientation.East)
                    player.changespeed(5, 0)
                if event.key == pygame.K_UP:
                    #player.SetOrient(Orientation.North)
                    player.changespeed(0, -5)
                if event.key == pygame.K_DOWN:
                    #player.SetOrient(Orientation.South)
                    player.changespeed(0, 5)
                if event.key == pygame.K_a:
                    player.attack()


            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    player.changespeed(5, 0)
                if event.key == pygame.K_RIGHT:
                    player.changespeed(-5, 0)
                if event.key == pygame.K_UP:
                    player.changespeed(0, 5)
                if event.key == pygame.K_DOWN:
                    player.changespeed(0, -5)

            
        player.move(levels[level], enemies)
        for enemy in enemies:
            enemy.move(levels[level], player)
        
        global heroTiles
        global enemyTiles
        levels[level].DrawBG()
        DrawMob(player, heroTiles)
        for enemy in enemies:
            DrawMob(enemy, enemyTiles)


        pygame.display.flip()
        pygame.display.update()
        clock.tick(60)

def main():
    """ Main Program """

    # Call this function so the Pygame library can initialize itself
    pygame.init()

    # Create an 320x320 sized screen
    global screen 
    screen = pygame.display.set_mode([10*TILESIZE, 10*TILESIZE])

    # Set the title of the window
    pygame.display.set_caption('Chaos Hunter')

    # load tilesets
    global bgTiles
    global heroTiles
    global enemyTiles

    bgTiles = load_tile_table("assets/bgtiles.png", TILESIZE, TILESIZE)
    heroTiles = load_tile_table("assets/hero.png", MOBSIZE, MOBSIZE)
    enemyTiles = load_tile_table("assets/enemy.png", MOBSIZE, MOBSIZE)

    # load level layouts
    levels = LoadLevels()


    # Run game!
    global level
    global lives
    global score

    level = 0
    lives = 3
    score = 0
    while level < len(levels):
        DrawLevel(level, levels)
        RunLevel(level,levels)
        if lives > 0:
            level += 1
        else:
            GameOver()
    
    if level > len(levels):
        GameWon()


    pygame.quit()

if __name__ == "__main__":
    main()
