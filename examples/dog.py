from protobot.can_bus import Robot
from math import radians, cos, sin, sqrt, atan2, acos, asin

class Leg:
    
    LEN_D = 79.5
    LEN_L1 = 166
    LEN_L2 = 143.7
    
    def __init__(self, m0, m1, m2):
        self._motors = [m0, m1, m2]
        self._zeros = [0, 0, 0]
    
    def init(self):
        for i in range(3):
            count = 0
            for i in range(5):
                pos = self._motors[i].get_pos(0.3)
                if pos is not None:
                    self._zeros[i] = pos
                    return
            print('Error: motor {} lost connection'.format(i))
    
    def direct_mode(self):
        for i in range(3):
            self._motors[i].position_mode(1)
            
    def filter_mode(self):
        for i in range(3):
            self._motors[i].position_mode(3)
    
    def enable(self):
        for i in range(3):
            self._motors[i].enable()
    
    def disable(self):
        for i in range(3):
            self._motors[i].disable()
        
    def set_motor_radians(self, r0, r1, r2):
        angles = [r0, r1, r2]
#         self._motors[0].set_pos(angles[0] + self._zeros[0])
#         self._motors[1].set_pos(angles[1] + self._zeros[1])
#         self._motors[2].set_pos(angles[2] + self._zeros[2])
        for i in range(3):
            self._motors[2-i].set_pos(angles[2-i] + self._zeros[2-i])
    
    def set_motor_degrees(self, d0, d1, d2):
        angles = [radians(d0), radians(d1), radians(d2)]
        for i in range(3):
            self._motors[2-i].set_pos(angles[2-i] + self._zeros[2-i])
    
    def inverse_kinemetics(self, x, y, z):
        d = self.LEN_D
        l1 = self.LEN_L1
        l2 = self.LEN_L2
        l = sqrt(y * y + z * z - d * d)
        theta = atan2(l, d) + atan2(y, z)

        s = sqrt(l * l + x * x)

        beta = -acos(round((s*s - l1*l1 - l2*l2) / (2*l1*l2),10))

        ta = acos(round((-l2*l2 + s*s + l1*l1) / (2*l1*s),10))
        alpha = ta - asin(x / s)
        self.set_motor_radians(theta, alpha, beta)
    

class Dog(Robot):
    def __init__(self):
        super(Dog, self).__init__('can0')
        self.legs = [
            Leg(
                self.add_motor('LEG1_M0', can_id = 0x10, reduction = 44),
                self.add_motor('LEG1_M1', can_id = 0x11, reduction = 44),
                self.add_motor('LEG1_M2', can_id = 0x12, reduction = 44)
            ),
            Leg(
                self.add_motor('LEG2_M0', can_id = 0x13, reduction = -44),
                self.add_motor('LEG2_M1', can_id = 0x14, reduction = -44),
                self.add_motor('LEG2_M2', can_id = 0x15, reduction = -44)
            ),
            Leg(
                self.add_motor('LEG3_M0', can_id = 0x16, reduction = -44),
                self.add_motor('LEG3_M1', can_id = 0x17, reduction = 44),
                self.add_motor('LEG3_M2', can_id = 0x18, reduction = 44)
            ),
            Leg(
                self.add_motor('LEG4_M0', can_id = 0x19, reduction = 44),
                self.add_motor('LEG4_M1', can_id = 0x1a, reduction = -44),
                self.add_motor('LEG4_M2', can_id = 0x1b, reduction = -44)
            ),
        ]
        self.battery = self.set_battery()

    def init(self):
        for i in range(4):
            self.legs[i].init()
        
    def home(self):
        for i in range(4):
            self.legs[i].set_motor_radians(0, 0, 0)
    
    def stand(self):
        for i in range(4):
            self.legs[i].inverse_kinemetics(20, -250, Leg.LEN_D)
    
    def direct_mode(self):
        for i in range(4):
            self.legs[i].direct_mode()
    
    def filter_mode(self):
        for i in range(4):
            self.legs[i].filter_mode()
            
    def point_rotate(self, x, y, roll, pitch, yaw):
        xx = cos(yaw)*cos(pitch)*x+(cos(yaw)*sin(pitch)*sin(roll)-sin(yaw)*cos(roll))*y
        yy = sin(yaw)*cos(pitch)*x+(sin(yaw)*sin(pitch)*sin(roll)+cos(yaw)*cos(roll))*y
        zz = -sin(pitch)*x+cos(pitch)*sin(roll)*y
        
        return (xx,yy,zz)

    def body_pose(self, roll, pitch, yaw):
        v_stand = (20, -250, Leg.LEN_D)
        x0, y0, z0 = self.point_rotate(196.25,135, roll, pitch, yaw)
        vector0 = (196.25 - x0, z0, 135 - y0)
        self.legs[0].inverse_kinemetics(*[x + y for x, y in zip(v_stand, vector0)])
        x1, y1, z1 = self.point_rotate(196.25,-135, roll, pitch, yaw)
        vector1 = (196.25 - x1, z1, 135 + y1)
        self.legs[1].inverse_kinemetics(*[x + y for x, y in zip(v_stand, vector1)])
        x2, y2, z2 = self.point_rotate(-196.25,135, roll, pitch, yaw)
        vector2 = (196.25 + x2, z2, 135 - y2)
        self.legs[2].inverse_kinemetics(*[x + y for x, y in zip(v_stand, vector2)])
        x3, y3, z3 = self.point_rotate(-196.25,-135, roll, pitch, yaw)
        vector3 = (196.25 + x3, z3, 135 + y3)
        self.legs[3].inverse_kinemetics(*[x + y for x, y in zip(v_stand, vector3)])
    