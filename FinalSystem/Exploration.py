'''
CZ3004 MDP 18/19 S1 Group 5
Algorithm > FinalSystem > Exploration.py
By: Fang Meiyi

Module for Right Wall Hugging during exploration.

'''

import AhBot
import Explored

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


# Check if the front of the robot has no obstacles
# return boolean for whether can move 1 step forward
def front_clear():
    x,y = AhBot.x, AhBot.y
    face = AhBot.face %4
    # front is a list of tuples(the three blocks ahead), suppose robot is 3*3
    front_line = get_front(x, y, face)
    # Check for coordinates out of bound
    for element in front_line:
        if (not Explored.X_MIN <= element[0] <= Explored.X_MAX) or (not Explored.Y_MIN <= element[1] <= Explored.Y_MAX) :
            return False
        elif Explored.exp_map[element[0]][element[1]] == Explored.EXP_BLOCK: 
            return False    
    return True


# Check if the right-hand side of the robot has no obstacles
# return boolean for whether can turn right and move 1 step forward
def RHS_clear():
    x,y = AhBot.x, AhBot.y
    rhs = (AhBot.face + 1)%4
    # front is a list of tuples(the three blocks ahead), suppose robot is 3*3
    rhs_line = get_front(x, y, rhs)
    # Check for coordinates out of bound
    for element in rhs_line:
        if (not Explored.X_MIN <= element[0] <= Explored.X_MAX) or (not Explored.Y_MIN <= element[1] <= Explored.Y_MAX) :
            return False
        elif Explored.exp_map[element[0]][element[1]] == Explored.EXP_BLOCK: 
            return False
    return True


# Right wall following algorithm
def RHRwallFollowing():
    steps = []
    if RHS_clear():
        steps.append("d")
        steps.append("w")
    else:
        if front_clear():
            steps.append("w")
        else:
            steps.append("a")
            
    return steps


# Compute the next movement and return a list of action(s)
def next_step():  
	return RHRwallFollowing()

