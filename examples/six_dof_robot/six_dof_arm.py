from protobot.can_bus import Robot
from protobot.can_bus.nodes import MotorFactory,NanoBoardFactory,StepperBoardFactory
from kinemetics import invKine
import numpy as np
from math import pi

class SixDofArm(Robot):
    def __init__(self):
        super(SixDofArm, self).__init__('can0')
        self.add_device('M1', MotorFactory(), 0x10, reduction = -44)
        self.add_device('M2', MotorFactory(), 0x11, reduction = -44)
        self.add_device('M3', MotorFactory(), 0x12, reduction = -44)
        self.add_device('M4', MotorFactory(), 0x13, reduction = -12.45)
        self.add_device('M5', MotorFactory(), 0x14, reduction = -12.45)
        self.add_device('M6', MotorFactory(), 0x15, reduction = -12.45)
        self.motors = [
            self.device('M1'),
            self.device('M2'),
            self.device('M3'),
            self.device('M4'),
            self.device('M5'),
            self.device('M6'),
        ]
        self._zeros=[0 for i in range(6)]
        self.nozzel = self.add_device('nozzel', NanoBoardFactory(), 0x21)
    
    def init(self):
        for i in range(6):
            pos = None
            while not pos:
                pos = self.motors[i].get_pos(0.3)
            self._zeros[i] = pos
    
    def set_motor_pos(self, i, pos, max_vel = 0):
        if max_vel > 0:
            self.motors[i].set_vel_limit(max_vel)
        self.motors[i].set_pos(pos + self._zeros[i])
    
    def set_nozzel(self, on):
        if on:
            self.nozzel.set_pwm(1)
        else:
            self.nozzel.set_pwm(0)
    
    def home(self, max_vel = 0):
        for i in range(6):
            self.set_motor_pos(i, 0, max_vel)
            
    def pose1(self, max_vel = 0):
        self.set_motor_pos(0, -0.67, max_vel)
        self.set_motor_pos(1, -0.28, max_vel)
        self.set_motor_pos(2, -0.3, max_vel)
        self.set_motor_pos(3, 1.51, max_vel)
        self.set_motor_pos(4, 0, max_vel)
        self.set_motor_pos(5, -0.92,max_vel)
        
    def pose2(self, max_vel = 0):
        self.set_motor_pos(0, 0.81, max_vel)
        self.set_motor_pos(1, 0.17, max_vel)
        self.set_motor_pos(2, 0.57, max_vel)
        self.set_motor_pos(3, 0.35, max_vel)
        self.set_motor_pos(4, 0.88, max_vel)
        self.set_motor_pos(5, -0.22, max_vel)
    
    def inverse_kinemetics(self, x, y, z, max_vel = 0, sol_id = 2):
        np_pose = np.matrix(
          [[0, -1,  0,  -x],
          [ -1, 0, 0, z],
          [ 0, 0,  -1,  y],
          [ 0,  0,  0,  1]]
        )
        pos_arr = invKine(np_pose)[:,sol_id]
        pos_arr[1] = pi/2.0 + pos_arr[1,0]
        pos_arr[2] = -pos_arr[2,0]
        pos_arr[3] = pi/2.0 + pos_arr[3,0]
        pos_arr[5] = pi + pos_arr[5]
        for i in range(6):
            self.set_motor_pos(i, pos_arr[i,0], max_vel)