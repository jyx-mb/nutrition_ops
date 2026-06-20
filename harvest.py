# Copy the data into harvest_raw.json
# stamp when harvest started (for metadata.json)

from datetime import datetime, timezone     # Date+time utilities
import requests     # lib for HTTP requests 
import time     # polite pause btwn calls
import json     # json manipulation

# Base API URL endpoint
BASE = "https://dataportal.livsmedelsverket.se/livsmedel/api/v1"      

# Generate current timestamp in ISO format
started_at = datetime.now(timezone.utc).isoformat()     
print(f"Harvest started: {started_at}")

# Send initial request to read total records
resp = requests.get(f"{BASE}/livsmedel", params={"offset": 0, "limit": 1, "sprak": 2}) 
resp.raise_for_status()   

# Convert API response to JSON dictionary
data = resp.json()          

# Extract the total records count from the metadata
total = data["_meta"]["totalRecords"]   
print(f"Total Foods Available: {total}")  

# One call grabs every food; keep essentials only
resp = requests.get(f"{BASE}/livsmedel", params={"offset": 0, "limit": total, "sprak": 2})
resp.raise_for_status()
foods_raw = resp.json()["livsmedel"]    # List of food records, dug out of envelope

basket = []                         # empty basket
for food in foods_raw:              # walk every food record one at a time
    basket.append({                 # add small dict to basket
        "nummer": food["nummer"],   # stable ID - never translates
        "namn": food["namn"],       # food's name in english (sprak=2)
        "version": food["version"]  # per-record timestamp
    })

print(f"Foods collected: {len(basket)}")  # how many kept
print(f"First in basket: {basket[0]}")    # peek to prove shape

# Loop over foods, fetch nutrients, extract
measurements = []           # flat collector for every measurement
failures = []               # foods whose fetch failed — recorded, NOT fatal

for food in basket:
    nummer = food["nummer"]
    try:
        n_resp = requests.get(
            f"{BASE}/livsmedel/{nummer}/naringsvarden",
            params={"sprak": 2},
            timeout=30,     # give up on a frozen call after 30s
        )
        n_resp.raise_for_status()
        nutrients_raw = n_resp.json()
        for nutrient in nutrients_raw:
            measurements.append({
                "nummer": nummer,
                "namn": nutrient["namn"],
                "euroFIRkod": nutrient["euroFIRkod"],
                "varde": nutrient["varde"],
                "enhet": nutrient["enhet"],
            })
        print(f"Food {nummer}: {len(nutrients_raw)} nutrients collected")
    except requests.exceptions.RequestException as err:
        failures.append({"nummer": nummer, "error": str(err)})   # log it
        print(f"Food {nummer}: FAILED ({err})")
    time.sleep(0.2)     # pause runs either way, once per food

print(f"Done. {len(basket)} foods attempted, {len(failures)} failed, {len(measurements)} measurements total")

# insurance
raw = {
    "started_at": started_at,       # provenance: when this harvest began
    "total_expected": total,        # 2575, read live from _meta
    "foods": basket,                # nummer / namn / version  (version = the future PIN)
    "measurements": measurements,   # the long-format nutrient values (the expensive cargo)
    "failures": failures,           # empty this run, but recorded for honesty
}

with open("harvest_raw.json", "w", encoding="utf-8") as f:   # UTF-8 keeps Swedish chars safe
    json.dump(raw, f, ensure_ascii=False, indent=2)          # ensure_ascii=False -> å ä ö stay readable

print(f"Raw harvest saved -> harvest_raw.json ({len(measurements)} measurements)")

