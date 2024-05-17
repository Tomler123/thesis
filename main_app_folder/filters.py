import time

def timestamp_filter(filename):
    return f"{filename}?v={int(time.time())}"
