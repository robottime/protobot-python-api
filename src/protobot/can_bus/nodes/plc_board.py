from .node import Node, NodeFactory
import numpy as np

class PlcBoardFactory(NodeFactory):
    def get_node(self, network, node_id = 0x20):
        plc_board = PlcBoard(node_id)
        network[node_id] = plc_board
        return plc_board
  
class PlcBoard(Node):
    CMD_GET_API_VERSION = 0x01
    CMD_HEARTBEAT = 0x02
    CMD_GET_IO = 0x03
    CMD_SET_12V_IO = 0x04
    CMD_SET_6V_IO = 0x05

    def __init__(self, node_id):
        super(PlcBoard, self).__init__(node_id)
        self._status = {
            'input': 0,
            'output': 0,
            'output_12V': 0,
            'output_6V': 0,
            'UUID': 0,
            'timestamp': 0
        }

    @Node.get_func_decorator(CMD_GET_API_VERSION, '<u2,<u2,<u4')
    def get_api_ver(self, main_ver, sub_ver, uuid):
        return {
            'device_uuid': uuid,
            'main_version': main_ver,
            'sub_version': sub_ver,
        }

    def associate_network(self, network):
        super(PlcBoard, self).associate_network(network)
        self.network.subscribe(self.can_id(self.CMD_HEARTBEAT), self.heartbeat_callback)
    
    def heartbeat_callback(self, can_id, data, timestamp):
        in_io,out_io,out_12v_io,out_6v_io,_,_,_,mtype = list(np.frombuffer(data, dtype='<B'))
        self._status.update({
            'input': int(in_io),
            'output': int(out_io),
            'output_12V': int(out_12v_io),
            'output_6V': int(out_6v_io),
            'UUID': int(mtype),
            'timestamp': timestamp
        })

    def status(self):
        return self._status

    @Node.get_func_decorator(CMD_GET_IO, '<u2, <u2, <u2, <u2')
    def get_io(self, io1, io2, io3, io4):
        return (io1, io2, io3, io4)

    @Node.send_func_decorator(CMD_SET_12V_IO, '<B, <B, <B')
    def set_12v_io(self, io1, io2, io3):
        return (io1, io2, io3)
    
    @Node.send_func_decorator(CMD_SET_6V_IO, '<B, <B, <B')
    def set_6v_io(self, io1, io2, io3):
        return (io1, io2, io3)
