# Data notes

These are my notes from exploring Elexon's data before building anything. I looked at one day (27 Oct 2026) from each candidate dataset and checked the real values.

## What I chose for version 1

| Need | Dataset | Endpoint |
|---|---|---|
| Generation | AGPT (B1620) | `/datasets/AGPT` |
| Demand | INDO and ITSDO | `/demand/outturn` |
| Price | MID, APX provider only | `/balancing/pricing/market-index` |

## Why AGPT and not FUELHH

- FUELHH has no solar.
- FUELHH only covers plants on the transmission grid. When I compared both for 27 Oct, gas and nuclear matched closely, but FUELHH wind was 2-4 GW lower. AGPT seems to include small wind farms on the distribution grid.
- Adding AGPT's solar to FUELHH would mix two scopes: small solar counted, small wind not. Wind answers would come out about 20% too low.
- What I lose: FUELHH splits gas into CCGT and OCGT and shows interconnector flows by country. I can add it later as a separate table if needed.

## Things to watch out for

- The "to" date is inclusive, so a one-day request returns one extra half-hour from the next day.
- `/generation/actual/per-type` is down-sampled for longer periods. I'll use `/datasets/AGPT` instead.
- AGPT values are nested inside each half-hour and need flattening.
- MID has rows from N2EX with price 0 and volume 0. That is not a real price. I keep APX only and drop rows with volume 0.
- `settlementDate` is the UK local date, `startTime` is UTC. In summer a UK day starts at 23:00 UTC the day before. Clock-change days have 46 or 50 half-hours.
- Generation and demand are in MW (average power over the half-hour). Energy in MWh = MW x 0.5.

## Left out for now

- ATL: only 27 of 48 half-hours came back for 27 Oct. Not explained yet.
- System prices: these are imbalance prices, not the market price.
- NESO embedded wind and solar: possible later. It would add a new package, a new source and a different licence.

## Still to check

- How `/datasets/AGPT` works for longer periods (parameters, limits).
