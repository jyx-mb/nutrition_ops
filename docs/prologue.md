| Level | theme | what it delivers |
|---|---|
| 0 | being | repo, venv, Git, first commit |
| 1 | predicting | data load -> clean -> baseline model |
| 2 | remembering | experiment tracking (MLflow), data/model versioning (DVC) |
| 3 | serving | FastAPI endpoint, Docker container, tests |
| 4 | shipping | AWS, Terraform, CI/CD (GitHub Actions) |
| 5 | surviving | monitoring, drift (Evidently), retraining trigger |

## prologue — Level 0 setup + Level 1 harvest

Notation legend:                                                                             ##  what it's done
#/  what i'm about to do
/#  what just happened
/// important note
??  need to check


0) Audit first   /// overwriting an existing install can cause headaches

git --version            
python3 --version       
uv --version            

1) git, editor, shell settings

git config --global user.name "jyx-mb"  ## identity on commits
git config --global user.email "robert@digitalmaniacs.org"      ## email on commits
git config --global init.defaultBranch main   ## new repos start on 'main'

echo "setopt interactive_comments" >> ~/.zshrc  ## allow comments inside the terminal

brew install --cask visual-studio-code    ## install editor
/# app is there but 'code' isn't

#/ install code in path
echo 'export PATH="$PATH:/Applications/Visual Studio Code.app/Contents/Resources/app/bin"' >> ~/.zshrc

brew --version
gh --version
brew install gh

#/ log into github
gh auth login --hostname github.com --web --git-protocol https 
/# opens the browser -> i get a OAuth access token

 2) create project

mkdir -p ~/dev       ## make folder + missing parents
cd ~/dev        ## change directory

uv init nutrition_ops   ## generate starter files

cd nutrition_ops     ## go into the project


cat .gitignore pyproject.toml   ## check what uv generated  
 /// always check file generators

ls -la   ## list all files + hidden
uv run main.py      ## runs it and makes .venv folder

code .      ## open the project in VS Code   
#/ fill README (scope, disclaimer, data credit)

/// no projects in Desktop/Documents -> permission + icloud sync troubles
/// project first landed on Desktop -> privacy walls, icloud, finder accidents -> moved to ~/dev
/// renamed a folder + deleted its parent mid-session -> commit before change; rebuild was cheap here
/// ls failed and reached sudo out of reflex -> sudo is never step one;
/// the gh wizard gave me a fine-grained PAT -> the token prefix tells you which: githubPAT vs gho_ -> revoked the old one

---

mkdir docs      ## make a documentation folder
code docs/prologue.md      ## make + open a file in VS Code
touch climax.md epilogue.md     ## create the other documentation files

3) Data + API inspection

curl "https://dataportal.livsmedelsverket.se/livsmedel/api/v1/api-info"   ## call the api
/# apiName, apiVersion "1.0.0", apiReleased "2024-03-18", docs URL, apiStatus active
/// software info not food data

open "https://dataportal.livsmedelsverket.se/livsmedel/swagger/index.html"  ## open docs page

curl "https://dataportal.livsmedelsverket.se/livsmedel/api/v1/livsmedel?offset=0&limit=1"   ## call the api   /# hard to read raw

curl -s "https://dataportal.livsmedelsverket.se/livsmedel/api/v1/livsmedel?offset=0&limit=1" | python3 -m json.tool   ## same call, pretty-printed w/ python json.tool

curl -s "https://dataportal.livsmedelsverket.se/livsmedel/api/v1/livsmedel?offset=0&limit=1&sprak=1" | python3 -m json.tool --no-ensure-ascii   ## get chars as they are no (\u) sequence   /# swedish output

curl -s "https://dataportal.livsmedelsverket.se/livsmedel/api/v1/livsmedel?offset=0&limit=1&sprak=2" | python3 -m json.tool --no-ensure-ascii   ## sprak=2 gives english

