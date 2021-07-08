from .node import Node, NodeFactory

class NanoBoardFactory(NodeFactory):
    def get_node(self, network, node_id = 0x21):
        nano_board = NanoBoard(node_id)
        network[node_id] = nano_board
        return nano_board
  
class NanoBoard(Node):
    CMD_GET_API_VERSION = 0x01
    CMD_SET_NODE_ID = 0x02
    CMD_SET_SERVO_POS = 0x03
    CMD_SET_PWM = 0x04

    @Node.get_func_decorator(CMD_GET_API_VERSION, '<u2,<u2,<u4')
    def get_api_ver(self, main_ver, sub_ver, uuid):
        return {
            'device_uuid': uuid,
            'main_version': main_ver,
            'sub_version': sub_ver,
        }

    @Node.send_func_decorator(CMD_SET_NODE_ID, '<B')
    def set_node_id(self, node_id):
        if node_id > 0 and node_id <= 0x3f:
            return node_id
        else:
            raise ValueError('wrong node_id value, use a value in (0, 0x3f]')
    
    
    @Node.send_func_decorator(CMD_SET_SERVO_POS, '<B')
    def set_servo_pos(self, servo_pos = 0.5):
        return (int(servo_pos * 255.0), )
    
    @Node.send_func_decorator(CMD_SET_PWM, '<B')
    def set_pwm(self, pwm = 0):
        return (int(pwm * 255.0), )