import os
import time


def cleanup_temp(folder="temp", max_age=60):
    now = time.time()
    for f in os.listdir(folder):
        path = os.path.join(folder, f)
        if os.path.isfile(path) and now - os.path.getmtime(path) > max_age:
            os.remove(path)