curl -s "https://dataportal.livsmedelsverket.se/livsmedel/api/v1/livsmedel/1/naringsvarden?sprak=2" | python3 -m json.tool --no-ensure-ascii   ## full nutrients for food 1

curl -s "https://dataportal.livsmedelsverket.se/livsmedel/api/v1/livsmedel/1/naringsvarden?sprak=2" | python3 -m json.tool --no-ensure-ascii | head -n 40   ## just first 40 lines

/// href = where a link points (used in <a> tags)
/// rel = how page relates to the target (mostly in <link> inside <head>)
/// rel in <a> for SEO + security reasons

curl -s "https://dataportal.livsmedelsverket.se/livsmedel/api/v1/livsmedel?offset=0&limit=1&sprak=2" | python3 -m json.tool --no-ensure-ascii   ## check other endpoint   ??

curl -s "https://dataportal.livsmedelsverket.se/livsmedel/api/v1/livsmedel/1/naringsvarden?sprak=2" | python3 -m json.tool --no-ensure-ascii | head -n 40   ## first 40 again

curl -s "https://dataportal.livsmedelsverket.se/livsmedel/api/v1/livsmedel/1/naringsvarden?sprak=2" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))"   
## how many nutrients
## -c to run the code you pass in
## importing json and sys for python to read terminal
## json.load turns text from sys.stdin into a normal python object

curl -s "https://dataportal.livsmedelsverket.se/livsmedel/api/v1/livsmedel/1/naringsvarden?sprak=2" | python3 -m json.tool | grep -c '"namn":'   ## count the names another way

 #/ plan a script
 #/ ask sprak2 list endpoint for a page, read totalRecords from _meta; make an empty list for foods; from offset 0 until all foods harvested: get a page, save each food's nr/name/version, move offset by the page size; for each food get its naringsvarden (sprak=2); from each nutrient keep euroFIRkod, varde, enhet tagged with food nr. <-- Extract + Transform

/// hammering the site with lots of requests could get my IP blocked
 #/ load into foods.csv + metadata.json
 #/ use time module + time.sleep(0.2)

 ---

code ~/dev/nutrition_ops/harvest.py    #/ start writing the harvest

<#> Harvest

from datetime import datetime, timezone   ## date + time tools
started_at = datetime.now(timezone.utc).isoformat()   ## same ISO time format as the API
print(f"Harvest started: {started_at}")   ## note when it started

cd ~/dev/nutrition_ops   ## back into the project

uv run harvest.py   ## run it 
/# failed -> mistake in pyproject.toml (2 lines on 1)

?? how many foods are there

pip install requests   ## get the requests library
/// old habit - that installs outside uv's managed env

uv add requests   ## add requests the uv way

uv run python -c "import requests; print(requests.__version__)"   ## check it imports + show version, via uv   ??

grep requests pyproject.toml   ## confirm requests in dependecies


## Harvest

import requests   ## for http calls

BASE = "https://dataportal.livsmedelsverket.se/livsmedel/api/v1"   ## base url

resp = requests.get(f"{BASE}/livsmedel", params={"offset": 0, "limit": 1, "sprak": 2})  
## ask for one record   #/ read the total count

resp.raise_for_status()   ## stop if call fails
data = resp.json()    ## turn json into a dict

total = data["_meta"]["totalRecords"]    ## grab total from _meta
print(f"Total Foods Available: {total}")   ## show it

curl -s "https://dataportal.livsmedelsverket.se/livsmedel/api/v1/livsmedel?offset=0&limit=2575&sprak=2" | python3 -c "import json,sys; print(json.load(sys.stdin)['_meta'])"   ## prit _meta, watch the count

curl -s "https://dataportal.livsmedelsverket.se/livsmedel/api/v1/livsmedel?offset=0&limit=1&sprak=2" | python3 -c "import json,sys; print(list(json.load(sys.stdin).keys()))"   

## print top-level keys
/// keys stay swedish, only values get translated

## Harvest
## get every food, keep just the basics

