from abc import ABCMeta, abstractmethod
from typing import Iterable
from six import add_metaclass, wraps
from time import time
import numpy as np


@add_metaclass(ABCMeta)
class NodeFactory(object):
    @abstractmethod
    def get_node(self, network, node_id, *args, **kwargs):
        return None

class Node(object):
    def __init__(self, node_id):
        self.id = node_id
        self.network = None

    def associate_network(self, network):
        self.network = network

    def remove_network(self):
        for command in range(32):
            self.network.unsubscribe(self.can_id(command))
        self.network = None
    
    def can_id(self, command):
        return self.id << 5 | command

    @staticmethod
    def get_func_decorator(command, format, stamped = False):
        def wrapper(func):
            @wraps(func)
            def inner_wrapper(node, timeout = 0):
                if node.network is None:
                    raise RuntimeError('A network is required to get data')

                def on_get_data(can_id, data, timestamp):
                    on_get_data.updated = True
                    on_get_data.data = data
                    on_get_data.timestamp = timestamp
                on_get_data.updated = False
                on_get_data.data = None
                on_get_data.timestamp = None

                node.network.subscribe(node.can_id(command), on_get_data)
                node.network.send_message(node.can_id(command), b'', True)

                t_start = time()
                while timeout == 0 or time() - t_start < timeout:
                    if on_get_data.updated:
                        node.network.unsubscribe(node.can_id(command), on_get_data)
                        try:
                            data_tuple = np.frombuffer(on_get_data.data, dtype=format)[0]
                        except Exception as e:
                            raise RuntimeError('Getting data with unknown format.', e)
                        if isinstance(data_tuple, np.void):
                            data_tuple = tuple(data_tuple)
                        else:
                            data_tuple = (data_tuple, )
                        if stamped:
                            return func(node, on_get_data.timestamp, *data_tuple)
                        else:
                            return func(node, *data_tuple)
                node.network.unsubscribe(node.can_id(command), on_get_data)
                return None
            return inner_wrapper
        return wrapper

    @staticmethod
    def sync_func_decorator(command, format, stamped = False):
        def wrapper(func):
            @wraps(func)
            def inner_wrapper(node, callback):
                if node.network is None:
                    raise RuntimeError('A network is required to sync data')

                def on_sync_data(can_id, data, timestamp):
                    try:
                        data_tuple = np.frombuffer(data, dtype=format)[0]
                    except Exception as e:
                        raise RuntimeError('Getting data with unknown format.', e)
                    if isinstance(data_tuple, Iterable):
                        data_tuple = tuple(data_tuple)
                    else:
                        data_tuple = (data_tuple, )
                    if stamped:
                        callback(timestamp, *data_tuple)
                    else:
                        callback(*data_tuple)
                    node.network.unsubscribe(node.can_id(command), on_sync_data)

                node.network.subscribe(node.can_id(command), on_sync_data)
                node.network.send_message(node.can_id(command), b'', True)

                return func(node, on_sync_data)
            return inner_wrapper
        return wrapper
    
    @staticmethod
    def send_func_decorator(command, format = None, remote = False):
        def wrapper(func):
            @wraps(func)
            def inner_wrapper(node, *args, **kwargs):
                if node.network is None:
                    raise RuntimeError('A network is required to send data')
                if format is None:
                    node.network.send_message(node.can_id(command), b'', remote)
                else:
                    try:
                        data = func(node, *args, **kwargs)
                        if isinstance(data, Iterable):
                            data = tuple(data)
                        else:
                            data = (data, )
                        data_bytes = np.array([data], dtype=format).tobytes()
                    except Exception as e:
                        raise RuntimeError('Sending data with unknown format.', e)
                    node.network.send_message(node.can_id(command), data_bytes, remote)
            return inner_wrapper
        return wrapper
    