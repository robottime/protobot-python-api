from protobot.can_bus.protocols.motor_accessory_protocol import MotorAccessoryProtocol
from protobot.can_bus.protocols.message_queue import MessageQueue
from time import time
from math import pi


class Accessory():

    LED_TYPE_STATIC = 0
    LED_TYPE_BLINK = 1
    LED_TYPE_RUNNING = 2

    def __init__(self, manager, can_id):
        self._protocol = MotorAccessoryProtocol(manager, can_id)
        self._protocol.bind_callback(
            MotorAccessoryProtocol.GYRO_DATA_CMD_ID, self._gyro_cb)
        self._gyro_mq = MessageQueue()
        self._protocol.start()

    def __del__(self):
        self._protocol.stop()

    def set_led(self, type, period, rgb):
        return self._protocol.set_led(type, period, rgb)

    def set_servo(self, pos):
        return self._protocol.set_servo_pos(pos)

    def _gyro_cb(self, roll, pitch, yaw, temp):
        self._gyro_mq.call([roll/32768*pi, pitch/32768*pi, yaw/32768*pi])

    def get_gyro(self, timeout=1):
        return self._gyro_mq.get_data(timeout)

    def request_gyro(self, callback):
        self._gyro_mq.append_cb(callback)
