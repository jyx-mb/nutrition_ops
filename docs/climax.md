# Level 2 + Level 3

Notation legend:
#   title comment
<>  working file
##  comment                                                                             
#/  what i'm about to do
/#  what just happened
/// important note
??  need to check
//  note
#/ installl DVC via uv -> dependency recorded in pyproject.toml
#/ wake DVC inside the project and hand it harvest_raw.json
#/ wire DVC + git to build fresh clone
#/ MLflow to record the model running

#/ add data version control to keep fat files out of git, storing them into a small .dvc
uv add dvc    
uv run dvc     

ls -lh harvest_raw.json     ## the 20MB file i left behind

#/ turn this repo into a DVC repo
uv run dvc init

git status      ## check dvc's creation

#/ track the 20MB raw by creating a skinny pointer file
uv run dvc add harvest_raw.json

#/ ?? pointer
cat harvest_raw.json.dvc

#/ confirm pointer file in sight
git status

#/ staging skinny pointer + DVC files (not the blob)
git add harvest_raw.json.dvc .dvc .dvcignore .gitignore

git status 
git add docs/prologue.md
git commit -m "DVC tracking for harvest_raw.json + adjusted prologue.md"

/// pyproject.toml + uv.lock are required to install DVC 
/// not commited pyproject.toml + uv.lock -> command not found 

#/ stage produced dependecy + check + commit + push
git add pyproject.toml uv.lock
git status
git commit -m "record DVC as project dependency"
git push

#/ build the remote + push
mkdir -p ~/dev/dvc_remote       ## storage spot DVC pushes the real bytes to // later AWS S3 (real remote)
/// local folder remote not sharable, living local

#/ register folder as default remote (-d)
uv run dvc remote add -d localremote ~/dev/dvc_remote

#/ inspect config written by DVC
vim .dvc/config

#/ upload tracked 20MB raw data into remote
uv run dvc push

ls -R ~/dev/dvc_remote      ## confirm data landed

git add .dvc/config    ## stage
git commit -m "add default DVC remote (local store)"      ## commit
git push        ## push

#/ prove "remembered" is real
#/ delete local file + wipe DVC's cache and pull back from remote

#/ compare local cache ggn remote. "in sync / up to date" -> remote has the file
uv run dvc status -c

rm harvest_raw.json     ## delete the working copy of the 20MB raw

#/ wipe DVC's local cache -> pull forced to come from remote
rm -rf .dvc/cache

ls -lh harvest_raw.json     ## confirm is gone

uv run dvc pull     ## fetch data back from remote

ls -lh harvest_raw.json     ## proof of return
/# data is now remembered

#/ runs to be remembered - MLflow

uv add mlflow       ## mlflow drags in lots of dep, give it time, worry if err only
uv run mlflow --version
git add pyproject.toml uv.lock
git commit -m "record MLflow as project dependency"
git push 

mlflow --version        ## x
uv run mlflow --version     ## x
uv run python --version     ## 3.14.5
uv add "mlflow>=2"      ## x
uv add "mlflow>=3"      ## x
uv run mlflow --version     ## x

// hints point to pyproject.toml
#/ requires-python = ">=3.14"  -->  requires-python = ">=3.13,<3.14"
#/ "mlflow>=1.27.0",  -->. "mlflow>=2"

#/ pin Python, rebuild, verify
#/ pin this project's interpreter to 3.13 (write .python-version file; dwnl 3.13 if not present)
uv python pin 3.13      
/# -> 3.13

#/ delete old 3.14 env for fresh rebuilt (fully reproducible from lockfile)
rm -rf .venv

#/ recreate venv on 3.13 and re-resolve each dependency (hopefully mlflow will lock)
uv sync
uv run mlflow --version
uv run python --version

/// couldn't run mlflow, te actual fix was to downgrade pandas <3
// other fix mby -> uv run --prerelease=allow python --version 
// add prerelease to project     <-   uv add mlflow --prerelease=allow

#/ add back to pyproject.toml ,<3.14 on py

