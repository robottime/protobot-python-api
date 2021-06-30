from protobot.can_bus import Robot
from leg import Leg
from math import cos, sin

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
        self._mirror = False
        
    def direct_mode(self):
        for i in range(4):
            self.legs[i].direct_mode()
    
    def filter_mode(self, bandwidth = 10):
        for i in range(4):
            self.legs[i].filter_mode(bandwidth)
    
    def save_configuration(self):
        for i in range(4):
            self.legs[i].save_configuration()
        
    def clear_errors(self):
        for i in range(4):
            self.legs[i].clear_errors()

    def init(self):
        for i in range(4):
            self.legs[i].init()
            
    def init_from_floor(self):
        for i in range(4):
            self.legs[i].init_from_floor(i > 1)
        self.delay(0.1)
        self.legs[0].inverse_kinemetics(20,Leg.LEN_D,38, True)
        self.legs[1].inverse_kinemetics(20,Leg.LEN_D,38, True)
        self.legs[2].inverse_kinemetics(-20,Leg.LEN_D,38)
        self.legs[3].inverse_kinemetics(-20,Leg.LEN_D,38)
        self.delay(0.1)
        self.filter_mode(10)
        self.enable()
        self.delay(0.1)
        for i in range(55):
            h = 38 + i * 5
            self.legs[0].inverse_kinemetics(20,Leg.LEN_D, h,True)
            self.legs[1].inverse_kinemetics(20,Leg.LEN_D, h, True)
            self.legs[2].inverse_kinemetics(-20,Leg.LEN_D, h)
            self.legs[3].inverse_kinemetics(-20,Leg.LEN_D, h)
            self.delay(0.1)
        for i in range(12):
            h = 308 - i * 5
            self.legs[0].inverse_kinemetics(20,Leg.LEN_D,h)
            self.legs[1].inverse_kinemetics(20,Leg.LEN_D,h)
            self.legs[2].inverse_kinemetics(-20,Leg.LEN_D,h)
            self.legs[3].inverse_kinemetics(-20,Leg.LEN_D,h)
            self.delay(0.1)
        self.legs[0].inverse_kinemetics(20,Leg.LEN_D,250)
        self.legs[1].inverse_kinemetics(20,Leg.LEN_D,250)
        self.legs[2].inverse_kinemetics(-20,Leg.LEN_D,250)
        self.legs[3].inverse_kinemetics(-20,Leg.LEN_D,250)
    
    def rest(self):
        self.filter_mode(10)
        self.legs[0].inverse_kinemetics(20,Leg.LEN_D,253)
        self.legs[1].inverse_kinemetics(20,Leg.LEN_D,253)
        self.legs[2].inverse_kinemetics(-20,Leg.LEN_D,253)
        self.legs[3].inverse_kinemetics(-20,Leg.LEN_D,253)
        self.delay(1)
        for i in range(12):
            h = 253 + i * 5
            self.legs[0].inverse_kinemetics(20,Leg.LEN_D,h)
            self.legs[1].inverse_kinemetics(20,Leg.LEN_D,h)
            self.legs[2].inverse_kinemetics(-20,Leg.LEN_D,h)
            self.legs[3].inverse_kinemetics(-20,Leg.LEN_D,h)
            self.delay(0.1)
        for i in range(55):
            h = 308 - i * 5
            self.legs[0].inverse_kinemetics(20,Leg.LEN_D, h,True)
            self.legs[1].inverse_kinemetics(20,Leg.LEN_D, h, True)
            self.legs[2].inverse_kinemetics(-20,Leg.LEN_D, h)
            self.legs[3].inverse_kinemetics(-20,Leg.LEN_D, h)
            self.delay(0.1)
        self.delay(1)
        self.disable()
        
    def mirror(self):
        self.filter_mode(10)
        self.legs[0].inverse_kinemetics(20,Leg.LEN_D,253, self._mirror)
        self.legs[1].inverse_kinemetics(20,Leg.LEN_D,253, self._mirror)
        self.legs[2].inverse_kinemetics(-20,Leg.LEN_D,253)
        self.legs[3].inverse_kinemetics(-20,Leg.LEN_D,253)
        self.delay(1)
        for i in range(12):
            h = 253 + i * 5
            self.legs[0].inverse_kinemetics(20,Leg.LEN_D,h, self._mirror)
            self.legs[1].inverse_kinemetics(20,Leg.LEN_D,h, self._mirror)
            self.legs[2].inverse_kinemetics(-20,Leg.LEN_D,h)
            self.legs[3].inverse_kinemetics(-20,Leg.LEN_D,h)
            self.delay(0.1)
        for i in range(12):
            h = 308 - i * 5
            self.legs[0].inverse_kinemetics(20,Leg.LEN_D, h,not self._mirror)
            self.legs[1].inverse_kinemetics(20,Leg.LEN_D, h, not self._mirror)
            self.legs[2].inverse_kinemetics(-20,Leg.LEN_D, h)
            self.legs[3].inverse_kinemetics(-20,Leg.LEN_D, h)
            self.delay(0.1)
        self._mirror = not self._mirror
            
        
    def read_motor_poses(self):
        for i in range(4):
            print(self.legs[i].read_motor_poses())
            
    def home(self):
        for i in range(4):
            self.legs[i].set_motor_radians(0, 0, 0)
    
    def stand(self, h = 250):
        self.legs[0].inverse_kinemetics(20,Leg.LEN_D,h)
        self.legs[1].inverse_kinemetics(20,Leg.LEN_D,h)
        self.legs[2].inverse_kinemetics(-20,Leg.LEN_D,h)
        self.legs[3].inverse_kinemetics(-20,Leg.LEN_D,h)

    def body_pose(self,dx,dy,dz,roll, pitch, yaw):
        self._pose = (dx,dy,dz,roll,pitch,yaw)

        def point_rotate(x, y, roll, pitch, yaw):
            return (
                cos(yaw)*cos(pitch)*x+(cos(yaw)*sin(pitch)*sin(roll)-sin(yaw)*cos(roll))*y,
                sin(yaw)*cos(pitch)*x+(sin(yaw)*sin(pitch)*sin(roll)+cos(yaw)*cos(roll))*y,
                -sin(pitch)*x+cos(pitch)*sin(roll)*y
            )

        # feet stand coordinate
        HALF_BODY_LENGTH = 196.25
        HALF_WODY_WIDTH = 135
        
        INIT_FOOT_X = 20
        INIT_FOOT_Y = Leg.LEN_D
