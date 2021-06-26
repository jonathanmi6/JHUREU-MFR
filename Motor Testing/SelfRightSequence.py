#Tail Pitch: ID = 7
#Tail Yaw: ID = 8
#Right wing: ID = 10
#Left wing: ID = 11

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

from dynamixel_sdk import *                    # Uses Dynamixel SDK library

# Control table address
XL_TORQUE_ENABLE = 64               # Control table address is different in Dynamixel model
XL_GOAL_POSITION = 116
XL_PRESENT_POSITION = 132

# Data Byte Length
LEN_XL_GOAL_POSITION = 4
LEN_XL_PRESENT_POSITION = 4

# Protocol version
PROTOCOL_VERSION = 2.0               # See which protocol version is used in the Dynamixel

# Default setting
R_WING_ID = 10
L_WING_ID = 11  
TAIL_PITCH_ID = 7
TAIL_YAW_ID = 8
BAUDRATE = 1000000             # Dynamixel default baudrate : 57600
DEVICENAME = 'COM9'    # Check which port is being used on your controller  # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"

TORQUE_ENABLE = 1                 # Value for enabling the torque
TORQUE_DISABLE = 0                 # Value for disabling the torque

#position values
R_WING_CLOSED  = 2048           # Dynamixel will rotate between this value
R_WING_OPEN  = 3320            # and this value (note that the Dynamixel would not move when the position value is out of movable range. Check e-manual about the range of the Dynamixel you use.)
L_WING_CLOSED = 2048
L_WING_OPEN = 776

TAIL_PITCH_UP = 1075
TAIL_PITCH_DOWN = 3072
TAIL_PITCH_STRAIGHT = 2048
TAIL_YAW_RIGHT = 3072
TAIL_YAW_LEFT = 1024
TAIL_YAW_STRAIGHT = 2048

DXL_MOVING_STATUS_THRESHOLD = 30                # Dynamixel moving status threshold

index = 0 #used to identify whether to use closed or open value in the following array
rWingGoalPositions = [R_WING_CLOSED, R_WING_OPEN]         # Goal position
lWingGoalPositions = [L_WING_CLOSED, L_WING_OPEN]
tailPitchGoalPositions = [TAIL_PITCH_STRAIGHT, TAIL_PITCH_DOWN, TAIL_PITCH_UP]
tailYawGoalPositions = [TAIL_YAW_STRAIGHT, TAIL_YAW_RIGHT, TAIL_YAW_LEFT]

# Initialize PortHandler instance
# Set the port path
# Get methods and members of PortHandlerLinux or PortHandlerWindows
portHandler = PortHandler(DEVICENAME)

# Initialize PacketHandler instance
# Set the protocol version
# Get methods and members of Protocol1PacketHandler or Protocol2PacketHandler
packetHandler = PacketHandler(PROTOCOL_VERSION)

# Initialize GroupSyncWrite instance
groupSyncWrite = GroupSyncWrite(portHandler, packetHandler, XL_GOAL_POSITION, LEN_XL_GOAL_POSITION)

# Initialize GroupSyncRead instace for Present Position
groupSyncRead = GroupSyncRead(portHandler, packetHandler, XL_PRESENT_POSITION, LEN_XL_PRESENT_POSITION)

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

def enableTorque(id):
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, id, XL_TORQUE_ENABLE, TORQUE_ENABLE)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    else:
        print("Dynamixel#%d has been successfully connected" % id)

enableTorque(R_WING_ID)
enableTorque(L_WING_ID)
enableTorque(TAIL_YAW_ID)
enableTorque(TAIL_PITCH_ID)


def addParamRead(id):
    # Add parameter storage for ID present position value
    dxl_addparam_result = groupSyncRead.addParam(id)
    if dxl_addparam_result != True:
        print("[ID:%03d] groupSyncRead addparam failed" % id)
        quit()

addParamRead(R_WING_ID)
addParamRead(L_WING_ID)
addParamRead(TAIL_YAW_ID)
addParamRead(TAIL_PITCH_ID)

def addParamWrite(id, value):
    byteValue = value.to_bytes(4, 'little')
    dxl_addparam_result = groupSyncWrite.addParam(id, byteValue)
    if dxl_addparam_result != True:
        print("[ID:%03d] groupSyncWrite addparam failed" % R_WING_ID)
        quit()

def syncWriteGoal():
    dxl_comm_result = groupSyncWrite.txPacket()
    if dxl_comm_result != COMM_SUCCESS:
        print("Sync Write Goal Error:%s" % packetHandler.getTxRxResult(dxl_comm_result))

