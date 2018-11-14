import sys, pygame
from pygame.locals import *
import fastest_path
import time
#import asyncio
#import websockets
import threading
from collections import deque
from WebClient import *
#from process_sensor import *
import process_sensor as ps 
import Explored as E


fpath = False
IP_addr = ""
#websocket = websockets.connect('ws://192.168.5.5:8764')
interval = 0.1          
wifiout_Q = deque()
wifiin_Q = deque()

wifi = wifi_client()
wifi.connect_wifi()  ## *********************** REMOVE FOR WIFI *****************************

def wifi_read():
    try:
        while 1: 
            msg = wifi.read()
            if len(msg)> 0:
                wifiin_Q.append(msg)
                print("recv: " + msg ) 
            time.sleep(interval)
    except KeyboardInterrupt:
        print("closed")
        wifi.disconnect()

def wifi_write():
    try:
        while 1: 
            time.sleep(interval)
            if len(wifiout_Q)> 0:
                command = wifiout_Q.popleft()
                wifi.write(command)
    except KeyboardInterrupt:
        print("closed")
        wifi.disconnect()


Size = 16

size_x = Size
size_y = Size 

change_x = Size
change_y = Size

SPEED = Size
timer = 375

DAY9YELLOW = (255, 167, 26)
GOAL = (245, 163, 183)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (200, 200, 200)
BLUE = (50, 50, 255)
WHITE = (255,255,255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

## short: 10-30 long: 20-60
SHORT_SENSOR_RANGE = 3
LONG_SENSOR_RANGE = 6

# valid arena coordinates, inclusive
X_MIN = 1
X_MAX = 15
Y_MIN = 1
Y_MAX = 20

m = 17
n = 22  ## col

goal_x = 16*Size #576
goal_y = 1 * Size

lfmax = 4
cfmax = 4
rfmax = 4
r1max = 3
r2max = 3
lhsmax = 6

# List to hold all the sprites
all_sprite_list = pygame.sprite.Group()
clock = pygame.time.Clock()

robot = None
size = width, height = 17*Size, 22*Size
screen = pygame.display.set_mode(size)
pygame.display.set_caption('A Simulator')

## ********************* Game Window Controls ************************

def text_objects(text, font, color):
    textSurface = font.render(text, True, color)
    return textSurface, textSurface.get_rect()

def quit_game():
    wifi.disconnect()
    pygame.quit()
    quit()

def button(msg, x, y, w, h, ic, ac, action = None): # inactive color, active color
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed() #click is a tuple (left_click, right_click, middle_click)

    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(screen, ac, (x, y, w, h))  ## global screen???
        if click[0] == 1 and action != None:
            action() # Note that function reference is passed into this function
    else:
        pygame.draw.rect(screen, ic, (x, y, w, h)) 

    smallText = pygame.font.Font("freesansbold.ttf", 15)
    textSurface, textRect = text_objects(msg, smallText, WHITE)
    textRect.center = ((x + (w/2)), (y + (h/2)))
    screen.blit(textSurface, textRect) 

def intro_window():
    pygame.init()
    intro = True
    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        screen.fill(WHITE)
        largeText = pygame.font.Font('freesansbold.ttf', 30)
        textSurface, textRect = text_objects("A Simulator", largeText, BLACK)
        textRect.center = ((width/2),(height/2))
        screen.blit(textSurface, textRect)

        button("GO", width*0.5/4, height*3/4, Size*4, Size*2, GREEN, GREY, explore_loop)
        button("QUIT", width*2.5/4, height*3/4, Size*4, Size*2, RED, GREY, quit_game)

        pygame.display.update()
        clock.tick(15)  

def fp_window():
    fp_window = True
    while fp_window:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        screen.fill(WHITE)
        largeText = pygame.font.Font('freesansbold.ttf', 30)
        textSurface, textRect = text_objects("Fastest Path", largeText, BLACK)
        textRect.center = ((width/2),(height/2))
        screen.blit(textSurface, textRect)

        button("GO", width*0.5/4, height*3/4, Size*4, Size*2, GREEN, GREY, fp_loop)
        button("QUIT", width*2.5/4, height*3/4, Size*4, Size*2, RED, GREY, quit_game)

        pygame.display.update()
        clock.tick(15) 

def finish_window():
    finish_window = True
    while finish_window:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        screen.fill(WHITE)
        largeText = pygame.font.Font('freesansbold.ttf', 30)
        textSurface, textRect = text_objects("OK Done!", largeText, BLACK)
        textRect.center = ((width/2),(height/2))
        screen.blit(textSurface, textRect)

        #button("GO", width*0.5/4, height*3/4, Size*4, Size*2, GREEN, GREY, fp_loop)
        button("QUIT", width*2.5/4, height*3/4, Size*4, Size*2, RED, GREY, quit_game)

        pygame.display.update()
        clock.tick(15) 

## ************************ End of Game Contorls ********************* 


# This map is not used during actual run
            # x--->
           # 0 ------------------>                      21
maze = [    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],  # 0      y
            [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1],  # 1      |
            [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1],  # 2    \ | /  
            [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1],  # 3     \ /
            [1,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,1],  # 4      `
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],  # 5
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],  # 6
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,1],  # 7
            [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,1],  # 8
            [1,0,0,0,0,0,1,1,1,0,0,0,0,0,0,1,0,0,0,0,1,1],  # 9
            [1,0,0,0,0,0,1,1,1,0,0,0,0,0,0,1,1,0,0,0,0,1],  # 10
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],  # 11
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],  # 12
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],  # 13
            [1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],  # 14
            [1,0,0,0,0,0,1,0,0,0,0,0,0,1,1,1,0,0,0,0,0,1],  # 15
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]  # 16 
        ]  # 21


## On the exploration map: 1- space, 2-block, 0-unexplored
EXP_BLOCK = 2
EXP_UNKNOWN = 0
EXP_SPACE = 1
            # x--->
           # 0 ------------------>                      21
exp_map = [ [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],  # 0      y
            [2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],  # 1      |
            [2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],  # 2    \ | /  
            [2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],  # 3     \ /
            [2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],  # 4      `
            [2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],  # 5
            [2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],  # 6
            [2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],  # 7
            [2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],  # 8
            [2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],  # 9
            [2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],  # 10
            [2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],  # 11
            [2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],  # 12
            [2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],  # 13
            [2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],  # 14
            [2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],  # 15
            [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]  # 16 
        ]  # 21

def get_MDF():
    global exp_map
    p1 = ""
    p2 = ""
    mdf1 = ""
    mdf2 = ""
    cnt1 = 1
    cnt2 = 1
    for i in range(n-2, 0, -1):
        for j in range(1, m-1):
            if exp_map[j][i] == 0:
                p1 += "0"
            else:
                p1 += "1"
            if cnt1 % 4 == 0:
                mdf1 += str(hex(int(p1,2)))[2:]
                p1 = ""
            cnt1 += 1

    for i in range(n-2, 0, -1):
        for j in range(1, m-1):
            if exp_map[j][i] == 2:
                p2 += "1"
            else:
                p2 += "0"
            if cnt2 % 4 == 0:
                mdf2 += str(hex(int(p2,2)))[2:]
                p2 = ""
            cnt2 += 1

    return mdf1, mdf2


