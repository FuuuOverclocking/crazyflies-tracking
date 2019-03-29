def decide_state(last_state, data):
    pass

def vel_calculator(state):
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
        'global': 'unknown'
    }

    def __init__(self, data, mc):
        this.data = data
        this.mc = mc
    
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
        (v_x, v_y, v_z, rate_yaw) = vel_calculator(self.state)

        self.mc._set_vel_setpoint(v_x, v_y, v_z, rate_yaw)
