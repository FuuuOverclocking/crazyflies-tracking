import time

# 决定状态前采样时间，秒
STATE_DECIDE_TIME = 3
# 合适距离区间，米
OK_DISTANCE_FROM = 1
OK_DISTANCE_TO = 2


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
    else
        return 'approach'


def decide_state(last_state, data):
    state = last_state

    if state['global'] == 'unknown' or state['global'] == 'OK':
        if not state['should_keep']:
            state = state.copy()
            state['timer'] = time.perf_counter()
            state['beat_before_sampling'] = data.beat

        elif time.perf_counter() - state['timer'] > STATE_DECIDE_TIME:
            state = state.copy()
            state['sampling_data_number'] = data.beat - \
                state['beat_before_sampling']

            state['should_keep'] = False
            state['global'] = decide_global_state(
                data, state['sampling_data_number'])

    if state['global'] == 'approach':
        pass

    return state


def calculate_vel(state):
    pass


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

        'should_keep': False,
        'timer': 0,
        'beat_before_sampling': 0,
        'sampling_data_number': 0
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
            if self.init_counter == 500:
                self.inited = True

    def tick(self):
        if self.beat == data.beat:
            return
        self.beat = data.beat

        if not self.init():
            return

        self._tick()

    def _tick(self):
        # 函数式编程
        self.state = decide_state(self.state, self.data)
        (v_x, v_y, v_z, rate_yaw) = calculate_vel(self.state)

        self.mc._set_vel_setpoint(v_x, v_y, v_z, rate_yaw)