#/ check sync and pandas version again
uv sync
uv run python -c "import pandas as pd; print(pd.__version__)"

git add pyproject.toml uv.lock .python-version 
git commit -m "pin Python 3.13 + modern MLflow; cap pandas <3"
git push

/// commited before re-checking pandas ?? lock might've pin 3.x ggn pyproj <3 
/// did not dodge it, sync had to rewrite lock. pushed old lock -> sync, lock staged -> re-commit

git commit -m "reconcile uv.lock with pyproject (mlflow>=3, pandas<3>)"
git push
git status
git log --oneline

<> train_model.py

import mlflow       ## logs each run -> results never vanish

mlflow.set_experiment("food_group_baseline")        ## file every run under o named notebook

uv run train_model.py       ## run trainer inside proj venv
ls mlruns       ## prove it made it's tracking folder

# MLflow batch

<> train_model.py
import mlflow.sklearn       ## might save learning model

with mlflow.start_run():        ## open one run
    mlflow.log_param("model_type", "DecisionTreeClassifier")        ## record WHICH algorithm this run used
    mlflow.log_param("random_state", 42)        ## record the seed (reproducible split + tree)
    mlflow.log_param("test_size", 0.2)      ## record the 80/20 holdout ratio
    mlflow.log_param("n_features", X.shape[1])      ## record how many nutrient columns fed the model

    model = DecisionTreeClassifier(random_state=42)      ## same baseline tree as Level 1
    model.fit(X_train, y_train)     ## learn patterns from the training rows

    predictions = model.predict(X_test)     ## predict the unseen test rows

    accuracy = accuracy_score(y_test, predictions)      ## fraction predicted correctly
    mlflow.log_metric("accuracy", accuracy)     ## RECORD the score into this run
    print("accuracy:", round(accuracy, 3))      ## print for eyes

    mlflow.sklearn.log_model(model, name="model")       ## save trained tree as artifact (3.x: name=)

    print(classification_report(y_test, predictions))       ## per-group precision / recall / f1


uv run train_model.py

code .gitignore

git -C ~/dev/...       ## list changed/untracked files, short form

#/ trainer wrote to mlflow.db, UI default looks in mlruns/. -> point it at database
uv run mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5001    ## run from ~/dev/nutrition_ops

->127.0.0.1:5001

// all four params, the metrics, finished status . page still looks empty
// got the page also -> 0.6994

cd ~/dev/nutrition_ops      ## be in the repo before any git command
git add train_model.py .gitignore       
git status --short      ## check before commit

#/ commit only train_model and .gitignore . fix ignore b4 commiting
git commit -m "Level 2: instrument trainer with MLflow tracking + ignore local store"  
git push                                             
git log --oneline -3                              

# notes
// training was amnesiac — run it, read the accuracy, lose all record of what produced it.

## in DVC half - data remembered
#/ version the 20 MB harvest so it's reproducible, not just gitignored.
/# pointer (.dvc) in git, blob in a local remote; round-trip proven (deleted + pulled back intact).

## in MLflow half — runs remembered
#/ wrap the trainer in a tracked run; log the settings, the score, and the model itself.
/# one run logged: accuracy 0.699 

// MLflow 3.x stores runs in sqlite mlflow.db, NOT the old mlruns/ folder. The UI must be launched with --backend-store-uri sqlite:///mlflow.db or it shows an empty page.
// log_model uses name= in 3.x, not artifact_path=.
// gitignore both mlflow.db (the db) and mlruns/ (the artifacts).
// verify-don't-trust beat guessing twice today: the missing mlruns/ was never a bug, the empty UI was a stale page.


 ## DVC remote + MLflow db are local-only, true off-machine sharing in S3 


git status
git add dev/nutrition_ops
git commit -m " "
git push
git log --oneline
---

## Serving

## start using vim

vim load_check.py

import mlflow            ## tracking store + model loading
import mlflow.sklearn    ## knows how to rebuild sklearn models

