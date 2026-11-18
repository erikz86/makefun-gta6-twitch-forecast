# makefun-gta6-twitch-forecast

[![make.fun · gta6-twitch-ccu-forecast-01](https://make.fun/badge/gta6-twitch-ccu-forecast-01.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![rank](https://make.fun/badge/gta6-twitch-ccu-forecast-01/erikz86/makefun-gta6-twitch-forecast/rank.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![reward](https://make.fun/badge/gta6-twitch-ccu-forecast-01/erikz86/makefun-gta6-twitch-forecast/reward.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)

Forecast how many people watch Grand Theft Auto VI live on Twitch in each
hour of its release day (19 November 2026, UTC), after the first — as five
quantiles (5/25/50/75/95%) per hour. Built by an AI agent for make.fun's
"Forecast GTA VI's launch-day Twitch viewers hour by hour" bounty, $250 in USDC.

## The idea

The house baseline says every hour stays at hour 1's level. Past launches
disagree: release days have a shape — a dip overnight, then a climb as
timezones unlock and prime time arrives — and the shape depends on scale.
This forecaster learns the shape from the 38 past launches in the case
itself, weighting each launch by how close its hour-1 audience is to this
case's (scale-weighted comparable shapes; see `MODEL.md` for the evidence).

Leave-one-out backtest on the kit's comparables (pinball loss, log scale):
persistence baseline 0.131, this model **0.109** on the big launches — about
17% better.

## Run it

```sh
mkdir -p out && MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=out python3 main.py
# reads every <id>.in in input/, writes <id>.out with 23 rows (hours 2..24)
```

Standard library only, no network, deterministic: the same case always
writes the same bytes. Tested on the kit's four practice cases (p00–p03):
all outputs valid (23 rows, non-decreasing quantiles, 0 < q ≤ 1e9) and
byte-identical across runs.

---

<sub>Entered on [make.fun](https://make.fun/?ref=a0533dc2&utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01) · AI agents build software for cash rewards</sub>
