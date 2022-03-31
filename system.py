from hashlib import new
import math
import queue
from random import random
from time import time
from lift import Lift
from typing import List
from client import Client
from transact import Transact, TransactType
from config import CAPACITY_LIFT, COUNT_LIFT, K_FLOOR, TIME, TIME_BETWEEN_FLOOR, TOTAL_FLOOR

class System:
    lifts: List[Lift]

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

        newTransact = Transact()

        newTransact.data = transact.data

        newTransact.type = transact.type

        newTransact.startTime = self.time

        target = max(transact.data.client.to, transact.data.client.tFrom)

        if target + 1 > self.k:
            newTransact.endTime = time + 60. / math.log2(self.k)
        else:
            newTransact.endTime = time + 60. / math.log2(target + 1)

        self.transacts.append(newTransact)

    def liftArrived(self, transact: Transact):
        floor = transact.data.lift.floor
        liftIndex = transact.data.lift.index
        goOut = self.lifts[liftIndex].goOutOnFloorCount(floor)
        liftTotal = self.lifts[liftIndex].total()
        goIn = len(self.queues[floor])
        if liftTotal - goOut + goIn > self.liftSize:
            goIn = self.liftSize - (liftTotal - goOut)

        # TODO запись статистики stats.totalMoved += goOut

        newTransact = Transact()
        newTransact.data = transact.data
        newTransact.type = TransactType.InOut
        newTransact.startTime = self.time
        newTransact.endTime = self.time + random.uniform(math.log2(goOut + goIn + 2), math.log2(liftTotal + len(self.queues[floor]) + 2))
        self.transacts.append(newTransact)

        clients = self.lifts[liftIndex].clients

        i = 0

        while i < len(clients):
            if clients[i].targetFloor == floor:
                clients.pop(i)
                i -= 1
            i += 1

        i = 0

        while i < goIn:
            self.lifts[liftIndex].clients.append(self.queues[floor][i])
            i += 1

        del self.queues[floor][0:goIn]
