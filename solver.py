#/ tools needed
import pandas as pd                                  
from scipy.optimize import linprog                   

#/ load the daily targets built in Stage 1
targets = pd.read_csv("targets.csv")                 

#/ pull the two lists the optimizer needs, in matching order
nutrient_columns = targets["our_column"].tolist()    
rda_floors = targets["rda"].tolist()                 

#/ load the big food table and keep only the 5 foods + their 19 nutrient columns
foods = pd.read_csv("foods.csv")                     
chosen_nummers = [123, 1255, 4941, 702, 553, 78]         
chosen_foods = foods[foods["nummer"].isin(chosen_nummers)]   
food_values = chosen_foods[nutrient_columns]                 

#/ INGREDIENT 1 - the objective: minimize TOTAL grams of food
c = [1] * len(chosen_foods) 
                         

#/ INGREDIENT 2 - the rules: each nutrient must reach its floor
#/ linprog only does "<=", so we flip every ">=" by negating both sides
A_ub = []                                            
b_ub = []                                            
for column_name, floor in zip(nutrient_columns, rda_floors):   
    row = []                                          
    for value in food_values[column_name]:            
        row.append(-value / 100)                      
    A_ub.append(row)                                  
    b_ub.append(-floor)                               

#/ INGREDIENT 3 - bounds: every food >= 0 grams is linprog's default, so nothing to set

#/ 0-300g
result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=(0, 300))   

#/ report the outcome honestly
print("success:", result.success)                    
print("message:", result.message)                    

if result.success:                                   
    for food, grams in zip(chosen_foods["namn"], result.x):   
        print(food, "->", round(grams, 1), "g")       
    print("total grams:", round(result.x.sum(), 1))
     
     #/ PROVE it: independently total each nutrient and check it clears its floor
    met = 0                                            
    for column_name, floor in zip(nutrient_columns, rda_floors):   
        got = 0                                        
        for grams, value in zip(result.x, food_values[column_name]):   
            got = got + (grams / 100) * value          
        if got < floor - 0.01:                         
            print("MISS:", column_name, "got", round(got, 1), "need", floor)   
        else:                                          
            met = met + 1                              
    print("floors met:", met, "of", len(nutrient_columns))   
else:                                                 
    print("can't reach these even at 300 g of every food:")   
    for column_name, floor in zip(nutrient_columns, rda_floors):   
        most_possible = food_values[column_name].sum() * (300 / 100)   
        if most_possible < floor:                      
            print(column_name, "- best:", round(most_possible, 1), "needed:", floor)   