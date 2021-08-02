from dynamixel_sdk import *
from MFRv2_Constants import *
from MFRv2_MotorControl import *

import keyboard

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

def homeLegs():
    switchControlModeAllLegs(XL_POSITION_CONTROL)
    moveLegsFromHome(0)
    timeOut(GLOBAL_TIMEOUT, 'LEGS')
    switchControlModeAllLegs(XL_EXT_POSITION_CONTROL)
    
def stowLegs():
    switchControlModeAllLegs(XL_POSITION_CONTROL)
    moveLegsFromHome(1024)
    timeOut(GLOBAL_TIMEOUT, 'LEGS')
    switchControlModeAllLegs(XL_EXT_POSITION_CONTROL)
    print("Stowed Legs")

def offsetLegsRelative():
    switchControlModeAllLegs(XL_POSITION_CONTROL)

    moveMotorPos(RF_LEG_ID, 0)
    moveMotorPos(RM_LEG_ID, 4096 - LEG_OFFSET)
    moveMotorPos(RB_LEG_ID, 0)
    moveMotorPos(LF_LEG_ID, 0 + LEG_OFFSET)
    moveMotorPos(LM_LEG_ID, 0)
    moveMotorPos(LB_LEG_ID, 0 + LEG_OFFSET)

    timeOut(GLOBAL_TIMEOUT, 'LEGS')

    switchControlModeAllLegs(XL_EXT_POSITION_CONTROL)

def homeLegsRelative():
    switchControlModeAllLegs(XL_POSITION_CONTROL)

    moveMotorPos(RF_LEG_ID, 0)
    moveMotorPos(RM_LEG_ID, 0)
    moveMotorPos(RB_LEG_ID, 0)
    moveMotorPos(LF_LEG_ID, 0)
    moveMotorPos(LM_LEG_ID, 0)
    moveMotorPos(LB_LEG_ID, 0)

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
    while not(moveTail(TAIL_PITCH_DOWN, TAIL_YAW_STRAIGHT)):
        time.sleep(0.01)
        if(time.time() - st > GLOBAL_TIMEOUT):
            print("Timed Out")
            break
    shakeTail(2)
    st = time.time()
    while not(moveTail(TAIL_PITCH_STRAIGHT, TAIL_YAW_STRAIGHT)):
        time.sleep(0.01)
        if(time.time() - st > GLOBAL_TIMEOUT):
            print("Timed Out")
            break
    homeWings()

def walk(rotations):
    print("Walking ", rotations, " Rotations")
    pos = int(rotations * 4096)
    curr = getPos(LM_LEG_ID)
    moveLegsOffset(curr + pos)

def walkNonOffset(rotations):
    print("Walking ", rotations, " Rotations without leg offset")
    homeLegsRelative()
    pos = rotations * 4096
    curr = getPos(LM_LEG_ID)
    moveLegsFromHome(curr + pos)

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
    moveTail(TAIL_PITCH_IN_GROUND, TAIL_YAW_STRAIGHT)
    timeOut(GLOBAL_TIMEOUT, 'TAIL')

def shakeTailSmall(wags):
    print("Shaking Tail ", wags, " times")
    for i in range (wags):
        while not(moveTail(TAIL_PITCH_STRAIGHT, TAIL_YAW_LEFT_SMALL)):
            time.sleep(0.01)
        while not(moveTail(TAIL_PITCH_STRAIGHT, TAIL_YAW_RIGHT_SMALL)):
            time.sleep(0.01)
    homeTail()

def shakeTail(wags):
    print("Shaking Tail ", wags, " times")
    for i in range (wags):
        moveMotorPos(TAIL_YAW_ID, TAIL_YAW_RIGHT)
        timeOut(GLOBAL_TIMEOUT, 'TAIL')
        moveMotorPos(TAIL_YAW_ID, TAIL_YAW_LEFT)
        timeOut(GLOBAL_TIMEOUT, 'TAIL')
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



