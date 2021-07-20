import os

if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

from dynamixel_sdk import *

from MFRv2_Constants import *

# Initialize PortHandler instance & Set the port path
portHandler = PortHandler(DEVICENAME)


# Initialize PacketHandler instance & Set the protocol version
packetHandler = PacketHandler(PROTOCOL_VERSION)

# Open port
if portHandler.openPort():
    print("Succeeded to open the port")
else:
    print("Failed to open the port")
    print("Press any key to terminate...")
    getch()
    quit()

# Set port baudrate
if portHandler.setBaudRate(BAUDRATE):
    print("Succeeded to change the baudrate")
else:
    print("Failed to change the baudrate")
    print("Press any key to terminate...")
    getch()
    quit()



#motor control functions:

def enableTorque(id):
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, id, XL_TORQUE_ENABLE, TORQUE_ENABLE)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        # quit()
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    else:
        print("Dynamixel#%d has been successfully connected" % id)

def disableTorque(id):
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, id, XL_TORQUE_ENABLE, TORQUE_DISABLE)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        # quit()
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    else:
        print("Dynamixel#%d has been successfully disconnected" % id)

def atPosition(goal, curr):
    if(abs(goal - curr) > DXL_MOVING_STATUS_THRESHOLD):
        return False
    return True

def atPositionCustom(goal, curr, threshold):
    if(abs(goal - curr) > threshold):
        return False
    return True

def getPos(id): #get position of motor
    # currPos, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(portHandler, id, XL_PRESENT_POSITION)
    currPos = packetHandler.read4ByteTxRx(portHandler, id, XL_PRESENT_POSITION)[0]

    # if dxl_comm_result != COMM_SUCCESS:
    #     print("getPos Error: %s" % packetHandler.getTxRxResult(dxl_comm_result))
    # elif dxl_error != 0:
    #     print("%s" % packetHandler.getRxPacketError(dxl_error))


    # ------- Eric Lara's patch for a read bug (error with negative integers) -----------
    dxl_present_16Byte_1 = (currPos & 0xFFFF)
    dxl_present_16Byte_2 = (currPos >> 16) & 0xFFFF

    # print('[%s, %s]' % (dxl_present_16Byte_1, dxl_present_16Byte_2) )

    if dxl_present_16Byte_1 < dxl_present_16Byte_2:
        multiply  = 65535 - dxl_present_16Byte_2
        currPos = (dxl_present_16Byte_1 - 65535) - multiply*65535

	# -------------------------------------------------------------------------

    return currPos

def getVel(id):
    currVel, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(portHandler, id, XL_PRESENT_VELOCITY)
    if dxl_comm_result != COMM_SUCCESS:
        print("getPos Error: %s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))

    return currVel

def getPosGoal(id):
    goalPos = packetHandler.read4ByteTxRx(portHandler, id, XL_GOAL_POSITION)[0]

    # ------- Eric Lara's patch for a read bug (error with negative integers) -----------
    dxl_present_16Byte_1 = (goalPos & 0xFFFF)
    dxl_present_16Byte_2 = (goalPos >> 16) & 0xFFFF

    # print('[%s, %s]' % (dxl_present_16Byte_1, dxl_present_16Byte_2) )

    if dxl_present_16Byte_1 < dxl_present_16Byte_2:
        multiply  = 65535 - dxl_present_16Byte_2
        goalPos = (dxl_present_16Byte_1 - 65535) - multiply*65535

	# -------------------------------------------------------------------------

    return goalPos

def getVelGoal(id):
    currVel, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(portHandler, id, XL_GOAL_VELOCITY)
    if dxl_comm_result != COMM_SUCCESS:
        print("getPos Error: %s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))

    return currVel

def getProfileVelocity(id):
    return packetHandler.read4ByteTxRx(portHandler, id, XL_PROFILE_VELOCITY)[0]

def switchControlMode(id, mode):
    print("Switching Motor ", id, " to: ", mode)
    disableTorque(id)
    packetHandler.write1ByteTxRx(portHandler, id, XL_OPERATING_MODE, mode)
    enableTorque(id)

def switchControlModeAllLegs(mode):
    switchControlMode(RF_LEG_ID, mode)
    switchControlMode(RM_LEG_ID, mode)
    switchControlMode(RB_LEG_ID, mode)
    switchControlMode(LF_LEG_ID, mode)
    switchControlMode(LM_LEG_ID, mode)
    switchControlMode(LB_LEG_ID, mode)

def moveMotorPos(id, pos):
    dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler,id, XL_GOAL_POSITION, pos)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))

