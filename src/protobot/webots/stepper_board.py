from math import pi, fabs
from .node import NodeFactory

class StepperBoardFactory(NodeFactory):
    def get_node(self, robot, device_name, reduction = 10):
        stepper = StepperBoard(robot.getDevice(device_name), reduction)
        return stepper

class StepperBoard():

    POSITION_MODE = 0
    VELOCITY_MODE = 1

    def __init__(self, webots_motor, reduction):
        self._motor = webots_motor
        self._reduction = reduction
        self._motor.setAvailableTorque(0)
        self._enable = False
        self.set_vel_acc_limit(5 * pi, 20 * pi)
        self._vel = self._max_vel
        self._maxTorque = 1 * reduction
        self.velocity_mode()
    
    def set_vel_acc_limit(self, vel_lim, acc_lim):
        self._max_vel = vel_lim * self._reduction * 0.025
        self._motor.setAcceleration(acc_lim * self._reduction * 0.025)

    def position_mode(self):
        self._vel = self._max_vel
        self._motor.setVelocity(0)
        self._mode = StepperBoard.POSITION_MODE

    def velocity_mode(self):
        self._vel = self._max_vel
        self._motor.setVelocity(0)
        self._motor.setPosition(float('+inf'))
        self._mode = StepperBoard.VELOCITY_MODE
    
    def stop(self):
        self._motor.setVelocity(0)

    def set_pos(self, pos):
        if self._mode != StepperBoard.POSITION_MODE:
            print('Warning: should set pos in position mode.')
            return
        self._motor.setPosition(pos * 0.025)
        self._motor.setVelocity(self._vel)

    def get_pos(self):
        return self._motor.getTargetPosition() / 0.025

    def set_vel(self, vel):
        self._vel = vel * 0.025
        self._motor.setVelocity(vel * 0.025)

    def get_vel(self):
        return self._motor.getVelocity() / 0.025

    def enable(self):
        self._motor.setAvailableTorque(self._maxTorque)
        self._enable = True

    def disable(self):
        # TODO: wait position sensor
        self._motor.setVelocity(0)
        self._enable = False
