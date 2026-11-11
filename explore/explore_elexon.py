# Quick look at Elexon's candidate datasets for one day.
# Goal: see the real columns and values before choosing anything.

import requests
import pandas as pd

BASE = "https://data.elexon.co.uk/bmrs/api/v1"
DAY = "2026-10-27"       # a recent full day
NEXT_DAY = "2026-10-28"  # some endpoints want a from/to range

# name -> (endpoint path, query parameters)
CANDIDATES = {
    "FUELHH (generation by fuel)": ("/datasets/FUELHH", {"settlementDateFrom": DAY, "settlementDateTo": DAY}),
    "AGPT (generation per type)": ("/generation/actual/per-type", {"from": DAY, "to": NEXT_DAY}),
    "INDO/ITSDO (demand outturn)": ("/demand/outturn", {"settlementDateFrom": DAY, "settlementDateTo": DAY}),
    "ATL (actual total load)": ("/demand/actual/total", {"from": DAY, "to": NEXT_DAY}),
    "MID (market index price)": ("/balancing/pricing/market-index", {"from": DAY, "to": NEXT_DAY}),
    "System prices (imbalance)": (f"/balancing/settlement/system-prices/{DAY}", {}),
}

# Make printed tables wide enough to read
pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)

for name, (path, params) in CANDIDATES.items():
    print("=" * 80)
    print(name)
    resp = requests.get(BASE + path, params={**params, "format": "json"}, timeout=60)
    print("status:", resp.status_code)

    # If a request fails, the error text usually says which parameter is wrong
    if resp.status_code != 200:
        print(resp.text[:500])
        continue

    body = resp.json()
    # Most endpoints put the rows under "data", but not all of them
    rows = body["data"] if isinstance(body, dict) and "data" in body else body
    df = pd.DataFrame(rows)

    print("rows:", len(df))
    print("columns:", list(df.columns))
    print(df.head(3).to_string())
