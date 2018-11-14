'''
CZ3004 MDP 18/19 S1 Group 5
Algorithm > FinalSystem > main.py
By: Fang Meiyi

Module for coordination of all other modules. Run as main.

'''

from rfcomm_server import *
from arduino_interface import *
from collections import deque
import time
import threading
import detection
import Exploration
import AhBot
import process_sensor as ps
import fastest_path
import Explored


START_PT = [2,19]
END_PT = [14,2]
detection_on = True

## condition for initial probing
init_probing = False

## Run detection as a background thread
if detection_on:
    detection_mod = detection.detection_thread() # run the detection thread in the background
    detection_mod.daemon = True
    detection_mod.start()

## Set up bluetooth thread
bt = rfcomm_server()
bt.connect_bt()
btinQ = deque() # ard write to btQ, bt read from btQ
btoutQ = deque()
bt_interval = 0

## Set up serial communication thread
ard = arduino_interface()
ard.connect()
ardinQ = deque()
ardoutQ = deque()
ard_interval = 0

fp_movements = ""


## deprecated method for converting movement command to bytes
def decode_dir(bt_msg):
    if bt_msg == "w":
        return b'w'
    elif bt_msg == "a":
        return b'a'
    elif bt_msg == "s":
        return b's'
    elif bt_msg == "d":
        return b'd'
    elif bt_msg == "v":
        return b'v'
    elif len(bt_msg)>1:
        return bt_msg.encode('utf-8') 
    return b'na'


## method for converting movement command to bytes
def decode_dir_consec(bt_msg):
    if bt_msg == "w":
        return b'W_'
    elif bt_msg == "a":
        return b'A_'
    elif bt_msg == "s":
        return b'S_'
    elif bt_msg == "d":
        return b'D_'
    elif bt_msg == "v":
        return b'V_'
    elif len(bt_msg)>1:
        return bt_msg.encode('utf-8') 
    return b'na'


## Read from tablet
def bt_read():
    curByte = None
    while 1:
        curByte = bt.read()
        if len(curByte) > 0:
            #print("Received: " + str(curByte) + " at " + str(time.time()))
            btinQ.append(str(curByte)) 
        time.sleep(bt_interval)
    return curByte


## Write to tablet via Bluetooth
## msg is a string
def bt_write():
    while 1:
        time.sleep(bt_interval)
        if len(btoutQ) > 0:
            msg = btoutQ.popleft()
            bt.write(msg)
            #print("Write to bt " + msg + " at " + str(time.time()))

         
## Read from arduino through serial communication
def ard_read():
    cur_msg = None
    while 1:
        cur_msg = ard.read()
        if len(cur_msg) > 0:
            ardinQ.append(str(cur_msg))
            #print("Received: " + str(cur_msg) + " at " + str(time.time()))
        time.sleep(ard_interval)
    return str(cur_msg)


## Write to arduino through serial communication
def ard_write():
    while 1:
        #time.sleep(ard_interval)
        if len(ardoutQ) > 0:
            msg = ardoutQ.popleft()
            command = decode_dir_consec(msg)
            #print("Sent to arduino " + msg + " at " + str(time.time()))
            if command != b'na':
                ard.write(command)
            else:
                pass


## For exploration only
## Base on the movements computed, send the command to Arduino
## and update the robot status
## then poll the sensor readings from Arduino
## while polling, get the current detection result
def exp_move(action):
    final_count = 0 
    if detection_on:
        current_cnt = detection_mod.get_res()

    #send command to ard
    ardoutQ.append(action)
    # update ahbot
    if action == "w":
        AhBot.move_forward()
    elif action == "a":
        AhBot.turn_left()
    elif action == "d":
        AhBot.turn_right()
    elif action == "s":
        AhBot.move_backward()

    # wait for ard sensor feedback
    if detection_on:
        probed = False
        while not probed:
            if len(ardinQ)>0:
                sensors = ardinQ.popleft()
                probed = True
        
        next_cnt = detection_mod.get_res()
        final_count = next_cnt - current_cnt
        #print("Detection: " + str(final_count))

    else:
        probed = False
        while not probed:
            if len(ardinQ)>0:
                sensors = ardinQ.popleft()
                #print("Sensor readings " + sensors)
                probed = True
    #convert sensor reading string to list of int : raw_sensor
    raw_sensor = list(map(int, sensors.split(',')))
    # Probe the surrounding and update exp_map
    ps.update_exp_map(AhBot.x, AhBot.y, AhBot.face, raw_sensor)
    return final_count