def keyboardControl():
    print("Enabling Keyboard Control")
    while True:
        if(keyboard.is_pressed('esc')):
            break

        moveConst = 1200
        if(keyboard.is_pressed('w')):
            # # walk(0.1)
            # curr = getPos(LM_LEG_ID)
            # moveLegsOffset(curr + 1200)
            moveMotorPos(RF_LEG_ID, getPos(RF_LEG_ID) + moveConst)
            moveMotorPos(RM_LEG_ID, getPos(RM_LEG_ID) + moveConst)
            moveMotorPos(RB_LEG_ID, getPos(RB_LEG_ID) + moveConst)
            moveMotorPos(LF_LEG_ID, getPos(LF_LEG_ID) + moveConst)
            moveMotorPos(LM_LEG_ID, getPos(LM_LEG_ID) + moveConst)
            moveMotorPos(LB_LEG_ID, getPos(LB_LEG_ID) + moveConst)
        
        if(keyboard.is_pressed('s')):
            # curr = getPos(LM_LEG_ID)
            # moveLegsOffset(curr - 1200)
            # # walk(-0.1)
            moveMotorPos(RF_LEG_ID, getPos(RF_LEG_ID) - moveConst)
            moveMotorPos(RM_LEG_ID, getPos(RM_LEG_ID) - moveConst)
            moveMotorPos(RB_LEG_ID, getPos(RB_LEG_ID) - moveConst)
            moveMotorPos(LF_LEG_ID, getPos(LF_LEG_ID) - moveConst)
            moveMotorPos(LM_LEG_ID, getPos(LM_LEG_ID) - moveConst)
            moveMotorPos(LB_LEG_ID, getPos(LB_LEG_ID) - moveConst)

        turnConst = 800
        if(keyboard.is_pressed('a')):
            moveMotorPos(RF_LEG_ID, getPos(RF_LEG_ID) + turnConst)
            moveMotorPos(RM_LEG_ID, getPos(RM_LEG_ID) + turnConst)
            moveMotorPos(RB_LEG_ID, getPos(RB_LEG_ID) + turnConst)
            moveMotorPos(LF_LEG_ID, getPos(LF_LEG_ID) - turnConst)
            moveMotorPos(LM_LEG_ID, getPos(LM_LEG_ID) - turnConst)
            moveMotorPos(LB_LEG_ID, getPos(LB_LEG_ID) - turnConst)
            
        if(keyboard.is_pressed('d')):
            moveMotorPos(RF_LEG_ID, getPos(RF_LEG_ID) - turnConst)
            moveMotorPos(RM_LEG_ID, getPos(RM_LEG_ID) - turnConst)
            moveMotorPos(RB_LEG_ID, getPos(RB_LEG_ID) - turnConst)
            moveMotorPos(LF_LEG_ID, getPos(LF_LEG_ID) + turnConst)
            moveMotorPos(LM_LEG_ID, getPos(LM_LEG_ID) + turnConst)
            moveMotorPos(LB_LEG_ID, getPos(LB_LEG_ID) + turnConst)

        if(keyboard.is_pressed('x')):
            offsetLegsRelative()

            
        if(keyboard.is_pressed('up')):
            # walk(0.1)
            curr = getPos(LM_LEG_ID)
            moveLegsNonOffset(curr + 1200)
        
        if(keyboard.is_pressed('down')):
            curr = getPos(LM_LEG_ID) 
            moveLegsNonOffset(curr - 1200)
            # walk(-0.1)

        if(keyboard.is_pressed('j')):
            moveMotorPos(TAIL_PITCH_ID, TAIL_PITCH_DOWN)

        if(keyboard.is_pressed('k')):
            moveMotorPos(TAIL_PITCH_ID, TAIL_PITCH_IN_GROUND)

        if(keyboard.is_pressed('l')):
            moveMotorPos(TAIL_PITCH_ID, TAIL_PITCH_STRAIGHT)

        if(keyboard.is_pressed(';')):
            moveMotorPos(TAIL_PITCH_ID, TAIL_PITCH_UP-300)

        if(keyboard.is_pressed('\'')):
            moveMotorPos(TAIL_PITCH_ID, TAIL_PITCH_FORWARD)

        
        if(keyboard.is_pressed('o')):
            moveWings(L_WING_OPEN, R_WING_OPEN)
        
        if(keyboard.is_pressed('p')):
            moveWings(L_WING_CLOSED, R_WING_CLOSED)

        if(keyboard.is_pressed('m')):
            selfRight()

        if(keyboard.is_pressed('n')):
            rollOver()

        if(keyboard.is_pressed('f')):
            if(tailRoll == True):
                moveMotorPos(TAIL_ROLL_ID, TAIL_ROLL_LEFT_SMALL)
            else:
                moveMotorPos(TAIL_YAW_ID, TAIL_YAW_LEFT_SMALL)

        if(keyboard.is_pressed('g')):
            if(tailRoll == True):
                moveMotorPos(TAIL_ROLL_ID, TAIL_ROLL_STRAIGHT)
            else:
                moveMotorPos(TAIL_YAW_ID, TAIL_YAW_STRAIGHT)

        if(keyboard.is_pressed('h')):
            if(tailRoll == True):
                moveMotorPos(TAIL_ROLL_ID, TAIL_ROLL_RIGHT_SMALL)
            else:
                moveMotorPos(TAIL_YAW_ID, TAIL_YAW_RIGHT_SMALL)

        if(keyboard.is_pressed(',')):
            if(tailRoll == True):
                moveMotorPos(TAIL_ROLL_ID, TAIL_ROLL_LEFT)
            else:
                moveMotorPos(TAIL_YAW_ID, TAIL_YAW_LEFT)

        if(keyboard.is_pressed('.')):
            if(tailRoll == True):
                moveMotorPos(TAIL_ROLL_ID, TAIL_ROLL_RIGHT)
            else:
                moveMotorPos(TAIL_YAW_ID, TAIL_YAW_RIGHT)


        

enableAll()

#home everything
homeWings()
homeTail()
offsetLegsRelative()

#enable keyboard control
keyboardControl()


disableAll()

# Close port
portHandler.closePort()

print("Finished!")
