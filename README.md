# protobot-python-api
> latest update: 2021/12/02
## Python安装方式
``` 
cd src 
pip install -e .
```

## API文档
### 初始化电机对象

出厂ID：0x10


参数：
- reduction: 减速比

常用减速比：
- 二级行星：-12.45
- 三级行星：-44
- RV50：53.325
- RV100：110.205
- 谐波50：50
- 谐波100：100

``` python
from protobot.can_bus import Robot
from protobot.can_bus.nodes import MotorFactory
robot = Robot()
motor = robot.add_device('motor0', MotorFactory(), 0x15, reduction=12.45)
```

### 电机状态
`motor.status()`
最近一次心跳包的内容

返回值：
- 电机状态dict
    - state: 工作模式（1：空闲，8：使能）
    - error: 错误码（1：电压不足，14：急停）
    - motor_err: 电机相关错误码
    - encoder_err: 编码器相关错误码
    - controller_err: 控制器相关错误码
    - control_mode: 控制模式（1：力矩控制，2：速度控制，3：位置控制）
    - input_mode: 输入模式（1：直接值，2：带加速度，3：带滤波，5：梯形轨迹）
    - timestamp: 时间戳，上一次收到心跳包的时间


### 获取API版本
`get_api_version(timeout = 0)`

参数：
- timeout: 请求超时时间(s)，0代表无超时时间

返回值：
- API版本dict
    - device_uuid: 设备uuid
    - main_version: 主版本号
    - sub_version: 副版本号

### 电机软急停
`estop()`

### 电机重启
`reboot()`

### 清除错误
`clear_errors()`

### 保存设置
`save_configuration()`

设置参数后默认不会保存，直到调用此函数

### 设置电机CAN_ID
`set_can_id(id, rate)`

参数：
- id：电机新CAN_ID (0x01~0x3F)
- rate: 心跳包发送周期，ms

### 电机使能
`enable()`

### 电机失能
`disable()`

### 电机校准
`calibrate()`

校准后需保存参数

### 读取总线电压
`get_vbus(timeout)`

参数：
- timeout

返回值：
- 总线电压值(V)

### 读取电机温度
`get_temperature(timeout)`

参数：
- timeout

返回值：
- 电机温度(°C)

### 读取电机状态参数
`get_status(timeout)`

参数：
- timeout

返回值：
- 电机状态参数(位置rad, 速度rad/s, 力矩Nm)

### 读取电机位置
`get_pos(timeout)`

参数：
- timeout

返回值：
- 位置(rad)

### 读取电机速度
`get_vel(timeout)`

参数：
- timeout

返回值：
- 速度(rad/s)

### 读取电机力矩
`get_torque(timeout)`

参数：
- timeout

返回值：
- 力矩(Nm)

### 读取电机控制模式
`get_controller_modes(timeout)`

参数：
- timeout

返回值：
- 控制模式(control_mode, input_mode)
    - control_mode: 控制模式（1：力矩控制，2：速度控制，3：位置控制）
    - input_mode: 输入模式（1：直接值，2：带加速度，3：带滤波，5：梯形轨迹)

### 读取加速度输入模式参数
`get_ramp_mode_ramp(timeout)`

参数:
- timeout

返回值：
- ramp: 加速度(rad/s^2)

### 读取滤波输入模式参数
`get_filter_mode_bandwidth(timeout)`

参数：
- timeout

返回值：
- bandwidth: 滤波带宽 / 输入频率(Hz)

### 读取轨迹模式参数
`get_traj_mode_params(timeout)`

参数:
- timeout

返回值：
- 轨迹参数(最大速度, 加速度, 减速度)

### 读取电机PID参数
`get_controller_pid(timeout)`

参数：
- timeout

返回值：
- 电机PID(位置环P, 速度环P, 速度环I)

### 设置电机PID参数
`set_controller_pid(pos_p, vel_p, vel_i)`

参数:
- pos_p: 位置环比例系数
- vel_p: 速度环比例系数
- vel_i: 速度环积分系数

### 读取电机速度电流限制
`get_limits(timeout)`

参数:
- timeout

返回值：
- (输入端最大速度(r/s), 最大电流(A))

### 读取电机速度限制
`get_vel_limit(timeout)`

参数:
- timeout

返回值：
- 输出端最大速度(rad/s)

### 读取电机电流限制
`get_current_limit(timeout)`

参数:
- timeout

返回值：
- 最大电流(A)

### 设置电机速度电流限制
`set_limits(vel_limit, torque_limit)`

参数：
- vel_limit: 输入端最大速度(r/s)
- torque_limit: 最大电流(A)

### 设置电机速度限制
`set_vel_limit(vel_limit)`

参数：
- vel_limit: 输出端最大速度(rad/s)

### 进入直接位置模式
`position_mode()`

直接PID控制位置

### 进入滤波位置模式
`position_filter_mode(bandwidth)`

参数：
- bandwidth: 滤波带宽 / 控制频率(Hz)

### 进入轨迹位置模式
`position_traj_mode(max_vel, accel, decel)`

参数:
- max_vel: 最高速度
- accel: 加速度
- decel: 减速度

### 设置位置
`set_pos(position)`

参数:
- position: 目标位置(rad)

### 进入直接速度模式
`velocity_mode()`

速度PID控制

### 进入匀加减速速度模式
`velocity_ramp_mode(ramp)`

参数:
- ramp: 加速度(rad/s^2)

### 设置速度
`set_vel(velocity)`

参数：
- velocity: 目标速度(rad/s)

### 进入力矩控制模式
`torque_mode()`

### 设置力矩
`set_torque(torque)`

参数：
- torque: 目标力矩(Nm)
