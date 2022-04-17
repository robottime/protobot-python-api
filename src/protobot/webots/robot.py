from controller import Robot as WbRobot
from .node import NodeFactory

class Robot(object):
    def __init__(self):
        self._robot = WbRobot()
        self._timestep = int(self._robot.getBasicTimeStep())
        self.devices = {}

    def add_device(self, name, factory, *args, **kwargs):
        if not isinstance(factory, NodeFactory):
            raise RuntimeError('unknown factory to init device')
        self.devices[name] = factory.get_node(robot=self._robot, device_name=name, *args, **kwargs)
        return self.devices[name]

    def device(self, name):
        return self.devices.get(name, None)
    
    def remove_device(self, name):
        self.devices.pop(name, None)

    def getBasicTimeStep(self):
        return self._timestep

    def step(self):
        return self._robot.step(self._timestep)

    def delay(self, seconds):
        return self._robot.step(int(seconds * 1000))

    def time(self):
        return self._robot.getTime()

    def enable(self):
        # for key in self._motors:
        #     self._motors[key].enable()
        for key in self.devices:
            try:
                self.devices[key].enable()
            except:
                pass

    def disable(self):
        # for key in self._motors:
        #     self._motors[key].disable()
        for key in self.devices:
            try:
                self.devices[key].disable()
            except:
                pass