# NOT USED FOR ACTUAL RUN
def to_coord(pixel):
    return int(pixel/Size)

# Probing the surroundings
## TODO: read signals from arduino. e.g. "SIG 1,2,3,4,5,6" (F3 R2 L1)
def probe_update():
    # To be replaced with actual reading
    global robot
    x,y = to_coord(robot.rect.x), to_coord(robot.rect.y)
    face = robot.face%4
    # facing NORTH
    if face == 0:
        #RHS
        for j in range(-1, 2, 2):
            for i in range(SHORT_SENSOR_RANGE):
                if maze[x+2+i][y+j] == 1:
                    exp_map[x+2+i][y+j] = EXP_BLOCK
                    new_wall = Wall((x+2+i)*Size, (y+j)*Size, Size, Size)
                    all_sprite_list.add(new_wall)
                    break
                elif maze[x+2+i][y+j] == 0:
                    exp_map[x+2+i][y+j] = EXP_SPACE
                    new_space = Space((x+2+i)*Size, (y+j)*Size, Size, Size)
                    all_sprite_list.add(new_space)
        #LHS
        for j in range(-1,2):
            for i in range(LONG_SENSOR_RANGE):
                if (X_MIN-1) <= x-2-i <= (X_MAX+1):
                    if maze[x-2-i][y+j] == 1:
                        exp_map[x-2-i][y+j] = EXP_BLOCK
                        new_wall = Wall((x-2-i)*Size, (y+j)*Size, Size, Size)
                        all_sprite_list.add(new_wall)
                        break
                    elif maze[x-2-i][y+j] == 0:
                        exp_map[x-2-i][y+j] = EXP_SPACE
                        new_space = Space((x-2-i)*Size, (y+j)*Size, Size, Size)
                        all_sprite_list.add(new_space)

        # FRONT
        for j in range(-1,2):
            for i in range(SHORT_SENSOR_RANGE):
                if maze[x+j][y-2-i] == 1:
                    exp_map[x+j][y-2-i] = EXP_BLOCK
                    new_wall = Wall((x+j)*Size, (y-2-i)*Size, Size, Size)
                    all_sprite_list.add(new_wall)
                    break 
                elif maze[x+j][y-2-i] == 0:
                    exp_map[x+j][y-2-i] = EXP_SPACE
                    new_space = Space((x+j)*Size, (y-2-i)*Size, Size, Size)
                    all_sprite_list.add(new_space)

    # facing EAST
    elif face == 1:
        #RHS
        for j in range(-1, 2, 2):
            for i in range(SHORT_SENSOR_RANGE):
                if maze[x+j][y+2+i] == 1:
                    exp_map[x+j][y+2+i] = EXP_BLOCK
                    new_wall = Wall((x+j)*Size, (y+2+i)*Size, Size, Size)
                    all_sprite_list.add(new_wall)
                    break
                elif maze[x+j][y+2+i] == 0:
                    exp_map[x+j][y+2+i] = EXP_SPACE
                    new_space = Space((x+j)*Size, (y+2+i)*Size, Size, Size)
                    all_sprite_list.add(new_space)

        #LHS
        for j in range(0,1):
            for i in range(LONG_SENSOR_RANGE):
                if (Y_MIN-1) <= y-2-i <= (Y_MAX+1):
                    if maze[x+j][y-2-i] == 1:
                        exp_map[x+j][y-2-i] = EXP_BLOCK
                        new_wall = Wall((x+j)*Size, (y-2-i)*Size, Size, Size)
                        all_sprite_list.add(new_wall)
                        break 
                    elif maze[x+j][y-2-i] == 0:
                        exp_map[x+j][y-2-i] = EXP_SPACE
                        new_space = Space((x+j)*Size, (y-2-i)*Size, Size, Size)
                        all_sprite_list.add(new_space)


        # FRONT
        for j in range(-1, 2):
            for i in range(SHORT_SENSOR_RANGE):
                if maze[x+2+i][y+j] == 1:
                    exp_map[x+2+i][y+j] = EXP_BLOCK
                    new_wall = Wall((x+2+i)*Size, (y+j)*Size, Size, Size)
                    all_sprite_list.add(new_wall)
                    break 
                elif maze[x+2+i][y+j] == 0:
                    exp_map[x+2+i][y+j] = EXP_SPACE
                    new_space = Space((x+2+i)*Size, (y+j)*Size, Size, Size)
                    all_sprite_list.add(new_space)

    # facing SOUTH
    elif face == 2:
        #RHS
        for j in range(-1, 2, 2):
            for i in range(SHORT_SENSOR_RANGE):
                if maze[x-2-i][y+j] == 1:
                    exp_map[x-2-i][y+j] = EXP_BLOCK
                    new_wall = Wall((x-2-i)*Size, (y+j)*Size, Size, Size)
                    all_sprite_list.add(new_wall)
                    break
                elif maze[x-2-i][y+j] == 0:
                    exp_map[x-2-i][y+j] = EXP_SPACE
                    new_space = Space((x-2-i)*Size, (y+j)*Size, Size, Size)
                    all_sprite_list.add(new_space)
        #LHS
        for j in range(0,1):
            for i in range(LONG_SENSOR_RANGE):
                if (X_MIN-1) <= x+2+i <= (X_MAX+1):
                    if maze[x+2+i][y+j] == 1:
                        exp_map[x+2+i][y+j] = EXP_BLOCK
                        new_wall = Wall((x+2+i)*Size, (y+j)*Size, Size, Size)
                        all_sprite_list.add(new_wall)
                        break
                    elif maze[x+2+i][y+j] == 0:
                        exp_map[x+2+i][y+j] = EXP_SPACE
                        new_space = Space((x+2+i)*Size, (y+j)*Size, Size, Size)
                        all_sprite_list.add(new_space)

        # FRONT
        for j in range(-1,2):
            for i in range(SHORT_SENSOR_RANGE):
                if maze[x+j][y+2+i] == 1:
                    exp_map[x+j][y+2+i] = EXP_BLOCK
                    new_wall = Wall((x+j)*Size, (y+2+i)*Size, Size, Size)
                    all_sprite_list.add(new_wall)
                    break
                elif maze[x+j][y+2+i] == 0:
                    exp_map[x+j][y+2+i] = EXP_SPACE
                    new_space = Space((x+j)*Size, (y+2+i)*Size, Size, Size)
                    all_sprite_list.add(new_space)

    # facing WEST
    elif face == 3:
        #RHS
        for j in range(-1,2,2):
            for i in range(SHORT_SENSOR_RANGE):
                if maze[x+j][y-2-i] == 1:
                    exp_map[x+j][y-2-i] = EXP_BLOCK
                    new_wall = Wall((x+j)*Size, (y-2-i)*Size, Size, Size)
                    all_sprite_list.add(new_wall)
                    break
                elif maze[x+j][y-2-i] == 0:
                    exp_map[x+j][y-2-i] = EXP_SPACE
                    new_space = Space((x+j)*Size, (y-2-i)*Size, Size, Size)
                    all_sprite_list.add(new_space)
        #LHS
        for j in range(0, 1):
            for i in range(LONG_SENSOR_RANGE):
                if (Y_MIN-1) <= y+2+i <= (Y_MAX+1):
                    if maze[x+j][y+2+i] == 1:
                        exp_map[x+j][y+2+i] = EXP_BLOCK
                        new_wall = Wall((x+j)*Size, (y+2+i)*Size, Size, Size)
                        all_sprite_list.add(new_wall)
                        break   
                    elif maze[x+j][y+2+i] == 0:
                        exp_map[x+j][y+2+i] = EXP_SPACE
                        new_space = Space((x+j)*Size, (y+2+i)*Size, Size, Size)
                        all_sprite_list.add(new_space)

        # FRONT
        for j in range(-1,2):
            for i in range(SHORT_SENSOR_RANGE):
                if maze[x-2-i][y+j] == 1:
                    exp_map[x-2-i][y+j] = EXP_BLOCK
                    new_wall = Wall((x-2-i)*Size, (y+j)*Size, Size, Size)
                    all_sprite_list.add(new_wall)
                    break 
                elif maze[x-2-i][y+j] == 0:
                    exp_map[x-2-i][y+j] = EXP_SPACE
                    new_space = Space((x-2-i)*Size, (y+j)*Size, Size, Size)
                    all_sprite_list.add(new_space)