## For fastest path only
## Base on the movements computed, send the command to Arduino
## and update the robot status
def fp_move(action):
    # update ahbot
    if action == "w":
        AhBot.move_forward()
        #send command to ard
        ardoutQ.append(action)
    elif action == "a":
        AhBot.turn_left()
        #send command to ard
        ardoutQ.append(action)
    elif action == "d":
        AhBot.turn_right()
        #send command to ard
        ardoutQ.append(action)
    elif action == "s":
        AhBot.move_backward()
        #send command to ard
        ardoutQ.append(action)
    elif len(action)>1:
        step = int(action[1:])
        AhBot.move_consec_forward(step)
        #send command to ard
        ardoutQ.append(action + "_")
    # wait for ard sensor feedback: for syncing only
    probed = False
    while not probed:
        if len(ardinQ)>0:
            msg = ardinQ.popleft()
            print("Sensor readings " + msg)
            probed = True


## deprecated method for computing movement commands
## based on the fasted path coordinates computed
def follow_path(prev_element, element):
    if prev_element[0] == element[0] -1:
        dest_dir = 1
    elif prev_element[0] == element[0] + 1:
        dest_dir = 3
    elif prev_element[1] == element[1] + 1:
        dest_dir = 0
    elif prev_element[1] == element[1] - 1:
        dest_dir = 2
    source_dir = AhBot.face
    rotate_ref = source_dir - dest_dir
    if rotate_ref == 2 or rotate_ref == -2:
        fp_move("a")
        fp_move("a")
        fp_move("w")
    elif rotate_ref == 0:
        fp_move("w")
    else:
        if rotate_ref == -3 or rotate_ref == 1:
            fp_move("a")
            fp_move("w")
        elif rotate_ref == 3 or rotate_ref == -1:
            fp_move("d")
            fp_move("w")


## method for computing the movement commands
## based on the consective steps computed 
def follow_consec_path(element):
    global fp_movements
    dest_dir = element[0]
    dist = element[1]*10
    source_dir = AhBot.face
    rotate_ref = source_dir - dest_dir
    if rotate_ref == 2 or rotate_ref == -2:
        fp_movements += "A_"
        AhBot.turn_left()
        fp_movements += "A_"
        AhBot.turn_left()
        fp_movements += "I" + str(dist) + "_"
        AhBot.move_consec_forward(dist/10)
    elif rotate_ref == 0:
        fp_movements += "I" + str(dist) + "_"
        AhBot.move_consec_forward(dist/10)
    else:
        if rotate_ref == -3 or rotate_ref == 1:
            fp_movements += "A_"
            AhBot.turn_left()
            fp_movements += "I" + str(dist) + "_"
            AhBot.move_consec_forward(dist/10)
        elif rotate_ref == 3 or rotate_ref == -1:
            fp_movements += "D_"
            AhBot.turn_right()
            fp_movements += "I" + str(dist) + "_"
            AhBot.move_consec_forward(dist/10)


## Compute the MDF strings           
def get_MDF():
    p1 = "11"
    p2 = ""
    p3 = ""
    mdf1 = ""
    mdf2 = ""
    mdf3 = ""
    cnt1 = 2
    cnt2 = 1
    cnt3 = 0
    for i in range(Explored.EXP_MAP_COL-2, 0, -1):
        for j in range(1, Explored.EXP_MAP_ROW-1):
            if Explored.exp_map[j][i] == 0:
                p1 += "0"
            else:
                p1 += "1"
            cnt1 += 1
            if cnt1 % 4 == 0:
                mdf1 += str(hex(int(p1,2)))[2:]
                p1 = ""
    mdf1 += str(hex(int(p1+"11",2)))[2:]
            
    for i in range(Explored.EXP_MAP_COL-2, 0, -1):
        for j in range(1, Explored.EXP_MAP_ROW-1):
            if Explored.exp_map[j][i] == 2:
                p2 += "1"
            else:
                p2 += "0"
            if cnt2 % 4 == 0:
                mdf2 += str(hex(int(p2,2)))[2:]
                p2 = ""
            cnt2 += 1

    for i in range(Explored.EXP_MAP_COL-2, 0, -1):
        for j in range(1, Explored.EXP_MAP_ROW-1):
            #print("p2" + p2)
            if cnt3 % 4 == 0 and cnt3 != 0 and p3 != "":
                mdf3 += str(hex(int(p3,2)))[2:]
                p3 = ""
            if Explored.exp_map[j][i] == 2:
                p3 += "1"
                cnt3 += 1
            elif Explored.exp_map[j][i] == 1:
                p3 += "0"
                cnt3 += 1
            
    if len(p3) > 0:
        L = len(p3)
        for i in range(4-L):
            p3 += "0"
        mdf3 += str(hex(int(p3,2)))[2:]

    return mdf1, mdf2, mdf3


