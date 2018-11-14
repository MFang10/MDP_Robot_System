'''
CZ3004 MDP 18/19 S1 Group 5
Algorithm > FinalSystem > process_sensor.py
By: Fang Meiyi

Module for processing raw sensor readings from Arduino.
See project wiki for detailed explanation.

'''

import Explored as E

## max reliable grid distances
lfmax = 2
cfmax = 2
rfmax = 2
r1max = 2
r2max = 3
lhsmax = 4


## Decoding the raw readings for each sensor
## 100 indicates that the reading is beyond the max value that can be decoded.
def lf_to_grid(raw_lf):
    if (abs(raw_lf) <= 13): 
        return 1
    elif (abs(raw_lf) <= 24):
        return 2
    else:
        return 100 

def cf_to_grid(raw_cf):
    if (abs(raw_cf) <= 13):
        return 1
    elif (abs(raw_cf) <= 24):
        return 2
    else:
        return 100

def rf_to_grid(raw_rf):
    if (abs(raw_rf) <= 13):
        return 1
    elif (abs(raw_rf) <= 24):
        return 2
    else:
        return 100

def r1_to_grid(raw_r1):
    if (abs(raw_r1) <= 16):
        return 1
    elif (abs(raw_r1) <= 27):
        return 2
    elif (abs(raw_r1) <= 37):
        return 3
    else:
        return 100

## Not used
def r2_to_grid(raw_r2):
    if (6 <=abs(raw_r2) <= 14):
        return 1
    elif (abs(raw_r2) <= 24):
        return 2
    elif (abs(raw_r2) < 34):
        return 3
    else:
        return 100

def lhs_to_grid(raw_lhs):
    if (abs(raw_lhs) <= 14):
        return 1
    elif (abs(raw_lhs) <= 25):
        return 2
    elif (abs(raw_lhs) <= 34):
        return 3
    elif (abs(raw_lhs) <= 48):
        return 4
    #elif (abs(raw_lhs) < 57):
        #return 5
    #elif (abs(raw_lhs) < 65):
        #return 6
    else:
        return 100


## Convert raw values to number of grids
def decode_sensor(side, reading_list):
    if side == 0:
        return lf_to_grid(reading_list[0]), cf_to_grid(reading_list[1]), rf_to_grid(reading_list[2])
    #RIGHT
    elif side == 1:
        return r1_to_grid(reading_list[0])
    #LEFT
    elif side == 2:
        return lhs_to_grid(reading_list[0])



