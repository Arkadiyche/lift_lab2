from lift import Lift
from typing import List
from client import Client
from transact import Transact
from config import CAPACITY_LIFT, COUNT_LIFT, K_FLOOR, TIME, TIME_BETWEEN_FLOOR, TOTAL_FLOOR

class System:
    lift: List[Lift]

    queues: List[List[Client]]

    transacts: List[Transact]

    time = 0

    k = K_FLOOR
    liftMoveTime = TIME_BETWEEN_FLOOR
    numberOfFloors = TOTAL_FLOOR
    numberOfLifts = COUNT_LIFT
    endTime = TIME
    liftSize = CAPACITY_LIFT

    task = 2

    def __init__(self) -> None:
        self.lift = []
        self.queues = []
        self.transacts = []

    def addClient(self, transact: Transact):
        client = Client()
        client.targetFloor = transact.data.client.to
        client.startTime = self.time
        self.queues[transact.data.client.tFrom].append(client)





