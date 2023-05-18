#!/usr/bin/env python3

import time
import sys
import json
import random
from LMInterface import *
from loguru import *
# import plotly.graph_objects as go

DELTA_LOG = '/tmp/delta_interpolations.json'
CYCLE_LOG = '/tmp/cycle.json'

# fig = go.FigureWidget()
# fig.add_scatter()


handler = LMHandler()

# Make cycle "saw" 78 points, in range(0-100 %%) of all channels
LENGTH = 78
TIME_STEP = (60 * 24) // (LENGTH + 1)
OFFSET = (60 * 60 * 24) - 120  # offset time of start test in seconds
HIGHT_EMISSION = 40
NULL_EMISSION = 0
TIMEOUT = 5  # random timeout requests in range
# DAYTIME = 60*24


def get_timeline(length) -> list:
    ts = 0
    for n in range(length):
        _range = (60 * 24 - ts) // (length - n)
        print(f"{_range = }")
        ts += random.randint(1, _range)
        if ts < (60 * 24):
            yield ts


def gen_cycle():
    state = HIGHT_EMISSION
    cycle = []
    for i in get_timeline(LENGTH):
        cycle.append(
            [i] + [state * random.random()] * 12
        )
        if state == HIGHT_EMISSION:
            state = NULL_EMISSION
        else:
            state = HIGHT_EMISSION
    return cycle

# def gen_cycle():
#     cycle = []
#     for i in range(0, LENGTH, 3):
#         cycle.append(
#             [i * TIME_STEP] + [HIGHT_EMISSION] * 12
#         )
#         cycle.append(
#             [round((i + 1.5) * TIME_STEP)] + [HIGHT_EMISSION] * 12
#         )
#         cycle.append(
#             [round((i + 1.5) * TIME_STEP) + 1] + [NULL_EMISSION] * 12
#         )
#         cycle.append(
#             [(i + 3) * TIME_STEP - 1] + [NULL_EMISSION] * 12
#         )
#     return cycle


def get_interpolate_channels(ts, cycle) -> list:
    if (ts / 60) > cycle[-1][0] or (ts / 60) < cycle[0][0]:
        if (ts / 60) < cycle[0][0]:
            delta_time = (((60 * 60 * 24) - cycle[-1][0] * 60) + ts)
        else:
            delta_time = ts - cycle[-1][0] * 60
        angle = (cycle[-1][1] - cycle[0][1]) / (((60 * 60 * 24) - (cycle[-1][0] * 60)) + (cycle[0][0] * 60))
        return [round(abs(cycle[-1][1] + (delta_time * angle)), 2)] * 12
    else:
        for n, p in enumerate(cycle):
            next_point = cycle[n + 1]
            if next_point[0] * 60 > ts:
                # print(p, next_point)
                delta = ts - p[0] * 60
                angle = (next_point[1] - p[1]) / ((next_point[0] * 60) - (p[0] * 60))
                # print(f"{delta =}, {angle =}")
                return [round(p[1] + (delta * angle), 2)] * 12


def get_controller_ts() -> int:
    gt = handler.GT()['mess'][:4]
    # print(gt)
    hh = int(gt[:2])
    mm = int(gt[2:])
    # ss = int(gt[4:])
    minutes = (hh * 60) + mm
    seconds = minutes * 60  # + ss
    # logger.info(f"{hh:02d}:{mm:02d}, {minutes = }, {seconds = }")
    return seconds


t = time.monotonic()

cycle = gen_cycle()

with open(CYCLE_LOG, 'w') as j:
    json.dump(
        [[i[0] * 60] + i[1:] for i in cycle],
        j
    )

tm = time.monotonic()
# current_time = TIME_STEP * (LENGTH) * 60 - 60
current_time = OFFSET
logger.info(f"SetTime: {current_time//60//60:02d}{current_time//60%60:02d}00000000")

handler.ST(f'{current_time//60//60:02d}{current_time//60%60:02d}00000000')
tm_start = tm - current_time

ct = handler.GT()['mess'][:4]
print(
    f"Controll time: "
    f"{int(ct[:1]):02d}:{int(ct[2:]):02d} ({int(ct[:1]) * 60 + int(ct[2:])}), "
    f"{tm_start}, {tm}, {tm-tm_start}"
)

print(f"Start writting cycle: {time.monotonic() - t}")
if not handler.writeCycle(cycle=[[f"{i[0]//60:02d}{i[0]%60:02d}"] + i[1:] for i in cycle]):
    sys.exit(1)
logger.success(f"Done writting: {time.monotonic() - t}")
gc = [
    (10000 - int(i)) / 100
    for i in handler.GC()['mess'].split(b'\x1f')
]
logger.info(f"Controll GC: {gc}")

current_time = get_controller_ts()

with open(DELTA_LOG, 'w') as j:
    interpolate_chns = get_interpolate_channels(current_time, cycle)
    chns = [(10000 - int(i)) / 100 for i in handler.GC()['mess'].split(b'\x1f')]
    j.write(f"{{\"{current_time}\":["
            f"{interpolate_chns},"
            f"{chns}]" + "}"
            )
timers = []
time.sleep(5)
while True:
    # gt = get_controller_ts()
    if time.monotonic() - tm_start > (60 * 60 * 24):
        tm_start += (60 * 60 * 24)
    current_time = time.monotonic() - tm_start
    interpolate_chns = get_interpolate_channels(current_time, cycle)
    # ct = time.monotonic()
    chns = [(10000 - int(i)) / 100 for i in handler.GC()['mess'].split(b'\x1f')]
    # print(ct - time.monotonic())
    print(f"Int-e:\t[{round(current_time)}]\t{interpolate_chns}")
    print(f"Cntrl:\t[{get_controller_ts()}]\t{chns}\n")
    with open(DELTA_LOG, 'a') as j:
        j.seek(j.truncate(j.tell() - 1))
        j.write(f",\"{round(current_time)}\":[{interpolate_chns},{chns}]")
        j.write("}")
    timeout = random.randint(0, TIMEOUT)
    timers.append(timeout)
    time.sleep(timeout)
    print(f"Intermediate timeout: {sum(timers)/len(timers)}")
    # current_time += timeout
