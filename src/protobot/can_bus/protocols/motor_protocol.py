from protobot.can_bus.protocols.can_protocol import CanProtocol
import struct

class MotorProtocol(CanProtocol):
    HEARTBEAT_CMD_ID = 0x01
    ESTOP_CMD_ID = 0x02
    GET_MOTOR_ERR_CMD_ID = 0x03
    GET_ENCODER_ERR_CMD_ID = 0x04
    SET_NODE_ID_CMD_ID = 0x06
    SET_AXIS_REQ_STATE_CMD_ID = 0x07
    GET_ENCODER_EST_CMD_ID = 0x09
    GET_ENCODER_CNT_CMD_ID = 0x0A
    SET_CONTROL_MODE_CMD_ID = 0x0B
    SET_INPUT_POS_CMD_ID = 0x0C
    SET_INPUT_VEL_CMD_ID = 0x0D
    SET_INPUT_TORQ_CMD_ID = 0x0E
    SET_VEL_LIM_CMD_ID = 0x0F
    SET_TRAJ_VEL_LIM_CMD_ID = 0x11
    SET_TRAJ_ACC_LIM_CMD_ID = 0x12
    SET_TRAJ_INERTIA_CMD_ID = 0x13
    GET_IQ_CMD_ID = 0x14
    REBOOT_CMD_ID = 0x16
    GET_VBUS_VOLT_CMD_ID = 0x17
    CLEAR_ERR_CMD_ID = 0x18
    SAVE_CONFIG_CMD_ID = 0x19

    def __init__(self, manager, node_id):
        super(MotorProtocol, self).__init__(manager, node_id)
        self._handler_dict = {
            MotorProtocol.HEARTBEAT_CMD_ID: self.handle_heartbeat,
            MotorProtocol.GET_MOTOR_ERR_CMD_ID: self.handle_motor_error,
            MotorProtocol.GET_ENCODER_ERR_CMD_ID: self.handle_encoder_error,
            MotorProtocol.GET_ENCODER_EST_CMD_ID: self.handle_encoder_estimate,
            MotorProtocol.GET_ENCODER_CNT_CMD_ID: self.handle_encoder_count,
            MotorProtocol.GET_IQ_CMD_ID: self.handle_iq,
            MotorProtocol.GET_VBUS_VOLT_CMD_ID: self.handle_vbus_voltage
        }

    @CanProtocol.msg_handler(HEARTBEAT_CMD_ID)
    def handle_heartbeat(self, data):
        return struct.unpack('<II', data)

    def estop(self):
        self.send_data(MotorProtocol.ESTOP_CMD_ID)

    def get_motor_error(self):
        self.send_remote_frame(MotorProtocol.GET_MOTOR_ERR_CMD_ID)

    @CanProtocol.msg_handler(GET_MOTOR_ERR_CMD_ID)
    def handle_motor_error(self, data):
        return struct.unpack('<I', data[0:4])

    def get_encoder_error(self):
        self.send_remote_frame(MotorProtocol.GET_ENCODER_ERR_CMD_ID)

    @CanProtocol.msg_handler(GET_ENCODER_ERR_CMD_ID)
    def handle_encoder_error(self, data):
        return struct.unpack('<I', data[0:4])

    def set_node_id(self, id):
        self.send_data(
            MotorProtocol.SET_NODE_ID_CMD_ID, 
            data = struct.pack('<I', id)
        )

    def set_axis_request_state(self, state):
        self.send_data(
            MotorProtocol.SET_AXIS_REQ_STATE_CMD_ID, 
            data = struct.pack('<I', state)
        )

    def get_encoder_estimate(self):
        self.send_remote_frame(MotorProtocol.GET_ENCODER_EST_CMD_ID)

    @CanProtocol.msg_handler(GET_ENCODER_EST_CMD_ID)
    def handle_encoder_estimate(self, data):
        return struct.unpack('<ff', data)

    def get_encoder_count(self):
        self.send_remote_frame(MotorProtocol.GET_ENCODER_CNT_CMD_ID)

    @CanProtocol.msg_handler(GET_ENCODER_CNT_CMD_ID)
    def handle_encoder_count(self, data):
        return struct.unpack('<ii', data)

    def  set_controller_modes(self, control_mode, input_mode):
        self.send_data(
            MotorProtocol.SET_CONTROL_MODE_CMD_ID,
            data = struct.pack('<ii', control_mode, input_mode)
        )

    def set_input_pos(self, pos, vel_ff = 0, torque_ff = 0):
        self.send_data(
            MotorProtocol.SET_INPUT_POS_CMD_ID,
            data = struct.pack('<fhh', pos, vel_ff*1000, torque_ff*1000)
        )

    def set_input_vel(self, vel, torque_ff = 0):
        self.send_data(
            MotorProtocol.SET_INPUT_VEL_CMD_ID,
            data = struct.pack('<ff', vel, torque_ff)
        )

    def set_input_torque(self, torque):
        self.send_data(
            MotorProtocol.SET_INPUT_TORQ_CMD_ID,
            data = struct.pack('<f', torque)
        )

    def set_velocity_limit(self, vel_lim):
        self.send_data(
            MotorProtocol.SET_VEL_LIM_CMD_ID,
            data = struct.pack('<f', vel_lim)
        )

    def set_traj_vel_limit(self, traj_vel_lim):
        self.send_data(
            MotorProtocol.SET_TRAJ_VEL_LIM_CMD_ID,
            data = struct.pack('<f', traj_vel_lim)
        )

    def set_traj_accel_limits(self, traj_accel_lim, traj_decel_lim):
        self.send_data(
            MotorProtocol.SET_TRAJ_ACC_LIM_CMD_ID,
            data = struct.pack('<ff', traj_accel_lim, traj_decel_lim)
        )

    def set_traj_inertia(self, traj_inertia):
        self.send_data(
            MotorProtocol.SET_TRAJ_INERTIA_CMD_ID,
            data = struct.pack('<f', traj_inertia)
        )

    def get_iq(self):
        self.send_remote_frame(MotorProtocol.GET_IQ_CMD_ID)

    @CanProtocol.msg_handler(GET_IQ_CMD_ID)
    def handle_iq(self, data):
        return struct.unpack('<ff', data)

    def reboot(self):
        self.send_data(MotorProtocol.REBOOT_CMD_ID)

    def get_vbus_voltage(self):
        self.send_remote_frame(MotorProtocol.GET_VBUS_VOLT_CMD_ID)

    @CanProtocol.msg_handler(GET_VBUS_VOLT_CMD_ID)
    def handle_vbus_voltage(self, data):
        return struct.unpack('<f', data[0:4])

    def clear_errors(self):
        self.send_data(MotorProtocol.CLEAR_ERR_CMD_ID)
    
    def save_configuration(self):
        self.send_data(MotorProtocol.SAVE_CONFIG_CMD_ID)

    # def enter_closed_loop_state(self):
    #     self.set_axis_request_state(8)

    # def enter_idle_state(self):
    #     self.set_axis_request_state(1)
