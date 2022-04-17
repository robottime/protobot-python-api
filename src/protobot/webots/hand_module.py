from math import pi, fabs
from .node import NodeFactory

class HandModuleFactory(NodeFactory):
    def get_node(self, robot, device_name):
        motor = HandModule(robot.getDevice(device_name+"::left"))
        return motor

class HandModule():
    def __init__(self, webots_motor):
        self._motor = webots_motor
        self._motor.setPosition(0)
    
    def enable(self):
        pass
    
    def set_pos(self, pos):
        self._motor.setPosition(pos*0.02)
