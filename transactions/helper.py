from datetime import datetime
from random import random

def generate_id(base):
    today= datetime.today()
    id = str(today.year) + str(today.microsecond) + str(today.second)
    _,nums = str(random() * 10000).split('.')
    id = str(int(id) + int(nums) + today.minute )
    return base + id