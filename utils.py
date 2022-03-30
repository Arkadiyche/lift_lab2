import random
import math

def rand(time: float, interval: float):
    return random.uniform(time-interval, time+interval)


def stay_on_floor(lift_count: int, floor_count: int, exiting_count: int, entering_count: int):
    if exiting_count == 0 and entering_count == 0:
        return 0
    a = math.log2(exiting_count + entering_count + 2)
    b = math.log2(lift_count + floor_count + 4)
    r = random.uniform(a, b)
    return r
