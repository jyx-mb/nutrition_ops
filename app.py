## serve the food-group tree (path B = model loaded from MLflow).
## run from repo root so sqlite:///mlflow.db + mlruns/ resolve.

#/ web framework + clean errors, validate body, build one-row table, load the model
from fastapi import FastAPI, HTTPException   
from pydantic import BaseModel               
import pandas as pd                          
import mlflow                                
import mlflow.sklearn                        

# /// load the model once, not per request
mlflow.set_tracking_uri("sqlite:///mlflow.db")                        
_runs = mlflow.search_runs(experiment_names=["food_group_baseline"])  
_run_id = _runs.iloc[0]["run_id"]                                     
MODEL = mlflow.sklearn.load_model(f"runs:/{_run_id}/model")           
FEATURES = list(MODEL.feature_names_in_)                              

# /// health domain toy -> every ans
DISCLAIMER = "Educational project - not nutritional or medical advice."

#/ the app object the server runs
app = FastAPI(title="nutrition_ops food-group classifier")           

#/ define a valid /predict. fastAPI rejects bodies that don't match
class PredictRequest(BaseModel):                                     
    features: dict[str, float]                                       
#/ server alive ? -> status + expected feature count + disclaimer.
@app.get("/")                                                       
def root():                                                         
    return {"status": "ok", "n_features_expected": len(FEATURES), "disclaimer": DISCLAIMER}
#/ find missing required keys. if any -> reject w/ 422 + missing line
@app.post("/predict")                                              
def predict(req: PredictRequest):                                  
    missing = [f for f in FEATURES if f not in req.features]       
    if missing:                                                   
        raise HTTPException(status_code=422, detail={"missing_features": missing})  
    row = pd.DataFrame([[req.features[f] for f in FEATURES]], columns=FEATURES)
    guess = MODEL.predict(row)[0]                                 
    return {"food_group": str(guess), "disclaimer": DISCLAIMER}   