#/ import test client and app + feature list
from fastapi.testclient import TestClient       
from app import app, FEATURES                   

client = TestClient(app)      

#/ the heartbeat should 200 -> report 58 expected features
def test_root_heartbeat():
    response = client.get("/")      
    assert response.status_code == 200                    
    assert response.json()["n_features_expected"] == 58   

#/ a full 58 body should return a food group (happy time)
def test_predict_returns_food_group():
    body = {"features": {name: 0.0 for name in FEATURES}}  
    response = client.post("/predict", json=body)          
    assert response.status_code == 200      
    assert "food_group" in response.json()      

#/ checks rejection w/ 422
def test_predict_rejects_empty():
    response = client.post("/predict", json={"features": {}})        
    assert response.status_code == 422      
    assert len(response.json()["detail"]["missing_features"]) == 58  