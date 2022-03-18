from config import TIME_BETWEEN_FLOOR
from config import  TOTAL_FLOOR

class States:
    STAYING = "staying"
    UP = "up"
    DOWN = "down"

class Lift(object):
    _current_floor: int
    _people: dict
    _time_between_floor: int
    _time: float
    _state: str
    _time_to_come: float

    def __init__(self):
        self._current_floor = 1
        self._people = {}
        for i in range(TOTAL_FLOOR):
            self._people[i+1] = 0
        self._time_between_floor = TIME_BETWEEN_FLOOR
        self._time = 0
        self._state = States.STAYING
        self._time_to_come = 0


    def goto_floor(self, floor: int):
        self._time = 0
        self._time_to_come = self._time_between_floor * floor
        if floor == 1:
            self._state = States.DOWN
        else:
            self._state = States.UP

    def enter_people(self, destinations):
        for d in destinations:
            self._people[d] += 1

    def exit_people(self, floor: int):
        self._people[floor] = 0

    def stay_on_floor(self):


