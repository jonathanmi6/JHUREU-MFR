# JHUREU-MFR

Use respective repo for respective robot. MFRv1 for MFRv1, MFRv2 for MFRv2.

**See project documentation for robot operating instructions**

```MFRv#_Constants.py``` contains the motor constants for each robot. This includes the motor parameter addresses as well as motor positions. Make sure to update the COM port constant for your specific setup.

```MFRv#_MotorControl.py``` contains the lower level motor control code. This includes things like setting motor control mode, moving individual motors, getting motor positions, etc.

```Main.py``` is the top level control. You can either use keyboard control by executing ```keyboardControl()```. The keyboard controls are relativly self-explainatory in the method. ```WASD``` for movement. ```x``` to home legs. ```m``` to self right. ```fgh``` for tail yaw. ```jkl;'``` for tail pitch.

## Known Issues and Solutions:

> "could not open port '____'"

Solution: plug in DYNAMIXEL2USB properly and make sure COM port is correct

>"[TxRxResult] Incorrect status packet!"

Solution: Check motors are properly connected and IDs are correct. Also try power cycling the robot.

>"Hardware Error"

Solution: Power cycle



## Python info:

Code runs with Python 3.8

Required Libraries: ```DynamixelSDK``` (in the repo already). ```Keyboard```.