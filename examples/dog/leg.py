from math import radians, sqrt, atan2, acos, asin

class Leg:
    
    LEN_D = 79.5
    LEN_L1 = 166
    LEN_L2 = 143.7
    
    def __init__(self, m0, m1, m2):
        self._motors = [m0, m1, m2]
        self._zeros = [0, 0, 0]
    
    def init(self):
        for i in range(3):
            for count in range(5):
                pos = self._motors[i].get_pos(0.1)
                if pos is not None:
                    self._zeros[i] = pos
                    break
            if pos is None:
                raise Exception('Error: motor {} lost connection'.format(i))
                
    def init_from_floor(self, mirror = False):
        offset = [0, 1.4, -2.9]
        if mirror:
            offset = [0, -1.4, 2.9]
        for i in range(3):
            for count in range(5):
                pos = self._motors[i].get_pos(0.1)
                if pos is not None:
                    self._zeros[i] = pos + offset[i]
                    break
            if pos is None:
                raise Exception('Error: motor {} lost connection'.format(i))
                
    def read_motor_poses(self):
        poses = [None, None, None]
        for i in range(3):
            for count in range(5):
                pos = self._motors[i].get_pos(0.1)
                if pos is not None:
                    poses[i] = pos - self._zeros[i]
                    break
        return poses

    def motor(self, index):
        return self._motors[index]
    
    def direct_mode(self):
        for i in range(3):
            self._motors[i].position_mode()
            
    def filter_mode(self, bandwidth = 10):
        for i in range(3):
            self._motors[i].position_filter_mode(bandwidth)
        
    def save_configuration(self):
        for i in range(3):
            self._motors[i].save_configuration()
    
    def clear_errors(self):
        for i in range(3):
            self._motors[i].clear_errors()
    
    def enable(self):
        for i in range(3):
            self._motors[i].enable()
    
    def disable(self):
        for i in range(3):
            self._motors[i].disable()
        
    def set_motor_radians(self, r0, r1, r2):
        angles = [r0, r1, r2]
        for i in range(3):
            self._motors[2-i].set_pos(angles[2-i] + self._zeros[2-i])
    
    def set_motor_degrees(self, d0, d1, d2):
        angles = [radians(d0), radians(d1), radians(d2)]
        for i in range(3):
            self._motors[2-i].set_pos(angles[2-i] + self._zeros[2-i])
    
    def inverse_kinemetics(self, x, y, z, mirror = False):
        if mirror:
            x = -x
        d = self.LEN_D
        l1 = self.LEN_L1
        l2 = self.LEN_L2
        l = sqrt(y * y + z * z - d * d)
        theta = atan2(l, d) - atan2(z, y)

        s = sqrt(l * l + x * x)

        beta = -acos(round((s*s - l1*l1 - l2*l2) / (2*l1*l2),10))

        ta = acos(round((-l2*l2 + s*s + l1*l1) / (2*l1*s),10))
        alpha = ta - asin(x / s)
        if mirror:
            self.set_motor_radians(theta, -alpha, -beta)
        else:
            self.set_motor_radians(theta, alpha, beta)
    