# takes in a list of all the raw sensor values: [lf,cf,rf,r1,r2,lhs]
## Based on robot face direction and sensor placement, update the explored map
def update_exp_map(x, y, face, raw_sensor):
    #raw_sensor = list(map(int, raw_sensor_list.split(',')))
    if raw_sensor is not None:
        front_list = raw_sensor[:3]
        rhs_list = raw_sensor[3:4]
        lhs_list = [raw_sensor[-1]]
    
    for i in range(3):
        for j in range(3):
            E.exp_map[x-1+i][y-1+j] = E.EXP_SPACE

    # facing NORTH
    if face == 0:
        #RHS
        r1 = decode_sensor(1, rhs_list)
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
                    E.exp_map[x+2+i][y-1] = E.EXP_SPACE
            else:
                for i in range(r1-1):
                    #if exp_map[x+2+i][y-1] != E.EXP_BLOCK:
                    row, col = x+2+i, y-1
                    if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                        break
                    E.exp_map[x+2+i][y-1] = E.EXP_SPACE
                if E.X_MIN-1 <= x+1+r1 <= E.X_MAX+1 and E.Y_MIN-1 <= y-1 <= E.Y_MAX+1: 
                    if (x+1+r1, y-1) not in E.CLEARED:
                        E.exp_map[x+1+r1][y-1] = E.EXP_BLOCK
            

        #LHS
        lhs = decode_sensor(2, lhs_list)
        # no calibration for lhs
        if lhs == 100:
            for i in range(lhsmax):
                #if exp_map[x-2-i][y] != E.EXP_BLOCK:
                row, col = x-2-i, y
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                E.exp_map[x-2-i][y] = E.EXP_SPACE
        else:
            for i in range(lhs - 1):
                #if exp_map[x-2-i][y] != E.EXP_BLOCK:
                row, col = x-2-i, y
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                E.exp_map[x-2-i][y] = E.EXP_SPACE
            if E.X_MIN-1 <= x-1-lhs <= E.X_MAX+1 and E.Y_MIN-1 <= y <= E.Y_MAX+1:
                if (x-1-lhs, y) not in E.CLEARED:
                    E.exp_map[x-1-lhs][y] = E.EXP_BLOCK

        #FRONT
        fl, fc, fr = decode_sensor(0, front_list)
        # no calibration for front
        # FL
        if fl == 100:
            for i in range(lfmax):
                #if exp_map[x-1][y-2-i] != E.EXP_BLOCK:
                row, col = x-1, y-2-i
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                E.exp_map[x-1][y-2-i] = E.EXP_SPACE
        else:
            for i in range(fl - 1):
                row, col = x-1, y-2-i
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                #if exp_map[x-1][y-2-i] != E.EXP_BLOCK:
                E.exp_map[x-1][y-2-i] = E.EXP_SPACE
            if E.X_MIN-1 <= x-1 <= E.X_MAX+1 and E.Y_MIN-1 <= y-1-fl <= E.Y_MAX+1:
                if (x-1,y-1-fl) not in E.CLEARED:
                    E.exp_map[x-1][y-1-fl] = E.EXP_BLOCK

        # FC
        if fc == 100:
            for i in range(cfmax):
                #if exp_map[x][y-2-i] != E.EXP_BLOCK:
                row, col = x, y-2-i
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                E.exp_map[x][y-2-i] = E.EXP_SPACE
        else:
            for i in range(fc - 1):
                #if exp_map[x][y-2-i] != E.EXP_BLOCK:
                row, col = x, y-2-i
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                E.exp_map[x][y-2-i] = E.EXP_SPACE
            if E.X_MIN-1 <= x <= E.X_MAX+1 and E.Y_MIN-1 <= y-1-fc <= E.Y_MAX+1: 
                if (x,y-1-fc) not in E.CLEARED:
                    E.exp_map[x][y-1-fc] = E.EXP_BLOCK

        # FR
        if fr == 100:
            for i in range(rfmax):
                #if exp_map[x+1][y-2-i] != E.EXP_BLOCK:
                row, col = x+1, y-2-i
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                E.exp_map[x+1][y-2-i] = E.EXP_SPACE
        else:
            for i in range(fr - 1):
                #if exp_map[x+1][y-2-i] != E.EXP_BLOCK:
                row, col = x+1, y-2-i
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                E.exp_map[x+1][y-2-i] = E.EXP_SPACE
            if E.X_MIN-1 <= x+1 <= E.X_MAX+1 and E.Y_MIN-1 <= y-1-fr <= E.Y_MAX+1:
                if (x+1,y-1-fr) not in E.CLEARED:
                    E.exp_map[x+1][y-1-fr] = E.EXP_BLOCK


    # facing EAST
    elif face == 1:
        #RHS
        r1 = decode_sensor(1, rhs_list)
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
                    E.exp_map[x+1][y+2+i] = E.EXP_SPACE

            else:
                for i in range(r1-1):
                    #if exp_map[x+1][y+2+i] != E.EXP_BLOCK:
                    row, col = x+1, y+2+i
                    if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                        break
                    E.exp_map[x+1][y+2+i] = E.EXP_SPACE

                if E.X_MIN-1 <= x+1 <= E.X_MAX+1 and E.Y_MIN-1 <= y+1+r1 <= E.Y_MAX+1:
                    if (x+1,y+1+r1) not in E.CLEARED:
                        E.exp_map[x+1][y+1+r1] = E.EXP_BLOCK


        #LHS
        lhs = decode_sensor(2, lhs_list)
        # no calibration for lhs
        if lhs == 100:
            for i in range(lhsmax):
                #if exp_map[x][y-2-i] != E.EXP_BLOCK:
                row, col = x, y-2-i
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                E.exp_map[x][y-2-i] = E.EXP_SPACE
        else:
            for i in range(lhs - 1):
                #if exp_map[x][y-2-i] != E.EXP_BLOCK:
                row, col = x, y-2-i
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                E.exp_map[x][y-2-i] = E.EXP_SPACE
            if E.X_MIN-1 <= x+1 <= E.X_MAX+1 and E.Y_MIN-1 <= y-1-lhs <= E.Y_MAX+1:
                if (x+1,y-1-lhs) not in E.CLEARED:
                    E.exp_map[x+1][y-1-lhs] = E.EXP_BLOCK

        #FRONT
        fl, fc, fr = decode_sensor(0, front_list)
        # no calibration for front
        # FL
        if fl == 100:
            for i in range(lfmax):
                #if exp_map[x+2+i][y-1] != E.EXP_BLOCK:
                row, col = x+2+i, y-1
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                E.exp_map[x+2+i][y-1] = E.EXP_SPACE

        else:
            for i in range(fl - 1):
                #if exp_map[x+2+i][y-1] != E.EXP_BLOCK:
                row, col = x+2+i, y-1
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                E.exp_map[x+2+i][y-1] = E.EXP_SPACE

            if E.X_MIN-1 <= x+1+fl <= E.X_MAX+1 and E.Y_MIN-1 <= y-1 <= E.Y_MAX+1:
                if (x+1+fl,y-1) not in E.CLEARED:
                    E.exp_map[x+1+fl][y-1] = E.EXP_BLOCK

        # FC
        if fc == 100:
            for i in range(cfmax):
                #if exp_map[x+2+i][y] != E.EXP_BLOCK:
                row, col = x+2+i, y
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                E.exp_map[x+2+i][y] = E.EXP_SPACE

        else:
            for i in range(fc - 1):
                #if exp_map[x+2+i][y] != E.EXP_BLOCK:
                row, col = x+2+i, y
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                E.exp_map[x+2+i][y] = E.EXP_SPACE

            if E.X_MIN-1 <= x+1+fc <= E.X_MAX+1 and E.Y_MIN-1 <= y <= E.Y_MAX+1:
                if (x+1+fc,y) not in E.CLEARED:
                    E.exp_map[x+1+fc][y] = E.EXP_BLOCK

        # FR
        if fr == 100:
            for i in range(rfmax):
                #if exp_map[x+2+i][y+1] != E.EXP_BLOCK:
                row, col = x+2+i, y+1
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                E.exp_map[x+2+i][y+1] = E.EXP_SPACE

        else:
            for i in range(fr - 1):
                #if exp_map[x+2+i][y+1] != E.EXP_BLOCK:
                row, col = x+2+i, y+1
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                E.exp_map[x+2+i][y+1] = E.EXP_SPACE

            if E.X_MIN-1 <= x+1+fr <= E.X_MAX+1 and E.Y_MIN-1 <= y+1 <= E.Y_MAX+1:
                if (x+1+fr,y+1) not in E.CLEARED:
                    E.exp_map[x+1+fr][y+1] = E.EXP_BLOCK


    # facing SOUTH
    elif face == 2:
        #RHS
        r1 = decode_sensor(1, rhs_list)
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
                    E.exp_map[x-2-i][y+1] = E.EXP_SPACE
            else:
                for i in range(r1-1):
                    #if exp_map[x-2-i][y+1] != E.EXP_BLOCK:
                    row, col = x-2-i, y+1
                    if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                        break
                    E.exp_map[x-2-i][y+1] = E.EXP_SPACE
                if E.X_MIN-1 <= x-1-r1 <= E.X_MAX+1 and E.Y_MIN-1 <= y+1 <= E.Y_MAX+1:
                    if (x-1-r1,y+1) not in E.CLEARED:
                        E.exp_map[x-1-r1][y+1] = E.EXP_BLOCK


        #LHS
        lhs = decode_sensor(2, lhs_list)
        # no calibration for lhs
        if lhs == 100:
            for i in range(lhsmax):
                #if exp_map[x+2+i][y] != E.EXP_BLOCK:
                row, col = x+2+i, y
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                E.exp_map[x+2+i][y] = E.EXP_SPACE

        else:
            for i in range(lhs - 1):
                #if exp_map[x+2+i][y] != E.EXP_BLOCK:
                row, col = x+2+i, y
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                E.exp_map[x+2+i][y] = E.EXP_SPACE

            if E.X_MIN-1 <= x+1+lhs <= E.X_MAX+1 and E.Y_MIN-1 <= y <= E.Y_MAX+1:
                if (x+1+lhs,y) not in E.CLEARED:
                    E.exp_map[x+1+lhs][y] = E.EXP_BLOCK


        #FRONT
        fl, fc, fr = decode_sensor(0, front_list)
        # no calibration for front
        # FL
        if fl == 100:
            for i in range(lfmax):
                #if exp_map[x+1][y+2+i] != E.EXP_BLOCK:
                row, col = x+1, y+2+i
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                E.exp_map[x+1][y+2+i] = E.EXP_SPACE

        else:
            for i in range(fl - 1):
                #if exp_map[x+1][y+2+i] != E.EXP_BLOCK:
                row, col = x+1, y+2+i
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                E.exp_map[x+1][y+2+i] = E.EXP_SPACE
            if E.X_MIN-1 <= x+1 <= E.X_MAX+1 and E.Y_MIN-1 <= y+1+fl <= E.Y_MAX+1:
                if (x+1,y+1+fl) not in E.CLEARED:
                    E.exp_map[x+1][y+1+fl] = E.EXP_BLOCK

        # FC
        if fc == 100:
            for i in range(cfmax):
                #if exp_map[x][y+2+i] != E.EXP_BLOCK:
                row, col = x, y+2+i
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                E.exp_map[x][y+2+i] = E.EXP_SPACE
        else:
            for i in range(fc - 1):
                #if exp_map[x][y+2+i] != E.EXP_BLOCK:
                row, col = x, y+2+i
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                E.exp_map[x][y+2+i] = E.EXP_SPACE

            if E.X_MIN-1 <= x <= E.X_MAX+1 and E.Y_MIN-1 <= y+1+fc <= E.Y_MAX+1:
                if (x,y+1+fc) not in E.CLEARED:
                    E.exp_map[x][y+1+fc] = E.EXP_BLOCK

        # FR
        if fr == 100:
            for i in range(rfmax):
                #if exp_map[x-1][y+2+i] != E.EXP_BLOCK:
                row, col = x-1, y+2+i
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                E.exp_map[x-1][y+2+i] = E.EXP_SPACE

        else:
            for i in range(fr - 1):
                #if exp_map[x-1][y+2+i] != E.EXP_BLOCK:
                row, col = x-1, y+2+i
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                E.exp_map[x-1][y+2+i] = E.EXP_SPACE

            if E.X_MIN-1 <= x-1 <= E.X_MAX+1 and E.Y_MIN-1 <= y+1+fr <= E.Y_MAX+1:
                if (x-1,y+1+fr) not in E.CLEARED:
                    E.exp_map[x-1][y+1+fr] = E.EXP_BLOCK


    # facing WEST
    elif face == 3:
        #RHS
        r1 = decode_sensor(1, rhs_list)
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
                    E.exp_map[x-1][y-2-i] = E.EXP_SPACE

            else:
                for i in range(r1-1):
                    #if exp_map[x-1][y-2-i] != E.EXP_BLOCK:
                    row, col = x-1, y-2-i
                    if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                        break
                    E.exp_map[x-1][y-2-i] = E.EXP_SPACE
                if E.X_MIN-1 <= x-1 <= E.X_MAX+1 and E.Y_MIN-1 <= y-1-r1 <= E.Y_MAX+1:
                    if (x-1,y-1-r1) not in E.CLEARED:
                        E.exp_map[x-1][y-1-r1] = E.EXP_BLOCK


        #LHS
        lhs = decode_sensor(2, lhs_list)
        # no calibration for lhs
        if lhs == 100:
            for i in range(lhsmax):
                #if exp_map[x][y+2+i] != E.EXP_BLOCK:
                row, col = x, y+2+i
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                E.exp_map[x][y+2+i] = E.EXP_SPACE

        else:
            for i in range(lhs - 1):
                #if exp_map[x][y+2+i] != E.EXP_BLOCK:
                row, col = x, y+2+i
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                E.exp_map[x][y+2+i] = E.EXP_SPACE
            if E.X_MIN-1 <= x <= E.X_MAX+1 and E.Y_MIN-1 <= y+1+lhs <= E.Y_MAX+1:
                if (x,y+1+lhs) not in E.CLEARED:
                    E.exp_map[x][y+1+lhs] = E.EXP_BLOCK

        #FRONT
        fl, fc, fr = decode_sensor(0, front_list)
        # no calibration for front
        # FL
        if fl == 100:
            for i in range(lfmax):
                #if exp_map[x-2-i][y+1] != E.EXP_BLOCK:
                row, col = x-2-i, y+1
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                E.exp_map[x-2-i][y+1] = E.EXP_SPACE

        else:
            for i in range(fl - 1):
                #if exp_map[x-2-i][y+1] != E.EXP_BLOCK:
                row, col = x-2-i, y+1
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                E.exp_map[x-2-i][y+1] = E.EXP_SPACE
            if E.X_MIN-1 <= x-1-fl <= E.X_MAX+1 and E.Y_MIN-1 <= y+1 <= E.Y_MAX+1:
                if (x-1-fl,y+1) not in E.CLEARED:
                    E.exp_map[x-1-fl][y+1] = E.EXP_BLOCK

        # FC
        if fc == 100:
            for i in range(cfmax):
                #if exp_map[x-2-i][y] != E.EXP_BLOCK:
                row, col = x-2-i, y
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                E.exp_map[x-2-i][y] = E.EXP_SPACE
        else:
            for i in range(fc - 1):
                #if exp_map[x-2-i][y] != E.EXP_BLOCK:
                row, col = x-2-i, y
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                E.exp_map[x-2-i][y] = E.EXP_SPACE
            if E.X_MIN-1 <= x-1-fc <= E.X_MAX+1 and E.Y_MIN-1 <= y <= E.Y_MAX+1:
                if (x-1-fc,y) not in E.CLEARED:
                    E.exp_map[x-1-fc][y] = E.EXP_BLOCK

        # FR
        if fr == 100:
            for i in range(rfmax):
                #if exp_map[x-2-i][y-1] != E.EXP_BLOCK:
                row, col = x-2-i, y-1
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                E.exp_map[x-2-i][y-1] = E.EXP_SPACE
        else:
            for i in range(fr - 1):
                #if exp_map[x-2-i][y-1] != E.EXP_BLOCK:
                row, col = x-2-i, y-1
                if E.X_MIN > row or row > E.X_MAX or E.Y_MIN > col or E.Y_MAX < col:
                    break
                E.exp_map[x-2-i][y-1] = E.EXP_SPACE

            if E.X_MIN-1 <= x-1-fr <= E.X_MAX+1 and E.Y_MIN-1 <= y-1 <= E.Y_MAX+1:
                if (x-1-fr,y-1) not in E.CLEARED:
                    E.exp_map[x-1-fr][y-1] = E.EXP_BLOCK



