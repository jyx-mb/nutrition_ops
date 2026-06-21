#/ build the baseline: load clean data, split into features (X) and target (y)
import pandas as pd                                       
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier             
from sklearn.metrics import accuracy_score, classification_report  
import mlflow
import mlflow.sklearn       ## sub-

mlflow.set_experiment("food_group_baseline")
data = pd.read_csv("model_data.csv")                      

y = data["food_group"]                                    
X = data.drop(columns=["nummer", "namn", "version", "food_group"])  

#/ hide 20% of the data to u grade the model on rows it never saw
X_train, X_test, y_train, y_test = train_test_split(
    X, y,                       
    test_size=0.2,              
    random_state=42,            
    stratify=y,                 
)

print("train:", X_train.shape)  
print("test:", X_test.shape)    
print("X:", X.shape)                                      
print("y:", y.shape)                                      

#/ train + grade the baseline INSIDE one tracked MLflow run
with mlflow.start_run():                                      
    mlflow.log_param("model_type", "DecisionTreeClassifier")  
    mlflow.log_param("random_state", 42)                      
    mlflow.log_param("test_size", 0.2)                        
    mlflow.log_param("n_features", X.shape[1])                

    model = DecisionTreeClassifier(random_state=42)           
    model.fit(X_train, y_train)                               

    predictions = model.predict(X_test)                       

    accuracy = accuracy_score(y_test, predictions)            
    mlflow.log_metric("accuracy", accuracy)                   
    print("accuracy:", round(accuracy, 3))                    

    mlflow.sklearn.log_model(model, name="model")             

    print(classification_report(y_test, predictions))         