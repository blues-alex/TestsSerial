#!/usr/bin/env python3

import json
import plotly.graph_objects as go


DELTA_LOG = '/tmp/delta_interpolations.json'
CYCLE_LOG = '/tmp/cycle.json'
TEST_HTML = '/tmp/test_meassures.html'

with open(CYCLE_LOG) as j:
    cycle = json.load(j)
with open(DELTA_LOG) as j:
    meassures = json.load(j)

fig = go.Figure()


fig.add_trace(
    go.Contours(
        x=[i[0] for i in cycle],
        y=[i[1] for i in cycle],
        line={"color": '#33FF33'},
        name="Generate cycle"
    )
)
fig.add_trace(
    go.Contours(
        x=[int(i) for i in meassures],
        y=[meassures[i][0][0] for i in meassures],
        line={"color": '#3333FF', "dash": "dash"},
        name="Interpolate cycle"
    )
)

fig.add_trace(
    go.Contours(
        x=[int(i) for i in meassures],
        y=[meassures[i][1][0] for i in meassures],
        line={"color": '#FF3333'},
        name="Controller GC"
    )
)

fig.write_html(TEST_HTML)

