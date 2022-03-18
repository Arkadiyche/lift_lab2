from .config import K_FLOOR, TOTAL_FLOOR
import math

class Queue(object):
    _time: float
    _floor: float
    _list: list[int]
    _intensity: dict
    _interval: dict
    _timer: dict
    _activate: bool
    _timer: float

    def __init__(self, floor: float):
        self._time = 0
        self._floor = floor
        self._list = []
        if self._floor == 1:
            for i in range(TOTAL_FLOOR):
                self._intensity[i+1] = math.log2(self._floor) if self._floor < K_FLOOR else math.log2(K_FLOOR) # per min
                self._intensity[i+1] *= 60  # per sec
                self._interval[i+1] = 1 / self._intensity
                self._timer[i+1] = self._interval[i+1]

        else:
            self._intensity[1] = math.log2(self._floor) if self._floor < K_FLOOR else math.log2(K_FLOOR)
            self._intensity[1] *= 60  # per sec
            self._interval[1] = 1 / self._intensity
            self._timer[1] = self._interval[1]
        self._activate = False

    def len(self):
        return len(self._list)

    def empty(self):
        return len(self._list) == 0

    def pop(self):
        chel = self._list.pop(0)
        if self.empty:
            self._activate=False
        return chel

    def step(self, time: float):
        self._time += time
        for key in self._timer.keys():
            self._timer[key] -= time
            if self._timer[key] <= 0:
                self._timer[key] = self._interval[key]
                self._list.append(key)
                self._activate = True