resp = requests.get(f"{BASE}/livsmedel", params={"offset": 0, "limit": total, "spark": 2})   
## one call gets all foods

resp.raise_for_status()  ## stop if it failed
foods_raw = resp.json()["livsmedel"]    ## pull the list of foods out

basket = []      ## empty basket
for food in foods_raw:      ## lopp the foods
    basket.append({      ## add a small dict
        "nummer": food["nummer"],       ## stable id (never translated)
        "namn": food["namn"],      ## english name (spark=2)
        "version": food["version"]    ## timestamp
    })

print(f"Foods collected: {leb(basket)}")  ## how many did i keep
print(f"First in basket: {basket[0]}")    ## peek at one to check shape

uv run harvest.py   ## run it   ??

## Harvest

first_nummer = basket[0]["nummer"]       ## id of the first food   #/ get its nutrients

n_resp = requests.get(   ## get nutrients from the first food
    f"{BASE}/livsmedel/{first_nummer}/naringsvarden",   ## the food id goes in the url
    params={"sprak": 2},     ## language stays a query param
)
n_resp.raise_for_status()   ## stop if it failed
nutrients_raw = n_resp.json()     ## just a list of nutrients

print(f"Nutrients for food {first_nummer}: {len(nutrients_raw)}") ## show how many
print(f"First nutrient: {nutrients_raw[0]}")   ## peek at the first one

uv run harvest.py   ## run it   ??

## Harvest

measurements = []            ## one flat list for every measurement
for nutrient in nutrients_raw:                 ## go through the 58 records
    measurements.append({             ## add one
        "nummer": first_nummer,        ## tag: which food this belongs to
        "euroFIRkod": nutrient["euroFIRkod"],   ## the nutrient's stable id
        "varde": nutrient["varde"],        ## the value
        "enhet": nutrient["enhet"],           ## the unit
    })

print(f"Measurements from food {first_nummer}: {len(measurements)}") ## show how many
print(f"Sample measurement: {measurements[0]}")   ## peek at one

uv run harvest.py   ## run it   ??

## Harvest

basket = []      ## empty list for the foods i keep
for food in foods_raw:          ## go through each food from the api
    basket.append({      ## add one small dict per food
        "nummer": food["nummer"],   ## stable id, my linking key (never translated)
        "namn": food["namn"],           ## name in english (sprak=2)
        "version": food["version"]   ## its timestamp -> this is the pin later
    })

print(f"Foods collected: {len(basket)}")    ## not indented = runs once, after the loop
print(f"First in basket: {basket[0]}")    ## peek at one food to check the shape

measurements = []       ## flat list, one row per nutrient
for nutrient in nutrients_raw:       ## just testing: one food's nutrients
    measurements.append({          ## add one
        "nummer": first_nummer,        ## tag: which food this belongs to
        "namn": nutrient["namn"],        ## nutrient name (e.g. "Zinc, Zn")
        "euroFIRkod": nutrient["euroFIRkod"],  ## stable nutrient code -> a column later
        "varde": nutrient["varde"],      ## the value
        "enhet": nutrient["enhet"],      ## the unit (mg, g, kJ, kcal ...)
    })

/// Notes
  first_nummer + the plain nutrients_raw = the "test one food first" bit.
  the real harvest.py replaced this with the full 'for food in sample' loop,
  plus try/except, timeout, and sleep — a tougher version.
  euroFIRkod (the nutrient code) isn't unique on its own ( ENERC kJ/kcal clash).
  the real column key became euroFIRkod + "_" + enhet.
  see docs/incident0.md

print(f"Measurements from food {first_nummer}: {len(measurements)}")   
## runs once, after the loop
print(f"Sample measurement: {measurements[0]}")   ## peek at one

uv run harvest.py  

## Harvest

import time       ## to pause btwn calls so i don't hammer the server

measurements = []        ## flat list for ALL foods' measurements
sample = basket[:5]          ## test on the first 5 foods before the full run

