# -*- coding: utf-8 -*-
from typing import Any

from basehash import base62

base62 = base62(6)


def hash_base62(n: Any):
    return base62.hash(n)
