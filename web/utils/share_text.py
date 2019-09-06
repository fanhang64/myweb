import time
import base64
import random
import string
from random import choice

from web.config import Config


def gen_share_code():
    r = []
    src = string.ascii_letters+"".join([str(x) for x in range(10)])
    while True:
        if len(r) > 16:
            return "".join(r)
        r.append(choice(src))