mlflow.set_tracking_uri("sqlite:///mlflow.db")   ## use the sqlite db sitting in this folder

runs = mlflow.search_runs(experiment_names=["food_group_baseline"])  ## table of every run in experiment
run_id = runs.iloc[0]["run_id"]     ## grab the first row's id 
print("run_id:", run_id)        ## which run we're loading from

model = mlflow.sklearn.load_model(f"runs:/{run_id}/model")  ## f-string is address of saved tree

print("loaded model type:", type(model).__name__)      ## proof 1: what got back
print("expects feature count:", model.n_features_in_)  ## proof 2: the feature-order

cd ~/dev/nutrition_ops
uv run python load_check.py     ## check inside proj venv

# Level 3
#/ add fastAPI + standard extras (bundle: uvicorn server + fastapi dev CLI)

uv add fastapi[standard]

// zsh reads[] as filename pattern -> ""

uv add "fastapi[standard]"

cd ~/dev/nutrition_ops

uv run python load_check.py

vim load_check.py

print("feature names in order:", list(model.feature_names_in_))  ## proof 3: ordered 58 input keys

vim app.py

## serve the food-group tree (path B = model loaded from MLflow).
## run from repo root -> sqlite:///mlflow.db + mlruns/ resolve.

from fastapi import FastAPI, HTTPException   ## web framework + clean err responses
from pydantic import BaseModel               ## validates the incoming JSON body
import pandas as pd                          ## builds the single-row table the model expects
import mlflow                                ## access tracking store
import mlflow.sklearn                        ## load saved scikit-learn model

#/ load block
mlflow.set_tracking_uri("sqlite:///mlflow.db")                       ## set tracking URL
_runs = mlflow.search_runs(experiment_names=["food_group_baseline"]) ## find the run 
_run_id = _runs.iloc[0]["run_id"]                                    ## take run id
MODEL = mlflow.sklearn.load_model(f"runs:/{_run_id}/model")          ## MODEL = load_model()
FEATURES = list(MODEL.feature_names_in_)                             ## the 58 keys in order

DISCLAIMER = "Educational project - not nutritional/medical advice." ## say in every answer

app = FastAPI(title="nutrition_ops food-group classifier")           ## create application object

class PredictRequest(BaseModel):                                     ## define shape of a /predict body
    features: dict[str, float]                                       ## eg{"ENERC_kcal": 250, "FAT_g": 10}

@app.get("/")                                                        ## register GET at /
#/ returns status + expected feature count + disclaimer.
def root():   
    return {"status": "ok", "n_features_expected": len(FEATURES), "disclaimer": DISCLAIMER}
@app.post("/predict")                                                ## prediction route. reguster POST
def predict(req: PredictRequest):                                    ## FastAPI parses
    missing = [f for f in FEATURES if f not in req.features]         ## which required keys are absent?
    if missing:                                                      ## refuse to
        raise HTTPException(status_code=422, detail={"missing_features": missing})  ## refuse with 422
    row = pd.DataFrame([[req.features[f] for f in FEATURES]]), columns=FEATURES     ## build one row table
    guess = MODEL.predict(row)[0]                                    ## predict -> array of 1; take element
    return {"food_group": str(guess), "disclaimer": DISCLAIMER}      ## answer + disclaimer

---

cd ~/dev/nutrition_ops
uv run fastapi dev app.py     ## start the server

?? -> http://127.0.0.1:8000/docs
/# code 200 + disclaimer

#/ build a test body

vim test_body.py

<> test_body.py

## make_test_body.py -- throwaway helper: builds ONE real /predict test body from our data

import pandas as pd          ## pandas: reads our CSV into a table (a DataFrame)
import json                  ## json: turns a Python dict into JSON text we can paste
import mlflow.sklearn        ## lets us load the saved model and read its exact feature list

## point MLflow at the same local store the app uses (a relative file in the repo root)
mlflow.set_tracking_uri("sqlite:///mlflow.db")

