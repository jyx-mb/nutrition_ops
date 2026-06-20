# build_dataset.py
# Reads harvest_raw.json (DISK ONLY, no API) -> foods.csv + metadata.json

import json                              # read the raw harvest, write metadata
import csv                               # write the wide table
from collections import defaultdict      # a dict that auto-creates inner dicts

# Load the saved harvest (insurance file)
with open("harvest_raw.json", encoding="utf-8") as f:
    raw = json.load(f)
foods = raw["foods"]                     # nummer / namn / version
measurements = raw["measurements"]       # long format: one row per (food, nutrient)
print(f"Loaded {len(foods)} foods, {len(measurements)} measurements")

# pivot long -> wide
by_food = defaultdict(dict)              # nummer -> {euroFIRkod_enhet: varde}
for m in measurements:
      by_food[m["nummer"]][m["euroFIRkod"] + "_" + m["enhet"]] = m["varde"]   # key = nutrient + unit

# column union: every distinct nutrient+unit, sorted for a STABLE column order
nutrient_cols = sorted({m["euroFIRkod"] + "_" + m["enhet"] for m in measurements})   # one column per (nutrient, unit)
print(f"Distinct nutrient columns: {len(nutrient_cols)}")

# write foods.csv (row/foods , column/nutrient)
fieldnames = ["nummer", "namn", "version"] + nutrient_cols
with open("foods.csv", "w", encoding="utf-8", newline="") as f:   # newline="" = correct CSV on every OS
    writer = csv.DictWriter(f, fieldnames=fieldnames)             # missing keys -> blank cell
    writer.writeheader()
    for food in foods:
        row = {
            "nummer": food["nummer"],
            "namn": food["namn"],
            "version": food["version"],
        }
        row.update(by_food[food["nummer"]])    # fill in THIS food's nutrient values; gaps stay blank
        writer.writerow(row)
print(f"foods.csv written: {len(foods)} rows x {len(fieldnames)} columns")

# ---- STEP 10: write metadata.json (provenance + THE PIN) ----
max_version = max(food["version"] for food in foods)   # ISO 8601 strings sort chronologically
metadata = {
    "source": "Livsmedelsverket (Swedish Food Agency) Food Database",
    "source_api": "https://dataportal.livsmedelsverket.se/livsmedel/api/v1",
    "retrieval_date": raw["started_at"],        # UTC start harvest
    "apiVersion": "1.0.0",                      # software version (from recon / api-info)
    "sprak": 2,                                 # English values; KEYS stay Swedish
    "expected_count": raw["total_expected"],    # 2575, read live from _meta
    "received_count": len(foods),               # what i actually got
    "measurements_total": len(measurements),    
    "failures": len(raw["failures"]),
    "max_record_version": max_version,          # THE PIN: newest record timestamp seen
    "license": "CC BY 4.0",
    "attribution": "Source: Livsmedelsverket (Swedish Food Agency), CC BY 4.0",
    "note": "data unmodified - faithful copy, no unit conversions",
}
with open("metadata.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)
print(f"metadata.json written. Pin (max record version): {max_version}")