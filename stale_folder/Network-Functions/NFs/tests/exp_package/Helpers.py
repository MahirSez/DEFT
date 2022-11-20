import time

def get_current_time_in_ms():
    return time.time_ns() // 1_000_000