# takes in a list of all the raw sensor values: [lf,cf,rf,r1,r2,lhs]
## For now, calibration base on rhs sensors only
def update_exp_map(x, y, face, raw_sensor_list):

    print("Probing position: " + str(x) + str(y))

    raw_sensor = list(map(int, raw_sensor_list.split(',')))
    print(raw_sensor)
    if raw_sensor is not None:
        front_list = raw_sensor[:3]
        rhs_list = raw_sensor[3:4]
        lhs_list = [raw_sensor[-1]]
        print(front_list)
        print(rhs_list)
        print(lhs_list)

    for i in range(3):
        for j in range(3):
            exp_map[x-1+i][y-1+j] = E.EXP_SPACE
            new_space = Space((x-1+i)*Size, (y-1+j)*Size, Size, Size)
            all_sprite_list.add(new_space)

    # facing NORTH
    if face == 0:
        #RHS
        r1 = ps.decode_sensor(1, rhs_list)
        if r1 == -1:
            #calibrate_slip()
            return -1
        else:
            # R1
            if r1 == 100: ## blank space
                for i in range(r1max):
                    #if exp_map[x+2+i][y-1] != E.EXP_BLOCK:
                    row, col = x+2+i, y-1
                    if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                        break
                    exp_map[x+2+i][y-1] = E.EXP_SPACE
                    new_space = Space((x+2+i)*Size, (y-1)*Size, Size, Size)
                    all_sprite_list.add(new_space)
            else:
                for i in range(r1-1):
                    #if exp_map[x+2+i][y-1] != E.EXP_BLOCK:
                    row, col = x+2+i, y-1
                    if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                        break
                    exp_map[x+2+i][y-1] = E.EXP_SPACE
                    new_space = Space((x+2+i)*Size, (y-1)*Size, Size, Size)
                    all_sprite_list.add(new_space)
                if E.X_MIN-1 <= x+1+r1 <= E.X_MAX+1 and E.Y_MIN-1 <= y-1 <= E.Y_MAX+1: 
                    exp_map[x+1+r1][y-1] = E.EXP_BLOCK
                    new_wall = Wall((x+1+r1)*Size, (y-1)*Size, Size, Size)
                    all_sprite_list.add(new_wall)
            '''
            # R2
            if r2 == 100:
                for i in range(r2max):
                    #if exp_map[x+2+i][y+1] != E.EXP_BLOCK:
                    row, col = x+2+i, y+1
                    if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                        break
                    exp_map[x+2+i][y+1] = E.EXP_SPACE
                    new_space = Space((x+2+i)*Size, (y+1)*Size, Size, Size)
                    all_sprite_list.add(new_space)
            else:
                for i in range(r2-1):
                    #if exp_map[x+2+i][y+1] != E.EXP_BLOCK:
                    row, col = x+2+i, y+1
                    if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                        break
                    exp_map[x+2+i][y+1] = E.EXP_SPACE
                    new_space = Space((x+2+i)*Size, (y+1)*Size, Size, Size)
                    all_sprite_list.add(new_space)
                if E.X_MIN-1 <= x+1+r2 <= E.X_MAX+1 and E.Y_MIN-1 <= y+1 <= E.Y_MAX+1:
                    exp_map[x+1+r2][y+1] = E.EXP_BLOCK
                    new_wall = Wall((x+1+r2)*Size, (y+1)*Size, Size, Size)
                    all_sprite_list.add(new_wall)
            '''
            

        #LHS
        lhs = ps.decode_sensor(2, lhs_list)
        # no calibration for lhs
        if lhs == 100:
            for i in range(lhsmax):
                #if exp_map[x-2-i][y] != E.EXP_BLOCK:
                row, col = x-2-i, y
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                exp_map[x-2-i][y] = E.EXP_SPACE
                new_space = Space((x-2-i)*Size, (y)*Size, Size, Size)
                all_sprite_list.add(new_space)
        else:
            for i in range(lhs - 1):
                #if exp_map[x-2-i][y] != E.EXP_BLOCK:
                row, col = x-2-i, y
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                exp_map[x-2-i][y] = E.EXP_SPACE
                new_space = Space((x-2-i)*Size, (y)*Size, Size, Size)
                all_sprite_list.add(new_space)
            if E.X_MIN-1 <= x-1-lhs <= E.X_MAX+1 and E.Y_MIN-1 <= y <= E.Y_MAX+1:
                exp_map[x-1-lhs][y] = E.EXP_BLOCK
                new_wall = Wall((x-1-lhs)*Size, (y)*Size, Size, Size)
                all_sprite_list.add(new_wall)

        #FRONT
        fl, fc, fr = ps.decode_sensor(0, front_list)
        # no calibration for front
        # FL
        if fl == 100:
            for i in range(lfmax):
                #if exp_map[x-1][y-2-i] != E.EXP_BLOCK:
                row, col = x-1, y-2-i
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                exp_map[x-1][y-2-i] = E.EXP_SPACE
                new_space = Space((x-1)*Size, (y-2-i)*Size, Size, Size)
                all_sprite_list.add(new_space)
        else:
            for i in range(fl - 1):
                row, col = x-1, y-2-i
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                #if exp_map[x-1][y-2-i] != E.EXP_BLOCK:
                exp_map[x-1][y-2-i] = E.EXP_SPACE
                new_space = Space((x-1)*Size, (y-2-i)*Size, Size, Size)
                all_sprite_list.add(new_space)
            if E.X_MIN-1 <= x-1 <= E.X_MAX+1 and E.Y_MIN-1 <= y-1-fl <= E.Y_MAX+1:
                exp_map[x-1][y-1-fl] = E.EXP_BLOCK
                new_wall = Wall((x-1)*Size, (y-1-fl)*Size, Size, Size)
                all_sprite_list.add(new_wall)
        # FC
        if fc == 100:
            for i in range(cfmax):
                #if exp_map[x][y-2-i] != E.EXP_BLOCK:
                row, col = x, y-2-i
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                exp_map[x][y-2-i] = E.EXP_SPACE
                new_space = Space((x)*Size, (y-2-i)*Size, Size, Size)
                all_sprite_list.add(new_space)
        else:
            for i in range(fc - 1):
                #if exp_map[x][y-2-i] != E.EXP_BLOCK:
                row, col = x, y-2-i
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                exp_map[x][y-2-i] = E.EXP_SPACE
                new_space = Space((x)*Size, (y-2-i)*Size, Size, Size)
                all_sprite_list.add(new_space)
            if E.X_MIN-1 <= x <= E.X_MAX+1 and E.Y_MIN-1 <= y-1-fc <= E.Y_MAX+1: 
                exp_map[x][y-1-fc] = E.EXP_BLOCK
                new_wall = Wall((x)*Size, (y-1-fc)*Size, Size, Size)
                all_sprite_list.add(new_wall)
        # FR
        if fr == 100:
            for i in range(rfmax):
                #if exp_map[x+1][y-2-i] != E.EXP_BLOCK:
                row, col = x+1, y-2-i
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                exp_map[x+1][y-2-i] = E.EXP_SPACE
                new_space = Space((x+1)*Size, (y-2-i)*Size, Size, Size)
                all_sprite_list.add(new_space)
        else:
            for i in range(fr - 1):
                #if exp_map[x+1][y-2-i] != E.EXP_BLOCK:
                row, col = x+1, y-2-i
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                exp_map[x+1][y-2-i] = E.EXP_SPACE
                new_space = Space((x+1)*Size, (y-2-i)*Size, Size, Size)
                all_sprite_list.add(new_space)
            if E.X_MIN-1 <= x+1 <= E.X_MAX+1 and E.Y_MIN-1 <= y-1-fr <= E.Y_MAX+1:
                exp_map[x+1][y-1-fr] = E.EXP_BLOCK
                new_wall = Wall((x+1)*Size, (y-1-fr)*Size, Size, Size)
                all_sprite_list.add(new_wall)


    # facing EAST
    elif face == 1:
        #RHS
        r1 = ps.decode_sensor(1, rhs_list)
        if r1 == -1:
            #calibrate_slip()
            return -1
        else:
            # R1
            if r1 == 100: ## blank space
                for i in range(r1max):
                    #if exp_map[x+1][y+2+i] != E.EXP_BLOCK:
                    row, col = x+1, y+2+i
                    if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                        break
                    exp_map[x+1][y+2+i] = E.EXP_SPACE
                    new_space = Space((x+1)*Size, (y+2+i)*Size, Size, Size)
                    all_sprite_list.add(new_space)
            else:
                for i in range(r1-1):
                    #if exp_map[x+1][y+2+i] != E.EXP_BLOCK:
                    row, col = x+1, y+2+i
                    if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                        break
                    exp_map[x+1][y+2+i] = E.EXP_SPACE
                    new_space = Space((x+1)*Size, (y+2+i)*Size, Size, Size)
                    all_sprite_list.add(new_space)
                if E.X_MIN-1 <= x+1 <= E.X_MAX+1 and E.Y_MIN-1 <= y+1+r1 <= E.Y_MAX+1:
                    exp_map[x+1][y+1+r1] = E.EXP_BLOCK
                    new_wall = Wall((x+1)*Size, (y+1+r1)*Size, Size, Size)
                    all_sprite_list.add(new_wall)
            '''
            # R2
            if r2 == 100:
                for i in range(r2max):
                    #if exp_map[x-1][y+2+i] != E.EXP_BLOCK:
                    row, col = x-1, y+2+i
                    if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                        break
                    exp_map[x-1][y+2+i] = E.EXP_SPACE
                    new_space = Space((x-1)*Size, (y+2+i)*Size, Size, Size)
                    all_sprite_list.add(new_space)
            else:
                for i in range(r2-1):
                    #if exp_map[x-1][y+2+i] != E.EXP_BLOCK:
                    row, col = x-1, y+2+i
                    if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                        break
                    exp_map[x-1][y+2+i] = E.EXP_SPACE
                    new_space = Space((x-1)*Size, (y+2+i)*Size, Size, Size)
                    all_sprite_list.add(new_space)
                if E.X_MIN-1 <= x-1 <= E.X_MAX+1 and E.Y_MIN-1 <= y+1+r2 <= E.Y_MAX+1:
                    exp_map[x-1][y+1+r2] = E.EXP_BLOCK
                    new_wall = Wall((x-1)*Size, (y+1+r2)*Size, Size, Size)
                    all_sprite_list.add(new_wall)
            '''



        #LHS
        lhs = ps.decode_sensor(2, lhs_list)
        # no calibration for lhs
        if lhs == 100:
            for i in range(lhsmax):
                #if exp_map[x][y-2-i] != E.EXP_BLOCK:
                row, col = x, y-2-i
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                exp_map[x][y-2-i] = E.EXP_SPACE
                new_space = Space((x)*Size, (y-2-i)*Size, Size, Size)
                all_sprite_list.add(new_space)
        else:
            for i in range(lhs - 1):
                #if exp_map[x][y-2-i] != E.EXP_BLOCK:
                row, col = x, y-2-i
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                exp_map[x][y-2-i] = E.EXP_SPACE
                new_space = Space((x)*Size, (y-2-i)*Size, Size, Size)
                all_sprite_list.add(new_space)
            if E.X_MIN-1 <= x+1 <= E.X_MAX+1 and E.Y_MIN-1 <= y-1-lhs <= E.Y_MAX+1:
                exp_map[x+1][y-1-lhs] = E.EXP_BLOCK
                new_wall = Wall((x)*Size, (y-1-lhs)*Size, Size, Size)
                all_sprite_list.add(new_wall)

        #FRONT
        fl, fc, fr = ps.decode_sensor(0, front_list)
        # no calibration for front
        # FL
        if fl == 100:
            for i in range(lfmax):
                #if exp_map[x+2+i][y-1] != E.EXP_BLOCK:
                row, col = x+2+i, y-1
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                exp_map[x+2+i][y-1] = E.EXP_SPACE
                new_space = Space((x+2+i)*Size, (y-1)*Size, Size, Size)
                all_sprite_list.add(new_space)
        else:
            for i in range(fl - 1):
                #if exp_map[x+2+i][y-1] != E.EXP_BLOCK:
                row, col = x+2+i, y-1
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                exp_map[x+2+i][y-1] = E.EXP_SPACE
                new_space = Space((x+2+i)*Size, (y-1)*Size, Size, Size)
                all_sprite_list.add(new_space)
            if E.X_MIN-1 <= x+1+fl <= E.X_MAX+1 and E.Y_MIN-1 <= y-1 <= E.Y_MAX+1:
                exp_map[x+1+fl][y-1] = E.EXP_BLOCK
                new_wall = Wall((x+1+fl)*Size, (y-1)*Size, Size, Size)
                all_sprite_list.add(new_wall)
        # FC
        if fc == 100:
            for i in range(cfmax):
                #if exp_map[x+2+i][y] != E.EXP_BLOCK:
                row, col = x+2+i, y
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                exp_map[x+2+i][y] = E.EXP_SPACE
                new_space = Space((x+2+i)*Size, (y)*Size, Size, Size)
                all_sprite_list.add(new_space)
        else:
            for i in range(fc - 1):
                #if exp_map[x+2+i][y] != E.EXP_BLOCK:
                row, col = x+2+i, y
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                exp_map[x+2+i][y] = E.EXP_SPACE
                new_space = Space((x+2+i)*Size, (y)*Size, Size, Size)
                all_sprite_list.add(new_space)
            if E.X_MIN-1 <= x+1+fc <= E.X_MAX+1 and E.Y_MIN-1 <= y <= E.Y_MAX+1:
                exp_map[x+1+fc][y] = E.EXP_BLOCK
                new_wall = Wall((x+1+fc)*Size, (y)*Size, Size, Size)
                all_sprite_list.add(new_wall)
        # FR
        if fr == 100:
            for i in range(rfmax):
                #if exp_map[x+2+i][y+1] != E.EXP_BLOCK:
                row, col = x+2+i, y+1
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                exp_map[x+2+i][y+1] = E.EXP_SPACE
                new_space = Space((x+2+i)*Size, (y+1)*Size, Size, Size)
                all_sprite_list.add(new_space)
        else:
            for i in range(fr - 1):
                #if exp_map[x+2+i][y+1] != E.EXP_BLOCK:
                row, col = x+2+i, y+1
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                exp_map[x+2+i][y+1] = E.EXP_SPACE
                new_space = Space((x+2+i)*Size, (y+1)*Size, Size, Size)
                all_sprite_list.add(new_space)
            if E.X_MIN-1 <= x+1+fr <= E.X_MAX+1 and E.Y_MIN-1 <= y+1 <= E.Y_MAX+1:
                exp_map[x+1+fr][y+1] = E.EXP_BLOCK
                new_wall = Wall((x+1+fr)*Size, (y+1)*Size, Size, Size)
                all_sprite_list.add(new_wall)


    # facing SOUTH
    elif face == 2:
        #RHS
        r1 = ps.decode_sensor(1, rhs_list)
        if r1 == -1:
            #calibrate_slip()
            return -1
        else:
            # R1
            if r1 == 100: ## blank space
                for i in range(r1max):
                    #if exp_map[x-2-i][y+1] != E.EXP_BLOCK:
                    row, col = x-2-i, y+1
                    if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                        break
                    exp_map[x-2-i][y+1] = E.EXP_SPACE
                    new_space = Space((x-2-i)*Size, (y+1)*Size, Size, Size)
                    all_sprite_list.add(new_space)
            else:
                for i in range(r1-1):
                    #if exp_map[x-2-i][y+1] != E.EXP_BLOCK:
                    row, col = x-2-i, y+1
                    if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                        break
                    exp_map[x-2-i][y+1] = E.EXP_SPACE
                    new_space = Space((x-2-i)*Size, (y+1)*Size, Size, Size)
                    all_sprite_list.add(new_space)
                if E.X_MIN-1 <= x-1-r1 <= E.X_MAX+1 and E.Y_MIN-1 <= y+1 <= E.Y_MAX+1:
                    exp_map[x-1-r1][y+1] = E.EXP_BLOCK
                    new_wall = Wall((x-1-r1)*Size, (y+1)*Size, Size, Size)
                    all_sprite_list.add(new_wall)
            
            '''
            # R2
            if r2 == 100:
                for i in range(r2max):
                    #if exp_map[x-2-i][y-1] != E.EXP_BLOCK:
                    row, col = x-2-i, y-1
                    if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                        break
                    exp_map[x-2-i][y-1] = E.EXP_SPACE
                    new_space = Space((x-2-i)*Size, (y-1)*Size, Size, Size)
                    all_sprite_list.add(new_space)
            else:
                for i in range(r2-1):
                    #if exp_map[x-2-i][y-1] != E.EXP_BLOCK:
                    row, col = x-2-i, y-1
                    if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                        break
                    E.exp_map[x-2-i][y-1] = E.EXP_SPACE
                    new_space = Space((x-2-i)*Size, (y-1)*Size, Size, Size)
                    all_sprite_list.add(new_space)
                if E.X_MIN-1 <= x-1-r2 <= E.X_MAX+1 and E.Y_MIN-1 <= y-1 <= E.Y_MAX+1:
                    exp_map[x-1-r2][y-1] = E.EXP_BLOCK
                    new_wall = Wall((x-1-r2)*Size, (y-1)*Size, Size, Size)
                    all_sprite_list.add(new_wall)
            '''

        #LHS
        lhs = ps.decode_sensor(2, lhs_list)
        # no calibration for lhs
        if lhs == 100:
            for i in range(lhsmax):
                #if exp_map[x+2+i][y] != E.EXP_BLOCK:
                row, col = x+2+i, y
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                exp_map[x+2+i][y] = E.EXP_SPACE
                new_space = Space((x+2+i)*Size, (y)*Size, Size, Size)
                all_sprite_list.add(new_space)
        else:
            for i in range(lhs - 1):
                #if exp_map[x+2+i][y] != E.EXP_BLOCK:
                row, col = x+2+i, y
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                exp_map[x+2+i][y] = E.EXP_SPACE
                new_space = Space((x+2+i)*Size, (y)*Size, Size, Size)
                all_sprite_list.add(new_space)
            if E.X_MIN-1 <= x+1+lhs <= E.X_MAX+1 and E.Y_MIN-1 <= y <= E.Y_MAX+1:
                exp_map[x+1+lhs][y] = E.EXP_BLOCK
                new_wall = Wall((x+1+lhs)*Size, (y)*Size, Size, Size)
                all_sprite_list.add(new_wall)

        #FRONT
        fl, fc, fr = ps.decode_sensor(0, front_list)
        # no calibration for front
        # FL
        if fl == 100:
            for i in range(lfmax):
                #if exp_map[x+1][y+2+i] != E.EXP_BLOCK:
                row, col = x+1, y+2+i
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                exp_map[x+1][y+2+i] = E.EXP_SPACE
                new_space = Space((x+1)*Size, (y+2+i)*Size, Size, Size)
                all_sprite_list.add(new_space)
        else:
            for i in range(fl - 1):
                #if exp_map[x+1][y+2+i] != E.EXP_BLOCK:
                row, col = x+1, y+2+i
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                exp_map[x+1][y+2+i] = E.EXP_SPACE
                new_space = Space((x+1)*Size, (y+2+i)*Size, Size, Size)
                all_sprite_list.add(new_space)
            if E.X_MIN-1 <= x+1 <= E.X_MAX+1 and E.Y_MIN-1 <= y+1+fl <= E.Y_MAX+1:
                exp_map[x+1][y+1+fl] = E.EXP_BLOCK
                new_wall = Wall((x+1)*Size, (y+1+fl)*Size, Size, Size)
                all_sprite_list.add(new_wall)
        # FC
        if fc == 100:
            for i in range(cfmax):
                #if exp_map[x][y+2+i] != E.EXP_BLOCK:
                row, col = x, y+2+i
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                exp_map[x][y+2+i] = E.EXP_SPACE
                new_space = Space((x)*Size, (y+2+i)*Size, Size, Size)
                all_sprite_list.add(new_space)
        else:
            for i in range(fc - 1):
                #if exp_map[x][y+2+i] != E.EXP_BLOCK:
                row, col = x, y+2+i
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                exp_map[x][y+2+i] = E.EXP_SPACE
                new_space = Space((x)*Size, (y+2+i)*Size, Size, Size)
                all_sprite_list.add(new_space)
            if E.X_MIN-1 <= x <= E.X_MAX+1 and E.Y_MIN-1 <= y+1+fc <= E.Y_MAX+1:
                exp_map[x][y+1+fc] = E.EXP_BLOCK
                new_wall = Wall((x)*Size, (y+1+fc)*Size, Size, Size)
                all_sprite_list.add(new_wall)
        # FR
        if fr == 100:
            for i in range(rfmax):
                #if exp_map[x-1][y+2+i] != E.EXP_BLOCK:
                row, col = x-1, y+2+i
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                exp_map[x-1][y+2+i] = E.EXP_SPACE
                new_space = Space((x-1)*Size, (y+2+i)*Size, Size, Size)
                all_sprite_list.add(new_space)
        else:
            for i in range(fr - 1):
                #if exp_map[x-1][y+2+i] != E.EXP_BLOCK:
                row, col = x-1, y+2+i
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                exp_map[x-1][y+2+i] = E.EXP_SPACE
                new_space = Space((x-1)*Size, (y+2+i)*Size, Size, Size)
                all_sprite_list.add(new_space)
            if E.X_MIN-1 <= x-1 <= E.X_MAX+1 and E.Y_MIN-1 <= y+1+fr <= E.Y_MAX+1:
                exp_map[x-1][y+1+fr] = E.EXP_BLOCK
                new_wall = Wall((x-1)*Size, (y+1+fr)*Size, Size, Size)
                all_sprite_list.add(new_wall)


    # facing WEST
    elif face == 3:
        #RHS
        r1 = ps.decode_sensor(1, rhs_list)
        if r1 == -1:
            #calibrate_slip()
            return -1
        else:
            # R1
            if r1 == 100: ## blank space
                for i in range(r1max):
                    #if exp_map[x-1][y-2-i] != E.EXP_BLOCK:
                    row, col = x-1, y-2-i
                    if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                        break
                    exp_map[x-1][y-2-i] = E.EXP_SPACE
                    new_space = Space((x-1)*Size, (y-2-i)*Size, Size, Size)
                    all_sprite_list.add(new_space)
            else:
                for i in range(r1-1):
                    #if exp_map[x-1][y-2-i] != E.EXP_BLOCK:
                    row, col = x-1, y-2-i
                    if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                        break
                    exp_map[x-1][y-2-i] = E.EXP_SPACE
                    new_space = Space((x-1)*Size, (y-2-i)*Size, Size, Size)
                    all_sprite_list.add(new_space)
                if E.X_MIN-1 <= x-1 <= E.X_MAX+1 and E.Y_MIN-1 <= y-1-r1 <= E.Y_MAX+1:
                    exp_map[x-1][y-1-r1] = E.EXP_BLOCK
                    new_wall = Wall((x-1)*Size, (y-1-r1)*Size, Size, Size)
                    all_sprite_list.add(new_wall)

            '''
            # R2
            if r2 == 100:
                for i in range(r2max):
                    #if exp_map[x+1][y-2-i] != E.EXP_BLOCK:
                    row, col = x+1, y-2-i
                    if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                        break
                    exp_map[x+1][y-2-i] = E.EXP_SPACE
                    new_space = Space((x+1)*Size, (y-2-i)*Size, Size, Size)
                    all_sprite_list.add(new_space)
            else:
                for i in range(r2-1):
                    #if exp_map[x+1][y-2-i] != E.EXP_BLOCK:
                    row, col = x+1, y-2-i
                    if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                        break
                    exp_map[x+1][y-2-i] = E.EXP_SPACE
                    new_space = Space((x+1)*Size, (y-2-i)*Size, Size, Size)
                    all_sprite_list.add(new_space)
                if E.X_MIN-1 <= x+1 <= E.X_MAX+1 and E.Y_MIN-1 <= y-1-r2 <= E.Y_MAX+1:
                    exp_map[x+1][y-1-r2] = E.EXP_BLOCK
                    new_wall = Wall((x+1)*Size, (y-1-r2)*Size, Size, Size)
                    all_sprite_list.add(new_wall)
            '''


        #LHS
        lhs = ps.decode_sensor(2, lhs_list)
        # no calibration for lhs
        if lhs == 100:
            for i in range(lhsmax):
                #if exp_map[x][y+2+i] != E.EXP_BLOCK:
                row, col = x, y+2+i
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                exp_map[x][y+2+i] = E.EXP_SPACE
                new_space = Space((x)*Size, (y+2+i)*Size, Size, Size)
                all_sprite_list.add(new_space)
        else:
            for i in range(lhs - 1):
                #if exp_map[x][y+2+i] != E.EXP_BLOCK:
                row, col = x, y+2+i
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                exp_map[x][y+2+i] = E.EXP_SPACE
                new_space = Space((x)*Size, (y+2+i)*Size, Size, Size)
                all_sprite_list.add(new_space)
            if E.X_MIN-1 <= x <= E.X_MAX+1 and E.Y_MIN-1 <= y+1+lhs <= E.Y_MAX+1:
                exp_map[x][y+1+lhs] = E.EXP_BLOCK
                new_wall = Wall((x)*Size, (y+1+lhs)*Size, Size, Size)
                all_sprite_list.add(new_wall)

        #FRONT
        fl, fc, fr = ps.decode_sensor(0, front_list)
        # no calibration for front
        # FL
        if fl == 100:
            for i in range(lfmax):
                #if exp_map[x-2-i][y+1] != E.EXP_BLOCK:
                row, col = x-2-i, y+1
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                exp_map[x-2-i][y+1] = E.EXP_SPACE
                new_space = Space((x-2-i)*Size, (y+1)*Size, Size, Size)
                all_sprite_list.add(new_space)
        else:
            for i in range(fl - 1):
                #if exp_map[x-2-i][y+1] != E.EXP_BLOCK:
                row, col = x-2-i, y+1
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                exp_map[x-2-i][y+1] = E.EXP_SPACE
                new_space = Space((x-2-i)*Size, (y+1)*Size, Size, Size)
                all_sprite_list.add(new_space)
            if E.X_MIN-1 <= x-1-fl <= E.X_MAX+1 and E.Y_MIN-1 <= y+1 <= E.Y_MAX+1:
                exp_map[x-1-fl][y+1] = E.EXP_BLOCK
                new_wall = Wall((x-1-fl)*Size, (y+1)*Size, Size, Size)
                all_sprite_list.add(new_wall)
        # FC
        if fc == 100:
            for i in range(cfmax):
                #if exp_map[x-2-i][y] != E.EXP_BLOCK:
                row, col = x-2-i, y
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                exp_map[x-2-i][y] = E.EXP_SPACE
                new_space = Space((x-2-i)*Size, (y)*Size, Size, Size)
                all_sprite_list.add(new_space)
        else:
            for i in range(fc - 1):
                #if exp_map[x-2-i][y] != E.EXP_BLOCK:
                row, col = x-2-i, y
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                exp_map[x-2-i][y] = E.EXP_SPACE
                new_space = Space((x-2-i)*Size, (y)*Size, Size, Size)
                all_sprite_list.add(new_space)
            if E.X_MIN-1 <= x-1-fc <= E.X_MAX+1 and E.Y_MIN-1 <= y <= E.Y_MAX+1:
                exp_map[x-1-fc][y] = E.EXP_BLOCK
                new_wall = Wall((x-1-fc)*Size, (y)*Size, Size, Size)
                all_sprite_list.add(new_wall)
        # FR
        if fr == 100:
            for i in range(rfmax):
                #if exp_map[x-2-i][y-1] != E.EXP_BLOCK:
                row, col = x-2-i, y-1
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                exp_map[x-2-i][y-1] = E.EXP_SPACE
                new_space = Space((x-2-i)*Size, (y-1)*Size, Size, Size)
                all_sprite_list.add(new_space)
        else:
            for i in range(fr - 1):
                #if exp_map[x-2-i][y-1] != E.EXP_BLOCK:
                row, col = x-2-i, y-1
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                exp_map[x-2-i][y-1] = E.EXP_SPACE
                new_space = Space((x-2-i)*Size, (y-1)*Size, Size, Size)
                all_sprite_list.add(new_space)
            if E.X_MIN-1 <= x-1-fr <= E.X_MAX+1 and E.Y_MIN-1 <= y-1 <= E.Y_MAX+1:
                exp_map[x-1-fr][y-1] = E.EXP_BLOCK
                new_wall = Wall((x-1-fr)*Size, (y-1)*Size, Size, Size)
                all_sprite_list.add(new_wall)

