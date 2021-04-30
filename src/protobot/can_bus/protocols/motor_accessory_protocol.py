from protobot.can_bus.protocols.can_protocol import CanProtocol
import struct


class MotorAccessoryProtocol(CanProtocol):
    GYRO_DATA_CMD_ID = 0x00
    SERVO_SET_CMD_ID = 0x01
    LED_SET_CMD_ID = 0x02

    def __init__(self, manager, node_id):
        super(MotorAccessoryProtocol, self).__init__(manager, node_id)
        self._handler_dict = {
            MotorAccessoryProtocol.GYRO_DATA_CMD_ID: self.handle_gyro_data,
        }

    @CanProtocol.msg_handler(GYRO_DATA_CMD_ID)
    def handle_gyro_data(self, data):
        return struct.unpack('<hhhh', data)

    def set_servo_pos(self, servo_pos):
        self.send_data(
            MotorAccessoryProtocol.SERVO_SET_CMD_ID,
            data=struct.pack('B', int(servo_pos * 0xff))
        )

    def set_led(self, type, period, color):
        self.send_data(
            MotorAccessoryProtocol.LED_SET_CMD_ID,
            data=struct.pack('BBBBB', type, period*10,
                             color[0], color[1], color[2])
        )
