#Tail Pitch: ID = 7
#Tail Yaw: ID = 8
#Right wing: ID = 10
#Left wing: ID = 11

import os

from dynamixel_sdk import *
from Constants import *
from MotorControl import *

def timeOut(secs, system):
    st = time.time()
    if(system == 'LEGS'):
        while not (legsAtPos()):
            time.sleep(0.01)
            if(time.time() - st > secs):
                print("Legs Timed Out")
                break
    elif(system == 'WINGS'):
        while not (wingsAtPos()):
            time.sleep(0.01)
            if(time.time() - st > secs):
                print("Wings Timed Out")
                break
    elif(system == 'TAIL'):
        while not (tailAtPos()):
            time.sleep(0.01)
            if(time.time() - st > secs):
                print("Tail Timed Out")
                break
    else:
        print("ERROR: Wrong system for timeOut")

def homeTail():
    moveTail(TAIL_PITCH_STRAIGHT, TAIL_YAW_STRAIGHT)
    timeOut(GLOBAL_TIMEOUT, 'TAIL')
    print("Homed Tail")
        
def homeWings():
    moveWings(L_WING_CLOSED, R_WING_CLOSED)
    timeOut(GLOBAL_TIMEOUT, 'WINGS')
    print("Homed Wings")

# def homeLegs():
#     moveLegsFromHome(0)
#     timeOut(GLOBAL_TIMEOUT, 'LEGS')
#     print("Homed Legs")

def homeLegs():
    switchControlModeAllLegs(XL_POSITION_CONTROL)
    moveLegsFromHome(0)
    timeOut(GLOBAL_TIMEOUT, 'LEGS')
    switchControlModeAllLegs(XL_EXT_POSITION_CONTROL)
    
def stowLegs():
    switchControlModeAllLegs(XL_POSITION_CONTROL)
    moveLegsFromHome(2048)
    timeOut(GLOBAL_TIMEOUT, 'LEGS')
    switchControlModeAllLegs(XL_EXT_POSITION_CONTROL)
    print("Stowed Legs")

def offsetLegsRelative():
    switchControlModeAllLegs(XL_POSITION_CONTROL)

    # moveMotorPos(RF_LEG_ID, 4096 - LEG_OFFSET)
    # moveMotorPos(RM_LEG_ID, 0 + LEG_OFFSET)
    # moveMotorPos(RB_LEG_ID, 4096 - LEG_OFFSET)
    # moveMotorPos(LF_LEG_ID, 0 + LEG_OFFSET)
    # moveMotorPos(LM_LEG_ID, 4096 - LEG_OFFSET)
    # moveMotorPos(LB_LEG_ID, 0 + LEG_OFFSET)

    moveMotorPos(RF_LEG_ID, 0)
    moveMotorPos(RM_LEG_ID, 4096 - LEG_OFFSET)
    moveMotorPos(RB_LEG_ID, 0)
    moveMotorPos(LF_LEG_ID, 0 + LEG_OFFSET)
    moveMotorPos(LM_LEG_ID, 0)
    moveMotorPos(LB_LEG_ID, 0 + LEG_OFFSET)

    timeOut(GLOBAL_TIMEOUT, 'LEGS')

    switchControlModeAllLegs(XL_EXT_POSITION_CONTROL)

        

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

def walkLoopSmart(rotations):
    print("Walking ", rotations, " Rotations Uninterrupted")
    pos = rotations * 4096
    curr = getPos(LM_LEG_ID)

    setAllLegProfileVelocity(RUN_PROFILE_VELOCITY)
    moveLegsOffset(curr + pos)
    while not(legsAtPos()):
        if(((abs(getPos(RM_LEG_ID)) % 4096) < SLOW_GAIT_RANGE_LOWER) or ((abs(getPos(RM_LEG_ID)) % 4096) > SLOW_GAIT_RANGE_UPPER)):
            print("walking")
            setOffsetLegProfileVelocity(WALK_PROFILE_VELOCITY)
        else:
            setOffsetLegProfileVelocity(RUN_PROFILE_VELOCITY)

        if(((abs(getPos(LM_LEG_ID)) % 4096) < SLOW_GAIT_RANGE_LOWER) or ((abs(getPos(LM_LEG_ID)) % 4096) > SLOW_GAIT_RANGE_UPPER)):
            print("walking")
            setNonOffsetLegProfileVelocity(WALK_PROFILE_VELOCITY)
        else:
            setNonOffsetLegProfileVelocity(RUN_PROFILE_VELOCITY)

        # print("LF goal: ", getPosGoal(LF_LEG_ID), "LF curr: ", getPos(LF_LEG_ID), "LF PV: ", getProfileVelocity(LF_LEG_ID))
        # print("RF goal: ", getPosGoal(RF_LEG_ID), "RF curr: ", getPos(RF_LEG_ID), "RF PV: ", getProfileVelocity(RF_LEG_ID))

    # setAllLegProfileVelocity(RUN_PROFILE_VELOCITY)

