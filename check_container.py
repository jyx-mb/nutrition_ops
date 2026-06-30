## this tests the /predict endpoint of my running docker container
## it takes one real food row from the data and sends its 58 nutrient numbers to the api
import pandas as pd                                   
import requests                                       

## read the clean dataset and take the very first food row
data = pd.read_csv("model_data.csv")                  
first_row = data.iloc[0]                              

## these four columns are labels, not nutrient features, so i will skip them
label_columns = ["nummer", "namn", "version", "food_group"]   

## build a dict of the 58 nutrient features, turning each value into a plain python float
features = {}                                         
for col in data.columns:                              
    if col not in label_columns:                      
        features[col] = float(first_row[col])         

## send the features to the container's /predict endpoint and print the answer
url = "http://127.0.0.1:8000/predict"                 
response = requests.post(url, json={"features": features})    
print("status code:", response.status_code)           
print("answer:", response.json())                     