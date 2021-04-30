from protobot.can_bus.protocols.motor_protocol import MotorProtocol
from protobot.can_bus.protocols.message_queue import MessageQueue
from math import pi, fabs
from time import time


class Motor():

    def __init__(self, manager, can_id, reduction=1):
        self._protocol = MotorProtocol(manager, can_id)
        self._reduction = reduction
        self._factor = reduction / 2.0 / pi

        self._protocol.bind_callback(
            MotorProtocol.CMD_ODRIVE_HEARTBEAT, self._heartbeat_cb)
        self._heartbeat_mq = MessageQueue()

        self._protocol.bind_callback(
            MotorProtocol.CMD_GET_API_VERSION, self._api_ver_cb)
        self._api_ver_mq = MessageQueue()

        self._protocol.bind_callback(
            MotorProtocol.CMD_GET_HARDWARE_STATUS, self._hardware_status_cb)
        self._hardware_status_mq = MessageQueue()

        self._protocol.bind_callback(
            MotorProtocol.CMD_GET_MOTOR_STATUS, self._motor_status_cb)
        self._motor_status_mq = MessageQueue()

        self._protocol.bind_callback(
            MotorProtocol.CMD_GET_CONTROLLER_MODES, self._controller_modes_cb)
        self._controller_modes_mq = MessageQueue()

        self._protocol.bind_callback(
            MotorProtocol.CMD_GET_CONTROLLER_PID, self._controller_pid_cb)
        self._controller_pid_mq = MessageQueue()

        self._protocol.bind_callback(
            MotorProtocol.CMD_GET_LIMITS, self._limits_cb)
        self._limits_mq = MessageQueue()

        self._status = {
            'state': 0,
            'error': 0,
            'motor_err': 0,
            'encoder_err': 0,
            'controller_err': 0,
            'control_mode': 3,
            'input_mode': 1,
            'update_rate': float('inf')
        }
        self._recent_heartbeat = time()

        self._protocol.start()

    def __del__(self):
        self._protocol.stop()

    def _heartbeat_cb(self, state, error, merr, eerr, cerr, cmode, imode, mtype):
        self._status.update({
            'state': state,
            'error': error,
            'motor_err': merr,
            'encoder_err': eerr,
            'controller_err': cerr,
            'control_mode': cmode,
            'input_mode': imode,
            'update_rate': time() - self._recent_heartbeat # ERROR WHEN LOSE CONNECTION
        })
        self._recent_heartbeat = time()

    def status(self, timeout=3):
        if self._status['update_rate'] > timeout:
            print('Disconnected')
        elif self._status['error']:
            print('Error')
        elif self._status['state'] == 8:
            mode_msg = ['Enabled', 'In Torque Mode',
                        'In Velocity Mode', 'In Position Mode']
            print(mode_msg[self._status['control_mode']])
        else:
            print('Disabled')
        return self._status

    def _api_ver_cb(self, main_ver, sub_ver, release):
        self._api_ver_mq.call('{}.{}.{}'.format(main_ver, sub_ver, release))

    def get_api_ver(self, timeout=0.1):
        self._protocol.request_api_version()
        return self._api_ver_mq.get_data(timeout)

    def estop(self):
        self._protocol.estop()

    def reboot(self):
        self._protocol.reset()

    def clear_errors(self):
        self._protocol.clear_errors()

    def save_configuration(self):
        self._protocol.save_configuration()

    def set_can_id(self, id=0x10, rate=1000):
        self._protocol.set_axis_node_id(id, rate)

    def enable(self):
        self._protocol.set_axis_request_state(8)

    def disable(self):
        self._protocol.set_axis_request_state(1)

    def calibrate(self):
        self._protocol.set_axis_request_state(3)

    def _hardware_status_cb(self, voltage, temperature):
        self._hardware_status_mq.call((voltage, temperature))

    def get_vbus(self, timeout=0.1):
        self._protocol.request_hardware_status()
        data = self._hardware_status_mq.get_data(timeout)
        return data[0]

    def get_temperature(self, timeout=0.1):
        self._protocol.request_hardware_status()
        data = self._hardware_status_mq.get_data(timeout)
        return data[1]

    def _motor_status_cb(self, pos, vel, torque):
        self._motor_status_mq.call((pos, vel, torque))

    def get_pos(self, timeout=0.1):
        self._protocol.request_motor_status()
        data = self._motor_status_mq.get_data(timeout)
        return data[0] / self._factor

    def get_vel(self, timeout=0.1):
        self._protocol.request_motor_status()
        data = self._motor_status_mq.get_data(timeout)
        return data[1] / self._factor

    def get_torque(self, timeout=0.1):
        self._protocol.request_motor_status()
        data = self._motor_status_mq.get_data(timeout)
        return data[2] * self._factor

    def _controller_modes_cb(self, control_mode, input_mode, *args):
        self._controller_modes_mq.call([control_mode, input_mode]+list(args))

    def get_controller_modes(self, timeout=0.1):
        self._protocol.request_controller_modes()
        return self._controller_modes_mq.get_data(timeout)

    def _controller_pid_cb(self, pos_p, vel_p, vel_i):
        self._controller_pid_mq.call((pos_p, vel_p, vel_i))

    def get_controller_pid(self, timeout=0.1):
        self._protocol.request_controller_pid()
        return self._controller_pid_mq.get_data(timeout)

    def set_controller_pid(self, pos_p=10, vel_p=0.03, vel_i=0.005):
        self._protocol.set_controller_pid(pos_p, vel_p, vel_i)

    def _limits_cb(self, vel_limit, torque_limit):
        self._limits_mq.call((vel_limit, torque_limit))

    def get_limits(self, timeout=0.1):
        self._protocol.request_limits()
        return self._limits_mq.get_data(timeout)

    def set_limits(self, vel_limit = 0, torque_limit = 0):
        self._protocol.set_limits(vel_limit, torque_limit)

    def set_pos(self, pos, vel_ff = 0, torque_ff = 0):
        self._protocol.set_input_pos(
            pos * self._factor, vel_ff * self._factor, torque_ff / self._factor)

    def set_vel(self, vel, torque_ff = 0):
        self._protocol.set_input_vel(
            vel * self._factor, torque_ff / self._factor)

    def set_torque(self, torque):
        self._protocol.set_input_torque(torque / self._factor)

    def position_mode(self):
        self._protocol.set_controller_modes(3, 1)

    def velocity_mode(self):
        self._protocol.set_controller_modes(2, 1)

    def torque_mode(self):
        self._protocol.set_controller_modes(1, 1)

    def position_filter_mode(self, bandwidth = 20.0): # bandwidth in Hz
        self._protocol.set_controller_modes(3, 3, bandwidth)

    def position_traj_mode(self, vel, accel, decel):
        self._protocol.set_controller_modes(3, 5, vel, accel, decel)

    def velocity_ramp_mode(self, ramp):
        self._protocol.set_controller_modes(2, 2, ramp)
        pass

    # def request_pos(self, callback):
    #     self._protocol.get_encoder_estimate()
    #     self._pos_mq.append_cb(callback)

    # def request_vel(self, callback):
    #     self._protocol.get_encoder_estimate()
    #     self._vel_mq.append_cb(callback)

