from protobot.can_bus.protocols.motor_protocol import MotorProtocol
from protobot.can_bus.protocols.message_queue import MessageQueue
from math import pi, fabs

class Motor():

  POSITION_MODE = 3
  VELOCITY_MODE = 2

  def __init__(self, manager, can_id, reduction = 1):
    self._protocol = MotorProtocol(manager, can_id)
    self._protocol.bind_callback(MotorProtocol.GET_ENCODER_EST_CMD_ID, self._encoder_cb)
    self._reduction = reduction
    self._factor = reduction / 2.0 / pi
    self._enable = False
    self._maxVel = 60.0
    self._recent_vel_lim = 0
    self._mode = Motor.POSITION_MODE
    self._pos_mq = MessageQueue()
    self._vel_mq = MessageQueue()
    self._protocol.start()

  
  def __del__(self):
    self._protocol.stop()

  def status(self):
    return {
      'mode': 'position' if self._mode == Motor.POSITION_MODE else 'velocity',
      'enable': self._enable
    }

  def _encoder_cb(self, pos, vel):
    self._pos_mq.call(pos / self._factor)
    self._vel_mq.call(vel / self._factor)

  def position_mode(self, type = 3):
    if self._enable:
      print('Failed: disable motor before setting mode.')
      return
    self._protocol.set_controller_modes(control_mode=3, input_mode=type)
    self._mode = Motor.POSITION_MODE

  def velocity_mode(self, type = 1):
    if self._enable:
      print('Failed: disable motor before setting mode.')
      return
    self._protocol.set_velocity_limit(self._maxVel)
    self._recent_vel_lim = self._maxVel
    self._protocol.set_controller_modes(control_mode=2, input_mode=type)
    self._mode = Motor.VELOCITY_MODE

  def set_pos(self, pos, max_vel = 20):
    if self._mode != Motor.POSITION_MODE:
      print('Failed: only set pos in position mode.')
      return
    vel_lim = min(self._maxVel, fabs(max_vel * self._factor))
    if self._recent_vel_lim != vel_lim:
      self._protocol.set_velocity_limit(vel_lim)
      self._recent_vel_lim = vel_lim
    self._protocol.set_input_pos(pos * self._factor)

  def set_vel(self, vel):
    if self._mode != Motor.VELOCITY_MODE:
      print('Failed: only set vel in velocity mode.')
      return
    self._protocol.set_input_vel(vel * self._factor)

  def get_pos(self, timeout = 1):
    self._protocol.get_encoder_estimate()
    return self._pos_mq.get_data(timeout)

  def request_pos(self, callback):
    self._protocol.get_encoder_estimate()
    self._pos_mq.append_cb(callback)

  def get_vel(self, timeout = 1):
    self._protocol.get_encoder_estimate()
    return self._vel_mq.get_data(timeout)

  def request_vel(self, callback):
    self._protocol.get_encoder_estimate()
    self._vel_mq.append_cb(callback)
  
  def enable(self):
    self._protocol.set_axis_request_state(8)
    self._enable = True

  def disable(self):
    self._protocol.set_axis_request_state(1)
    self._enable = False

  def save_configuration(self):
    self._protocol.save_configuration()
  
  def set_can_id(self, id):
    self._protocol.set_node_id(id)
  
  def estop(self):
    self._protocol.estop()
  
  def clear_errors(self):
    self._protocol.clear_errors()
  
  def reboot(self):
    self._protocol.reboot()
