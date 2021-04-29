from protobot.can_bus.protocols.can_protocol import CanProtocol
import struct

class NanoProtocol(CanProtocol):
    SET_SERVO_CMD_ID = 0x00

    def __init__(self, manager, node_id):
        super(NanoProtocol, self).__init__(manager, node_id)

    def set_servo(self, servo_pos):
        data = int(servo_pos * 128 + 128)
        data = max(128, data)
        data = min(255, data)
        self.send_data(
            NanoProtocol.SET_SERVO_CMD_ID, 
            data = struct.pack('B', data)
        )