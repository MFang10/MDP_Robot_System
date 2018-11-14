'''
CZ3004 MDP 18/19 S1 Group 5
Algorithm > FinalSystem > AhBot.py
By: Fang Meiyi

Module for storing robot status and properties.

'''


# public robot status, updated during execution
x = 2
y = 19
face = 1


# Update robot status for each movement. Coordinate updates depend on face direction.
# Step by step movements
def move_forward():
    global face
    global x,y
    if face == 0:
        y -= 1
    elif face == 1:
        x += 1
    elif face == 2:
        y += 1
    elif face == 3:
        x -= 1


# Consecutive movements
def move_consec_forward(steps):
    global face
    global x,y
    # Move base on face direction
    print("steps:" + str(steps))
    if face == 0:
        y -= steps
    elif face == 1:
        x += steps
    elif face == 2:
        y += steps
    elif face == 3:
        x -= steps          
 

def turn_right():
    global face
    face = (face+1)%4


def turn_left():
    global face
    face = (face-1)%4
    

def move_backward():
    global face
    global x,y
    if face == 0:
        y += 1
    elif face == 1:
        x -= 1
    elif face == 2:
        y -= 1
    elif face == 3:
        x += 1


def get_state():
    global x,y,face
    return x, y, face