for food in sample:             ## outer loop: one food at a time
    nummer = food["nummer"]           ## this food's id (for the url + the tag)

    n_resp = requests.get(   ## get this food's nutrients
        f"{BASE}/livsmedel/{nummer}/naringsvarden",
        params={"sprak": 2},
    )
    n_resp.raise_for_status()   ## crash early if the response is bad
    nutrients_raw = n_resp.json()     

    for nutrient in nutrients_raw:   ## inner loop: one nutrient at a time
        measurements.append({   ## one row per nutrient
            "nummer": nummer,               ## tag
            "namn": nutrient["namn"],     # nute name
            "euroFIRkod": nutrient["euroFIRkod"],   # stable nute code
            "varde": nutrient["varde"],     # value
            "enhet": nutrient["enhet"],     # unit (g, mg...)
        })

    print(f"Food {nummer}: {len(nutrients_raw)} nutrients collected")   ## progress line
## INSIDE the outer loop
    time.sleep(0.2)         ## small wait, inside the loop, after each food

print(f"Done. {len(sample)} foods, {len(measurements)} measurements total")   ## final count


uv run harvest.py 

## Harvest

## ALL 2575 foods
measurements = []        ## flat list for every measurement
sample = basket     ## the full list this time (all 2575)

for food in sample:     ## outer loop: one food at a time
    nummer = food["nummer"]     ## this food's id (url + tag)

    n_resp = requests.get(      ## get this food's nutrients
        f"{BASE}/livsmedel/{nummer}/naringsvarden,      ## the food id goes IN the url
        params={"sprak": 2},        ## english values
    )
    n_resp.raise_for_status()       ## crash early if the response is bad
    nutrients_raw = n_resp.json()       ## list of nutrients (no wrapper)

    for nutrient in nutrients_raw:      ## inner loop: one nutrient at a time
        measurements.append({       ## one row per nutrient
            "nummer": nummer,       ## which food this belongs to
            "namn": nutrient["namn"],       ## nutrient name
            "euroFIRkod": nutrient["euroFIRkod"],  ## stable nutrient code -> a column
            "varde": nutrient["varde"],     ## the value
            "enhet": nutrient["enhet"],     ## the unit (mg, g, kJ, kcal ...)
        })

    print(f"Food {nummer}: {len(nutrients_raw)} nutrients collected")       ## progress line
    time.sleep(0.2) ## small wait between calls

print(f"Done. {len(sample)} foods, {len(measurements)} measurements total")   ## final count

/// this run errored partway and wasted time -> i need a safety net

## Harvest

## go through foods, get nutrients, survive failures, count

measurements = []       ## flat list for every measurement
failures = []       ## foods whose call failed - saved, not fatal
sample = basket[:2575]      ## all foods

for food in sample:     ## outer loop: one food at a time
    nummer = food["nummer"]     ## this food's id
    try:
        n_resp = requests.get(      ## get this food's nutrients (protected by try)
            f"{BASE}/livsmedel/{nummer}/naringsvarden",     ## food id in the url
            params={"sprak": 2},        ## english values
            timeout=30,     ## give up on a stuck call after 30s
        )
        n_resp.raise_for_status()       ## bad response -> jump to except
        nutrients_raw = n_resp.json()       ## list of nutrients
        for nutrient in nutrients_raw:      ## inner loop: one nutrient at a time
            measurements.append({       ## one row per nutrient
                "nummer": nummer,       ## which food this belongs to
                "namn": nutrient["namn"],       ## nutrient name
                "euroFIRkod": nutrient["euroFIRkod"],       ## nutrient code -> a column
                "varde": nutrient["varde"],     ## the value
                "enhet": nutrient["enhet"],     ## the unit
            })
        print(f"Food {nummer}: {len(nutrients_raw)} nutrients collected")   ## progress
    except requests.exceptions.RequestException as err:
        failures.append({"nummer": nummer, "error": str(err)})      ## save it, keep going
        print(f"Food {nummer}: FAILED ({err})")     ## note the failure, don't crash
    time.sleep(0.2)     ## wait either way, once per food

