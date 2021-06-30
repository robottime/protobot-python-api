from protobot.can_bus import Robot
# from kinemetics import invKine
# import numpy as np
from math import pi

class SixDofArm(Robot):
    def __init__(self):
        super(SixDofArm, self).__init__('can0')
        self.add_motor('M1', can_id = 0x10, reduction = 53.325)
        self.add_motor('M2', can_id = 0x11, reduction = 110.205)
        self.add_motor('M3', can_id = 0x12, reduction = 110.205)
        self.add_motor('M4', can_id = 0x13, reduction = 53.325)
        self.add_motor('M5', can_id = 0x14, reduction = 53.325)
        self.add_motor('M6', can_id = 0x15, reduction = -12.45)
        self.motors = [
            self.motor('M1'),
            self.motor('M2'),
            self.motor('M3'),
            self.motor('M4'),
            self.motor('M5'),
            self.motor('M6'),
        ]
        self._zeros=[0 for i in range(6)]
        self._acc = self.add_device('acc')
    
    def init(self):
        for i in range(6):
            pos = None
            while not pos:
                pos = self.motors[i].get_pos(0.3)
            self._zeros[i] = pos
    
    def set_motor_pos(self, i, pos):
        self.motors[i].set_pos(pos + self._zeros[i])
    
    def set_servo(self, pos):
        self._acc.set_servo(pos*0.5+0.5)
    
    def home(self):
        for i in range(6):
            self.set_motor_pos(i, 0)
            
    def pose1(self):
        self.set_motor_pos(0, -0.67)
        self.set_motor_pos(1, -0.28)
        self.set_motor_pos(2, -0.3)
        self.set_motor_pos(3, 1.51)
        self.set_motor_pos(4, 0)
        self.set_motor_pos(5, -0.92)
        
    def pose2(self):
        self.set_motor_pos(0, 0.81)
        self.set_motor_pos(1, 0.17)
        self.set_motor_pos(2, 0.57)
        self.set_motor_pos(3, 0.35)
        self.set_motor_pos(4, 0.88)
        self.set_motor_pos(5, -0.22)
    
#     def inverse_kinemetics(self, x, y, z, ):
#         np_pose = np.matrix(
#           [[0, -1,  0,  -x],
#           [ -1, 0, 0, z],
#           [ 0, 0,  -1,  y],
#           [ 0,  0,  0,  1]]
#         )
#         pos_arr = invKine(np_pose)[:,2]
#         pos_arr[1] = pi/2.0 + pos_arr[1,0]
#         pos_arr[2] = -pos_arr[2,0]
#         pos_arr[3] = pi/2.0 + pos_arr[3,0]
#         pos_arr[5] = pi + pos_arr[5]
#         for i in range(6):
#             self.set_motor_pos(i, pos_arr[i,0])