# get coordinates of the three blocks ahead of the robot
def get_front(x, y, face):
    front_line = []
    #NORTH
    if face == 0: 
        front_line.append((x, y-2))
        front_line.append((x-1, y-2))
        front_line.append((x+1, y-2))
    #EAST
    if face == 1:
        front_line.append((x+2, y))
        front_line.append((x+2, y-1))
        front_line.append((x+2, y+1))
    #SOUTH
    if face == 2:
        front_line.append((x, y+2))
        front_line.append((x-1, y+2))
        front_line.append((x+1, y+2))
    #WEST
    if face == 3:
        front_line.append((x-2, y))
        front_line.append((x-2, y-1))
        front_line.append((x-2, y+1))

    return front_line

# return boolean for whether can move 1 step forward
def front_clear():
    global robot
    x,y = to_coord(robot.rect.x), to_coord(robot.rect.y)
    face = robot.face %4
    # front is a list of tuples(the three blocks ahead), suppose robot is 3*3
    front_line = get_front(x, y, face)
    # Check for coordinates out of bound
    for element in front_line:
        if (not X_MIN <= element[0] <= X_MAX) or (not Y_MIN <= element[1] <= Y_MAX) :
            return False
        elif exp_map[element[0]][element[1]] == EXP_BLOCK: 
            return False    
    return True