print(f"Done. {len(sample)} foods attempted, {len(failures)} failed, {len(measurements)} measurements total")       ## final count

## Harvest

import json     ## save python data as json file

## the safety-net file
raw = {     ## one bundle to save
    "started_at": started_at,       ## when this harvest started
    "total_expected": total,        ## 2575, read live from _meta
    "foods": basket,        ## nummer / namn / version  (version = the pin later)
    "measurements": measurements,       ## the nutrient values (slower to fetch)
    "failures": failures,       ## empty this run, but kept to be honest
}

with open("harvest_raw.json", "w", encoding="utf-8") as f: ## utf-8 keeps swedish letters safe
    json.dump(raw, f, ensure_ascii=False, indent=2) ## ensure_ascii=False -> å ä stay readable

print(f"Raw harvest saved -> harvest_raw.json ({len(measurements)} measurements)")  ## confirm + count

uv run harvest.py       ## run the full harvest  

ls -lj harvest_raw.json     ## look at the saved file (typo: -lj)

pwd     ## where me balls at
touch build_dataset.py      ## make the build script

## Dataset

## build_dataset.py
## reads harvest_raw.json (from disk, no api) -> foods.csv + metadata.json

import json     ## read the raw file, write metadata
import csv      ## write the wide table
from collections import defaultdict     ## a dict that makes inner dicts on its own

with open("harvest_raw.json", encoding="utf-8") as f:       ## open the saved harvest
    raw = json.load(f)      ## json -> dict
foods = raw["foods"]        ## nummer / namn / version
measurements = raw["measurements"]      ## long form: one row/food, nutrient
print(f"Loaded {len(foods)} foods, {len(measurements)} measurements")  ## confirm + counts

## reshape long -> wide
by_food = defaultdict(dict)    ## nummer -> {euroFIRkod: varde}
for m in measurements:   ## go through each measurement
    by_food[m["nummer"]][m["euroFIRkod"]] = m["varde"]   
    ## each value under its food + nutrient

nutrient_cols = sorted({m["euroFIRkod"] for m in measurements})   
## sorted list of distinct nutrient codes (stable columns)
print(f"Distinct nutrient columns: {len(nutrient_cols)}")       ## how many columns?

## write foods.csv
fieldnames = ["nummer", "namn", "version"] + nutrient_cols      ## column order
with open("foods.csv", "w", encoding="utf-8", newline="") as f:     
## newline="" = correct csv everywhere
    writer = csv.DictWriter(f, fieldnames=fieldnames)       ## missing keys -> blank cell
    writer.writeheader()        ## write the header row
    for food in foods:      ## one row per food
        row = {     ## the fixed columns
            "nummer": food["nummer"],
            "namn": food["namn"],
            "version": food["version"],
        }
        row.update(by_food[food["nummer"]]) 
        ## fill in this food's nutrient values; gaps stay blank
        writer.writerow(row)        ## write the row
print(f"foods.csv written: {len(foods)} rows x {len(fieldnames)} columns")  
## confirm rows x cols

## write metadata.json
max_version = max(food["version"] for food in foods)        ## ISO dates sort by time
metadata = {        ## the provenance info
    "source": "Livsmedelsverket (Swedish Food Agency) Food Database",
    "source_api": "https://dataportal.livsmedelsverket.se/livsmedel/api/v1",        # API
    "retrieval_date": raw["started_at"],        ## when the harvest started (UTC)
    "apiVersion": "1.0.0",          ## the software version (from api-info)
    "sprak": 2,      ## english values; keys stay swedish
    "expected_count": raw["total_expected"],    ## 2575, read live from _meta
    "received_count": len(foods),          ## what i actually got
    "measurements_total": len(measurements),        ## total count
    "failures": len(raw["failures"]),       ## how many failed
    "max_record_version": max_version,      /// the pin: newest record timestamp i saw
    "license": "CC BY 4.0",     ## the source's open license
    "attribution": "Source: Livsmedelsverket (Swedish Food Agency), CC BY 4.0",  
    ## credit i have to give
    "note": "data unmodified - faithful copy, no unit conversions",
}