## rebuild the trained tree from its logged run (the same run_id the app loads)
model = mlflow.sklearn.load_model("runs:/be2a6a4c0a0b4af392b21be912150788/model")

## the 58 nutrient column names, in the EXACT order the model learned them
features = list(model.feature_names_in_)   ## feature_names_in_ is a numpy array -> make it a plain list

## load the cleaned dataset (the 1727 rows we trained on)
df = pd.read_csv("model_data.csv")

## take the FIRST food row, but only the 58 feature columns
row = df[features].iloc[0]                 ## df[features] = just those columns; .iloc[0] = first row by position

## build a {name: value} dict, forcing plain Python floats (JSON cannot read numpy floats)
features_dict = {key: float(value) for key, value in row.items()}

## wrap it in the shape /predict expects: {"features": {...}}
body = {"features": features_dict}

## print it as pretty JSON, ready to copy-paste into Swagger
print(json.dumps(body, indent=2))

uv run python test_body.py

-> http://127.0.0.1:8000/docs

POST /predict -> expand -> try it -> wipe req body -> paste helper -> execute -> sv response -> 200 {}

uv run python load_check.py
uv run python test_body.py

___

#/ pytest as dev dependecy 

uv add --dev pytest
vim pyproject.toml  # check new dep
vim test_app.py     # automated checks for food-group API

<> test_app.py

from fastapi.testclient import TestClient       ## calls the app in-memory, no running server needed
from app import app, FEATURES                   ## fastapi app object + 58 feature names

client = TestClient(app)        # fake client wired to the app

def test_root_heartbeat():
    response = client.get("/")      ## call GET /
    assert response.status_code == 200                    ## should be OK
    assert response.json()["n_features_expected"] == 58   ## should report 58 features

def test_predict_returns_food_group():
    body = {"features": {name: 0.0 for name in FEATURES}}  ## all 58, dummy 0.0 values
    response = client.post("/predict", json=body)          ## POST it to /predict
    assert response.status_code == 200      ## should succeed
    assert "food_group" in response.json()      ## response includes a food_group

def test_predict_returs_food_group():
    response = client.post("/predict", json={"features": {}})        ## send zero features
    assert response.status_code == 422      ## should be rejected
    assert len(response.json()["detail"]["missing_features"]) == 58  ## all 58 reported missing

uv run pytest -v        # from repo root to let importing app load model


uv add --dev pytest
uv run pytest -v

<> test_app.py

def test_predict_returns_food_group():
⇣⇣⇣
def test_predict_rejects_empty():

uv run pytest.py -v

git status
git add test_app.py pyproject.toml uv.lock .gitignore
git diff --staged
git commit -m "add pytests for the API (heartbeat, predict, 422)"
git git log --oneline

uv sync     ## install dep
uv run fastapi dev app.py       start the API -> http://127.0.0.1:8000/docs
uv run pytest -v        ## run tests

vim README.md 

cd ~/dev/nutrition_ops   ## move into the project repo
git status               ## show staged / modified / untracked
git log --oneline -3     ## show last 3 commits (HEAD + history)


uv sync && uv run pytest -v     ## install deps, then run the tests verbosely
uv run fastapi dev app.py       ## start the api

docker --version     ## print the installed Docker version
docker info          ## confirm the Docker engine is runnin
___

vim fix_mlflow.py

<> fix_mlflow.py

## i only run it one time, from inside the nutrition_ops folder

import sqlite3      ## sqlite3 lets python open and change the mlflow.db database
import shutil       ## shutil lets me copy a file, so i can make a backup first


shutil.copy("mlflow.db", "mlflow.db.bak")     ## copy mlflow.db into a new file called mlflow.db.bak
print("backup made: mlflow.db.bak")          ## print a message so i know the backup worked


old_path = "/Users/jyx/dev/nutrition_ops/"    ## everything before "mlruns/" is the part that is not portable


con = sqlite3.connect("mlflow.db")            ## open a connection to the mlflow.db file
cur = con.cursor()                           ## the cursor is the thing that actually runs my sql commands


