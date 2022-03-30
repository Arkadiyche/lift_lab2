import math

from config import TIME_BETWEEN_FLOOR, TIME
from config import TOTAL_FLOOR, CAPACITY_LIFT
from utils import stay_on_floor
from all_queues import AllQueues
EPS = 0.001

class States:
    STAYING = "staying"
    UP = "up"
    DOWN = "down"
    ENTERING = "entering"

class Lift(object):
    _current_floor: float
    _people: dict
    _time_between_floor: int
    _time: float
    _state: str
    _time_to_come: float
    _index: int

    def __init__(self, index):
        self._current_floor = 1
        self._people = {}
        for i in range(TOTAL_FLOOR):
            self._people[i+1] = 0
        self._time_between_floor = TIME_BETWEEN_FLOOR
        self._time = 0
        self._state = States.STAYING
        self._time_to_come = 0
        self._index = index

    def __str__(self):
        return f"Lift #{self._index} current floor {self._current_floor}"


    def goto_floor(self, floor: int):
        self._time = 0
        self._time_to_come = self._time_between_floor * floor
        if floor == 1:
            self._state = States.DOWN
        else:
            self._state = States.UP

    def enter_people(self, destinations):
        print(self, " enter people")
        for d in destinations:
            self._people[d] += 1

    def exit_people(self, floor: int):
        print(self, " высаживаю людей на ", floor, " этаже")
        exiting = self._people[floor]
        self._people[floor] = 0
        return exiting

    def get_people_in_lift(self):
        sum = 0
        for p in self._people.keys():
            sum += self._people[p]
        return sum

    def closest_floor(self):
        min = TOTAL_FLOOR
        closest = 0
        for key in AllQueues.queue.keys():
            if not AllQueues.queue[key].empty() and min > math.fabs(self._current_floor - key):
                min = math.fabs(self._current_floor - key)
                closest = key
        return closest

    def get_time_to_next_floor(self):
        if self._current_floor % 1 == 0:
            return TIME
        if self._state == States.UP:
            return (math.ceil(self._current_floor) - self._current_floor) / TIME_BETWEEN_FLOOR
        if self._state == States.DOWN:
            return (self._current_floor - math.floor(self._current_floor)) / TIME_BETWEEN_FLOOR
        return TIME


    def step(self, time: float):
        if self._time != 0:
            self._time -= time
            return
        closest_floor = self.closest_floor()
        if self.get_people_in_lift() == 0 and closest_floor != 0:
            if closest_floor - self._current_floor >= 0:
                self._state = States.UP
            else:
                self._state = States.DOWN
        if self.get_people_in_lift() == 0 and closest_floor == 0:
            return
        if self._current_floor % 1 <= EPS:
            people_in_lift = self.get_people_in_lift()
            exiting = self.exit_people(int(self._current_floor / 1))
            free_seats = CAPACITY_LIFT - people_in_lift
            list_people = []
            current_queue = AllQueues.queue[int(self._current_floor / 1)]
            people_on_floor = current_queue.len()
            while free_seats != 0 and not current_queue.empty():
                list_people.append(current_queue.pop())
                free_seats -= 1
            self.enter_people(list_people)
            self._time = stay_on_floor(people_in_lift, people_on_floor, exiting, len(list_people))
            return
        if self._state == States.UP and self._current_floor < TOTAL_FLOOR:
            print(self, " going up")
            self._current_floor += time / self._time_between_floor
        elif self._current_floor > 1:
            print(self, " going down")
            self._current_floor -= time / self._time_between_floor





