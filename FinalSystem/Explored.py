'''
CZ3004 MDP 18/19 S1 Group 5
Algorithm > FinalSystem > Explored.py
By: Fang Meiyi

Module for explored arena during exploration phase.
Map generated during exploration, modified only in process_sensor.py. 
Read only in other suvroutines.

'''


## On the exploration map: 1- space, 2-block, 0-unexplored
EXP_BLOCK = 2
EXP_UNKNOWN = 0
EXP_SPACE = 1

# valid arena coordinates, inclusive
X_MIN = 1
X_MAX = 15
Y_MIN = 1
Y_MAX = 20

# Number of rows and columns
EXP_MAP_ROW = 17
EXP_MAP_COL = 22

# Define start zone and goal zone
START_ZONE = [[1,19], [2,19], [3,19], [1,18], [2,18], [3, 18], [1,20], [2, 20], [3,20]]
GOAL_ZONE = [[13,2], [14,2], [15,2], [13,1], [14,1], [15,1], [13,3], [14,3], [15,3]]

# CLEARED is a set containing grids that can never be obstacles
CLEARED = set([(1,19), (2,19), (3,19), (1,18), (2,18), (3, 18), (1,20), (2, 20), (3,20), (13,2), (14,2), (15,2), (13,1), (14,1), (15,1), (13,3), (14,3), (15,3)])


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
        ]  # 21      ---------> X


# put the grids that have been occupied by the robot into the set CLEARED
def set_cleared(x,y):
      global CLEARED
      for i in range(3):
            for j in range(3):
                  CLEARED.add((x+i-1, y+j-1))
