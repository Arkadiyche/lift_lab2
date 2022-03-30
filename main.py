from config import TIME, TOTAL_FLOOR, COUNT_LIFT
from all_queues import AllQueues
from lift import Lift
from my_queue import MyQueue

if __name__ == '__main__':
    timer = 0
    queue = {}
    for i in range(TOTAL_FLOOR):
        queue[i + 1] = MyQueue(i + 1)
    AllQueues.queue = queue
    lifts = []
    for i in range(COUNT_LIFT):
        lifts.append(Lift(i))

    while timer < TIME:
        min_next = TIME
        for q in AllQueues.queue.keys():
            for t in AllQueues.queue[q]._timer.keys():
                if min_next > AllQueues.queue[q]._timer[t] and AllQueues.queue[q]._timer[t] != 0:
                    min_next = AllQueues.queue[q]._timer[t]
        for lift in lifts:
            if min_next > lift._time and lift._time != 0:
                min_next = lift._time
            if min_next > lift.get_time_to_next_floor():
                min_next = lift.get_time_to_next_floor()
        print(min_next)
        for lift in lifts:
            lift.step(min_next)
        for q in AllQueues.queue.keys():
            AllQueues.queue[q].step(min_next)
        timer += min_next