def atPosition(goal, curr):
    if(abs(goal - curr) > DXL_MOVING_STATUS_THRESHOLD):
        return False
    return True

def getPos(id):
    #Check if groupsyncread data of Dynamixel is available
    dxl_getdata_result = groupSyncRead.isAvailable(id, XL_PRESENT_POSITION, LEN_XL_PRESENT_POSITION)
    if dxl_getdata_result != True:
        print("getPos Error: [ID:%03d] groupSyncRead getdata failed" % id)
        quit()
        
    dxl_comm_result = groupSyncRead.txRxPacket()
    if dxl_comm_result != COMM_SUCCESS:
        print("getPos Error: %s" % packetHandler.getTxRxResult(dxl_comm_result))
    currPos = groupSyncRead.getData(id, XL_PRESENT_POSITION, LEN_XL_PRESENT_POSITION)
    return currPos

def moveMotor(id, pos):
    addParamWrite(id, pos)
    syncWriteGoal()
    groupSyncWrite.clearParam()
    return atPosition(pos, getPos(id))

def moveMotors(rWingGoal, lWingGoal, tailYawGoal, tailPitchGoal):
    # while 1:
        # print("Press any key to continue! (or press ESC to quit!)")
        # if getch() == chr(0x1b):
        #     break

        ##IDEA: create python function with inputs of position bytes to set all at once
        # Add rWing position value to the Syncwrite parameter storage
        addParamWrite(R_WING_ID, rWingGoal)
        addParamWrite(L_WING_ID, lWingGoal)
        addParamWrite(TAIL_YAW_ID, tailYawGoal)
        addParamWrite(TAIL_PITCH_ID, tailPitchGoal)
        

        # Syncwrite goal position
        syncWriteGoal()

        # Clear syncwrite parameter storage
        groupSyncWrite.clearParam()

        while 1:
            # Syncread present position
            dxl_comm_result = groupSyncRead.txRxPacket()
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % packetHandler.getTxRxResult(dxl_comm_result))

            # Get position values
            rWingCurrPos = groupSyncRead.getData(R_WING_ID, XL_PRESENT_POSITION, LEN_XL_PRESENT_POSITION)
            lWingCurrPos = groupSyncRead.getData(L_WING_ID, XL_PRESENT_POSITION, LEN_XL_PRESENT_POSITION)
            tailYawCurrPos = groupSyncRead.getData(TAIL_YAW_ID, XL_PRESENT_POSITION, LEN_XL_PRESENT_POSITION)
            tailPitchCurrPos = groupSyncRead.getData(TAIL_PITCH_ID, XL_PRESENT_POSITION, LEN_XL_PRESENT_POSITION)

            print("[ID:%03d] GoalPos:%03d  CurrPos:%03d\t[ID:%03d] GoalPos:%03d  CurrPos:%03d" % (R_WING_ID, rWingGoal, rWingCurrPos, L_WING_ID, lWingGoal, lWingCurrPos))

            if(atPosition(rWingGoal, rWingCurrPos) and atPosition(lWingGoal, lWingCurrPos) and atPosition(tailYawGoal, tailYawCurrPos) and atPosition(tailPitchGoal, tailPitchCurrPos)):
                done = True
                break #if goal and curr position are within the threshold, break out of loop
        # if(done):
            # break

def moveTail(yawPos, pitchPos):
    return (moveMotor(TAIL_YAW_ID, yawPos) and moveMotor(TAIL_PITCH_ID, pitchPos))

def moveWings(lPos, rPos):
    return (moveMotor(L_WING_ID, lPos) and moveMotor(R_WING_ID, rPos))

#old movemotors function
# time.sleep(5)
# moveMotors(R_WING_CLOSED, L_WING_CLOSED, TAIL_YAW_STRAIGHT, TAIL_PITCH_STRAIGHT)
# moveMotors(R_WING_OPEN, L_WING_OPEN, TAIL_YAW_STRAIGHT, TAIL_PITCH_DOWN)
# moveMotors(R_WING_OPEN, L_WING_OPEN, TAIL_YAW_RIGHT, TAIL_PITCH_DOWN)
# moveMotors(R_WING_OPEN, L_WING_OPEN, TAIL_YAW_LEFT, TAIL_PITCH_DOWN)
# time.sleep(1)
# moveMotors(R_WING_OPEN, L_WING_OPEN, TAIL_YAW_STRAIGHT, TAIL_PITCH_STRAIGHT)
# moveMotors(R_WING_CLOSED, L_WING_CLOSED, TAIL_YAW_STRAIGHT, TAIL_PITCH_STRAIGHT)

