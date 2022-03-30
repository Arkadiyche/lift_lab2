from client import Client
from typing import List


class Lift:
    movingUp: bool
    clients: List[Client]

    def __init__(self):
        self.movingUp = True
        self.clients = []

    def total(self):
        return len(self.clients)

    def goOutOnFloorCount(self, target: int):
        count = 0
        for client in self.clients:
            if client.targetFloor == target:
                count += 1
        return count