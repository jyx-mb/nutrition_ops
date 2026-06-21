## load both files, join them, drop Other, drop rows with missing cells
import pandas as pd    

foods = pd.read_csv("foods.csv")       
labels = pd.read_csv("food_groups.csv")    

data = foods.merge(labels, on="nummer")    

data = data[data["food_group"] != "Other"]     
data = data.drop(columns=["VITD_x_µg"])
data = data.dropna()
data.to_csv("model_data.csv", index=False)    ## model's input file
# diagnose
print("shape:", data.shape)    
print(data.dtypes.value_counts())      
print(data.isna().sum().sort_values(ascending=False).head(15))