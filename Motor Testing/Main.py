#Tail Pitch: ID = 7
#Tail Yaw: ID = 8
#Right wing: ID = 10
#Left wing: ID = 11

import os

from dynamixel_sdk import *                    # Uses Dynamixel SDK library
from Constants import *
from MotorControl import *


def homeTail():
    st = time.time()
    while not(moveTail(TAIL_PITCH_STRAIGHT, TAIL_YAW_STRAIGHT)):
        print("Homing Tail")
        time.sleep(0.01)
        if(time.time() - st > GLOBAL_TIMEOUT):
            print("Timed Out")
            break
    print("Homed Tail")
        
def homeWings():
    st = time.time()
    while not(moveWings(L_WING_CLOSED, R_WING_CLOSED)):
        print("Homing Wings")
        time.sleep(0.01)
        if(time.time() - st > GLOBAL_TIMEOUT):
            print("Timed Out")
            break
    print("Homed Wings")
def homeLegs():
    st = time.time()
    while not(moveLegsFromHome(0)):
        print("Homing Legs")
        time.sleep(0.01)
        if(time.time() - st > GLOBAL_TIMEOUT):
            print("Timed Out")
            break
    print("Homed Legs")
def stowLegs():
    st = time.time()
    while not(moveLegsFromHome(2048)):
        time.sleep(0.01)
        if(time.time() - st > GLOBAL_TIMEOUT):
            print("Timed Out")
            break
    print("Stowed Legs")
        

def selfRight():
    print("Self Righting")
    stowLegs()
    st = time.time()
    while not(moveTail(TAIL_PITCH_STRAIGHT, TAIL_YAW_STRAIGHT) and moveWings(L_WING_CLOSED, R_WING_CLOSED)):
        time.sleep(0.01)
        if(time.time() - st > GLOBAL_TIMEOUT):
            print("Timed Out")
            break
    st = time.time()
    while not(moveWings(L_WING_OPEN, R_WING_OPEN) and moveTail(TAIL_PITCH_DOWN, TAIL_YAW_STRAIGHT)):
        time.sleep(0.01)
        if(time.time() - st > GLOBAL_TIMEOUT):
            print("Timed Out")
            break
    st = time.time()
    while not(moveTail(TAIL_PITCH_DOWN, TAIL_YAW_LEFT)):
        time.sleep(0.01)
        if(time.time() - st > GLOBAL_TIMEOUT):
            print("Timed Out")
            break
    time.sleep(0.5)
    st = time.time()
    while not(moveTail(TAIL_PITCH_STRAIGHT, TAIL_YAW_STRAIGHT)):
        time.sleep(0.01)
        if(time.time() - st > GLOBAL_TIMEOUT):
            print("Timed Out")
            break
    homeWings()

def walk(rotations):
    print("Walking ", rotations, " Rotations")
    pos = rotations * 4096
    curr = getPos(LM_LEG_ID)
    moveLegsOffset(curr + pos)

def walkLoop(rotations):
    print("Walking ", rotations, " Rotations Uninterrupted")
    pos = rotations * 4096
    curr = getPos(LM_LEG_ID)
    while not(moveLegsOffset(curr + pos)):
        time.sleep(0.01)

def pitchUp():
    print("Pitching up")
    while not (moveTail(TAIL_PITCH_UP, TAIL_YAW_STRAIGHT)):
        time.sleep(0.01)
    time.sleep(0.5)
    # st = time.time()
    # while not (moveTail(TAIL_PITCH_UP_SMALL, TAIL_YAW_STRAIGHT)):
    #     time.sleep(0.01)
    #     if(time.time() - st > GLOBAL_TIMEOUT):
    #         print("Timed Out")
    #         break
    # time.sleep(1.5)
    homeTail()

def shakeTail(wags):
    print("Shaking Tail ", wags, " times")
    for i in range (wags):
        while not(moveTail(TAIL_PITCH_STRAIGHT, TAIL_YAW_LEFT_SMALL)):
            time.sleep(0.01)
        while not(moveTail(TAIL_PITCH_STRAIGHT, TAIL_YAW_RIGHT_SMALL)):
            time.sleep(0.01)
    homeTail()

def rollOver():
    print("Rolling Over")
    stowLegs()
    st = time.time()
    while not(moveTail(TAIL_PITCH_DOWN, TAIL_YAW_STRAIGHT)):
        time.sleep(0.01)
        if(time.time() - st > GLOBAL_TIMEOUT):
            print("Timed Out")
            break
    time.sleep(0.5)
    st = time.time()
    while not(moveTail(TAIL_PITCH_DOWN, TAIL_YAW_RIGHT)):
        time.sleep(0.01)
        if(time.time() - st > GLOBAL_TIMEOUT):
            print("Timed Out")
            break
    homeTail()

enableAll()

# selfRight()

time.sleep(3)
homeWings()
homeTail()
# homeLegs()

# offsetLegsFromHome()

# rollOver()
# selfRight()
pitchUp()
# shakeTail(10)

# walkLoop(5)
# walk(5)
# pitchUp()
# shakeTail(5)
# walkLoop(-4)
# walk(-5)

# stowLegs()


disableAll()

# Close port
portHandler.closePort()

print("Finished!")