# return boolean for whether can turn right and move 1 step forward
def RHS_clear():
    global robot
    x,y = to_coord(robot.rect.x), to_coord(robot.rect.y)
    rhs = (robot.face + 1)%4
    # front is a list of tuples(the three blocks ahead), suppose robot is 3*3
    rhs_line = get_front(x, y, rhs)
    # Check for coordinates out of bound
    for element in rhs_line:
        if (not X_MIN <= element[0] <= X_MAX) or (not Y_MIN <= element[1] <= Y_MAX) :
            return False
        elif exp_map[element[0]][element[1]] == EXP_BLOCK: 
            return False

    return True

class Robot(pygame.sprite.Sprite):

    def __init__(self, x, y): 
        # Call the parent's constructor
        super().__init__()

        # Set height, width
        self.image = pygame.Surface([Size, Size])
        self.image.fill(DAY9YELLOW)
 
        # Make our top-left corner the passed-in location.
        self.rect = self.image.get_rect()
        self.rect.y = y
        self.rect.x = x
        
        self.face = 5
        self.lhs = 4
 
        # Set speed vector
        self.change_x = 0
        self.change_y = 0

        self.walls = None
        self.goals = None
        self.space = None


    def move_forward(self):
        # TODO: Send command to arduino *****************
        #global wifiin_Q, wifiout_Q
        global fpath
        wifiout_Q.append(b'w')
        feedback = False
        msg_str = ""
        while not feedback:
            if len(wifiin_Q) > 0:
                msg = wifiin_Q.popleft()
                msg_str = str(msg)
                feedback = True
                print("from wifi:" + msg_str)        

        if self.face == 0:
            self.rect.y -= Size
        elif self.face == 1:
            self.rect.x += Size
        elif self.face == 2:
            self.rect.y += Size
        elif self.face == 3:
            self.rect.x -= Size
        if not fpath:
            update_exp_map(to_coord(self.rect.x), to_coord(self.rect.y), self.face, msg_str[2:len(msg_str)-5])

    def turn_right(self):
        # TODO: Send turn command to arduino ************
        #global wifiin_Q, wifiout_Q
        global fpath
        wifiout_Q.append(b'd')
        feedback = False
        msg_str = ""
        while not feedback:
            if len(wifiin_Q) > 0:
                msg = wifiin_Q.popleft()
                msg_str = str(msg)
                feedback = True
                print("from wifi:" + msg_str)  
        self.face = (self.face + 1)%4
        if not fpath:
            update_exp_map(to_coord(self.rect.x), to_coord(self.rect.y), self.face, msg_str[2:len(msg_str)-5])
        #self.move_forward()

    def turn_left(self):
        # TODO: Send turn command to arduino *************
        #global wifiin_Q, wifiout_Q
        global fpath
        wifiout_Q.append(b'a')
        feedback = False
        msg_str = ""
        while not feedback:
            if len(wifiin_Q) > 0:
                msg = wifiin_Q.popleft()
                msg_str = str(msg)
                feedback = True
                print("from wifi:" + msg_str)  

        #print("Turning left")
        self.face = (self.face - 1)%4
        if not fpath:
            update_exp_map(to_coord(self.rect.x), to_coord(self.rect.y), self.face, msg_str[2:len(msg_str)-5])


    def move_backward(self):
        # TODO: Send command to arduino
        #global wifiin_Q, wifiout_Q
        global fpath
        wifiout_Q.append(b's')
        feedback = False
        msg_str = ""
        while not feedback:
            if len(wifiin_Q) > 0:
                msg = wifiin_Q.popleft()
                msg_str = str(msg)
                feedback = True
                print("from wifi:" + msg)  
        if self.face == 0:
            self.rect.y += Size
        elif self.face == 1:
            self.rect.x -= Size
        elif self.face == 2:
            self.rect.y -= Size
        elif self.face == 3:
            self.rect.x += Size  
        if not fpath:
            update_exp_map(to_coord(self.rect.x), to_coord(self.rect.y), self.face, msg_str[2:len(msg_str)-5])
     


