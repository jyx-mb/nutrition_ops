## rebuild the trained tree from its MLflow run BEFORE wrapping it in an API.
## MUST be run from the repo root (~/dev/nutrition_ops) so the relative paths resolve.

import mlflow            ## MLflow Python API (tracking store + model loading)
import mlflow.sklearn    ## the scikit-learn "flavor": knows how to rebuild sklearn models

## !! point MLflow at the SAME store the trainer wrote to.
## skip this and MLflow defaults to ./mlruns, finds nothing, and the search comes back EMPTY.
mlflow.set_tracking_uri("sqlite:///mlflow.db")   

#/ table of runs, grab first id, print it
runs = mlflow.search_runs(experiment_names=["food_group_baseline"])  
run_id = runs.iloc[0]["run_id"]                  
print("run_id:", run_id)                         

#/ rebuild tree
model = mlflow.sklearn.load_model(f"runs:/{run_id}/model")  

print("loaded model type:", type(model).__name__)      
print("expects feature count:", model.n_features_in_)  

## Add one line to the end of load_check.py

print("feature names in order:", list(model.feature_names_in_))  
print("loaded model type:", type(model).__name__)      
print("expects feature count:", model.n_features_in_)  
print("feature names in order:", list(model.feature_names_in_))  
