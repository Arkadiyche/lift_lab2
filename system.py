from hashlib import new
import math
from pydoc import cli
import queue
import random
from time import time
from lift import Lift
from typing import List
from client import Client
from transact import Transact, TransactType
from config import CAPACITY_LIFT, COUNT_LIFT, K_FLOOR, TIME, TIME_BETWEEN_FLOOR, TOTAL_FLOOR


class Stats:
    totalClientsMoved: int
    totalWaitTime: int
    totalPeople: int

    def __init__(self):
        self.totalClientsMoved = 0
        self.totalWaitTime = 0
        self.totalPeople = 0

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

    stats: Stats

    def __init__(self) -> None:
        self.lifts = []
        for i in range(self.numberOfLifts):
            self.lifts.append(Lift())
        self.queues = []
        for i in range(self.numberOfFloors):
            cls: List[Client] = []
            self.queues.append(cls)
        self.transacts = []
        self.stats = Stats()

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
            newTransact.endTime = self.time + 60. / math.log2(self.k)
        else:
            newTransact.endTime = self.time + 60. / math.log2(target + 1)

        self.transacts.append(newTransact)

    def liftArrived(self, transact: Transact):
        floor = transact.data.lift.floor
        liftIndex = transact.data.lift.index
        goOut = self.lifts[liftIndex].goOutOnFloorCount(floor)
        liftTotal = self.lifts[liftIndex].total()
        goIn = len(self.queues[floor])
        if liftTotal - goOut + goIn > self.liftSize:
            goIn = self.liftSize - (liftTotal - goOut)

        self.stats.totalClientsMoved += goOut

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
        for i in range(goIn):
            self.stats.totalWaitTime += self.time - self.queues[floor][i].startTime
            self.stats.totalPeople += 1
        del self.queues[floor][0:goIn]

    def inOutAndMoveLift(self, transact: Transact):
        lift = transact.data.lift
        floor = lift.floor
        liftIndex = lift.index

        floorAboveFound = False
        targetFloor = len(self.queues)
        if self.lifts[liftIndex].movingUp:

            for client in self.lifts[liftIndex].clients:
                if client.targetFloor > floor and client.targetFloor < targetFloor:
                    targetFloor = client.targetFloor
                    floorAboveFound = True

            if self.task != 2:
                f = floor + 1
                while f < targetFloor:
                    if len(self.queues[f]):
                        targetFloor = f
                        floorAboveFound = True
                        break
                    f += 1

        if not floorAboveFound or not self.lifts[liftIndex].movingUp:
            self.lifts[liftIndex].movingUp = False
            targetFloor = 0
            for client in self.lifts[liftIndex].clients:
                if client.targetFloor > floor and client.targetFloor < targetFloor:
                    targetFloor = client.targetFloor
            
            f = floor - 1
            while f >= targetFloor:
                if len(self.queues[f]):
                    targetFloor = f
                    break
                f -= 1
            if targetFloor == 0:
                self.lifts[liftIndex].movingUp = True

        newTransact = Transact()
        newTransact.type = TransactType.MoveLift
        newTransact.data.lift.index = transact.data.lift.index
        newTransact.data.lift.floor = targetFloor
        newTransact.startTime = self.time
        newTransact.endTime = self.time + self.liftMoveTime * abs(targetFloor - floor)
        self.transacts.append(newTransact)

    def run(self):
        i = 1
        while i < len(self.queues):
            d = self.k if i + 1 > self.k else i
            newTransact = Transact()
            newTransact.type = TransactType.AddClient
            newTransact.data.client.tFrom = 0
            newTransact.data.client.to = i
            newTransact.startTime = self.time
            newTransact.endTime = self.time + 60./math.log2(d + 1)
            self.transacts.append(newTransact)
            newTransact2 = Transact()
            newTransact2.type = TransactType.AddClient
            newTransact2.data.client.tFrom = i
            newTransact2.data.client.to = i - 1
            newTransact2.startTime = self.time
            newTransact2.endTime = self.time + 60./math.log2(d + 1)
            self.transacts.append(newTransact2)
            i += 1

        i = 0
        while i < len(self.lifts):
            newTransactLift = Transact()
            newTransactLift.type = TransactType.MoveLift
            newTransactLift.data.lift.floor = 0
            newTransactLift.data.lift.index = i
            newTransactLift.startTime = self.time
            newTransactLift.endTime = self.time + 60
            self.transacts.append(newTransactLift)
            i += 1

        while self.time < self.endTime:
            handled: int = 0
            for transact in self.transacts:
                if transact.endTime > self.time:
                    break
                handled += 1
                if transact.type == TransactType.AddClient:
                    self.addClient(transact)
                elif transact.type == TransactType.MoveLift:
                    self.liftArrived(transact)
                elif transact.type == TransactType.InOut:
                    self.inOutAndMoveLift(transact)
                else:
                    print("error")
                    break
            del self.transacts[0:handled]
            self.transacts = sorted(self.transacts, key=lambda t: t.endTime)
            self.time = self.transacts[0].endTime

    def show(self):
        print(self.stats.totalClientsMoved)
        print(float(self.stats.totalWaitTime) / float(self.stats.totalPeople))

