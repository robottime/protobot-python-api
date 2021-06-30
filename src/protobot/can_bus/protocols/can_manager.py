import can

def filter_from_node_id(node_id):
    return {
        'can_id': node_id << 5,
        'can_mask': 0x7E0,
        'extended': False
    }

class CanManager():

    def __init__(self, channel = 'can0', bitrate = 250000):
        self._filters = []
        self._listeners = {}
        self._channel=channel
        self._bitrate = bitrate
        self._bus = can.ThreadSafeBus(
            bustype='socketcan',
            channel=self._channel,
            bitrate=self._bitrate,
            can_filters = self._filters
        )
        self._notifier = can.Notifier(self._bus, [self._message_listener])

    def _message_listener(self, msg):
        node_id = (msg.arbitration_id & 0x7E0) >> 5
        command_id = msg.arbitration_id & 0x1F
        listener = self._listeners.get(node_id, None)
        if listener:
            listener(command_id, msg.data)

    def register_can_listener(self, node_id, listener):
        filter = filter_from_node_id(node_id)
        
        if filter not in self._filters:
            self._filters.append(filter)
            self._bus.set_filters(self._filters)
        self._listeners[node_id] = listener

    def deregister_can_listener(self, node_id):
        filter = filter_from_node_id(node_id)
        if filter in self._filters:
            self._filters.remove(filter)
            self._bus.set_filters(self._filters)
        self._listeners.pop(node_id, None)

    def send_can_msg(self, node_id, command_id, data = None, is_remote_frame = False):
        arbitration_id = node_id << 5 | command_id
        try:
            self._bus.send(can.Message(
                arbitration_id=arbitration_id,
                data = data,
                is_remote_frame=is_remote_frame,
                is_extended_id=False
            ))
        except:
            # self._bus.shutdown()
            # self._bus = can.ThreadSafeBus(
            #     bustype='socketcan',
            #     channel=self._channel,
            #     bitrate=self._bitrate,
            #     can_filters = self._filters
            # )
            return False
        else:
            return True

    def __del__(self):
        if self._bus:
            self._bus.shutdown()

