import Explored as E

lfmax = 2
cfmax = 2
rfmax = 2
r1max = 3
r2max = 3
lhsmax = 4

def lf_to_grid(raw_lf):
	if (abs(raw_lf) <= 13): 
		return 1
	elif (abs(raw_lf) <= 24):
	 return 2
	#elif (abs(raw_lf) <= 34):
	 #return 3
	#elif (abs(raw_lf) < 48):
	 #return 4
	else:
	 return 100

def cf_to_grid(raw_cf):
	if (abs(raw_cf) <= 13):
		return 1
	elif (abs(raw_cf) <= 24):
		return 2
	#elif (abs(raw_cf) <= 35):
		#return 3
	#elif (abs(raw_cf) < 46):
		#return 4
	else:
		return 100

def rf_to_grid(raw_rf):
	if (abs(raw_rf) <= 13):
		return 1
	elif (abs(raw_rf) <= 24):
		return 2
	#elif (abs(raw_rf) <= 34):
		#return 3
	#elif (abs(raw_rf) < 48):
		#return 4
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
	elif (abs(raw_lhs) <= 45):
		return 4
	#elif (abs(raw_lhs) <= 57):
		#return 5
	#elif (abs(raw_lhs) < 65):
		#return 6
	else:
		return 100

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
## For now, calibration base on rhs sensors only
## TODO: set max distance as constants
def update_exp_map(x, y, face, raw_sensor_list):

    if raw_sensor_list is not None:
        front_list = raw_sensor_list[:3]
        rhs_list = raw_sensor_list[3:4]
        lhs_list = raw_sensor_list[-1]

    # facing NORTH
    if face == 0:
        #RHS
        r1,r2 = decode_sensor(1, rhs_list)
        if r1 == -1:
            #calibrate_slip()
            return -1
        else:
        	# R1
            if r1 == 100: ## blank space
                for i in range(r1max):
                    E.exp_map[x+2+i][y-1] = E.EXP_SPACE
            else:
                for i in range(r1-1):
                    E.exp_map[x+2+i][y-1] = E.EXP_SPACE
                E.exp_map[x+1+r1][y-1] = E.EXP_BLOCK
            # R2
            if r2 == 100:
                for i in range(r2max):
                    E.exp_map[x+2+i][y+1] = E.EXP_SPACE
            else:
                for i in range(r2-1):
                    E.exp_map[x+2+i][y+1] = E.EXP_SPACE
                E.exp_map[x+1+r2][y+1] = E.EXP_BLOCK

        #LHS
        lhs = decode_sensor(2, lhs_list)
        # no calibration for lhs
        if lhs == 100:
            for i in range(lhsmax):
                E.exp_map[x-2-i][y] = E.EXP_SPACE
        else:
            for i in range(lhs - 1):
                E.exp_map[x-2-i][y] = E.EXP_SPACE
            E.exp_map[x-1-lhs][y] = E.EXP_BLOCK

        #FRONT
        fl, fc, fr = decode(0, front_list)
        # no calibration for front
        # FL
        if fl == 100:
        	for i in range(lfmax):
        		E.exp_map[x-1][y-2-i] = E.EXP_SPACE
        else:
        	for i in range(fl - 1):
        		E.exp_map[x-1][y-2-i] = E.EXP_SPACE
        	E.exp_map[x-1][y-1-fl] = E.EXP_BLOCK
        # FC
        if fc == 100:
        	for i in range(cfmax):
        		E.exp_map[x][y-2-i] = E.EXP_SPACE
        else:
        	for i in range(fc - 1):
        		E.exp_map[x][y-2-i] = E.EXP_SPACE
        	E.exp_map[x][y-1-fc] = E.EXP_BLOCK
        # FR
        if fr == 100:
        	for i in range(rfmax):
        		E.exp_map[x+1][y-2-i] = E.EXP_SPACE
        else:
        	for i in range(fr - 1):
        		E.exp_map[x+1][y-2-i] = E.EXP_SPACE
        	E.exp_map[x+1][y-1-fr] = E.EXP_BLOCK


    # facing EAST
    elif face == 1:
        #RHS
        r1,r2 = decode_sensor(1, rhs_list)
        if r1 == -1:
            #calibrate_slip()
            return -1
        else:
        	# R1
            if r1 == 100: ## blank space
                for i in range(r1max):
                    E.exp_map[x+1][y+2+i] = E.EXP_SPACE
            else:
                for i in range(r1-1):
                    E.exp_map[x+1][y+2+i] = E.EXP_SPACE
                E.exp_map[x+1][y+1+r1] = E.EXP_BLOCK
            # R2
            if r2 == 100:
                for i in range(r2max):
                    E.exp_map[x-1][y+2+i] = E.EXP_SPACE
            else:
                for i in range(r2-1):
                    E.exp_map[x-1][y+2+i] = E.EXP_SPACE
                E.exp_map[x-1][y+1+r2] = E.EXP_BLOCK

        #LHS
        lhs = decode_sensor(2, lhs_list)
        # no calibration for lhs
        if lhs == 100:
            for i in range(lhsmax):
                E.exp_map[x][y-2-i] = E.EXP_SPACE
        else:
            for i in range(lhs - 1):
                E.exp_map[x][y-2-i] = E.EXP_SPACE
            E.exp_map[x][y-1-lhs] = E.EXP_BLOCK

        #FRONT
        fl, fc, fr = decode(0, front_list)
        # no calibration for front
        # FL
        if fl == 100:
        	for i in range(lfmax):
        		E.exp_map[x+2+i][y-1] = E.EXP_SPACE
        else:
        	for i in range(fl - 1):
        		E.exp_map[x+2+i][y-1] = E.EXP_SPACE
        	E.exp_map[x+1+fl][y-1] = E.EXP_BLOCK
        # FC
        if fc == 100:
        	for i in range(cfmax):
        		E.exp_map[x+2+i][y] = E.EXP_SPACE
        else:
        	for i in range(fc - 1):
        		E.exp_map[x+2+i][y] = E.EXP_SPACE
        	E.exp_map[x+1+fc][y] = E.EXP_BLOCK
        # FR
        if fr == 100:
        	for i in range(rfmax):
        		E.exp_map[x+2+i][y+1] = E.EXP_SPACE
        else:
        	for i in range(fr - 1):
        		E.exp_map[x+2+i][y+1] = E.EXP_SPACE
        	E.exp_map[x+1+fr][y+1] = E.EXP_BLOCK


    # facing SOUTH
    elif face == 2:
        #RHS
        r1,r2 = decode_sensor(1, rhs_list)
        if r1 == -1:
            #calibrate_slip()
            return -1
        else:
        	# R1
            if r1 == 100: ## blank space
                for i in range(r1max):
                    E.exp_map[x-2-i][y+1] = E.EXP_SPACE
            else:
                for i in range(r1-1):
                    E.exp_map[x-2-i][y+1] = E.EXP_SPACE
                E.exp_map[x-1-r1][y+1] = E.EXP_BLOCK
            # R2
            if r2 == 100:
                for i in range(r2max):
                    E.exp_map[x-2-i][y-1] = E.EXP_SPACE
            else:
                for i in range(r2-1):
                    E.exp_map[x-2-i][y-1] = E.EXP_SPACE
                E.exp_map[x-1-r2][y-1] = E.EXP_BLOCK

        #LHS
        lhs = decode_sensor(2, lhs_list)
        # no calibration for lhs
        if lhs == 100:
            for i in range(lhsmax):
                E.exp_map[x+2+i][y] = E.EXP_SPACE
        else:
            for i in range(lhs - 1):
                E.exp_map[x+2+i][y] = E.EXP_SPACE
            E.exp_map[x+1+lhs][y] = E.EXP_BLOCK

        #FRONT
        fl, fc, fr = decode(0, front_list)
        # no calibration for front
        # FL
        if fl == 100:
        	for i in range(lfmax):
        		E.exp_map[x+1][y+2+i] = E.EXP_SPACE
        else:
        	for i in range(fl - 1):
        		E.exp_map[x+1][y+2+i] = E.EXP_SPACE
        	E.exp_map[x+1][y+1+fl] = E.EXP_BLOCK
        # FC
        if fc == 100:
        	for i in range(cfmax):
        		E.exp_map[x][y+2+i] = E.EXP_SPACE
        else:
        	for i in range(fc - 1):
        		E.exp_map[x][y+2+i] = E.EXP_SPACE
        	E.exp_map[x][y+1+fc] = E.EXP_BLOCK
        # FR
        if fr == 100:
        	for i in range(rfmax):
        		E.exp_map[x-1][y+2+i] = E.EXP_SPACE
        else:
        	for i in range(fr - 1):
        		E.exp_map[x-1][y+2+i] = E.EXP_SPACE
        	E.exp_map[x-1][y+1+fr] = E.EXP_BLOCK


    # facing WEST
    elif face == 3:
        #RHS
        r1,r2 = decode_sensor(1, rhs_list)
        if r1 == -1:
            #calibrate_slip()
            return -1
        else:
        	# R1
            if r1 == 100: ## blank space
                for i in range(r1max):
                    E.exp_map[x-1][y-2-i] = E.EXP_SPACE
            else:
                for i in range(r1-1):
                    E.exp_map[x-1][y-2-i] = E.EXP_SPACE
                E.exp_map[x-1][y-1-r1] = E.EXP_BLOCK
            # R2
            if r2 == 100:
                for i in range(r2max):
                    E.exp_map[x+1][y-2-i] = E.EXP_SPACE
            else:
                for i in range(r2-1):
                    E.exp_map[x+1][y-2-i] = E.EXP_SPACE
                E.exp_map[x+1][y-1-r2] = E.EXP_BLOCK

        #LHS
        lhs = decode_sensor(2, lhs_list)
        # no calibration for lhs
        if lhs == 100:
            for i in range(lhsmax):
                E.exp_map[x][y+2+i] = E.EXP_SPACE
        else:
            for i in range(lhs - 1):
                E.exp_map[x][y+2+i] = E.EXP_SPACE
            E.exp_map[x][y+1+lhs] = E.EXP_BLOCK

        #FRONT
        fl, fc, fr = decode(0, front_list)
        # no calibration for front
        # FL
        if fl == 100:
        	for i in range(lfmax):
        		E.exp_map[x-2-i][y+1] = E.EXP_SPACE
        else:
        	for i in range(fl - 1):
        		E.exp_map[x-2-i][y+1] = E.EXP_SPACE
        	E.exp_map[x-1-fl][y+1] = E.EXP_BLOCK
        # FC
        if fc == 100:
        	for i in range(cfmax):
        		E.exp_map[x-2-i][y] = E.EXP_SPACE
        else:
        	for i in range(fc - 1):
        		E.exp_map[x-2-i][y] = E.EXP_SPACE
        	E.exp_map[x-1-fc][y] = E.EXP_BLOCK
        # FR
        if fr == 100:
        	for i in range(rfmax):
        		E.exp_map[x-2-i][y-1] = E.EXP_SPACE
        else:
        	for i in range(fr - 1):
        		E.exp_map[x-2-i][y-1] = E.EXP_SPACE
        	E.exp_map[x-1-fr][y-1] = E.EXP_BLOCK


