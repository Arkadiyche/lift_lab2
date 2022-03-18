from .config import TIME, TOTAL_FLOOR

from .queue import Queue
if __name__ == '__main__':
    timer = 0

    queue = [Queue(i+1) for i in range(TOTAL_FLOOR)]
