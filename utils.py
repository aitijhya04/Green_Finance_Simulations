"""Utility functions and constants"""
import random
import string
import uuid
from datetime import datetime, timedelta

RNG = random.Random(12345)

def make_id(prefix='', length=6):
    chars = string.ascii_uppercase + string.digits
    return prefix + ''.join(RNG.choices(chars, k=length))


def now():
    return datetime.now()