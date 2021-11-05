from math import pi, fabs
from .node import NodeFactory

class MotorFactory(NodeFactory):
    def get_node(self, robot, device_name, reduction = 12.45):
        motor = Motor(robot.getDevice(device_name), reduction)
        return motor

class Motor():

    POSITION_MODE = 0
    VELOCITY_MODE = 1

    def __init__(self, webots_motor, reduction=12.45):
        self._motor = webots_motor
        self._reduction = reduction
        self._motor.setAvailableTorque(0)
        self._enable = False
        self._max_vel = 40 * pi / reduction
        self._vel = 40 * pi / reduction
        self._maxTorque = 0.5 * reduction
        self._mode = Motor.POSITION_MODE

    def status(self):
        # return {
        #     'mode': 'position' if self._mode == Motor.POSITION_MODE else 'velocity',
        #     'enable': self._enable
        # }
        return {
            'state': 8 if self._enable else 1,
            'control_mode': 3 if self._mode == Motor.POSITION_MODE else 2,
        }

    def position_mode(self):
        self._vel = self._max_vel
        self._motor.setVelocity(0)
        self._motor.setAcceleration(-1)
        self._mode = Motor.POSITION_MODE

    def position_traj_mode(self, max_vel, max_acc):
        self._vel = min(fabs(max_vel), self._max_vel)
        self._motor.setVelocity(0)
        self._motor.setAcceleration(fabs(max_acc))
        self._mode = Motor.POSITION_MODE

    def velocity_mode(self):
        self._vel = self._max_vel
        self._motor.setVelocity(0)
        self._motor.setAcceleration(-1)
        self._motor.setPosition(float('+inf'))
        self._mode = Motor.VELOCITY_MODE

    def velocity_ramp_mode(self, ramp):
        self._vel = self._max_vel
        self._motor.setVelocity(0)
        self._motor.setAcceleration(ramp)
        self._motor.setPosition(float('+inf'))
        self._mode = Motor.VELOCITY_MODE

    def set_vel_limit(self, vel_limit):
        self._max_vel = min(fabs(vel_limit), self._max_vel)

    def set_pos(self, pos):
        if self._mode != Motor.POSITION_MODE:
            print('Warning: should set pos in position mode.')
            return
        self._motor.setPosition(pos)
        self._motor.setVelocity(self._vel)

    def get_pos(self):
        return self._motor.getTargetPosition()

    def set_vel(self, vel):
        if self._mode != Motor.VELOCITY_MODE:
            print('Warning: should set vel in velocity mode.')
            return
        self._motor.setVelocity(vel)

    def get_vel(self):
        return self._motor.getVelocity()

    def enable(self):
        self._motor.setAvailableTorque(self._maxTorque)
        self._enable = True

    def disable(self):
        # TODO: wait position sensor
        self._motor.setVelocity(0)
        # self._motor.setAvailableTorque(0)
        self._enable = False
