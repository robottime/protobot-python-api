from protobot.can_bus.protocols.can_protocol import CanProtocol
import struct

class BatteryProtocol(CanProtocol):
    STATUS_CMD_ID = 0x00
    LED_SET_CMD_ID = 0x01
    GYRO_DATA_CMD_ID = 0x02

    def __init__(self, manager, node_id):
        super(BatteryProtocol, self).__init__(manager, node_id)
        self._handler_dict = {
            BatteryProtocol.STATUS_CMD_ID: self.handle_status,
            BatteryProtocol.GYRO_DATA_CMD_ID: self.handle_gyro_data,
        }

    @CanProtocol.msg_handler(STATUS_CMD_ID)
    def handle_status(self, data):
        return struct.unpack('<fB', data)

    @CanProtocol.msg_handler(GYRO_DATA_CMD_ID)
    def handle_gyro_data(self, data):
        return struct.unpack('<hhhh', data)


    def set_led(self, type, period, color):
        self.send_data(
            BatteryProtocol.LED_SET_CMD_ID,
            data = struct.pack('BBBBB', type, period*10, color[0], color[1], color[2])
        )
