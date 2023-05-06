#!/usr/bin/env python3

import time
import sys
import json
# import random
from LMInterface import *
from loguru import *
# import plotly.graph_objects as go

DELTA_LOG = '/tmp/delta_interpolations.json'
CYCLE_LOG = '/tmp/cycle.json'

# fig = go.FigureWidget()
# fig.add_scatter()


handler = LMHandler()

# Make cycle "saw" 78 points, in range(0-100 %%) of all channels
LENGTH = 48
TIME_STEP = (60 * 24) // (LENGTH + 1)
HIGHT_EMISSION = 40
NULL_EMISSION = 0
TIMEOUT = 5
# DAYTIME = 60*24


def gen_cycle():
    state = HIGHT_EMISSION
    cycle = []
    tss = []
    for i in range(1, LENGTH + 1, 1):
        # ts = f"{i*TIME_STEP//60:02d}{i*TIME_STEP%60:02d}"
        # fig.update()
        cycle.append(
            [i * TIME_STEP] + [state] * 12
        )
        if state == HIGHT_EMISSION:
            state = NULL_EMISSION
        else:
            state = HIGHT_EMISSION
        tss.append(i * TIME_STEP)
        # fig.data[0].y = [i[1] for i in cycle]
        # fig.data[0].x = [i[0] for i in cycle]
    return cycle


def get_interpolate_channels(ts, cycle) -> list:
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
    print(gt)
    hh = int(gt[:2])
    mm = int(gt[2:])
    minutes = (hh * 60) + mm
    seconds = minutes * 60
    # logger.info(f"{hh:02d}:{mm:02d}, {minutes = }, {seconds = }")
    return seconds


t = time.monotonic()

cycle = gen_cycle()
# fig.show()
with open(CYCLE_LOG, 'w') as j:
    json.dump(
        [[i[0] * 60] + i[1:] for i in cycle],
        j
    )

print(f"Start writting cycle: {time.monotonic() - t}")
if not handler.writeCycle(cycle=[[f"{i[0]//60:02d}{i[0]%60:02d}"] + i[1:] for i in cycle]):
    sys.exit(1)
logger.success(f"Done writting: {time.monotonic() - t}")
# logger.info(str(wc))
# logger.info(f'ST: {TIME_STEP*3//60:02d}{TIME_STEP*3%60:02d}00000000')
handler.ST(f'{TIME_STEP*3//60:02d}{TIME_STEP*3%60-1:02d}00000000')
tm = time.monotonic()
current_time = TIME_STEP * 3 * 60 - 60
tm_start = tm - current_time
ct = handler.GT()['mess'][:3]
print(
    f"Controll time: "
    f"{int(ct[:1]):02d}:{int(ct[2:]):02d} ({int(ct[:1]) * 60 + int(ct[2:])}), "
    f"{tm_start}, {tm}, {tm-tm_start}"
)
time.sleep(1)
current_time += 1
# meassures = {}
with open(DELTA_LOG, 'w') as j:
    interpolate_chns = get_interpolate_channels(current_time, cycle)
    chns = [(10000 - int(i)) / 100 for i in handler.GC()['mess'].split(b'\x1f')]
    j.write(f"{{\"{current_time}\":["
            f"{interpolate_chns},"
            f"{chns}]" + "}"
            )

while True:
    interpolate_chns = get_interpolate_channels(current_time, cycle)
    gt = get_controller_ts()
    chns = [(10000 - int(i)) / 100 for i in handler.GC()['mess'].split(b'\x1f')]
    print(f"\x1b[0;33m{current_time}: \x1b[0;32m{interpolate_chns}\x1b[0m")
    print(f"\x1b[0;33m{gt}: \x1b[0;34m{chns}\x1b[0m")
    with open(DELTA_LOG, 'a') as j:
        j.seek(j.truncate(j.tell() - 1))
        # meassures[current_time] = [interpolate_chns, chns]
        j.write(f",\"{current_time}\":[{interpolate_chns},{chns}]")
        j.write("}")
    # print(meassures)
    time.sleep(TIMEOUT)
    current_time += TIMEOUT
