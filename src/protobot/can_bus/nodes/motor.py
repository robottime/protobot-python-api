from .node import Node, NodeFactory
from math import pi, fabs
import numpy as np
from time import time

class MotorFactory(NodeFactory):
    def get_node(self, network, node_id = 0x10, reduction = -12.45):
        motor = Motor(node_id, reduction)
        network[node_id] = motor
        return motor

class Motor(Node):
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
    CMD_ERASE_ODRIVE = 0x14
    CMD_UNLOCK = 0x15

    def __init__(self, node_id, reduction):
        super(Motor, self).__init__(node_id)
        self.reduction = reduction
        self._factor = reduction / 2.0 / pi
        self._status = {
            'state': 0,
            'error': 0,
            'motor_err': 0,
            'encoder_err': 0,
            'controller_err': 0,
            'control_mode': 3,
            'input_mode': 1,
            'timestamp': 0
        }

    def associate_network(self, network):
        super(Motor, self).associate_network(network)
        self.network.subscribe(self.can_id(self.CMD_ODRIVE_HEARTBEAT), self.heartbeat_callback)
    
    def heartbeat_callback(self, can_id, data, timestamp):
        state,err,merr,eerr,cerr,cmode,imode,mtype = list(np.frombuffer(data, dtype='<B'))
        self._status.update({
            'state': int(state),
            'error': int(err),
            'motor_err': int(merr),
            'encoder_err': int(eerr),
            'controller_err': int(cerr),
            'control_mode': int(cmode),
            'input_mode': int(imode),
            'timestamp': timestamp
        })

    def status(self):
        print(time())
        return self._status

    @Node.get_func_decorator(CMD_GET_API_VERSION, '<u2,<u2,<u4')
    def get_api_ver(self, main_ver, sub_ver, uuid):
        return {
            'device_uuid': uuid,
            'main_version': main_ver,
            'sub_version': sub_ver,
        }
    
    @Node.send_func_decorator(CMD_ODRIVE_ESTOP)
    def estop(self):
        pass

    @Node.send_func_decorator(CMD_RESET_ODRIVE)
    def reboot(self):
        pass

    @Node.send_func_decorator(CMD_CLEAR_ERRORS)
    def clear_errors(self):
        pass

    @Node.send_func_decorator(CMD_SAVE_CONFIGURATION)
    def save_configuration(self):
        pass

    @Node.send_func_decorator(CMD_SET_AXIS_NODE_ID, '<u2,<u2,<u4')
    def set_can_id(self, id = 0x10, rate = 1000, bitrate = 1000000):
        bitrate_id = 2
        if bitrate == 250000:
            bitrate_id = 0
        elif bitrate == 500000:
            bitrate_id = 1
        return (id, bitrate_id, rate)

    @Node.send_func_decorator(CMD_SET_AXIS_REQUESTED_STATE, '<u4')
    def enable(self):
        return (8, )
    
    @Node.send_func_decorator(CMD_SET_AXIS_REQUESTED_STATE, '<u4')
    def disable(self):
        return (1, )

    @Node.send_func_decorator(CMD_SET_AXIS_REQUESTED_STATE, '<u4')
    def calibrate(self):
        return (3, )

    @Node.get_func_decorator(CMD_GET_HARDWARE_STATUS, '<f4,<f4')
    def get_hardware_info(self, vbus, temperature):
        return (vbus, temperature)
    
    @Node.get_func_decorator(CMD_GET_HARDWARE_STATUS, '<f4,<f4')
    def get_vbus(self, vbus, temperature):
        return vbus

    @Node.get_func_decorator(CMD_GET_HARDWARE_STATUS, '<f4,<f4')
    def get_temperature(self, vbus, temperature):
        return temperature

    @Node.get_func_decorator(CMD_GET_MOTOR_STATUS, '<f4,<f2,<f2')
    def get_status(self, pos, vel, torque):
        return (pos / self._factor, vel / self._factor, torque * self.reduction)
    
    @Node.get_func_decorator(CMD_GET_MOTOR_STATUS, '<f4,<f2,<f2')
    def get_pos(self, pos, vel, torque):
        return pos / self._factor
    
    @Node.get_func_decorator(CMD_GET_MOTOR_STATUS, '<f4,<f2,<f2')
    def get_vel(self, pos, vel, torque):
        return vel / self._factor
    
    @Node.get_func_decorator(CMD_GET_MOTOR_STATUS, '<f4,<f2,<f2')
    def get_torque(self, pos, vel, torque):
        return torque * self.reduction

    # @Node.get_func_decorator(CMD_GET_MOTOR_STATUS, '<f4,<f2,<f2')
    # def get_phase_current(self, pos, vel, torque):
    #     k = 240
    #     if self.reduction < 50 and self.reduction > -50:
    #         k = 470
    #     return torque / 8.27 * k

    @Node.get_func_decorator(CMD_GET_CONTROLLER_MODES, '<B,<B')
    def get_controller_modes(self, control_mode, input_mode):
        return (control_mode, input_mode)
    
    @Node.get_func_decorator(CMD_GET_CONTROLLER_MODES, '<B,<B,<f4,<f2')
    def get_ramp_mode_ramp(self, control_mode, input_mode, ramp,_):
        assert input_mode == 2
        return ramp / fabs(self._factor)
    
    @Node.get_func_decorator(CMD_GET_CONTROLLER_MODES, '<B,<B,<f4,<f2')
    def get_filter_mode_bandwidth(self, control_mode, input_mode, bandwidth,_):
        assert input_mode == 3
        return bandwidth
    
    @Node.get_func_decorator(CMD_GET_CONTROLLER_MODES, '<B,<B,<f2,<f2,<f2')
    def get_traj_mode_params(self, control_mode, input_mode, max_vel, max_acc, max_dec):
        assert input_mode == 5
        return (fabs(max_vel / self._factor), fabs(max_acc / self._factor), fabs(max_dec / self._factor))
    
    @Node.send_func_decorator(CMD_SET_CONTROLLER_MODES, '<B,<B')
    def position_mode(self):
        return (3, 1)
    
    @Node.send_func_decorator(CMD_SET_CONTROLLER_MODES, '<B,<B')
    def velocity_mode(self):
        return (2, 1)

    @Node.send_func_decorator(CMD_SET_CONTROLLER_MODES, '<B,<B')
    def torque_mode(self):
        return (1, 1)
    
    @Node.send_func_decorator(CMD_SET_CONTROLLER_MODES, '<B,<B,<f4')
    def position_filter_mode(self, bandwidth = 20):
        return (3, 3, bandwidth)
    
    @Node.send_func_decorator(CMD_SET_CONTROLLER_MODES, '<B,<B,<f2,<f2,<f2')
    def position_traj_mode(self, max_vel, max_acc, max_dec):
        return (3, 5, fabs(max_vel * self._factor), fabs(max_acc * self._factor), fabs(max_dec * self._factor))
    
    @Node.send_func_decorator(CMD_SET_CONTROLLER_MODES, '<B,<B,<f4')
    def velocity_ramp_mode(self, ramp):
        return (2, 2, ramp * fabs(self._factor))
    
    @Node.get_func_decorator(CMD_GET_CONTROLLER_PID, '<f4,<f2,<f2')
    def get_controller_pid(self, pp, vp, vi):
        return (pp, vp, vi)
    
    @Node.send_func_decorator(CMD_SET_CONTROLLER_PID, '<f4,<f2,<f2')
    def set_controller_pid(self, pos_p, vel_p, vel_i):
        return (pos_p, vel_p, vel_i)

    @Node.get_func_decorator(CMD_GET_LIMITS, '<f4,<f4')
    def get_limits(self, vel_limit, current_limit):
        return (vel_limit, current_limit)
    
    @Node.get_func_decorator(CMD_GET_LIMITS, '<f4,<f4')
    def get_vel_limit(self, vel_limit, current_limit):
        return vel_limit / fabs(self._factor)
    
    @Node.get_func_decorator(CMD_GET_LIMITS, '<f4,<f4')
    def get_current_limit(self, vel_limit, current_limit):
        return current_limit

    @Node.send_func_decorator(CMD_SET_LIMITS, '<f4,<f4')
    def set_limits(self, vel_limit = 0, current_limit = 0):
        return (vel_limit, current_limit)

    @Node.send_func_decorator(CMD_SET_LIMITS, '<f4,<f4')
    def set_vel_limit(self, vel_limit):
        return (vel_limit * fabs(self._factor), 0)

    @Node.send_func_decorator(CMD_SET_INPUT_POS, '<f4,<f2,<f2')
    def set_pos(self, pos, vel_ff = 0, torque_ff = 0):
        return (pos * self._factor, vel_ff * self._factor, torque_ff / self._factor)
    
    @Node.send_func_decorator(CMD_SET_INPUT_VEL, '<f4,<f4')
    def set_vel(self, vel, torque_ff=0):
        return (vel * self._factor, torque_ff / self._factor)

    @Node.send_func_decorator(CMD_SET_INPUT_TORQUE, '<f4')
    def set_torque(self, torque):
        return (torque / self.reduction, )

    @Node.send_func_decorator(CMD_ERASE_ODRIVE)
    def reset_motor(self):
        pass

    @Node.send_func_decorator(CMD_UNLOCK)
    def unlock(self):
        pass