#         INIT_FOOT_Y = 0
        INIT_FOOT_Z = 250
       
        # shoulder poses
        s_x0, s_y0, s_z0 = point_rotate(HALF_BODY_LENGTH,HALF_WODY_WIDTH, roll, pitch, yaw)
        s_x1, s_y1, s_z1 = point_rotate(HALF_BODY_LENGTH,-HALF_WODY_WIDTH, roll, pitch, yaw)
        s_x2, s_y2, s_z2 = point_rotate(-HALF_BODY_LENGTH,HALF_WODY_WIDTH, roll, pitch, yaw)
        s_x3, s_y3, s_z3 = point_rotate(-HALF_BODY_LENGTH,-HALF_WODY_WIDTH, roll, pitch, yaw)

        self.legs[0].inverse_kinemetics(
            INIT_FOOT_X + HALF_BODY_LENGTH - s_x0 - dx,
            INIT_FOOT_Y + HALF_WODY_WIDTH - s_y0 - dy,
            INIT_FOOT_Z - s_z0 - dz
        )
        self.legs[1].inverse_kinemetics(
            INIT_FOOT_X + HALF_BODY_LENGTH - s_x1 - dx,
            INIT_FOOT_Y + HALF_WODY_WIDTH + s_y1 + dy,
            INIT_FOOT_Z - s_z1 - dz
        )
        self.legs[2].inverse_kinemetics(
            -INIT_FOOT_X - HALF_BODY_LENGTH - s_x2 - dx,
            INIT_FOOT_Y + HALF_WODY_WIDTH - s_y2 - dy,
            INIT_FOOT_Z - s_z2 - dz
        )
        self.legs[3].inverse_kinemetics(
            -INIT_FOOT_X - HALF_BODY_LENGTH - s_x3 - dx,
            INIT_FOOT_Y + HALF_WODY_WIDTH + s_y3 + dy,
            INIT_FOOT_Z - s_z3 - dz
        )
