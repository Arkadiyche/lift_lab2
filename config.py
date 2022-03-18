import os
from dotenv import load_dotenv

load_dotenv()

TOTAL_FLOOR = os.getenv('TOTAL_FLOOR', default=2)
K_FLOOR = os.getenv('K_FLOOR', default=1)
TIME = os.getenv('TIME', default=2)
COUNT_LIFT = os.getenv('COUNT_LIFT', default=1)
CAPACITY_LIFT = os.getenv('CAPACITY_LIFT', default=1)
TIME_BETWEEN_FLOOR = os.getenv('TIME_BETWEEN_FLOOR', default=1)





    
