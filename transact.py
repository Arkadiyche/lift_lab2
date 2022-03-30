import enum


class TransactType(enum.Enum):
    AddClient = "AddClient"
    MoveLift = "MoveLift"
    InOut = "InOut"

class Transact:
    type: TransactType
