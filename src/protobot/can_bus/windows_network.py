try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping
import logging
import threading

try:
    import candle_driver as can
except ImportError:
    can = None

logger = logging.getLogger(__name__)

class Network(MutableMapping):
    def __init__(self):
        self.device = can.list_devices()[0]
        self.channel = self.device.channel(0)
        self.notifier = None
        self.nodes = {}
        self.subscribers = {}
        self.send_lock = threading.Lock()
        self._running = True
        self.read_lock = threading.Lock()
        self.read_thread = threading.Thread(
            target=self._rx_thread,
            args=(self.channel,),
            name=f'can.notifier',
        )
        self.read_thread.daemon = True
    
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
        bitrate = 1000000
        if 'bitrate' in kwargs:
            bitrate = kwargs['bitrate']
        if not self.device.open():
            raise IOError("Failed to open can bus. Maybe can bus is in use.")
        self.channel.set_bitrate(bitrate)
        if not self.channel.start():
            raise IOError("Failed to open can bus. Maybe can bus is in use.")
        self.read_thread.start()
        logger.info('Connected to "%s"', self.device.name())
        return self
        
    def disconnect(self):
        self._running = False
        self.read_thread.join(5)
        self.channel.stop()
        self.device.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        self.disconnect()
    
    def add_node(self, node):
        self[node.id] = node
        return node

    def send_message(self, can_id, data, remote=False):
        
        with self.send_lock:
            rtr = 0
            if remote:
                rtr = can.CANDLE_ID_RTR
            self.channel.write(can_id | rtr, data)
    
    def notify(self, can_id, data, timestamp):
        if can_id in self.subscribers:
            callbacks = self.subscribers[can_id]
            for callback in callbacks:
                callback(can_id, data, timestamp)
    
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

    def _rx_thread(self, channel) -> None:
        new = False
        can_id = 0
        can_data = b''
        ts = 0
        try:
            while self._running:
                if new:
                    with self.read_lock:
                        self.notify(can_id, can_data, ts)
                try:
                    _frame_type, _can_id, _can_data, _, _ts = channel.read(1000)
                    if _frame_type == can.CANDLE_FRAMETYPE_RECEIVE:
                        can_id = _can_id
                        can_data = _can_data
                        ts = _ts
                        new = True
                    else:
                        new = False
                except:
                    new = False

        except Exception as exc:  # pylint: disable=broad-except
            logger.info("suppressed exception: %s", exc)
   