def walkLoopSmartVel(secs):
    print("Walking ", secs, " Seconds Uninterrupted")
    setAllLegProfileVelocity(RUN_PROFILE_VELOCITY)
    switchControlModeAllLegs(XL_VELOCITY_CONTROL)
    setAllLegsVel(STOP_VELOCITY)

    st = time.time()

    while (time.time() - st < secs):
        if(((abs(getPos(RM_LEG_ID)) % 4096) < SLOW_GAIT_RANGE_LOWER) or ((abs(getPos(RM_LEG_ID)) % 4096) > SLOW_GAIT_RANGE_UPPER)):
            setOffsetLegsVel(WALK_VELOCITY)
        else:
            setOffsetLegsVel(RUN_VELOCITY)

        if(((abs(getPos(LM_LEG_ID)) % 4096) < SLOW_GAIT_RANGE_LOWER) or ((abs(getPos(LM_LEG_ID)) % 4096) > SLOW_GAIT_RANGE_UPPER)):
            setNonOffsetLegsVel(WALK_VELOCITY)
        else:
            setNonOffsetLegsVel(RUN_VELOCITY)


    switchControlModeAllLegs(XL_EXT_POSITION_CONTROL)


def walkLoop(rotations, vel):
    print("Walking ", rotations, " Rotations Uninterrupted")
    pos = rotations * 4096
    curr = getPos(LM_LEG_ID)

    setAllLegProfileVelocity(vel)
    moveLegsOffset(curr + pos)
    while not(legsAtPos()):
        time.sleep(0.01)

def walkLoopShaking(rotations, vel):
    print("Walking ", rotations, " Rotations While Shaking")
    pos = rotations * 4096
    curr = getPos(LM_LEG_ID)

    setAllLegProfileVelocity(vel)
    moveLegsOffset(curr + pos)
    wingIndex = 0
    tailIndex = 0
    moveWings(L_WING_CLOSED, R_WING_CLOSED)
    st = time.time()
    while not(legsAtPos()):
        # in ground: 2600, beams 22cm apart
        
        if((tailAtPos() and tailIndex == 0) or time.time() - st > 0.25):
            moveTail(TAIL_PITCH_IN_GROUND, TAIL_YAW_RIGHT_SMALL)
            tailIndex = 1
            st = time.time()

        elif((tailAtPos() and tailIndex == 1) or time.time() - st > 0.25):
            moveTail(TAIL_PITCH_IN_GROUND, TAIL_YAW_LEFT_SMALL)
            tailIndex = 0
            st = time.time()
            
    homeTail()
    homeWings()

def walkLoopShaking2(rotations, vel):
    print("Walking ", rotations, " Rotations While Shaking")
    pos = rotations * 4096
    curr = getPos(LM_LEG_ID)

    setAllLegProfileVelocity(vel)
    moveLegsOffset(curr + pos)
    wingIndex = 0
    tailIndex = 0
    moveWings(L_WING_CLOSED, R_WING_CLOSED)
    st = time.time()
    while not(legsAtPos()):
        if((tailAtPos() and tailIndex == 0) or time.time() - st > 0.5):
            moveTail(2600, TAIL_YAW_STRAIGHT)
            tailIndex = 1
            st = time.time()
        elif((tailAtPos() and tailIndex == 1) or time.time() - st > 0.5):
            moveTail(2500, 1800)
            tailIndex = 0
            st = time.time()
    homeTail()
    homeWings()


