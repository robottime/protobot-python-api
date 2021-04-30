from protobot.can_bus.protocols.can_protocol import CanProtocol
import struct

class MotorProtocol(CanProtocol):
    CMD_GET_API_VERSION = 0x01
    CMD_ODRIVE_HEARTBEAT = 0x02
    CMD_ODRIVE_ESTOP = 0x03
    CMD_RESET_ODRIVE = 0x04
    CMD_CLEAR_ERRORS = 0x05
    CMD_SAVE_CONFIGURATION = 0x06
    CMD_SET_AXIS_NODE_ID = 0x07
    CMD_SET_AXIS_REQUESTED_STATE = 0x08
    CMD_GET_HARDWARE_STATUS = 0x09
    CMD_GET_MOTOR_STATUS = 0x0A
    CMD_GET_CONTROLLER_MODES = 0x0B
    CMD_SET_CONTROLLER_MODES = 0x0C
    CMD_GET_CONTROLLER_PID = 0x0D
    CMD_SET_CONTROLLER_PID = 0x0E
    CMD_GET_LIMITS = 0x0F
    CMD_SET_LIMITS = 0x10
    CMD_SET_INPUT_POS = 0x11
    CMD_SET_INPUT_VEL = 0x12
    CMD_SET_INPUT_TORQUE = 0x13

    def __init__(self, manager, node_id):
        super(MotorProtocol, self).__init__(manager, node_id)
        self._handler_dict = {
            MotorProtocol.CMD_ODRIVE_HEARTBEAT: self.handle_heartbeat,
            MotorProtocol.CMD_GET_API_VERSION: self.handle_api_version,
            MotorProtocol.CMD_GET_HARDWARE_STATUS: self.handle_hardware_status,
            MotorProtocol.CMD_GET_MOTOR_STATUS: self.handle_motor_status,
            MotorProtocol.CMD_GET_CONTROLLER_MODES: self.handle_controller_modes,
            MotorProtocol.CMD_GET_CONTROLLER_PID: self.handle_controller_pid,
            MotorProtocol.CMD_GET_LIMITS: self.handle_limits,
        }

    @CanProtocol.msg_handler(CMD_ODRIVE_HEARTBEAT)
    def handle_heartbeat(self, data):
        return struct.unpack('<BBBBBBBB', data)

    def request_api_version(self):
        self.send_remote_frame(MotorProtocol.CMD_GET_API_VERSION)

    @CanProtocol.msg_handler(CMD_GET_API_VERSION)
    def handle_api_version(self, data):
        return struct.unpack('<HHI', data)
    
    def estop(self):
        self.send_data(MotorProtocol.CMD_ODRIVE_ESTOP)
    
    def reset(self):
        self.send_data(MotorProtocol.CMD_RESET_ODRIVE)

    def clear_errors(self):
        self.send_data(MotorProtocol.CMD_CLEAR_ERRORS)

    def save_configuration(self):
        self.send_data(MotorProtocol.CMD_SAVE_CONFIGURATION)
    
    def set_axis_node_id(self, id, rate):
        self.send_data(
            MotorProtocol.CMD_SET_AXIS_NODE_ID,
            data = struct.pack('<II', id, rate)
        )
    
    def set_axis_request_state(self, state):
        self.send_data(
            MotorProtocol.CMD_SET_AXIS_REQUESTED_STATE,
            data = struct.pack('<I', state)
        )
    
    def request_hardware_status(self):
        self.send_remote_frame(MotorProtocol.CMD_GET_HARDWARE_STATUS)
    
    @CanProtocol.msg_handler(CMD_GET_HARDWARE_STATUS)
    def handle_hardware_status(self, data):
        return struct.unpack('<ff', data)
    
    def request_motor_status(self):
        self.send_remote_frame(MotorProtocol.CMD_GET_MOTOR_STATUS)
    
    @CanProtocol.msg_handler(CMD_GET_MOTOR_STATUS)
    def handle_motor_status(self, data):
        return struct.unpack('<fee', data)

    def request_controller_modes(self):
        self.send_remote_frame(MotorProtocol.CMD_GET_CONTROLLER_MODES)
    
    @CanProtocol.msg_handler(CMD_GET_CONTROLLER_MODES)
    def handle_controller_modes(self, data):
        cmode, imode = struct.unpack('<BB', data[0:2])
        if imode == 5:
            return [cmode, imode]+list(struct.unpack('<eee', data[2:8]))
        elif imode in [2,3,6,7]:
            return [cmode, imode]+list(struct.unpack('f', data[2:6]))
        else:
            return [cmode, imode]
    
    def set_controller_modes(self, control_mode, input_mode, *args):
        if input_mode == 5 and len(args) == 3:
            self.send_data(
                MotorProtocol.CMD_SET_CONTROLLER_MODES,
                data = struct.pack('<BBeee', control_mode, input_mode, *args)
            )
        elif input_mode in [2,3,6,7] and len(args) == 1:
            self.send_data(
                MotorProtocol.CMD_SET_CONTROLLER_MODES,
                data = struct.pack('<BBf', control_mode, input_mode, *args)
            )
        else:
            self.send_data(
                MotorProtocol.CMD_SET_CONTROLLER_MODES,
                data = struct.pack('<BB', control_mode, input_mode)
            )
    
    def request_controller_pid(self):
        self.send_remote_frame(MotorProtocol.CMD_GET_CONTROLLER_PID)
    
    @CanProtocol.msg_handler(CMD_GET_CONTROLLER_PID)
    def handle_controller_pid(self, data):
        return struct.unpack('<fee', data)
    
    def set_controller_pid(self, pos_p, vel_p, vel_i):
        self.send_data(
            MotorProtocol.CMD_SET_CONTROLLER_PID,
            data = struct.pack('<fee', pos_p, vel_p, vel_i)
        )
    
    def request_limits(self):
        self.send_remote_frame(MotorProtocol.CMD_GET_LIMITS)
    
    @CanProtocol.msg_handler(CMD_GET_LIMITS)
    def handle_limits(self, data):
        return struct.unpack('ff', data)

    def set_limits(self, vel_limit, torque_limit):
        self.send_data(
            MotorProtocol.CMD_SET_LIMITS,
            data = struct.pack('<ff', vel_limit, torque_limit)
        )
    
    def set_input_pos(self, pos, vel_ff, torque_ff):
        self.send_data(
            MotorProtocol.CMD_SET_INPUT_POS,
            data = struct.pack('<fee', pos, vel_ff, torque_ff)
        )
    
    def set_input_vel(self, vel, torque_ff):
        self.send_data(
            MotorProtocol.CMD_SET_INPUT_VEL,
            data = struct.pack('<ff', vel, torque_ff)
        )
    
    def set_input_torque(self, torque):
        self.send_data(
            MotorProtocol.CMD_SET_INPUT_TORQUE,
            data = struct.pack('f', torque)
        )
