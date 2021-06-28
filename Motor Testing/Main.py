#Tail Pitch: ID = 7
#Tail Yaw: ID = 8
#Right wing: ID = 10
#Left wing: ID = 11

import os

from dynamixel_sdk import *                    # Uses Dynamixel SDK library
from Constants import *
from MotorControl import *

def selfRight():
    print("Self Righting")
    while not(moveTail(TAIL_PITCH_STRAIGHT, TAIL_YAW_STRAIGHT) and moveWings(L_WING_CLOSED, R_WING_CLOSED)):
        time.sleep(0.01)
    while not(moveWings(L_WING_OPEN, R_WING_OPEN) and moveTail(TAIL_PITCH_DOWN, TAIL_YAW_STRAIGHT)):
        time.sleep(0.01)
    while not(moveTail(TAIL_PITCH_DOWN, TAIL_YAW_LEFT)):
        time.sleep(0.01)
    time.sleep(0.5)
    while not(moveTail(TAIL_PITCH_STRAIGHT, TAIL_YAW_STRAIGHT)):
        time.sleep(0.01)
    while not(moveWings(L_WING_CLOSED, R_WING_CLOSED)):
        time.sleep(0.01)

enableAll()

selfRight()

# moveTail(TAIL_YAW_STRAIGHT, TAIL_PITCH_STRAIGHT)
# moveWings(L_WING_CLOSED, R_WING_CLOSED)

# while not(atPosition(TAIL_YAW_STRAIGHT, getPos(TAIL_YAW_ID)) and atPosition(TAIL_PITCH_STRAIGHT, getPos(TAIL_PITCH_ID)) and atPosition(L_WING_CLOSED, getPos(L_WING_ID)) and atPosition(R_WING_CLOSED, getPos(R_WING_ID))):
#     time.sleep(0.01)
#     print("curr position tail pitch", getPos(TAIL_PITCH_ID))

disableAll()

# Close port
portHandler.closePort()

print("Finished!")
