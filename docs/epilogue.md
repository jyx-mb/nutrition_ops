#/ small pivot, sticking t o the original plan of recommandations
#/ lock the join keys

cd ~/dev/nutrition_ops    
head -1 foods.csv           ## print first line = the column headers

vim check_targets.py

<> check_targets.py

import pandas as pd     ## bring in the pandas library

targets = pd.read_csv("targets.csv")      ## read targets.csv into a table called targets
print(targets)          ## print every row for easy eyeball
print(targets.shape)                      ## print (rows, columns) 

uv run python check_targets.py

mv targets.csv check_targets.py ../   
cd ..
ls targets.csv check_targets.py foods.csv     
uv run python check_targets.py                

uv add spicy  ## record it as direct dependency in pyproj + uv.lock
vim check_spicy.py

<> check_spicy.py

import scipy        
from scipy.optimize import linprog    ## the solver 

print(scipy.__version__)              ## show scipy's version so we know it is really here
print("linprog ready")                ## a plain message proving the import worked

uv run python check_scipy.py

vim solver.py

<> solver.py

import pandas as pd     ## bring in pandas

targets = pd.read_csv("targets.csv")        ## read targets.csv into a table


nutrient_columns = targets["our_column"].tolist()   ## the 19 foods.csv column names
rda_floors = targets["rda"].tolist()                ## the 19 daily floor numbers


print(nutrient_columns)         ## expect 19 column-name strings
print(rda_floors)           ## expect 19 numbers
print("how many:", len(nutrient_columns))           ## expect 19

vim find_food.py

<> find_food.py


import pandas as pd                                        ## bring in pandas

foods = pd.read_csv("foods.csv")                           ## read the big food table

word = "milk"                                              ## CHANGE this to the food you want


matches = foods[foods["namn"].str.contains(word, case=False, na=False)]   ## filter rows by name


print("matches found:", len(matches))                  ## how many foods contain the word
print(matches[["nummer", "namn"]].to_string())         ## show EVERY match - id + name, no truncation

vim solver.py

<> solver.py 
#/ replace

import pandas as pd         ## pandas in

targets = pd.read_csv("targets.csv")        ## read targets.csv into a table


nutrient_columns = targets["our_column"].tolist()    ## the 19 foods.csv column names
rda_floors = targets["rda"].tolist()                 ## the 19 daily floor numbers


foods = pd.read_csv("foods.csv")        ## read foods.csv


chosen_nummers = [123, 1255, 4941, 702, 553]         ## milk, salmon, spinach, rolled oats, banana


chosen_foods = foods[foods["nummer"].isin(chosen_nummers)]   ## filter foods to the picked ids


print(chosen_foods[["nummer", "namn"]])              ## should list the 5 foods


food_values = chosen_foods[nutrient_columns]         ## a small table: 5 foods x 19 nutrients
print("shape:", food_values.shape)                   ## expect (5, 19)


print("missing cells:", food_values.isna().sum().sum())   ## total NaN count across the table


uv run solver.py

<> solver.py

import pandas as pd     ## pandas in
from scipy.optimize import linprog      ## bring in the LP solver


targets = pd.read_csv("targets.csv")        ## read targets.csv into a table


nutrient_columns = targets["our_column"].tolist()    ## the 19 foods.csv column names
rda_floors = targets["rda"].tolist()                 ## the 19 daily floor numbers


foods = pd.read_csv("foods.csv")                     ## read foods.csv
chosen_nummers = [123, 1255, 4941, 702, 553]         ## milk, salmon, spinach, rolled oats, banana
chosen_foods = foods[foods["nummer"].isin(chosen_nummers)]   ## filter foods to the picked ids
food_values = chosen_foods[nutrient_columns]                 ## table: 5 foods x 19 nutrients (per 100 g)


c = [1] * len(chosen_foods)     ## a 1 for each food, so c@x = total grams



A_ub = []           ## will hold one row per nutrient
b_ub = []           ## will hold one floor per nutrient (negated)
for column_name, floor in zip(nutrient_columns, rda_floors):   ## pair each nutrient with its RDA
    row = []        ## this nutrient's coefficient for each food
    for value in food_values[column_name]:            ## each food's per-100g amount of this nutrient
        row.append(-value / 100)        ## per-GRAM amount, NEGATED for the >= -> <= flip
    A_ub.append(row)        ## add this nutrient's row to the matrix
    b_ub.append(-floor)     ## the floor, also negated




result = linprog(c, A_ub=A_ub, b_ub=b_ub)            ## run the optimizer


print("success:", result.success)                    ## True = it found a valid combination
print("message:", result.message)                    ## the solver's plain-language status
if result.success:                                   ## only read amounts if a solution exists
    for food, grams in zip(chosen_foods["namn"], result.x):   ## pair each food with its g
        print(food, "->", round(grams, 1), "g")       ## how many grams of that food to eat
    print("total grams:", round(result.x.sum(), 1))   ## the total amount of food for the


uv run solver.py -> recommanded 1.3kg os spinach 

#/ cap foods at a maximum of 300g 

<> solver.py

result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=(0, 300))   ## each food must be between 0 and 300 g


uv run solver.py

<> solver.py

print("success:", result.success)       ## True = it found a valid combination
print("message:", result.message)       ## the solver's plain-language status

