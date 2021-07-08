from .node import Node, NodeFactory
from math import pi

class StepperBoardFactory(NodeFactory):
    def get_node(self, network, node_id = 0x22, reduction = 10):
        stepper_board = StepperBoard(node_id, reduction)
        network[node_id] = stepper_board
        return stepper_board
  
class StepperBoard(Node):
    CMD_GET_API_VERSION = 0x01
    CMD_SET_NODE_ID = 0x02
    CMD_SET_SUBDIVISION = 0x03
    CMD_SET_VEL_ACC_LIMIT = 0x04;
    CMD_ENABLE = 0x05;
    CMD_DISABLE = 0x06;
    CMD_STOP = 0x07;
    CMD_SET_POSITION = 0x08;
    CMD_SET_VELOCITY = 0x09;
    CMD_GET_POSITION = 0x0a;
    CMD_GET_VELOCITY = 0x0b;

    def __init__(self, node_id, reduction = 10):
        super(StepperBoard, self).__init__(node_id)
        self._reduction = reduction
        self._set_subdivision(8)

    def _set_subdivision(self, subdivision):
        if subdivision in [8, 16, 32, 64]:
            self._subdivision = subdivision
            self._factor = 200.0 * subdivision * self._reduction / 2.0 / pi
            return True
        return False

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
    
    @Node.send_func_decorator(CMD_SET_SUBDIVISION, '<B')
    def set_subdivision(self, subdivision):
        if self._set_subdivision(subdivision):
            return subdivision
        else:
            raise ValueError('wrong subdivision value, use a value in [8, 16, 32, 64]')

    @Node.send_func_decorator(CMD_SET_VEL_ACC_LIMIT, '<f4,<f4')
    def set_vel_acc_limit(self, max_vel, acc = None):
        if acc is None:
            acc = max_vel * 4.0
        return (max_vel * self._factor, acc * self._factor)

    @Node.send_func_decorator(CMD_ENABLE)
    def enable(self):
        pass

    @Node.send_func_decorator(CMD_DISABLE)
    def disable(self):
        pass

    @Node.send_func_decorator(CMD_STOP)
    def stop(self):
        pass

    @Node.send_func_decorator(CMD_SET_POSITION, '<i4')
    def set_pos(self, position):
        return int(position * self._factor)

    @Node.send_func_decorator(CMD_SET_VELOCITY, '<f4')
    def set_vel(self, velocity):
        return velocity * self._factor

    @Node.get_func_decorator(CMD_GET_POSITION, '<i4')
    def get_pos(self, pos):
        return pos / self._factor

    @Node.get_func_decorator(CMD_GET_VELOCITY, '<f4')
    def get_vel(self, vel):
        return vel / self._factor
