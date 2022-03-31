import enum


class TransactType(enum.Enum):
    AddClient = "AddClient"
    MoveLift = "MoveLift"
    InOut = "InOut"

class trClient:
    tFrom: int
    to: int

    def __init__(self):
        self.tFrom = 0
        self.to = 0

class trLift:
    index: int
    floor: int

    def __init__(self):
        self.index = 0
        self.floor = 0

class Data:
    client: trClient
    lift: trLift

    def __init__(self):
        self.client = trClient()
        self.lift = trLift()


class Transact:
    type: TransactType
    data: Data
    startTime: float
    endTime: float

    def __init__(self):
        self.data = Data()
        self.startTime = 0.
        self.endTime = 0.