def moveMotorVel(id, vel):
    dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler,id, XL_GOAL_VELOCITY, vel)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))    

def moveTail(pitchPos, yawPos):
    # return (moveMotor(TAIL_YAW_ID, yawPos) and moveMotor(TAIL_PITCH_ID, pitchPos))
    moveMotorPos(TAIL_YAW_ID, yawPos)
    moveMotorPos(TAIL_PITCH_ID, pitchPos)
    return (tailAtPos())

def moveWings(lPos, rPos):
    # return (moveMotor(L_WING_ID, lPos) and moveMotor(R_WING_ID, rPos))
    moveMotorPos(L_WING_ID, lPos)
    moveMotorPos(R_WING_ID, rPos)
    # return (wingsAtPos())

def tailAtPos():
    return (atPosition(getPosGoal(TAIL_YAW_ID), getPos(TAIL_YAW_ID)) and atPositionCustom(getPosGoal(TAIL_PITCH_ID), getPos(TAIL_PITCH_ID), TAIL_MOVING_THRESHOLD))

def wingsAtPos():
    return (atPosition(getPosGoal(L_WING_ID), getPos(L_WING_ID)) and atPosition(getPosGoal(R_WING_ID), getPos(R_WING_ID)))

def legsAtPos():
    return (atPosition(getPosGoal(RF_LEG_ID), getPos(RF_LEG_ID)) and atPosition(getPosGoal(RM_LEG_ID), getPos(RM_LEG_ID)) and atPosition(getPosGoal(RB_LEG_ID), getPos(RB_LEG_ID)) and atPosition(getPosGoal(LF_LEG_ID), getPos(LF_LEG_ID)) and atPosition(getPosGoal(LM_LEG_ID), getPos(LM_LEG_ID)) and atPosition(getPosGoal(LB_LEG_ID), getPos(LB_LEG_ID)))

def moveLegsFromHome(pos):
    moveMotorPos(RF_LEG_ID, RF_LEG_HOME + pos)
    moveMotorPos(RM_LEG_ID, RM_LEG_HOME + pos)
    moveMotorPos(RB_LEG_ID, RB_LEG_HOME + pos)
    moveMotorPos(LF_LEG_ID, LF_LEG_HOME + pos)
    moveMotorPos(LM_LEG_ID, LM_LEG_HOME + pos)
    moveMotorPos(LB_LEG_ID, LB_LEG_HOME + pos)
    # return (legsAtPos())

def moveLegsOffset(pos):
    moveMotorPos(RF_LEG_ID, pos)
    moveMotorPos(RM_LEG_ID, 4096 - LEG_OFFSET + pos)
    moveMotorPos(RB_LEG_ID, pos)
    moveMotorPos(LF_LEG_ID, LEG_OFFSET + pos)
    moveMotorPos(LM_LEG_ID, pos)
    moveMotorPos(LB_LEG_ID, LEG_OFFSET + pos)
    # return (legsAtPos())

def moveLegsNonOffset(pos):
    moveMotorPos(RF_LEG_ID, pos)
    moveMotorPos(RM_LEG_ID, pos)
    moveMotorPos(RB_LEG_ID, pos)
    moveMotorPos(LF_LEG_ID, pos)
    moveMotorPos(LM_LEG_ID, pos)
    moveMotorPos(LB_LEG_ID, pos)
    # return (legsAtPos())

def setAllLegsVel(vel):
    moveMotorVel(RF_LEG_ID, vel)
    moveMotorVel(RM_LEG_ID, vel)
    moveMotorVel(RB_LEG_ID, vel)
    moveMotorVel(LF_LEG_ID, vel)
    moveMotorVel(LM_LEG_ID, vel)
    moveMotorVel(LB_LEG_ID, vel)

def setOffsetLegsVel(vel):
    moveMotorVel(RM_LEG_ID, vel)
    moveMotorVel(LF_LEG_ID, vel)
    moveMotorVel(LB_LEG_ID, vel)

def setNonOffsetLegsVel(vel):
    moveMotorVel(RF_LEG_ID, vel)
    moveMotorVel(RB_LEG_ID, vel)
    moveMotorVel(LM_LEG_ID, vel)

