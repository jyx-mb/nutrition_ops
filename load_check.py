## prove the model can be reloaded from MLflow

#/ load the saved model back from MLflow 
import mlflow.sklearn     

mlflow.set_tracking_uri("sqlite:///mlflow.db")                                    
model = mlflow.sklearn.load_model("runs:/be2a6a4c0a0b4af392b21be912150788/model") 

#/ prove the model and its feature contract came back intact
print(model)                          
print(model.feature_names_in_)        
print(len(model.feature_names_in_))   