def pitchUp():
    print("Pitching up")
    moveTail(TAIL_PITCH_UP, TAIL_YAW_STRAIGHT)
    timeOut(GLOBAL_TIMEOUT, 'TAIL')
    time.sleep(0.25)
    moveTail(TAIL_PITCH_GROUND, TAIL_YAW_STRAIGHT)
    timeOut(GLOBAL_TIMEOUT, 'TAIL')

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


def pain(secs):
    print("Walking ", secs, " Seconds Uninterrupted")
    st = time.time()
    switchControlModeAllLegs(XL_VELOCITY_CONTROL)
    moveMotorVel(RF_LEG_ID, STOP_VELOCITY)

    while not(time.time() - st > secs):
        if(abs(getPos(RF_LEG_ID)%4096) < SLOW_GAIT_RANGE_LOWER or abs(getPos(RF_LEG_ID)%4096) > SLOW_GAIT_RANGE_UPPER):
            moveMotorVel(RF_LEG_ID, WALK_VELOCITY)
        else:
            moveMotorVel(RF_LEG_ID, RUN_VELOCITY)
        print("RF goal: ", getPosGoal(RF_LEG_ID), "RF curr: ", getPos(RF_LEG_ID), "RF PV: ", getProfileVelocity(RF_LEG_ID))
    
    switchControlModeAllLegs(XL_EXT_POSITION_CONTROL)

enableAll()

# time.sleep(3)
homeWings()
homeTail()
# homeLegs()
offsetLegsRelative()

# pain(6)
# walkLoopSmart(10)
# walkLoopSmartVel(10)
# st = time.time()
# switchControlModeAllLegs(XL_VELOCITY_CONTROL)
# while not(time.time() - st > 10 ):
#     if(time.time() - st < 5 or time.time() - st > 8):
#         moveMotorVel(RF_LEG_ID, RUN_VELOCITY)
#     else:
#         moveMotorVel(RF_LEG_ID, WALK_VELOCITY)
#     print("Time: ", time.time() - st, " Vel goal: ", getVelGoal(RF_LEG_ID), " Curr Vel: ", getVel(RF_LEG_ID), "Curr Pos: ", getPos(RF_LEG_ID)%4096)


# disableAll()
# while 1:
#     if(abs(getPos(RF_LEG_ID)%4096) < SLOW_GAIT_RANGE_LOWER or abs(getPos(RF_LEG_ID)%4096) > SLOW_GAIT_RANGE_UPPER):
#         print("walking")
#     else:
#         print("running")


# walkLoop(10,RUN_PROFILE_VELOCITY)

walkLoopShaking(15, RUN_PROFILE_VELOCITY)

# moveTail(TAIL_PITCH_IN_GROUND, TAIL_YAW_LEFT_SMALL)
# walkLoop(10,RUN_PROFILE_VELOCITY)


# print("Goal: ", getPosGoal(RF_LEG_ID), " Curr: ", getPos(RF_LEG_ID), "Profile Velocity: ", getProfileVelocity(RF_LEG_ID))
# print("Goal: ", getPosGoal(RM_LEG_ID), " Curr: ", getPos(RM_LEG_ID), "Profile Velocity: ", getProfileVelocity(RM_LEG_ID))
# print("Goal: ", getPosGoal(RB_LEG_ID), " Curr: ", getPos(RB_LEG_ID), "Profile Velocity: ", getProfileVelocity(RB_LEG_ID))
# print("Goal: ", getPosGoal(LF_LEG_ID), " Curr: ", getPos(LF_LEG_ID), "Profile Velocity: ", getProfileVelocity(LF_LEG_ID))
# print("Goal: ", getPosGoal(LM_LEG_ID), " Curr: ", getPos(LM_LEG_ID), "Profile Velocity: ", getProfileVelocity(LM_LEG_ID))
# print("Goal: ", getPosGoal(LB_LEG_ID), " Curr: ", getPos(LB_LEG_ID), "Profile Velocity: ", getProfileVelocity(LB_LEG_ID))

# setAllLegProfileVelocity(RUN_PROFILE_VELOCITY)



# walkLoop(3)


disableAll()

# Close port
portHandler.closePort()

print("Finished!")
