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

#/ a feasible food set should return a real plan that meets every floor
def test_recommend_returns_plan():                                 
    body = {"nummers": [123, 1255, 4941, 702, 553, 78]}            
    response = client.post("/recommend", json=body)               
    assert response.status_code == 200                            
    data = response.json()                                        
    assert data["feasible"] == True                               
    assert data["floors_met"] == data["floors_total"]            
    assert "disclaimer" in data                                   

#/ an empty list is not a real request -> refuse it, never guess
def test_recommend_rejects_empty():                               
    response = client.post("/recommend", json={"nummers": []})    
    assert response.status_code == 422                            
    assert response.json()["detail"] == "give at least one food id"

#/ an id not in foods.csv must be rejected, never silently ignored
def test_recommend_rejects_unknown_id():                          
    response = client.post("/recommend", json={"nummers": [999999999]}) 
    assert response.status_code == 422                            
    assert 999999999 in response.json()["detail"]["unknown_nummers"] 

#/ an impossible set (one banana can't hit 18 floors) must answer HONESTLY, not fake a plan
def test_recommend_infeasible_is_honest():                        
    response = client.post("/recommend", json={"nummers": [553]}) 
    assert response.status_code == 200                            
    data = response.json()                                        
    assert data["feasible"] == False                             
    assert len(data["blockers"]) > 0                             
    assert "plan" not in data                                    