with open("metadata.json", "w", encoding="utf-8") as f:   ## utf-8 keeps å ä ö safe
    json.dump(metadata, f, ensure_ascii=False, indent=2)   ## ensure_ascii=False -> real letters; indent=2 -> readable

print(f"metadata.json written. Pin (max record version): {max_version}")   ## confirm + show the pin

uv run build_dataset.py   ## run build

ls -lh foods.csv metadata.json && echo "---rows---" && wc -l foods.csv && echo "---meta---" && cat metadata.json    ## check the output

touch docs/incident0.md ## make the incident note


## Dataset

by_food[m["nummer"]][m["euroFIRkod"]] = m["varde"]

                 ## changed to

by_food[m["nummer"]][m["euroFIRkod"] + "_" + m["enhet"]] = m["varde"]   ## key = nutrient + unit

                     &

nutrient_cols = sorted({m["euroFIRkod"] for m in measurements})

                ## changed to

nutrient_cols = sorted({m["euroFIRkod"] + "_" + m["enhet"] for m in measurements})   ## one column per (nutrient, unit)

uv run build_dataset.pu   ## re-run -> overwrite the broken foods.csv

head -1 foods.csv | tr ',' '\n' | grep -n ENERC   ## find ENERC in the header 
/# the two ENERC columns came out separate

cat .gitignore     ## check for raw harvest
echo "harvest_raw.json" >> .gitignore
git status      ## no harvest_raw
git add -A     
git status      
git commit -m "nutrition_ops: API harvest + dataset build pipeline" 
git log --oneline       
gh repo create nutrition_ops --public --spurce=. --remote=origin --push  # first push

---
/// the nordics didn't label on food-groups
#/ build food-group classifier
#/ tally the words that appear across all food names, show the top 30
python3 -c "
import csv, re
from collections import Counter
words = Counter()       ## a tally box (word -> count)
with open('foods.csv', newline='') as f:
    for row in csv.DictReader(f):       ## each row as a dict keyed by header
        for w in re.findall(r'[a-z]+', row['namn'].lower()):        ## pull letter-only words
            if len(w) > 2:      ## skip tiny noise (of, e, g)
                words[w] += 1
for w, n in words.most_common(30):      ## top 30 most frequent
    print(f'{n:5d}  {w}')"

touch label_foods.py

# Food Labeling

import re       ## regex, used to split a name into whole words

## RULES: ordered list, FIRST match wins. order = priority -> settle collision on purpose
## "beef tallow" -> Fats, "chocolate milk" -> Sweets.
## ?? bare "fat" is a trap (low fat, 80% fat) -> we list oil/lard/tallow instead.
RULES = [                                                                                 
    ("Sweets",        ["chocolate", "sugar", "candy", "cake", "biscuit", "jam", "honey"]), 
    ("Fats & oils",   ["oil", "butter", "margarine", "lard", "tallow", "spread", "ghee"]), 
    ("Dairy & eggs",  ["cheese", "milk", "cream", "yoghurt", "yogurt", "egg"]),            
    ("Meat & fish",   ["meat", "beef", "pork", "chicken", "sausage", "ham", "fish", "cod"]),
    ("Grains & bread",["bread", "wheat", "wholegrain", "rice", "pasta", "oat", "flour"]),   
    ("Fruit & veg",   ["fruit", "potato", "apple", "berry", "tomato", "carrot", "onion"]),  
]                                                                                         
DEFAULT = "Other"       ## catch-all when no matches

def classify(name):     ## take one food name and return it's group
    words = set(re.findall(r"[a-z]+", name.lower()))    ## split name into set of whole lowercase words
    for group, keywords in RULES:       ## walk the rules in priority order (first match wins)
        for kw in keywords:     ## check each keyword belonging to this rule
            if kw in words:     ## TRUE only if kw is a WHOLE word -> kills the oil/boiled trap
                return group        ## first matching group wins -> hand it back
    return DEFAULT      ## nothing matched? -> Other

