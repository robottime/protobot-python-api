from math import pi, fabs
from .node import NodeFactory

class HandFactory(NodeFactory):
    def get_node(self, robot, device_name):
        motor = Hand(robot.getDevice(device_name+"::left"))
        return motor

class Hand():
    def __init__(self, webots_motor):
        self._motor = webots_motor
        self._motor.setPosition(0)
    def set_pos(self, pos):
        self._motor.setPosition(pos*0.02)
