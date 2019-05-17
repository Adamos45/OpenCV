from enum import Enum


class Messages(Enum):
    # Control car
    TURNING = 1
    GO_FORWARDS = 2
    GO_BACKWARDS = 3
    SOFT_STOP = 4
    HARD_STOP = 5

    # values as control to setup what we want to read from Arduino
    READ_TURNING = 11
    READ_GO_FORWARDS = 22
    READ_GO_BACKWARDS = 33
    READ_ENCODER_IMPULSES = 101

    # values for second Arduino to read data from sensors
    READ_DISTANCE_SENSORS = 201
    READ_LINE_SENSORS = 202

    # MQTT handler
    PARKING_FULL = 'Parking is full'
    PARKING_CLOSED = 'Parking is closed'
    SUBSCRIBED = 'Subscribed'
    OK = 'Ok'
    ALARM = 'Alarm is triggered'

    #OpenCVEnums
    #Driving
    TURN_LEFT = 'Turn left'
    TURN_RIGHT = 'Turn right'
    SIGNAL_NOISE = 'Signal noise'
    #Parking
    CONTINUE_TURNING = 'Continue turning'
    STOP_TURNING = 'Stop turning'