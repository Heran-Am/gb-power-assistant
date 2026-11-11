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



## AGPT raw endpoint (checked 11 Nov 2026)

- `/datasets/AGPT` only filters by publish time (`publishDateTimeFrom`, `publishDateTimeTo`). Settlement dates are not accepted.
- Data is published about 2.5 hours after each half-hour starts (2h29m on 27 Oct, very stable).
- So asking for one publish day gives the end of the previous day and misses the end of the day I want. I ask for a wider window (+12 hours) and keep only the settlement date I need.
- Result for 27 Oct: 528 rows = 48 half-hours x 11 types, no duplicates, no missing half-hours, only revision 1.
- The rows are flat (one row per half-hour and type), unlike the down-sampled endpoint.
- I didn't see any revisions, but the column exists. The loader should stop with an error if the same half-hour and type appears twice, instead of silently picking one.

## Still to check

- The biggest date range allowed per request for `/datasets/AGPT`.
- Expected number of half-hours on clock-change days (46 or 50).
