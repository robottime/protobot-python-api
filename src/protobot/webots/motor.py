from math import pi

class Motor():

  POSITION_MODE = 0
  VELOCITY_MODE = 1

  def __init__(self, webots_motor, reduction = 1):
    self._motor = webots_motor
    self._reduction = reduction
    self._motor.setAvailableTorque(0)
    self._enable = False
    self._maxVel = 50 * pi / reduction
    self._maxTorque = 0.5 * reduction
    self._mode = Motor.POSITION_MODE
  
  def status(self):
    return {
      'mode': 'position' if self._mode == Motor.POSITION_MODE else 'velocity',
      'enable': self._enable
    }

  def position_mode(self):
    if self._enable:
      print('Failed: disable motor before setting mode.')
      return
    self._motor.setVelocity(0)
    self._mode = Motor.POSITION_MODE
  
  def velocity_mode(self):
    if self._enable:
      print('Failed: disable motor before setting mode.')
      return
    self._motor.setVelocity(0)
    self._motor.setPosition(float('+inf'))
    self._mode = Motor.VELOCITY_MODE

  def set_pos(self, pos, max_vel = 10):
    if self._mode != Motor.POSITION_MODE:
      print('Failed: only set pos in position mode.')
      return
    self._motor.setPosition(pos)
    self._motor.setVelocity(min(self._maxVel, max_vel))
  
  def get_pos(self):
    return self._motor.getTargetPosition()

  def set_vel(self, vel):
    if self._mode != Motor.VELOCITY_MODE:
      print('Failed: only set vel in velocity mode.')
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
    #self._motor.setAvailableTorque(0)
    self._enable = False


