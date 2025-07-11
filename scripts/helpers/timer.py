import time
class Timer:
    def __init__(self):
        self.start = time.perf_counter()

    def get_elapsed(self):
        return int((time.perf_counter() - self.start) * 1000 + 0.5)

