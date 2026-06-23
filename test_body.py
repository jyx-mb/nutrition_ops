## builds ONE real /predict test body from the data

#/ load the libraries we need
import pandas as pd       
import json               
import mlflow.sklearn     

#/ rebuild the trained model from MLflow and read its 58-feature contract
mlflow.set_tracking_uri("sqlite:///mlflow.db")                                    
model = mlflow.sklearn.load_model("runs:/be2a6a4c0a0b4af392b21be912150788/model") 
features = list(model.feature_names_in_)                                          

#/ pull one real food from the data and shape it the way /predict expects
df = pd.read_csv("model_data.csv")                                
row = df[features].iloc[0]                                        
features_dict = {key: float(value) for key, value in row.items()} 
body = {"features": features_dict}                                
print(json.dumps(body, indent=2))                                 
