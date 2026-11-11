# How long a date range can /datasets/AGPT handle in one request?
# Try growing windows and stop at the first failure.

import time
import requests
import pandas as pd

URL = "https://data.elexon.co.uk/bmrs/api/v1/datasets/AGPT"
START = pd.Timestamp("2026-08-01T00:00Z")

for days in [3, 4, 5]:
    end = START + pd.Timedelta(days=days)
    params = {
        "publishDateTimeFrom": START.strftime("%Y-%m-%dT%H:%MZ"),
        "publishDateTimeTo": end.strftime("%Y-%m-%dT%H:%MZ"),
        "format": "json",
    }
    t0 = time.time()
    resp = requests.get(URL, params=params, timeout=120)
    secs = round(time.time() - t0, 1)

    print("=" * 60)
    print(f"{days} days -> status {resp.status_code} in {secs}s")

    # Stop at the first failure and show why
    if resp.status_code != 200:
        print(resp.text[:400])
        break

    # A 200 doesn't prove we got everything, so compare with the expected count
    df = pd.DataFrame(resp.json()["data"])
    expected = days * 48 * 11
    print(f"rows: {len(df)} (about {expected} expected)")
    print("settlement dates:", df["settlementDate"].min(), "to", df["settlementDate"].max())
