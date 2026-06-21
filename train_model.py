#/ build the baseline: load clean data, split into features (X) and target (y)
import pandas as pd                                       
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier             
from sklearn.metrics import accuracy_score, classification_report  
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

#/ train the baseline tree, then grade it on the unseen test set
model = DecisionTreeClassifier(random_state=42)  
model.fit(X_train, y_train)                       

predictions = model.predict(X_test)              

accuracy = accuracy_score(y_test, predictions)   
print("accuracy:", round(accuracy, 3))           

print(classification_report(y_test, predictions))