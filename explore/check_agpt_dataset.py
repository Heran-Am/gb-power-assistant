# How does the raw AGPT dataset endpoint work?
# Try a few parameter styles for one day and see what comes back.

import requests
import pandas as pd

URL = "https://data.elexon.co.uk/bmrs/api/v1/datasets/AGPT"

tries = {
    "no dates": {},
    "publish time": {"publishDateTimeFrom": "2026-10-27T00:00Z", "publishDateTimeTo": "2026-10-28T00:00Z"},
    "settlement date": {"settlementDateFrom": "2026-10-27", "settlementDateTo": "2026-10-27"},
}

for name, params in tries.items():
    print("=" * 60)
    print(name, params)
    resp = requests.get(URL, params={**params, "format": "json"}, timeout=60)
    print("status:", resp.status_code)

    # A failed request usually explains which parameters it expects
    if resp.status_code != 200:
        print(resp.text[:400])
        continue

    df = pd.DataFrame(resp.json()["data"])
    print("rows:", len(df))
    print("columns:", list(df.columns))
    if len(df):
        print(df.head(3).to_string())
        if "settlementDate" in df.columns:
            print("settlement dates:", sorted(df["settlementDate"].unique()))
