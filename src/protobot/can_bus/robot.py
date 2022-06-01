import sys
from .network import Network as LinuxNetwork
from .windows_network import Network as WindowNetwork
from .socket_network import Network as SocketNetwork
from .nodes import NodeFactory
import time

class Robot(object):
    def __init__(self, channel = 'can0', bitrate = 1000000, bustype = 'socketcan', **kwargs):
        self.network = None
        if 'host' in kwargs:
            self.network = SocketNetwork()
        else:
            if sys.platform == 'win32':
                self.network = WindowNetwork()
            elif sys.platform.startswith('linux'):
                self.network = LinuxNetwork()
            else:
                raise OSError('Your system is not supported.')
        self.network.connect(channel = channel, bitrate = bitrate, bustype = bustype, **kwargs)
        self.devices = {}
        self.node_id = {}
        self._init_time = time.time()
    
    def __del__(self):
        self.network.disconnect()

    def add_device(self, name, factory, node_id, *args, **kwargs):
        if not isinstance(factory, NodeFactory):
            raise RuntimeError('unknown factory to init device')
        self.node_id[name] = node_id
        self.devices[name] = factory.get_node(network = self.network, node_id = node_id, *args, **kwargs)
        return self.devices[name]

    def device(self, name):
        return self.devices.get(name, None)
    
    def device_id(self, name):
        return self.node_id.get(name, None)
    
    def remove_device(self, name):
        try:
            del self.network[self.node_id[name]]
        except:
            print(self.node_id[name])
            pass
    
    def delay(self, seconds):
        time.sleep(seconds)
    
    def time(self):
        return time.time() - self._init_time
    
    def enable(self):
        for key in self.devices:
            try:
                self.devices[key].enable()
            except:
                pass
    
    def disable(self):
        for key in self.devices:
            try:
                self.devices[key].disable()
            except:
                pass