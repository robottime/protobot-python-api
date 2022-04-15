try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping
import logging
import threading

import socket
import time

logger = logging.getLogger(__name__)

class Network(MutableMapping):
    def __init__(self):
        self.socket = socket.socket()
        self.host = '192.168.31.174'
        self.port = 9109
        self.nodes = {}
        self.subscribers = {}
        self.send_lock = threading.Lock()
        self._running = True
        self.read_lock = threading.Lock()
        self.read_thread = threading.Thread(
            target=self._rx_thread,
            args=(self.socket,),
            name=f'sock.notifier',
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
        if 'host' in kwargs:
            self.host = kwargs['host']
        if 'port' in kwargs:
            self.port = kwargs['port']
        self.socket.connect((self.host, self.port))
        self.read_thread.start()
        return self
        
    def disconnect(self):
        self._running = False
        self.read_thread.join(5)
        self.socket.close()
    
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
        
        with self.send_lock:
            rtr = 1 if remote else 0
            req = bytes([0x71, can_id >> 5, can_id & 0x1F, rtr << 4 | len(data)])
            req += data
            self.socket.send(req)
    
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

    def _rx_thread(self, sock) -> None:
        new = False
        can_id = 0
        can_data = b''
        ts = 0
        try:
            while self._running:
                if new:
                    with self.read_lock:
                        self.notify(can_id, can_data, ts)
                res_bit = sock.recv(1)
                if ord(res_bit) == 0x73:
                    header = list(sock.recv(3))
                    node_id = header[0]
                    cmd_id = header[1]
                    flag = header[2]
                    len = flag & 0x0f
                    can_id = node_id << 5 | cmd_id
                    can_data = sock.recv(len)
                    ts = time.time()
                    new = True
                else:
                    new = False

        except Exception as exc:
            logger.info("suppressed exception: %s", exc)
