import sys, pygame
from pygame.locals import *
import fastest_path
import time

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

## short: 10-30 long: 20-60
SHORT_SENSOR_RANGE = 2
LONG_SENSOR_RANGE = 5

# valid arena coordinates, inclusive
X_MIN = 1
X_MAX = 15
Y_MIN = 1
Y_MAX = 20

m = 17
n = 22  ## col

goal_x = 16*Size #576
goal_y = 1 * Size

# List to hold all the sprites
all_sprite_list = pygame.sprite.Group()
clock = pygame.time.Clock()

robot = None

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

def to_coord(pixel):
    return int(pixel/Size)

# Probing the surroundings
def probe_update():
    global robot
    x,y = to_coord(robot.rect.x), to_coord(robot.rect.y)
    face = robot.face%4

    for i in range(3):
        for j in range(3):
            exp_map[x-1+i][y-1+j] = EXP_SPACE
            new_space = Space((x-1+i)*Size, (y-1+j)*Size, Size, Size)
            all_sprite_list.add(new_space)

    # facing NORTH
    if face == 0:
        #RHS
        for j in range(-1, 2, 2):
            for i in range(SHORT_SENSOR_RANGE):
                if maze[x+2+i][y+j] == 1:
                    exp_map[x+2+i][y+j] = EXP_BLOCK
                    new_wall = Wall((x+2+i)*Size, (y+j)*Size, Size, Size)
                    robot.walls.add(new_wall)
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
                        robot.walls.add(new_wall)
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
                    robot.walls.add(new_wall)
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
                    robot.walls.add(new_wall)
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
                        robot.walls.add(new_wall)
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
                    robot.walls.add(new_wall)
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
                    robot.walls.add(new_wall)
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
                        robot.walls.add(new_wall)
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
                    robot.walls.add(new_wall)
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
                    robot.walls.add(new_wall)
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
                        robot.walls.add(new_wall)
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
                    robot.walls.add(new_wall)
                    all_sprite_list.add(new_wall)
                    break 
                elif maze[x-2-i][y+j] == 0:
                    exp_map[x-2-i][y+j] = EXP_SPACE
                    new_space = Space((x-2-i)*Size, (y+j)*Size, Size, Size)
                    all_sprite_list.add(new_space)


def get_MDF():

    global exp_map
    p1 = "11"
    p2 = ""
    mdf1 = ""
    mdf2 = ""
    cnt1 = 2
    cnt2 = 0
    for i in range(n-2, 0, -1):
        for j in range(1, m-1):
            if exp_map[j][i] == 0:
                p1 += "0"
            else:
                p1 += "1"
            cnt1 += 1
            if cnt1 % 4 == 0:
                mdf1 += str(hex(int(p1,2)))[2:]
                p1 = ""
    mdf1 += str(hex(int(p1+"11",2)))[2:]


    for i in range(n-2, 0, -1):
        for j in range(1, m-1):
            #print("p2" + p2)
            if cnt2 % 4 == 0 and cnt2 != 0 and p2 != "":
                mdf2 += str(hex(int(p2,2)))[2:]
                p2 = ""
            if exp_map[j][i] == 2:
                p2 += "1"
                cnt2 += 1
            elif exp_map[j][i] == 1:
                p2 += "0"
                cnt2 += 1
            
    if len(p2) > 0:
        L = len(p2)
        print("len: " + str(L))
        for i in range(4-L):
            p2 += "0"
        mdf2 += str(hex(int(p2,2)))[2:]
    '''
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
    '''

    return mdf1, mdf2


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
        if self.face == 0:
            self.rect.y -= Size
        elif self.face == 1:
            self.rect.x += Size
        elif self.face == 2:
            self.rect.y += Size
        elif self.face == 3:
            self.rect.x -= Size
        probe_update()

    def turn_right(self):
        # TODO: Send turn command to arduino ************
        self.face = (self.face + 1)%4
        #self.move_forward()
        probe_update()

    def turn_left(self):
        # TODO: Send turn command to arduino *************
        #print("Turning left")
        self.face = (self.face - 1)%4
        probe_update()

    def move_backward(self):
        # TODO: Send command to arduino
        if self.face == 0:
            self.rect.y += Size
        elif self.face == 1:
            self.rect.x -= Size
        elif self.face == 2:
            self.rect.y -= Size
        elif self.face == 3:
            self.rect.x += Size  
        probe_update()     


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
    mdf1, mdf2 = get_MDF()
    print(mdf1)
    print(mdf2)

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

def main():
    global robot
    pygame.init()
    size = width, height = 17*Size, 22*Size
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Arena')

    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill(WHITE)
    
    # Make the walls. (x_pos, y_pos, width, height)
    wall_list = pygame.sprite.Group()
    # Make the goal. (x_pos, y_pos, width, height)
    goal_list = pygame.sprite.Group()
    # Make the space. (x_pos, y_pos, width, height)
    space_list = pygame.sprite.Group()

    # init robot states
    robot = Robot(2*Size, 19*Size)
    robot.face = 1 # facing EAST
    robot.lhs = 0
    robot.walls = wall_list
    robot.goals = goal_list
    robot.space = space_list

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
    exploring = True
    fastest = False
    fp_counter = 0
    #path = []

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
                path = fp.compute_path([2, 19], [14, 2])
                print(path)
                #print(fp.consec_step([2, 19], [14, 2]))
                for indv_path in path:
                    old_space = Space(indv_path[0]* Size, indv_path[1]*Size, Size, Size)
                    all_sprite_list.remove(old_space)
                    new_space = Space(indv_path[0]* Size, indv_path[1]*Size, Size, Size, True)
                    all_sprite_list.add(new_space)
                ## Change mode
                exploring = False
                fastest = True

        # main execution
        if exploring:
            #probe_update()
            RHRwallFollowing()
        elif fastest:
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

    pygame.quit()
    
if __name__ == '__main__': 
    main()