class Wall(pygame.sprite.Sprite):
    """ Wall the robot can run into. """
    def __init__(self, x, y, width, height):
        """ Constructor for the wall that the robot can run into. """
        super().__init__()
        #
        self.viewed = False
        # Make a black wall, of the size specified in the parameters
        self.image = pygame.Surface([width, height])
        if self.viewed:
            self.image.fill(RED)
        else:
            self.image.fill(BLACK)
 
        # Make our top-left corner the passed-in location.
        self.rect = self.image.get_rect()
        self.rect.y = y
        self.rect.x = x
    def set_viewed(self):
        self.viewed = True

class Space(pygame.sprite.Sprite):
    """ Wall the robot can run into. """
    def __init__(self, x, y, width, height, on_path = False):
        """ Constructor for the wall that the robot can run into. """
        super().__init__()
        
        self.on_path = on_path
        # Make a transparent wall, of the size specified in the parameters
        self.image = pygame.Surface([width, height], pygame.SRCALPHA, Size)
        #self.image = self.image.convert_alpha()
        if self.on_path:
            self.image.fill(BLUE)
        else:
            self.image.fill(WHITE)
        #self.image = self.image.convert_alpha()
        
        # Make our top-left corner the passed-in location.
        self.rect = self.image.get_rect()
        self.rect.y = y
        self.rect.x = x
       
