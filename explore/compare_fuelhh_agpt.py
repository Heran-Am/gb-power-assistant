# Compare FUELHH and AGPT for the same day.
# Question: do they measure the same thing, or different parts of the system?

import requests
import pandas as pd

BASE = "https://data.elexon.co.uk/bmrs/api/v1"
DAY = "2026-10-27"

# --- FUELHH: one row per half-hour and fuel type ---
fuel = requests.get(
    f"{BASE}/datasets/FUELHH",
    params={"settlementDateFrom": DAY, "settlementDateTo": DAY, "format": "json"},
    timeout=60,
).json()["data"]
fuel = pd.DataFrame(fuel).pivot_table(index="settlementPeriod", columns="fuelType", values="generation")

# --- AGPT: values are nested inside each half-hour, so we flatten them first ---
agpt_raw = requests.get(
    f"{BASE}/generation/actual/per-type",
    params={"from": DAY, "to": "2026-10-28", "format": "json"},
    timeout=60,
).json()["data"]

rows = []
for period in agpt_raw:
    for item in period["data"]:
        rows.append({
            "startTime": period["startTime"],
            "settlementPeriod": period["settlementPeriod"],
            "psrType": item["psrType"],
            "quantity": item["quantity"],
        })
agpt = pd.DataFrame(rows)

# Drop the extra half-hour from the next day (the "to" date is inclusive).
# Note: this simple date check only works in winter, when UK time = UTC.
agpt = agpt[agpt["startTime"].str.startswith(DAY)]
agpt = agpt.pivot_table(index="settlementPeriod", columns="psrType", values="quantity")

# --- Put matching categories side by side ---
interconnectors = [c for c in fuel.columns if c.startswith("INT")]

compare = pd.DataFrame({
    "FUELHH wind": fuel["WIND"],
    "AGPT wind (on+off)": agpt["Wind Onshore"] + agpt["Wind Offshore"],
    "FUELHH gas (CCGT+OCGT)": fuel["CCGT"] + fuel["OCGT"],
    "AGPT gas": agpt["Fossil Gas"],
    "FUELHH nuclear": fuel["NUCLEAR"],
    "AGPT nuclear": agpt["Nuclear"],
    "AGPT solar": agpt["Solar"],
    "FUELHH total (no interconn.)": fuel.drop(columns=interconnectors).sum(axis=1),
    "AGPT total": agpt.sum(axis=1),
})

print("Half-hours:", len(fuel), "in FUELHH,", len(agpt), "in AGPT")
print("FUELHH fuel types:", list(fuel.columns))
print()
# Four moments of the day: night, morning, midday, evening
print(compare.loc[[1, 13, 25, 37]].round(0).T.to_string())
