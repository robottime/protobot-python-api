__metaclass__ = type

class CanProtocol():
    def __init__(self, manager, node_id):
        self._manager = manager
        self._node_id = node_id
        self._handler_dict = {}
        self._callback_dict = {}

    def start(self):
        self._manager.register_can_listener(self._node_id, self.listener)
        return self
    
    def stop(self):
        self._manager.deregister_can_listener(self._node_id)

    @staticmethod
    def msg_handler(command_id):
        def wrapper(func):
            def inner_wrapper(protocol, data):
                try:
                    protocol._callback_dict[command_id](*func(protocol, data))
                except:
                    pass
            return inner_wrapper
        return wrapper

    def bind_callback(self, command_id, callback):
        self._callback_dict[command_id] = callback
    
    def listener(self, command_id, data):
        handler = self._handler_dict.get(command_id, None)
        if handler:
            handler(data)

    def send_data(self, command_id, data = None):
        self._manager.send_can_msg(
            node_id = self._node_id,
            command_id = command_id,
            data = data,
            is_remote_frame = False
        )
    
    def send_remote_frame(self, command_id):
        self._manager.send_can_msg(
            node_id = self._node_id,
            command_id = command_id,
            is_remote_frame = True
        )
