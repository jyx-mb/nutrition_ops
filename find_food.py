#/ find_food.py - search foods.csv by name to get a food's nummer (id)
import pandas as pd                                        

foods = pd.read_csv("foods.csv")                           

word = "milk"                                              

#/ keep only rows whose name contains that word (ignore upper/lower case)
matches = foods[foods["namn"].str.contains(word, case=False, na=False)]   


print("matches found:", len(matches))                  
print(matches[["nummer", "namn"]].to_string())        
