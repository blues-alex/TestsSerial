# by blues

from os import path
from time import time


def logger(func, name, file_name, args=None, mode=None):
    start_time = time()
    if args:
        result = func(args, mode=mode)
    else:
        result = func()
    log_string = f"Function name: {name}\nElapsed time: {time()-start_time}\nResult: {result}\nArgs :{args}"
    if path.isfile(file_name):
        mod = "a"
    else:
        mod = "w"
    with open(file_name, mod) as file:
        file.write(log_string)
    print(log_string)
