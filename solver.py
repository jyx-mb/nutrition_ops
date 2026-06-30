#/ tools needed
import pandas as pd                                   
from scipy.optimize import linprog                    

#/ load the daily targets once - same for every request
targets = pd.read_csv("targets.csv")                  
nutrient_columns = targets["our_column"].tolist()     
rda_floors = targets["rda"].tolist()                  

#/ load the whole food table once - filter it per call inside the function
foods = pd.read_csv("foods.csv")                      


#/ given the food ids the user chose, work out grams to meet every floor
def recommend(chosen_nummers):                                 
    #/ keep only the chosen foods + their nutrient columns
    chosen_foods = foods[foods["nummer"].isin(chosen_nummers)] 
    food_values = chosen_foods[nutrient_columns]              

    #/ INGREDIENT 1 - objective: minimize TOTAL grams of food
    c = [1] * len(chosen_foods)                               

    #/ INGREDIENT 2 - rules: each nutrient must reach its floor
    #/ linprog only does "<=", so flip every ">=" by negating both sides
    A_ub = []                                                 
    b_ub = []                                                 
    for column_name, floor in zip(nutrient_columns, rda_floors): 
        row = []                                             
        for value in food_values[column_name]:               
            row.append(-value / 100)                         
        A_ub.append(row)                                     
        b_ub.append(-floor)                                  

    #/ INGREDIENT 3 - solve, with a flat 0-300 g cap per food
    result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=(0, 300)) 

    #/ feasible: build the plan dict instead of printing it
    if result.success:                                       
        plan = []                                            
        for food, grams in zip(chosen_foods["namn"], result.x): 
            plan.append({"food": food, "grams": round(grams, 1)}) 

        #/ PROVE it: re-total each nutrient and count floors met
        met = 0                                              
        for column_name, floor in zip(nutrient_columns, rda_floors): 
            got = 0                                          
            for grams, value in zip(result.x, food_values[column_name]): 
                got = got + (grams / 100) * value            
            if got >= floor - 0.01:                          
                met = met + 1                                

        return {                                             
            "feasible": True,       
            "plan": plan,       
            "total_grams": round(result.x.sum(), 1),         
            "floors_met": met,      
            "floors_total": len(nutrient_columns),      
        }

    #/ infeasible: report which nutrients can't be reached - never fake a plan
    else:           
        blockers = []       
        for column_name, floor in zip(nutrient_columns, rda_floors): 
            most_possible = food_values[column_name].sum() * (300 / 100) 
            if most_possible < floor:           
                blockers.append({           
                    "nutrient": column_name,        
                    "best_possible": round(most_possible, 1), 
                    "needed": floor,        
                })
        return {        
            "feasible": False,      
            "blockers": blockers,       
        }


#/ run with the test foods so "uv run solver.py" still works as a quick check
if __name__ == "__main__":          
    chosen_nummers = [123, 1255, 4941, 702, 553, 78]         
    answer = recommend(chosen_nummers)      
    print("feasible:", answer["feasible"])                   
    if answer["feasible"]:          
        for item in answer["plan"]:         
            print(item["food"], "->", item["grams"], "g")    
        print("total grams:", answer["total_grams"])         
    else:              
        print("floors met:", answer["floors_met"], "of", answer["floors_total"]) 
        for blocker in answer["blockers"]:                   
            print(blocker["nutrient"], "- best:", blocker["best_possible"], "needed:", blocker["needed"]) ## the gap