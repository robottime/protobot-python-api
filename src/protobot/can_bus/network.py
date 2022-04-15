try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping
import logging
import threading
import struct

try:
    import can
    from can import Listener
    from can import CanError
except ImportError:
    can = None
    Listener = object
    CanError = Exception

logger = logging.getLogger(__name__)

class Network(MutableMapping):
    def __init__(self, bus = None):
        self.bus = bus
        self.scanner = NodeScanner(self)
        self.listeners = [MessageListener(self)]
        self.notifier = None
        self.nodes = {}
        self.subscribers = {}
        self.send_lock = threading.Lock()
    
    def subscribe(self, can_id, callback):
        self.subscribers.setdefault(can_id, list())
        if callback not in self.subscribers[can_id]:
            self.subscribers[can_id].append(callback)
    
    def unsubscribe(self, can_id, callback=None):
        if callback is None:
            try:
                del self.subscribers[can_id]
            except:
                pass
        else:
            self.subscribers[can_id].remove(callback)
    
    def connect(self, *args, **kwargs):
        if 'bustype' not in kwargs:
            kwargs['bustype'] = 'socketcan'
        if 'channel' not in kwargs:
            kwargs['channel'] = 'can0'
        if 'bitrate' not in kwargs:
            kwargs['bitrate'] = 1000000
        self.bus = can.interface.Bus(*args, **kwargs)
        logger.info('Connected to "%s"', self.bus.channel_info)
        self.notifier = can.Notifier(self.bus, self.listeners, 1)
        return self
        
    def disconnect(self):
        if self.notifier is not None:
            self.notifier.stop()
        if self.bus is not None:
            self.bus.shutdown()
        self.bus = None
        self.check()
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        self.disconnect()
    
    def __del__(self):
        self.disconnect()
        
    def add_node(self, node):
        self[node.id] = node
        return node

    def send_message(self, can_id, data, remote=False):
        if not self.bus:
            raise RuntimeError('Not connected to CAN bus')
        msg = can.Message(is_extended_id=False, 
                          arbitration_id=can_id, 
                          data=data,
                          is_remote_frame=remote)
        with self.send_lock:
            self.bus.send(msg)
        self.check()
    
    def notify(self, can_id, data, timestamp):
        if can_id in self.subscribers:
            callbacks = self.subscribers[can_id]
            for callback in callbacks:
                callback(can_id, data, timestamp)
        self.scanner.on_message_received(can_id, data)

    def check(self):
        if self.notifier is not None:
            exc = self.notifier.exception
            if exc is not None:
                logger.error('An error has caused receiving of messages to stop')
                raise exc
    
    def __getitem__(self, node_id):
        return self.nodes[node_id]
    
    def __setitem__(self, node_id, node):
        assert node_id == node.id
        self.nodes[node_id] = node
        node.associate_network(self)
    
    def __delitem__(self, node_id):
        self.nodes[node_id].remove_network()
        del self.nodes[node_id]
    
    def __iter__(self):
        return iter(self.nodes)
    
    def __len__(self):
        return len(self.nodes)

class MessageListener(Listener):
    def __init__(self, network):
        self.network = network
    
    def on_message_received(self, msg):
        if msg.is_error_frame or msg.is_remote_frame:
            return
        
        try:
            self.network.notify(msg.arbitration_id, msg.data, msg.timestamp)
        except Exception as e:
            logger.error(str(e))

class NodeScanner(object):
    def __init__(self, network = None):
        self.network = network
        self.nodes = {}
    
    def on_message_received(self, can_id, data):
        node_id = (can_id & 0x7E0)>>5
        command = can_id & 0x1F
        if node_id not in self.nodes and node_id != 0 and command == 0x01:
            mver, sver, dID = struct.unpack('<HHI', data)
            self.nodes[node_id] = dID
    
    def reset(self):
        self.nodes = []
    
    def search(self, limit=64):
        if self.network is None:
            raise RuntimeError('A network is required to do active scanning')
        for node_id in range(limit):
            self.network.send_message(node_id & 0x01, None, remote = True)
