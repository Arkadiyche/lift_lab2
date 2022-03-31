from config import TIME, K_FLOOR, TOTAL_FLOOR, COUNT_LIFT, CAPACITY_LIFT, TIME_BETWEEN_FLOOR
from system import System


if __name__ == '__main__':
    system = System()
    system.run()
    system.show()
