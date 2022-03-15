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
        self.add_device('M4', MotorFactory(), 0x13, reduction = -44)
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
        for motor in self.motors:
            motor.position_filter_mode(8)
        self._zeros = [0 for i in range(6)]
        self._poses = [0 for i in range(6)]
        self.nozzel = self.add_device('nozzel', NanoBoardFactory(), 0x21)
    
    def init(self):
        for i in range(6):
            pos = None
            while not pos:
                pos = self.motors[i].get_pos(0.3)
            self._zeros[i] = pos
            self._poses[i] = 0
    
    def set_motor_pos(self, i, pos):
        self.motors[i].set_pos(pos + self._zeros[i])
        self._poses[i] = pos
    
    def set_nozzel(self, on):
        if on:
            self.nozzel.set_pwm(1)
        else:
            self.nozzel.set_pwm(0)
    
    def move_to_axis(self, target, dur = 0):
        if dur > 0:
            t0 = self.time()
            start = self._poses.copy()
            while self.time() - t0 < dur :
                ratio = (self.time() - t0) / dur
                for i in range(6):
                    pos = (target[i]-start[i])*ratio+start[i]
                    self.set_motor_pos(i, pos)
                self.delay(0.02)
        for i in range(6):
            self.set_motor_pos(i, target[i])
    
    def move_to_xyz(self, start, target, sol_id=2, dur = 0):
        if dur > 0:
            t0 = self.time()
            while self.time() - t0 < dur :
                ratio = (self.time() - t0) / dur
                x = (target[0]-start[0])*ratio+start[0]
                y = (target[1]-start[1])*ratio+start[1]
                z = (target[2]-start[2])*ratio+start[2]
                self.move_to_axis(self.inverse_kinemetics(x,y,z, sol_id=sol_id))
                self.delay(0.02)
        self.move_to_axis(self.inverse_kinemetics(target[0],target[1],target[2],sol_id=sol_id))
    
    def home(self, dur = 5):
        self.move_to_axis((0,0,0,0,0,0), dur)
            
    def pose1(self, dur = 5):
        self.move_to_axis((-0.67,-0.28,-0.3,1.51,0,-0.92), dur)
        
    def pose2(self, dur = 5):
        self.move_to_axis((0.81,0.17,0.57,0.35,0.88,-0.22), dur)
    
    def inverse_kinemetics(self, x, y, z, sol_id = 2):
        np_pose = np.matrix(
          [[0, -1,  0,  -x],
          [ -1, 0, 0, z],
          [ 0, 0,  -1,  y],
          [ 0,  0,  0,  1]]
        )
        pos_arr = invKine(np_pose)[:,sol_id].flatten().tolist()[0]
        pos_arr[1] = pi/2.0 + pos_arr[1]
        pos_arr[2] = -pos_arr[2]
        pos_arr[3] = pi/2.0 + pos_arr[3]
        pos_arr[5] = pi + pos_arr[5]
        return pos_arr