import itertools
import threading
from time import perf_counter


class FastWriteCounter(object):
    """
    https://github.com/jd/fastcounter
    https://julien.danjou.info/atomic-lock-free-counters-in-python/
    """

    __slots__ = (
        "_number_of_read",
        "_counter",
        "_lock",
        "_step",
    )

    def __init__(self, init=0, step=1):
        self._number_of_read = 0
        self._step = step
        self._counter = itertools.count(init, step)
        self._lock = threading.Lock()

    def increment(self):
        next(self._counter)

    @property
    def value(self):
        with self._lock:
            value = next(self._counter) - self._number_of_read
            self._number_of_read += self._step
        return value


class Metrics:
    START_TIME = perf_counter()
    TOTAL_REQUESTS = FastWriteCounter()