if result.success:                                   ## a solution exists -> show the plan
    for food, grams in zip(chosen_foods["namn"], result.x):   ## pair each food with its grams
        print(food, "->", round(grams, 1), "g")       ## how many grams of that food to eat
    print("total grams:", round(result.x.sum(), 1))   ## total food for the day
else:                                                 ## no solution -> explain which floors block it
    print("can't reach these even at 300 g of every food:")   ## the honest report
    for column_name, floor in zip(nutrient_columns, rda_floors):   ## check each nutrient
        most_possible = food_values[column_name].sum() * (300 / 100)   ## all 5 foods maxed at 300 g
        if most_possible < floor:                      ## still below the floor?
            print(column_name, "- best:", round(most_possible, 1), "needed:", floor)   ## show the gap


uv run solver.py

<> solver.py

add
 #/ PROVE it: independently total each nutrient and check it clears its floor
    met = 0                                            ## how many floors the plan actually reaches
    for column_name, floor in zip(nutrient_columns, rda_floors):   ## check each nutrient
        got = 0                                        ## this nutrient's total from the plan
        for grams, value in zip(result.x, food_values[column_name]):   ## each food's grams x its value
            got = got + (grams / 100) * value          ## add this food's contribution
        if got < floor - 0.01:                         ## fell short of the floor?
            print("MISS:", column_name, "got", round(got, 1), "need", floor)   ## report it
        else:                                          ## reached it
            met = met + 1                              ## count this floor as met
    print("floors met:", met, "of", len(nutrient_columns))   ## expect every one


#/ re-write solver.py

<> solver.py

import pandas as pd             ## read the CSV tables
from scipy.optimize import linprog          ## the linear-programming solver


targets = pd.read_csv("targets.csv")            ## the 18-nutrient targets file
nutrient_columns = targets["our_column"].tolist()     ## foods.csv column name per nutrient, in order
rda_floors = targets["rda"].tolist()        ## the daily floor per nutrient, same order


foods = pd.read_csv("foods.csv")                      ## all 2575 foods


def recommend(chosen_nummers):          ## the function the API will call
    #/ keep only the chosen foods + their nutrient columns
    chosen_foods = foods[foods["nummer"].isin(chosen_nummers)] ## rows whose nummer is in the user's list
    food_values = chosen_foods[nutrient_columns]              ## just the nutrient columns (per 100 g)


    c = [1] * len(chosen_foods)         ## weight 1 per food = add up all the grams



    A_ub = []           ## left side, one row per nu
    b_ub = []               ## right side, the negated floors
    for column_name, floor in zip(nutrient_columns, rda_floors): ## each nutrient + its fl
        row = []            ## this nutrient's per-gram amount per food
        for value in food_values[column_name]:               ## per-100g value for each fo
            row.append(-value / 100)            ## per-gram, negated for the flip
        A_ub.append(row)            ## store the row
        b_ub.append(-floor)         ## store the negated floor


    result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=(0, 300)) ## run the solver


    if result.success:          ## the solver found a plan
        plan = []           ## list of {food, grams}
        for food, grams in zip(chosen_foods["namn"], result.x): ## pair each food with its grams
            plan.append({"food": food, "grams": round(grams, 1)}) ## one row per food


        met = 0         ## how many floors clear
        for column_name, floor in zip(nutrient_columns, rda_floors): ## each nutrient + fl
            got = 0         ## running total for this nutrient
            for grams, value in zip(result.x, food_values[column_name]): ## each food's gr
                got = got + (grams / 100) * value            ## add this food's contribution
            if got >= floor - 0.01:         ## clears it (tiny rounding a
                met = met + 1           ## count it

        return {            ## the feasible answer
            "feasible": True,           ## a plan exists
            "plan": plan,                                    ## the gram amounts
            "total_grams": round(result.x.sum(), 1),         ## total food for the day
            "floors_met": met,          ## how many floors are met
            "floors_total": len(nutrient_columns),           ## should equal floors_met wh
        }


    else:           ## no plan can meet every flo
        blockers = []           ## the nutrients that fall short
        for column_name, floor in zip(nutrient_columns, rda_floors): ## each nutrient + fl
            most_possible = food_values[column_name].sum() * (300 / 100) ## max at 300 g of every food
            if most_possible < floor:                        ## still short even maxed out
                blockers.append({           ## record the honest gap
                    "nutrient": column_name,                 ## which nutrient
                    "best_possible": round(most_possible, 1), ## the most these foods can give
                    "needed": floor,                         ## what the floor needs
                })
        return {            ## the honest "can't do it" a
            "feasible": False,                               ## no plan for these foods
            "blockers": blockers,                            ## exactly which nutrients fa
        }


if __name__ == "__main__":                                   ## only when run directly, not when imported
    chosen_nummers = [123, 1255, 4941, 702, 553, 78]         ## the 6 test foods from Stag
    answer = recommend(chosen_nummers)                       ## call the function
    print("feasible:", answer["feasible"])                   ## did it work?
    if answer["feasible"]:      ## yes - show the plan
        for item in answer["plan"]:                          ## each food in the plan
            print(item["food"], "->", item["grams"], "g")    ## name and grams
        print("total grams:", answer["total_grams"])         ## total for the day
        print("floors met:", answer["floors_met"], "of", answer["floors_total"]) ## regression check
    else:                                                    ## no - show the blockers
        for blocker in answer["blockers"]:                   ## each blocking nutrient
            print(blocker["nutrient"], "- best:", blocker["best_possible"], "needed:", blocker["needed"])


uv run fastapi dev app.py