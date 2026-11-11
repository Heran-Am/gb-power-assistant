# Get one complete settlement day of AGPT and check it.
# AGPT is filtered by publish time and published with a delay,
# so we ask for a wider window and keep only the day we want.

import requests
import pandas as pd

URL = "https://data.elexon.co.uk/bmrs/api/v1/datasets/AGPT"
DAY = "2026-10-27"

params = {
    "publishDateTimeFrom": "2026-10-27T00:00Z",
    "publishDateTimeTo": "2026-10-28T12:00Z",  # 12 extra hours for late publishing
    "format": "json",
}
df = pd.DataFrame(requests.get(URL, params=params, timeout=60).json()["data"])
print("rows downloaded:", len(df))

day = df[df["settlementDate"] == DAY].copy()
print("rows for", DAY, ":", len(day))
print("half-hours:", day["settlementPeriod"].nunique(), "| types:", day["psrType"].nunique())

# Same half-hour and type more than once means revisions
dupes = day.duplicated(subset=["settlementPeriod", "psrType"], keep=False)
print("duplicate rows:", dupes.sum())
print("revision numbers seen:", sorted(day["documentRevisionNumber"].unique()))

# Time between the half-hour starting and being published
lag = pd.to_datetime(day["publishTime"]) - pd.to_datetime(day["startTime"])
print("publish delay: min", lag.min(), "| median", lag.median(), "| max", lag.max())

missing = sorted(set(range(1, 49)) - set(day["settlementPeriod"]))
print("missing half-hours:", missing)
