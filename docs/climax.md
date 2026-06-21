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