if __name__ == "__main__":      ## run test block only when the file is run directly
    samples = [     ## tricky names that prove the logic
        "Beef tallow",      ## Fats (tallow), not Meat (beef)
        "Low fat milk 0.5%",        ## Dairy (milk); fat must NOT trigger Fats
        "Chocolate milk drink",     ## Sweets (chocolate beats milk by order)
        "Potato boiled",        ## Fruit & veg - boiled must NOT match oil anymore
        "Soy milk",     ## documented collision -> Dairy (milk)
        "Wholegrain bread",     ## Grains
    ]       
    for s in samples:       ## loop over each sample name
        print(f"{classify(s):15s} <- {s}")      ## print group padded 15

#/ full run: classify every food in foods.csv 
    groups = Counter()      ## tally box: group name -> how many foods got it
    with open("foods.csv", newline="") as f:        ## newline="" is the csv-safe way
        for row in csv.DictReader(f):       ## read each row as a dict keyed by the header
            groups[classify(row["namn"])] += 1      ## classify this food's name, +1 to that group
    print()     ## blank line, separates samples from the real counts
    for group, n in groups.most_common():       ## list groups from most foods to fewest
        print(f"{group:15s} {n}")       ## group (padded to 15) then its count
    print(f"{'TOTAL':15} {sum(groups.values())}")      ## sanity check -> must equal 2575

 ## diagnose Other:
    other_words = Counter()         ## tally box for words found in Other foods
    with open("foods.csv", newline="") as f:        ## open the dataset again
        for row in csv.DictReader(f):       ## walk every row
            if classify(row["namn"]) == "Other":        ## keep only the ones that fell to Other
                for w in re.findall(r"[a-z]+", row["namn"].lower()):    ## split that name into words
                    if len(w) > 2:      ## skip tiny noise (of, e, g)
                        other_words[w] += 1     ## add 1 to this word's tally
    print()     ## spacer line
    print("top words inside Other:")        ## header for the diagnostic
    for w, n in other_words.most_common(25):        ## the 25 most common words in Other
        print(f"{n:5d}  {w}")       ## count, then the word

#/ replacing in rules

("Meat & fish",   ["meat", "beef", "pork", "chicken", "sausage", "ham", "fish", "cod", "veal"]),  
## animal protein
("Fruit & veg",   ["fruit", "potato", "potatoes", "apple", "berry", "tomato", "tomatoes", "carrot", "carrots", "onion", "onions", "vegetable", "vegetables", "bean", "beans", "pea", "peas", "soy"]),  
## plants (+ plurals, + soy/veg)

#/ replace/add in diagnostic flag
## already judged
    SKIP = {"raw", "fried", "frozen", "boiled", "canned", "dried", "homemade", 
            "fortified", "white", "salt", "product", "fat", "brine", "rtd",    
            "vol", "based", "plant", "fresh", "whole", "cooked",               
            "sauce", "soup", "protein"}                                        

if len(w) > 2:
to
if len(w) > 2 and w not in SKIP:        ## skip tiny words AND known ones

print("top words inside Other:")
to
print("top UNKNOWN words inside Other:")    ## header

#/ replace
("Dairy & eggs",  ["cheese", "milk", "cream", "yoghurt", "yogurt", "egg", "fraiche"]),

("Meat & fish",   ["meat", "beef", "pork", "chicken", "sausage", "ham", "fish", "cod", "veal", "salmon", "herring", "lamb", "liver", "fillet"]),

("Fruit & veg",   ["fruit", "potato", "potatoes", "apple", "berry", "tomato", "tomatoes", "carrot", "carrots", "onion", "onions", "vegetable", "vegetables", "bean", "beans", "pea", "peas", "soy", "salad", "cabbage", "corn", "mushroom", "orange"]),