## Incident 0 — ENERC column collision (silent data loss in foods.csv)


## id     -> INC-2026-06-19-01
## where  -> build_dataset.py -> Level 1 ETL (Transform/Load)
## sev    -> high -> silent data loss in a built file (no error, no warning)
## status -> fixed + checked 2026-06-19
## caught -> first build of foods.csv
## by     -> jyx-mb


## what happened
i reshaped long->wide using just euroFIRkod as the column key.
euroFIRkod is NOT unique inside a food -> Energy shows up twice per food:
   ENERC in kJ   +   ENERC in kcal      ## same code, two units
setting d[k]=v twice on the same key -> python quietly overwrites the first
   -> kcal overwrote kJ
   -> Energy(kJ) got dropped for ALL 2575 foods, with no complaint from python


## impact
- scope  -> all 2575 rows of the FIRST foods.csv
- lost   -> Energy in kJ for every food (only in the built file)
         -> the energy column that survived had no unit label = confusing anyway
- raw    -> NOT touched. harvest_raw.json (20 MB, 150,472 measurements) still had both
         -> no re-harvest needed, just a local re-run
- damage -> none. caught BEFORE foods.csv was committed or used. gucci.


## how it surfaced   (the math gave it away, not the data)
foods.csv -> 58 distinct nutrient columns
recon -> a food with up to 59 measurements (food #4)

quick check ->
- every one of the 2575 foods repeats ENERC (kJ + kcal)
- ENERC = the ONLY code with more than one unit in the whole set
- key on (euroFIRkod, enhet) -> 0 repeats, 59 columns


## root cause
i assumed euroFIRkod was a unique key per food. it isn't.
it's a fine id for a nutrient, but what one row really represents is
(nutrient, unit). Energy = one nutrient, two facts (kJ + kcal), sharing one code.
/// a python dict silently overwrites a repeated key -> no error to catch it.


## the fix
column key   euroFIRkod   ->   euroFIRkod + "_" + enhet
changed in BOTH spots: the pivot line + the column list.

   by_food[m["nummer"]][m["euroFIRkod"]] = m["varde"]
                          ## changed to
   by_food[m["nummer"]][m["euroFIRkod"] + "_" + m["enhet"]] = m["varde"]

                            &

   nutrient_cols = sorted({m["euroFIRkod"] for m in measurements})
                          ## changed to
   nutrient_cols = sorted({m["euroFIRkod"] + "_" + m["enhet"] for m in measurements})

result ->
- ENERC_kJ + ENERC_kcal = separate columns, nothing lost
- the unit is now in every column name = clearer where each value came from
- 59 nutrient columns (+ nummer, namn, version = 62 total)
/// only renames columns, no value changed -> the "data unchanged" promise still holds


## verify   (re-run 2026-06-19)
Loaded 2575 foods, 150472 measurements
Distinct nutrient columns: 59
foods.csv written: 2575 rows x 62 columns
metadata.json written. Pin (max record version): 2025-10-29T14:27:35.13

?? check the header -> both energy columns there + labelled with units:
   head -1 foods.csv | tr ',' '\n' | grep -n ENERC
   11:ENERC_kJ
   12:ENERC_kcal


## lessons   (cheap lesson)
/// something can be a fine id and STILL not be unique for each row.
    reshape using what a row really is -> here (nutrient, unit).
/// a silent overwrite (dict[k]=v on a repeated key) = data lost with no warning.
    when reshaping -> check that row count == number of distinct keys.
/// count checks earn their keep. the bug was invisible in the data, obvious in the
    math (58 != 59).
/// saving the raw data first paid off. it was written before any reshaping -> recovery
    took seconds, not a 20-minute re-harvest.


#/ add a check in the build (fail LOUDLY if rows != distinct keys)
#/ add a nutrient legend (code -> name -> unit) in metadata for readability
#/ remember the (nutrient, unit) idea in the cleaning step (unit conversions = later, written down)
