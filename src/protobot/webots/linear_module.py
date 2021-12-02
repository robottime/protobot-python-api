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
        self._motor.setVelocity(0.015)

    def set_pos(self, pos):
        pos = min(pos, 0.05)
        pos = max(pos, -0.05)
        self._motor.setPosition(pos)

    def get_pos(self):
        return self._motor.getTargetPosition()

    def get_vel(self):
        return self._motor.getVelocity()