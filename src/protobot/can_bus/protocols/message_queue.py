from time import time

class MessageQueue():
  def __init__(self):
    self._queue = []
    self._data = None
    self._updated = False

  def call(self, data):
    if len(self._queue) > 0:
      self._queue.pop(0)(data)

  def get_data(self, timeout = 1):
    self._queue.append(self._set_data)
    t0 = time()
    while time() - t0 < timeout:
      if self._updated:
        self._updated = False
        return self._data
    self._updated = False
    self._queue.pop()
    return None

  def append_cb(self, callback):
    self._queue.append(callback)

  def _set_data(self, data):
    self._data = data
    self._updated = True