cur.execute("UPDATE experiments SET artifact_location = REPLACE(artifact_location, ?, '')", (old_path,))   ## fix the experiments table

cur.execute("UPDATE logged_models SET artifact_location = REPLACE(artifact_location, ?, '')", (old_path,)) ## fix the logged_models table

cur.execute("UPDATE runs SET artifact_uri = REPLACE(artifact_uri, ?, '')", (old_path,))                    ## fix the runs table


con.commit()                                 ## commit means save my changes into the file for real
con.close()                                  ## close the connection now that i am done
print("done, the paths are now relative")    ## print a message so i know it finished

#/ run the script from repo-root
cd ~/dev/nutrition_ops
uv run python fix_mlflow.py

#/ check
uv run fastapi dev app.py -> http://127.0.0.1:8000
___
Docker plan: build a small Python 3.13 image, install deps with uv, copy in only what the API needs at runtime (app.py + mlflow.db + mlruns/), serve with fastapi run bound to 0.0.0.0.
#/fastapi run instead of fastapi dev (dev binds to 127.0.0.1, meaning only reachable inside the containter)

vim dockerfile

#/start from an image that already has python 3.13
FROM python:3.13-slim

#/ /app as working folder inside container
WORKDIR /app

#/ install uv
RUN pip install uv

#/ copy just the 2 deps first, so docker can reuse this layer when only code changes later
COPY pyproject.toml uv.lock ./

#/ install deps in a venv inside
## --frozen = obey the lockfile exactly, --no-intall-project = deps only, --no-dev = skip test tool

RUN uv sync --frozen --no-install-project --no-dev
#/ copy api code into the image
COPY app.py ./

## copy mlflow db (records where the model lives)
COPY mlflow.db ./

## copy the model files themselves (whole mlruns folder)
COPY mlruns ./mlruns

## put venv's programs on PATH for calling fastapi directly
ENV PATH="/app/.venv/bin:$PATH"

## tell docker the app listens on port 8000
EXPOSE 8000

## start the api in production mode on 0.0.0.0 to be reachable from outside of container
CMD ["fastapi", "run", "app.py", "--host", "0.0.0.0", "--port", "8000"]

vim .dockerignore

## this file lists things docker should NOT copy into the build, to keep it fast and small
#/// do NOT list mlflow.db or mlruns here, because the app needs them inside the image

## the local virtual environment is huge (600+ MB) and gets rebuilt inside the container anyway
.venv
## the 20 MB raw data file is only used for training, not for serving
harvest_raw.json
## git history is not needed inside the image
.git
## python's cached bytecode folders, anywhere they appear
**/__pycache__
## pytest's cache folder
.pytest_cache
## the database backup we made before the path fix
mlflow.db.bak
## mac finder junk files, anywhere they appear
**/.DS_Store

#/ build the image
docker build -t nutrition_ops 
/# fail, no live engine running
colima start
docker ps ## check

#/ run image & link port on my mac to port on container
docker run -p 8000:8000 nutrition_ops 

vim test_container.py

## this script tests the /predict endpoint of my running docker container
import pandas as pd     ## pandas reads my csv file
import requests     ## requests sends http calls to my api


data = pd.read_csv("model_data.csv")        ## load the csv into a table
first_row = data.iloc[0]        ## grab row number 0, the first food


label_columns = ["nummer", "namn", "version", "food_group"]   ## the non-feature columns


features = {}       ## start with an empty dict
for col in data.columns:        ## go through every column name
    if col not in label_columns:        ## skip the four label columns
        features[col] = float(first_row[col])       ## add the nutrient value as a plain float


url = "http://127.0.0.1:8000/predict"                 ## the address of my api running in docker
response = requests.post(url, json={"features": features})    ## post the body the api expects
print("status code:", response.status_code)           ## 200 means it worked
print("answer:", response.json())                     ## the predicted food group + disclaimer

vim README.md

git status
git add README.md fix_mlflow.py .dockerignore dockerfile test_container.py
git commit -m ""
git status
git push
git log --oneline