class Goal(pygame.sprite.Sprite):
    """ Wall the robot can run into. """
    def __init__(self, x, y, width, height):
        """ Constructor for the wall that the robot can run into. """
        # Call the parent's constructor
        super().__init__()
 
        # Make the goal, of the size specified in the parameters
        self.image = pygame.Surface([width, height])
        self.image.fill(GOAL)
 
        # Make our top-left corner the passed-in location.
        self.rect = self.image.get_rect()
        self.rect.y = y
        self.rect.x = x
         
        
# Right-Hand Rule wall following algorithm
def RHRwallFollowing():
    global robot
    global all_sprite_list
    all_sprite_list.remove(robot)
    face = robot.face # 0 is north, 1 is east, 2 is south, 3 is west
    if RHS_clear():
        robot.turn_right()
        robot.move_forward()
    else:
        #print("right obstacles")
        if front_clear():
            robot.move_forward()
        else:
            #print("front obstacles")
            robot.turn_left()

    print("Current Pos: " + str(to_coord(robot.rect.x)) + " "+ str(to_coord(robot.rect.y)))
    all_sprite_list.add(robot) 

# follow the path given. path: [[]] (start->end)
def follow_path(path):
    global robot
    cnt = 0
    prev_element = None
    for element in path:
        if cnt == 0:
            prev_element = element
            pass
        else:
            if prev_element[0] == element[0] -1:
                dest_dir = 1
            elif prev_element[0] == element[0] + 1:
                dest_dir = 3
            elif prev_element[1] == element[1] + 1:
                dest_dir = 0
            elif prev_element[1] == element[1] - 1:
                dest_dir = 2
            source_dir = robot.face
            rotate_ref = source_dir - dest_dir
            if rotate_ref % 2 == 0:
                robot.turn_left()
                robot.turn_left()
                robot.move_forward()
            else:
                if rotate_ref == -3 or rotate_ref == 1:
                    robot.turn_left()
                    robot.move_forward()
                elif rotate_ref == 3 or rotate_ref == -1:
                    robot.turn_right()
                    robot.move_forward()
            prev_element = element

