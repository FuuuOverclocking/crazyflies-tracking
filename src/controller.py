import time
from math import pi, cos, sin

# 决定状态前采样时间，秒
STATE_DECIDE_TIME = 3
# 合适距离区间，米
OK_DISTANCE_FROM = 1
OK_DISTANCE_TO = 1.5

MOVE_SAMPLING_TIME = 1.0
MOVE_LASTING_TIME = 3.0

THRESHOLD = 0.2
BASIC_VEL = 0.6


def get_distance_avg(data, sampling_data_number):
    result = 0.0
    i = 0
    for dist in reversed(data.distance):
        result += dist

        i += 1
        if i == sampling_data_number:
            break

    result /= sampling_data_number
    return result


def compute_degree(old_degree, new_dist, old_dist, direction):
    diff = new_dist - old_dist
    new_degree = old_degree

    if diff < THRESHOLD and diff > -THRESHOLD:
        new_degree += pi / 2
        new_degree = new_degree % (2*pi)
    elif (diff > 0 and direction == 'approach') or (diff < 0 and direction == 'leave'):
        new_degree += pi
        new_degree = new_degree % (2*pi)

    return new_degree


def decide_global_state(data, sampling_data_number):
    ok_num = 0
    too_near_num = 0
    too_far_num = 0

    i = 0
    for dist in reversed(data.distance):
        if dist < OK_DISTANCE_FROM:
            too_near_num += 1
        elif dist > OK_DISTANCE_TO:
            too_far_num += 1
        else:
            ok_num += 1

        i += 1
        if i == sampling_data_number:
            break

    if ok_num >= too_near_num and ok_num >= too_far_num:
        return 'OK'
    elif too_near_num >= ok_num and too_near_num >= too_far_num:
        return 'leave'
    else:
        return 'approach'


def decide_state(last_state, data):
    state = last_state

    if state['global'] == 'unknown' or state['global'] == 'OK':
        if not state['sampling']:
            state = state.copy()
            state['sampling'] = True
            state['timer'] = time.perf_counter()
            state['beat_before_sampling'] = data.beat

        elif time.perf_counter() - state['timer'] > STATE_DECIDE_TIME:
            state = state.copy()
            state['sampling_data_number'] = data.beat - \
                state['beat_before_sampling']

            state['sampling'] = False
            state['global'] = decide_global_state(
                data, state['sampling_data_number'])
            state['substate_init'] = 0


    if state['global'] == 'approach' or state['global'] == 'leave':
        if state['sampling']:
            if time.perf_counter() - state['timer'] > MOVE_SAMPLING_TIME:
                state = state.copy()

                # 采样完成的瞬间
                state['sampling'] = False
                state['sampling_data_number'] = data.beat - \
                    state['beat_before_sampling']
                new_dist = get_distance_avg(
                    data, state['sampling_data_number'])

                if state['substate_init'] == 1:
                    state['substate_init'] = 2

                    # 应记录平均，直接飞行
                    state['last_distance'] = new_dist
                    state['flying'] = True
                    state['timer'] = time.perf_counter()
                else:
                    # 应判断 global 状态，改变 degree
                    # 再飞行
                    global_state = decide_global_state(
                        data, state['sampling_data_number'])
                    if global_state == state['global']:
                        # global 未变
                        state['degree'] = compute_degree(
                            state['degree'], new_dist, state['last_distance'], global_state)
                        state['last_distance'] = new_dist
                        state['flying'] = True
                        state['timer'] = time.perf_counter()
                    else:
                        state['global'] = global_state
                        state['substate_init'] = 0

        if state['flying']:
            if time.perf_counter() - state['timer'] > MOVE_SAMPLING_TIME:
                state = state.copy()

                # 飞行完成的瞬间
                state['flying'] = False

                # 开始采样
                state['sampling'] = True
                state['timer'] = time.perf_counter()
                state['beat_before_sampling'] = data.beat

        if state['substate_init'] == 0:
            state = state.copy()
            state['substate_init'] = 1

            # 开始采样
            state['sampling'] = True
            state['timer'] = time.perf_counter()
            state['beat_before_sampling'] = data.beat

    return state


def calculate_vel(state):
    # return (v_x, v_y, v_z, rate_yaw)
    if state['global'] == 'OK' or state['global'] == 'unknown':
        return (0, 0, 0, 0)

    if state['flying']:
        v_x = BASIC_VEL * cos(state['degree'])
        v_y = BASIC_VEL * sin(state['degree'])
        return (v_x, v_y, 0, 0)

    return (0, 0, 0, 0)


class Controller(object):
    # 节拍
    beat = 0

    # 初始化过程使用的计数器
    init_counter = 0
    # 已初始化？
    initialized = False

    # 状态
    state = {
        # 枚举
        # unknown    - 未知
        # OK         - 悬停在合适区间
        # approach   - 接近中
        # leave      - 远离中
        'global': 'unknown',
        'sampling': False,
        'flying': False,
        'timer': 0,
        'beat_before_sampling': 0,
        'sampling_data_number': 0,

        # 当前飞行朝向角度，[ 0, 2π )
        'degree': 0,
        'substate_init': 0,
        'last_distance': 0
    }

    def __init__(self, data, mc):
        self.data = data
        self.mc = mc

    def land(self):
        self.mc.land()

    def init(self):
        if self.initialized:
            return True
        else:
            self.init_counter += 1
            if self.init_counter > 50:
                self.initialized = True

    def tick(self):
        if self.beat == self.data.beat:
            return
        self.beat = self.data.beat

        # print(self.beat)
        # print(self.data.distance[-1])

        if not self.init():
            return

        self._tick()

    log_timer = 0

    def _tick(self):
        # print('abc')
        # 函数式编程

        self.log_timer += 1
        self.log_timer = self.log_timer % 10
        if self.log_timer == 0:
            print('No. '+str(self.beat))
            print(self.state['global'])
            print('sampling:      ' + str(self.state['sampling']))
            print('flying:        ' + str(self.state['flying']))
            print('degree:        ' + str(self.state['degree']))
            print('last_distance: ' + str(self.state['last_distance']))
            print('substate_init: ' + str(self.state['substate_init']))
            print('dist[-1]:      ' + str(self.data.distance[-1]))

        self.data.distance_check()

        self.state = decide_state(self.state, self.data)
        (v_x, v_y, v_z, rate_yaw) = calculate_vel(self.state)

        self.mc._set_vel_setpoint(v_x, v_y, v_z, rate_yaw)