## For Exploration
## Update the detection, map and robot status through bluetooth
def update_bt(arrow_count, prev_state):
    mdf1, mdf2, mdf3 = get_MDF()

    if arrow_count > 0: ## if arrow detected
        bot_state = prev_state + "," + "T"
    else:
        bot_state = str(AhBot.x - 1) + "_" + str(20 - AhBot.y) + "_" + str(AhBot.face%4) + "," + "F"
    
    msg_for_bt = mdf1 + "," + mdf2 + "," + mdf3 + "," + bot_state

    #send bt command
    btoutQ.append(msg_for_bt)
    ack = False
    while not ack:
        if len(btinQ)>0:
            msg = btinQ.popleft()
            if msg == "ack":
                ack = True


## For Fastest Path
## Update robot status through bluetooth
def update_bt_fp():
    bot_state = str(AhBot.x - 1) + "_" + str(20 - AhBot.y) + "_" + str(AhBot.face%4)
    msg_for_bt = bot_state
    #send bt command
    btoutQ.append(msg_for_bt)


## Exploration loop
def explore_loop():
    global init_probing
    reached_goal = False
    finished = False

    if init_probing:
        ardoutQ.append("a")
        AhBot.turn_left()
        init_probed = False
        while not init_probed:
            if len(ardinQ)>0:
                sensors = ardinQ.popleft()
                print("init ignored" + str(sensors))
                init_probed = True
        detect = exp_move("d")

    # main loop
    while not finished:
        arrow = 0 # detection result
        Explored.set_cleared(AhBot.x, AhBot.y) # add the grids occuppied by the robot to the set CLEARED
        steps = Exploration.next_step() # compute the next step base on current explored map

        prev_bot_state = str(AhBot.x - 1) + "_" + str(20 - AhBot.y) + "_" + str(AhBot.face%4)
        for action in steps:
            arrow = exp_move(action)
            if AhBot.x == END_PT[0] and AhBot.y == END_PT[1]:
                reached_goal = True 
            if reached_goal and AhBot.x == START_PT[0] and AhBot.y == START_PT[1]: # back to the starting point
                finished = True
                break
        # send exp_map and ahbot state to bluetooth
        update_bt(arrow, prev_bot_state)


## Fastest path loop
def fp_loop(pass_thru):
    global fp_movements
    fp_counter = 0

    ## Compute the fastest path
    fp = fastest_path.astar(Explored.EXP_MAP_ROW, Explored.EXP_MAP_COL)
    fp.set_obstacle()
    path1 = fp.consec_step(START_PT, pass_thru) 
    path2 = fp.consec_step(pass_thru, END_PT)
    path = path1 + path2
    print(path)

    for single_step in path:
        follow_consec_path(single_step)
        update_bt_fp()
    print(str(fp_movements))
    ardoutQ.append(fp_movements)


## deprecated method for detection
def get_detect_result():
    #directions = {-1:"NA", 0:"UP", 1:"DOWN", 2:"LEFT", 3:"RIGHT"}
    #current_res = detection_mod.get_res()
    current_cnt = detection_mod.get_res()
    time.sleep(0.5)
    #next_res = detection_mod.get_res()
    next_cnt = detection_mod.get_res
    #final_res = [a-b for a, b in zip(next_res, current_res)]
    final_count = next_cnt - current_cnt
    if final_count > 3:
        return 1
    return 0


## main loop for the entire system
def main():
    start = False
    while not start:
        if len(btinQ)>0:
            msg = btinQ.popleft()
            if msg == "Start": # command for starting exploration
                start = True
            elif msg == "cl":
                ardoutQ.append("v") # calibration before exploration
     
    explore_loop()
    bt.write("End exp") # signal the tablet

    # turn to north after exploration. To save time for fastest path
    if AhBot.face == 1:
        ardoutQ.append("A_")
        AhBot.turn_left()
    elif AhBot.face == 2:
        ardoutQ.append("D_")
        ardoutQ.append("D_")
        AhBot.turn_right()
        AhBot.turn_right()
    elif AhBot.face == 3:
        ardoutQ.append("D_")
        AhBot.turn_right()
   
    # wait for fp command and way point from bluetooth
    way_pt = False
    info = None
    while not way_pt:
        if len(btinQ)>0:
            info = btinQ.popleft()
            if info[:2] == "FP" and info != "FP -1,-1" and info != "FP Start":
                way_pt = True
            elif info == "cl":
                ardoutQ.append("v")

    pass_thru = list(map(int, info[3:].split(',')))
    pass_thru = [pass_thru[0] + 1, 20 - pass_thru[1]]
    #print(pass_thru)
    fp_start = False
    while not fp_start:
        if len(btinQ)>0:
            info = btinQ.popleft()
            if info == "FP Start":
                fp_start = True
    fp_loop(pass_thru)
    # signal completion to android
    bt.write("Finish")


if __name__=='__main__':
    threading.Thread(target = bt_read).start()
    threading.Thread(target = bt_write).start()
    threading.Thread(target = ard_read).start()
    threading.Thread(target = ard_write).start()
    main()