#new moveMotor function
# while not(moveMotor(R_WING_ID, R_WING_OPEN) and moveMotor(L_WING_ID, L_WING_CLOSED)):
    # time.sleep(0.01)

while not(moveTail(TAIL_YAW_STRAIGHT, TAIL_PITCH_STRAIGHT) and moveWings(L_WING_CLOSED, R_WING_CLOSED)):
    time.sleep(0.01)
# while not(moveWings(L_WING_OPEN, R_WING_OPEN) and moveTail(TAIL_YAW_STRAIGHT, TAIL_PITCH_DOWN)):
#     time.sleep(0.01)
# while not(moveTail(TAIL_YAW_LEFT, TAIL_PITCH_DOWN)):
#     time.sleep(0.01)
# time.sleep(0.5)
# while not(moveTail(TAIL_YAW_STRAIGHT, TAIL_PITCH_STRAIGHT)):
#     time.sleep(0.01)
# while not(moveWings(L_WING_CLOSED, R_WING_CLOSED)):
#     time.sleep(0.01)

# while 1:
#     print("Press any key to continue! (or press ESC to quit!)")
#     if getch() == chr(0x1b):
#         break

#     ##IDEA: create python function with inputs of position bytes to set all at once
#     # Add rWing position value to the Syncwrite parameter storage
#     addParamWrite(R_WING_ID, rWingGoalPositions[0])
#     addParamWrite(L_WING_ID, lWingGoalPositions[0])
#     addParamWrite(TAIL_YAW_ID, tailYawGoalPositions[0])
#     addParamWrite(TAIL_PITCH_ID,tailPitchGoalPositions[0])
    

#     # Syncwrite goal position
#     syncWriteGoal()

#     # Clear syncwrite parameter storage
#     groupSyncWrite.clearParam()

#     while 1:
#         # Syncread present position
#         dxl_comm_result = groupSyncRead.txRxPacket()
#         if dxl_comm_result != COMM_SUCCESS:
#             print("%s" % packetHandler.getTxRxResult(dxl_comm_result))

#         # Check if groupsyncread data of Dynamixel#1 is available
#         dxl_getdata_result = groupSyncRead.isAvailable(R_WING_ID, XL_PRESENT_POSITION, LEN_XL_PRESENT_POSITION)
#         if dxl_getdata_result != True:
#             print("[ID:%03d] groupSyncRead getdata failed" % R_WING_ID)
#             quit()

#         # Check if groupsyncread data of Dynamixel#2 is available
#         dxl_getdata_result = groupSyncRead.isAvailable(L_WING_ID, XL_PRESENT_POSITION, LEN_XL_PRESENT_POSITION)
#         if dxl_getdata_result != True:
#             print("[ID:%03d] groupSyncRead getdata failed" % L_WING_ID)
#             quit()


#         # Get position values
#         rWingPresentPosition = groupSyncRead.getData(R_WING_ID, XL_PRESENT_POSITION, LEN_XL_PRESENT_POSITION)
#         lWingPresentPosition = groupSyncRead.getData(L_WING_ID, XL_PRESENT_POSITION, LEN_XL_PRESENT_POSITION)
#         tailYawPresentPosition = groupSyncRead.getData(TAIL_YAW_ID, XL_PRESENT_POSITION, LEN_XL_PRESENT_POSITION)
#         tailPitchPresentPosition = groupSyncRead.getData(TAIL_PITCH_ID, XL_PRESENT_POSITION, LEN_XL_PRESENT_POSITION)

#         print("[ID:%03d] GoalPos:%03d  PresPos:%03d\t[ID:%03d] GoalPos:%03d  PresPos:%03d" % (R_WING_ID, rWingGoalPositions[index], rWingPresentPosition, L_WING_ID, rWingGoalPositions[index], lWingPresentPosition))

#         if(atPosition(rWingGoalPositions[0], rWingPresentPosition) and atPosition(lWingGoalPositions[0], lWingPresentPosition) and atPosition(tailYawGoalPositions[0], tailYawPresentPosition) and atPosition(tailPitchGoalPositions[0], tailPitchPresentPosition)):
#             break #if goal and curr position are within the threshold, break out of loop


    # # Change goal position
    # if index == 0:
    #     index = 1
    # else:
    #     index = 0








# Clear syncread parameter storage
groupSyncRead.clearParam()

def disableTorque(id):
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, id, XL_TORQUE_ENABLE, TORQUE_DISABLE)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))

disableTorque(R_WING_ID)
disableTorque(L_WING_ID)
disableTorque(TAIL_PITCH_ID)
disableTorque(TAIL_YAW_ID)

    




# Close port
portHandler.closePort()

print("Finished!")
