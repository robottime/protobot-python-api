from protobot.webots.motor import Motor
from controller import Robot as WbRobot

__metaclass__ = type


class Robot():
    def __init__(self):
        self._robot = WbRobot()
        self._motors = {}

    def add_motor(self, name, reduction=1):
        self._motors[name] = Motor(self._robot.getMotor(name), reduction)
        return self._motors[name]

    def status(self):
        status = {'motors': []}
        if len(self._motors) > 0:
            print('Motors:')
        for key in self._motors:
            stat = self._motors[key].status()
            status['motors'].append({key: stat})
            print_str = 'Disabled'
            if stat['enable']:
                print_str = 'In ' + stat['mode'] + ' mode'
            print('  {}: {}'.format(key, print_str))
        return status

    def motor(self, name):
        return self._motors.get(name, None)

    def delay(self, seconds):
        self._robot.step(int(seconds * 1000))

    def time(self):
        return self._robot.getTime()

    def enable(self):
        for key in self._motors:
            self._motors[key].enable()

    def disable(self):
        for key in self._motors:
            self._motors[key].disable()
