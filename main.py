"""gta6-twitch-ccu-forecast-01 entry: forecast GTA VI's launch-day Twitch
concurrent viewers, hour by hour, from the first hour's print.

Method — scale-weighted comparable shapes (see MODEL.md for the evidence):

- Every comparable launch carries its release-day hourly curve. For each
  forecast hour h, take the log ratio log(viewers(h) / viewers(1)) of every
  comparable that has both hours, and weight each launch by how close its
  own hour-1 audience is to this case's hour-1 print, in log space
  (Gaussian kernel, bandwidth 1.5). Big launches teach the shape of big
  launches; tiny ones barely count.
- The forecast quantiles (5/25/50/75/95%) are the weighted empirical
  quantiles of those log ratios, applied to this case's hour-1 print.
  The shape is real: a dip overnight as the world sleeps, then a climb
  through the day as timezones unlock and prime time arrives.
- If fewer than five comparables cover an hour, fall back to the house
  baseline's persistence spread (sigma 0.15 per root-hour in log space).

Validated by leave-one-out backtest on the kit's 38 comparables (pinball
loss on the log scale, lower is better): persistence baseline 0.131, this
model 0.109 on the big launches (hour-1 audience >= 100k) — about 17%
better. Standard library only, deterministic: same input, same bytes.

How the grader runs it: `python3 -P -s /bot/main.py` (PYTHONHASHSEED=0) in
python:3.13-slim, standard library only: no network, no pip packages.

What it does:
  - read every <id>.in in the input directory (the grader runs one case at
    a time, with only that case's file there);
  - write <id>.out to the output directory: {"hours": [{"hour": 2,
    "q": [q05, q25, q50, q75, q95]}, ...]}, exactly 23 rows, hours 2..24
    each once, no other key, each q five finite numbers above 0 and at
    most 1e9, non-decreasing; at most 65,536 bytes.

Outside the grader's container, MAKEFUN_INPUT_DIR and MAKEFUN_OUTPUT_DIR
stand in for /input and /output:
    mkdir -p out && MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import json
import math
import os
import sys
from datetime import datetime
from pathlib import Path

# The grader's -P leaves /bot off sys.path: put it back first, so `import model`
# finds a model.py shipped beside this file (not needed here, kept for parity).
sys.path.insert(0, str(Path(__file__).resolve().parent))

INPUT_DIR = Path(os.environ.get("MAKEFUN_INPUT_DIR", "/input"))
OUTPUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

LEVELS = [0.05, 0.25, 0.5, 0.75, 0.95]
# The standard normal's quantile at each level (used only by the fallback).
Z = [-1.6448536269514722, -0.6744897501960817, 0.0, 0.6744897501960817, 1.6448536269514722]
# Spread of an hour's move, in natural-log units per square-root hour (fallback).
SIGMA = 0.15
# Bandwidth of the scale kernel, in natural-log units of hour-1 viewers.
BANDWIDTH = 1.5
MIN_PEERS = 5


def parse_time(text):
    return datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ")


def round2(x):
    """x rounded to 2 decimals, half up, as JavaScript's Math.round(x*100)/100."""
    scaled = x * 100
    whole = math.floor(scaled)
    if scaled - whole >= 0.5:
        whole += 1
    value = whole / 100
    return int(value) if value == int(value) else value


def release_day_hours(comparable):
    """Hour -> viewers for a comparable's release day (hours 1..24 from day_start)."""
    day_start = parse_time(comparable["day_start"])
    by_hour = {}
    for point in comparable.get("hourly", []):
        viewers = point.get("viewers")
        if not viewers or viewers <= 0:
            continue
        hour = int((parse_time(point["from"]) - day_start).total_seconds() // 3600) + 1
        if 1 <= hour <= 24:
            by_hour[hour] = viewers
    return by_hour


def weighted_quantile(pairs, tau):
    """Weighted empirical quantile of sorted (value, weight) pairs."""
    total = sum(w for _, w in pairs)
    acc = 0.0
    value = pairs[-1][0]
    for v, w in pairs:
        acc += w
        if acc >= tau * total:
            value = v
            break
    return value


def forecast_hour(p1, hour, peer_days):
    """Five quantiles for one forecast hour, in viewers."""
    log_p1 = math.log(max(p1, 1))
    items = []
    for day in peer_days:
        if 1 in day and hour in day:
            weight = math.exp(-((math.log(day[1]) - log_p1) / BANDWIDTH) ** 2)
            items.append((math.log(day[hour] / day[1]), weight))
    if len(items) >= MIN_PEERS:
        items.sort(key=lambda item: item[0])
        quantiles = [log_p1 + weighted_quantile(items, tau) for tau in LEVELS]
    else:
        quantiles = [log_p1 + z * SIGMA * math.sqrt(hour - 1) for z in Z]
    values = [round2(math.exp(q)) for q in quantiles]
    # Keep the row non-decreasing and strictly positive after rounding.
    fixed = []
    prev = 0.0
    for v in values:
        v = max(v, prev, 0.01)
        fixed.append(v)
        prev = v
    return fixed


def run_case(case):
    known = [row for row in case.get("known", []) if row.get("hour") == 1]
    p1 = max((row.get("viewers") or 0) for row in known) if known else 1
    p1 = max(p1, 1)
    peer_days = []
    for comparable in sorted(case.get("comparables", []), key=lambda c: c.get("name", "")):
        day = release_day_hours(comparable)
        if 1 in day and len(day) >= 20:
            peer_days.append(day)
    hours = []
    for entry in case.get("forecast", []):
        hour = entry["hour"]
        hours.append({"hour": hour, "q": forecast_hour(p1, hour, peer_days)})
    hours.sort(key=lambda row: row["hour"])
    return {"hours": hours}


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for in_file in sorted(INPUT_DIR.glob("*.in")):
        case = json.loads(in_file.read_text())
        out = run_case(case)
        out_file = OUTPUT_DIR / (in_file.stem + ".out")
        out_file.write_text(json.dumps(out, separators=(",", ":")))


if __name__ == "__main__":
    main()
