from collections import deque

class Data(object):
    # 滤波权重
    FILTER_POWER = (14, 13, 12, 11, 10, 10, 9, 8, 7, 6)
    # 滤波权重和
    FILTER_SUM = 100

    # 节拍
    beat = 0

    # 原始距离信息
    raw_distance = deque([0]*100, maxlen=1000)
    # 可用的距离数据，已滤波
    distance = deque([0]*100, maxlen=1000)
    # 衡量距离在快速变化的量
    distance_rapid_changing = 0

    def update(self, timestamp, data, logconf):
        self.push_raw_distance(_data['ranging.distance0'])

        self.distance_check()
        self.next_beat()

    def push_raw_distance(self, raw_distance):
        self.raw_distance.append(raw_distance)

        history = [self.raw_distance[-x] for x in range(1, 11)]
        filter_result = 0

        for i in range(10):
            filter_result += history[i] * self.FILTER_POWER[i]
        filter_result /= self.FILTER_SUM

        self.distance.append(filter_result)

    def next_beat(self):
        self.beat += 1
        self.beat = self.beat % 1024

    def distance_check(self):
        # 失联处理
        if self.raw_distance[-1] == self.raw_distance[-2] and \
            self.raw_distance[-1] == self.raw_distance[-3] and \
                self.raw_distance[-1] == self.raw_distance[-4]:
            print(self.raw_distance)
            print('失联前的数据 ↑')
            raise Exception('无人机与 anchor 失联')

        # 距离快速变化
        if self.distance[-1] > \
            0.5 + (self.distance[-2] + self.distance[-3] +
                   self.distance[-4] + self.distance[-5]) / 4:
            if self.rapid_changing >= 5:
                self.rapid_changing = 7
            else:
                self.distance[-1] = self.distance[-2]
                self.rapid_changing += 2
        else:
            if self.rapid_changing > 0:
                self.rapid_changing -= 1
