import can

def filter_from_node_id(node_id):
    return {
        'can_id': node_id << 5,
        'can_mask': 0x7E0,
        'extended': False
    }

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

def test_listener(msg):
    print(msg)

class CanManager():
    __metaclass__ = Singleton

    def __init__(self, channel = 'can0', bitrate = 250000):
        self._filters = [
            #{'can_id': 0x00, 'can_mask': 0x7E0, 'extended': False}
        ]
        self._listeners = {}
        self._bus = can.ThreadSafeBus(
            bustype='socketcan',
            channel=channel,
            bitrate=bitrate,
            #can_filters = self._filters
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
        self._bus.send(can.Message(
            arbitration_id=arbitration_id,
            data = data,
            is_remote_frame=is_remote_frame,
            is_extended_id=False
        ))

    def __del__(self):
        if self._bus:
            self._bus.shutdown()

#can_manager = CanManager(channel='can0', bitrate=250000)
