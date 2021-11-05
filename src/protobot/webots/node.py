from abc import ABCMeta, abstractmethod
from six import add_metaclass


@add_metaclass(ABCMeta)
class NodeFactory(object):
    @abstractmethod
    def get_node(self, robot, device_name, *args, **kwargs):
        return None