# def moveLegsRelative(pos):
#     switchControlModeAllLegs(XL_POSITION_CONTROL)
#     moveLegsFromHome(pos)
#     switchControlModeAllLegs(XL_EXT_POSITION_CONTROL)

# def offsetLegsFromHome():
#     moveMotorPos(RF_LEG_ID, RF_LEG_HOME)
#     moveMotorPos(RM_LEG_ID, RM_LEG_HOME - LEG_OFFSET)
#     moveMotorPos(RB_LEG_ID, RB_LEG_HOME)
#     moveMotorPos(LF_LEG_ID, LF_LEG_HOME + LEG_OFFSET)
#     moveMotorPos(LM_LEG_ID, LM_LEG_HOME)
#     moveMotorPos(LB_LEG_ID, LB_LEG_HOME + LEG_OFFSET)

#     while not (atPosition(RF_LEG_HOME, getPos(RF_LEG_ID)) and atPosition(LF_LEG_HOME + LEG_OFFSET, getPos(LF_LEG_ID))):
#         print("Offsetting Legs", RF_LEG_HOME, getPos(RF_LEG_ID), LF_LEG_HOME + LEG_OFFSET, getPos(LF_LEG_ID))
#         time.sleep(0.01)

def setProfileVelocity(id, vel):
    dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, id, XL_PROFILE_VELOCITY, vel)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))

def setAllLegProfileVelocity(vel):
    setProfileVelocity(RF_LEG_ID, vel)
    moveMotorPos(RF_LEG_ID, getPosGoal(RF_LEG_ID))
    setProfileVelocity(RM_LEG_ID, vel)
    moveMotorPos(RM_LEG_ID, getPosGoal(RM_LEG_ID))
    setProfileVelocity(RB_LEG_ID, vel)
    moveMotorPos(RB_LEG_ID, getPosGoal(RB_LEG_ID))
    setProfileVelocity(LF_LEG_ID, vel)
    moveMotorPos(LF_LEG_ID, getPosGoal(LF_LEG_ID))
    setProfileVelocity(LM_LEG_ID, vel)
    moveMotorPos(LM_LEG_ID, getPosGoal(LM_LEG_ID))
    setProfileVelocity(LB_LEG_ID, vel)
    moveMotorPos(LB_LEG_ID, getPosGoal(LB_LEG_ID))

def setOffsetLegProfileVelocity(vel):
    setProfileVelocity(RM_LEG_ID, vel)
    moveMotorPos(RM_LEG_ID, getPosGoal(RM_LEG_ID))
    setProfileVelocity(LF_LEG_ID, vel)
    moveMotorPos(LF_LEG_ID, getPosGoal(LF_LEG_ID))
    setProfileVelocity(LB_LEG_ID, vel)
    moveMotorPos(LB_LEG_ID, getPosGoal(LB_LEG_ID))

def setNonOffsetLegProfileVelocity(vel):
    setProfileVelocity(RF_LEG_ID, vel)
    moveMotorPos(RF_LEG_ID, getPosGoal(RF_LEG_ID))
    setProfileVelocity(RB_LEG_ID, vel)
    moveMotorPos(RB_LEG_ID, getPosGoal(RB_LEG_ID))
    setProfileVelocity(LM_LEG_ID, vel)
    moveMotorPos(LM_LEG_ID, getPosGoal(LM_LEG_ID))


def enableAll():
    enableTorque(RF_LEG_ID)
    enableTorque(RM_LEG_ID)
    enableTorque(RB_LEG_ID)
    enableTorque(LF_LEG_ID)
    enableTorque(LM_LEG_ID)
    enableTorque(LB_LEG_ID)
    enableTorque(TAIL_YAW_ID)
    enableTorque(TAIL_PITCH_ID)
    enableTorque(R_WING_ID)
    enableTorque(L_WING_ID)

def disableAll():
    disableTorque(RF_LEG_ID)
    disableTorque(RM_LEG_ID)
    disableTorque(RB_LEG_ID)
    disableTorque(LF_LEG_ID)
    disableTorque(LM_LEG_ID)
    disableTorque(LB_LEG_ID)
    disableTorque(TAIL_PITCH_ID)
    disableTorque(TAIL_YAW_ID)
    disableTorque(R_WING_ID)
    disableTorque(L_WING_ID)

## for motor testing:

enableAll()
disableAll()

# Close port
# portHandler.closePort()

print("Imported MotorControl")
