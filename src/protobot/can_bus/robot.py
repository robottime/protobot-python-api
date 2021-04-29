from protobot.can_bus.protocols.can_manager import CanManager
from protobot.can_bus.motor import Motor
from protobot.can_bus.battery import Battery
from protobot.can_bus.accessory import Accessory
from time import sleep, time

__metaclass__ = type

class Robot():
  def __init__(self, bus = 'can0', bitrate = 250000):
    self._can_manager = CanManager(channel=bus, bitrate=bitrate)
    self._motors = {}
    self._battery = None
    self._devices = {}
    self._start_time = time()

  def set_battery(self, can_id = 0x20):
    self._battery = Battery(self._can_manager, can_id)
    return self._battery

  def battery(self):
    return self._battery

  def add_device(self, name, can_id = 0x02, cls = Accessory, *args, **kwargs):
    self._devices[name] = cls(self._can_manager, can_id, *args, **kwargs)
    return self._devices[name]

  def add_motor(self, name, can_id = 0x10, reduction = 1):
    self._motors[name] = Motor(self._can_manager, can_id, reduction)
    return self._motors[name]

  def motor(self, name):
    return self._motors.get(name, None)

  def device(self, name):
    return self._devices.get(name, None)

  def status(self):
    status = {'motors': []}
    print('Motors:')
    for key in self._motors:
      stat = self._motors[key].status()
      status['motors'].append({key: stat})
      print_str = 'Disabled'
      if stat['enable']:
        print_str = 'In ' + stat['mode'] + ' mode'
      print('  {}: {}'.format(key, print_str))
    return status

  def delay(self, seconds):
    sleep(seconds)

  def time(self):
    return time() - self._start_time
  
  def enable(self):
    for key in self._motors:
      self._motors[key].enable()
    
  def disable(self):
    for key in self._motors:
      self._motors[key].disable()
