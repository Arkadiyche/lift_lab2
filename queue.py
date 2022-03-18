from .config import K_FLOOR

class Queue(object):
    _floor: float
    _list: int
    _intensity: float
    _activate: bool

    def __init__(self, floor: float):
        self._floor = floor
        self._list = []
        self._intensity = 