## Follow path for simulator
def follow_path_sim(prev_element, element):
    global robot
    global all_sprite_list
    all_sprite_list.remove(robot)
    print("moving from " + str(prev_element) + " to " + str(element))
    if prev_element[0] == element[0] -1:
        dest_dir = 1
    elif prev_element[0] == element[0] + 1:
        dest_dir = 3
    elif prev_element[1] == element[1] + 1:
        dest_dir = 0
    elif prev_element[1] == element[1] - 1:
        dest_dir = 2
    source_dir = robot.face
    rotate_ref = source_dir - dest_dir
    if rotate_ref == 2 or rotate_ref == -2:
        robot.turn_left()
        robot.turn_left()
        robot.move_forward()
    elif rotate_ref == 0:
        robot.move_forward()
    else:
        if rotate_ref == -3 or rotate_ref == 1:
            robot.turn_left()
            robot.move_forward()
        elif rotate_ref == 3 or rotate_ref == -1:
            robot.turn_right()
            robot.move_forward()

    print("facing " + str(robot.face))
    all_sprite_list.add(robot)

def explore_loop():
    global robot
    global screen
    global all_sprite_list

    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill(WHITE)

    # init robot states
    robot = Robot(2*Size, 19*Size)
    robot.face = 1 # facing EAST
    robot.lhs = 0

    # init starting area
    for i in range(1, 4):
        for j in range (18,21):
            space = Space(i*Size, j*Size, Size, Size)
            all_sprite_list.add(space)

    all_sprite_list.add(robot)
    clock = pygame.time.Clock()

    # Control var
    done = False
    reach_start_cnt = 0

    # Main Loop
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
        if to_coord(robot.rect.x) == 2 and to_coord(robot.rect.y) == 19:
            reach_start_cnt += 1
            if reach_start_cnt == 3:
                print("Map generated: ")
                for i in range(17):
                    print(exp_map[i])
                fp_window()

        # main execution
        #probe_update()
        RHRwallFollowing()
        print("Face: " + str(robot.face))

        mdf1, mdf2 = get_MDF()
        print(mdf1)
        print(mdf2)
        # Update Display
        all_sprite_list.update()
        screen.fill(GREY)
        all_sprite_list.draw(screen)
        pygame.display.flip()
        clock.tick(60)
        pygame.time.wait(timer)
   
def fp_loop():
    global robot
    global screen
    global fpath

    fpath = True

    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill(WHITE)

    clock = pygame.time.Clock()

    # Control var
    done = False
    fp_counter = 0
    ## point to pass through
    #pass_thru = [14,2]

    ## Compute the fastest path
    fp = fastest_path.astar(m, n)
    obstacles = []
    for i in range(m):
        for j in range(n):
            if exp_map[i][j] != 1:
                obstacles.append([i, j])
                if exp_map[i][j] == 2:
                    for a in range(3):
                        for b in range(3):
                            row = i - 1 + a
                            col = j - 1 + b
                            if X_MIN <= row <= X_MAX and Y_MIN <= col <= Y_MAX:
                                if exp_map[row][col] == 1:
                                    obstacles.append([row, col])

    fp.set_obstacle(obstacles)
    #path1 = fp.compute_path([2, 19], pass_thru)
    #path2 = fp.compute_path(pass_thru, [14,2])
    #path = path1 + path2[1:]
    path = fp.compute_path([2,19], [14,2])
    print(path)
    for indv_path in path:
        old_space = Space(indv_path[0]* Size, indv_path[1]*Size, Size, Size)
        all_sprite_list.remove(old_space)
        new_space = Space(indv_path[0]* Size, indv_path[1]*Size, Size, Size, True)
        all_sprite_list.add(new_space)

    # Main Loop
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        # main execution
        ## Follow FP in simulator
        if fp_counter == len(path):
            break
        else:
            element = path[fp_counter]
            if fp_counter == 0:
                prev_element = element
            else:
                follow_path_sim(prev_element, element)
                prev_element = element
            fp_counter += 1

        print("Face: " + str(robot.face))

        # Update Display
        all_sprite_list.update()
        screen.fill(GREY)
        all_sprite_list.draw(screen)
        pygame.display.flip()
        clock.tick(60)
        pygame.time.wait(timer)

    finish_window()
'''
def run_wifi():
    asyncio.get_event_loop().run_until_complete(connectionSlave())
'''
if __name__ == '__main__': 
    threading.Thread(target = wifi_read).start()
    threading.Thread(target = wifi_write).start()
    
    threading.Thread(target = wifi_read).start()
    threading.Thread(target = wifi_write).start()
    intro_window()
