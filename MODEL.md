# Model — scale-weighted comparable shapes

## The problem

Forecast GTA VI's launch-day Twitch concurrent viewers for hours 2–24,
given only hour 1's print. The house baseline says every hour stays at hour
1's level with a spread that widens like a random walk (sigma 0.15 per
root-hour in log space). That ignores the one thing past launches agree on:
release days have a shape.

## What the data says

The kit ships 38 past launches ("comparables"), each with its release-day
hourly Twitch curve (SullyGnome hourly category averages). Two facts:

1. **Hour 1 is a bad anchor for small launches.** Rolling-midnight unlocks
   mean hour 1 (00:00–01:00 UTC) catches only a few timezones: Hollow Knight:
   Silksong had 164 viewers in hour 1 and 178,413 in hour 24. For the big
   launches the picture is different: ELDEN RING 875,155 in hour 1 and
   631,975 in hour 24; Cyberpunk 2077 851,999 → 465,734. Scale changes the
   shape, so the model must weight by scale.
2. **The shape is a timezone wave.** Across the big launches (hour-1
   audience ≥ 100k), the median curve dips overnight (hour 10 ≈ 0.51× hour
   1) and climbs through the day (hour 19 ≈ 1.25×) as timezones unlock and
   prime time arrives.

## The model

For each forecast hour h, take log(viewers(h) / viewers(1)) from every
comparable covering both hours, weighted by a Gaussian kernel on log hour-1
audience (bandwidth 1.5): launches near this case's scale dominate, distant
ones fade out. The five forecast quantiles are the weighted empirical
quantiles of those log ratios, applied to this case's hour-1 print. Under
five covering comparables, fall back to the baseline's persistence spread.
Standard library only; fully deterministic.

## Evidence (leave-one-out backtest, pinball loss on the log scale)

Each comparable predicted from the other 37, scored against its own
release-day actuals:

| Model | Pinball, big targets (h1 ≥ 100k) |
|---|---|
| Persistence baseline (house) | 0.131 |
| Median shape, peers ≥ 50k | 0.113 |
| **Scale-weighted shape (this entry)** | **0.109** |

About 17% better than the house baseline on the launches that resemble GTA
VI. The same ranking holds on all 37 launches (0.465 → 0.357).

## Limits

- The final case is GTA VI itself, whose hour-1 print the model has never
  seen; the kernel extrapolates from the largest peers (ELDEN RING,
  Cyberpunk 2077, Diablo IV, Hogwarts Legacy) if it exceeds them.
- SullyGnome samples small categories sparsely, so some comparables miss
  hours; the model only uses hours a comparable actually recorded.
- Unlock times differ per launch (rolling midnight vs. global); the shape
  is the median over many launches, not a claim about Rockstar's schedule.
