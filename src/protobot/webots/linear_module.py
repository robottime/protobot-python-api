from math import pi, fabs
from .node import NodeFactory

class LinearModuleFactory(NodeFactory):
    def get_node(self, robot, device_name):
        motor = LinearModule(robot.getDevice(device_name))
        return motor

class LinearModule():
    def __init__(self, webots_motor):
        self._motor = webots_motor
        self._motor.setPosition(0)
        self._max_vel = 0.015
        self._motor.setVelocity(self._max_vel)

    def position_mode(self):
        self._motor.setVelocity(self._max_vel)
        self._motor.setAcceleration(-1)

    def position_filter_mode(self, bandwidth = 10):
        self._motor.setVelocity(self._max_vel)
        self._motor.setAcceleration(-1)

    def position_traj_mode(self, max_vel, max_acc):
        self._motor.setVelocity(min(fabs(max_vel), self._max_vel))
        self._motor.setAcceleration(fabs(max_acc))

    def enable(self):
        pass
    
    def disable(self):
        pass

    def set_pos(self, pos):
        pos = min(pos, 0.05)
        pos = max(pos, -0.05)
        self._motor.setPosition(pos)

    def get_pos(self):
        return self._motor.getTargetPosition()

    def get_vel(self):
        return self._motor.getVelocity()
