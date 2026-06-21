import re       ## re = regex, used to split a name into whole words
import csv                                   ## csv = read the foods.csv table row by row
from collections import Counter              ## Counter = a tally box that counts things for us

## lookup table: every food group + the keywords that signal it, in priority order
RULES = [                                                                                 
    ("Sweets",        ["chocolate", "sugar", "candy", "cake", "biscuit", "jam", "honey"]), 
    ("Fats & oils",   ["oil", "butter", "margarine", "lard", "tallow", "spread", "ghee"]), 
    ("Dairy & eggs",  ["cheese", "milk", "cream", "yoghurt", "yogurt", "egg", "fraiche"]),
    ("Meat & fish",   ["meat", "beef", "pork", "chicken", "sausage", "ham", "fish", "cod", 
                       "veal", "salmon", "herring", "lamb", "liver", "fillet"]),
    ("Grains & bread",["bread", "wheat", "wholegrain", "rice", "pasta", "oat", "flour"]),   
    ("Fruit & veg",   ["fruit", "potato", "potatoes", "apple", "berry", "tomato", "tomatoes", "carrot", 
                       "carrots", "onion", "onions", "vegetable", "vegetables", "bean", "beans", 
                       "pea", "peas", "soy", "salad", "cabbage", "corn", "mushroom", "orange"]),
    
]                                                                                         
DEFAULT = "Other"       ## catch-all when no matches

## the engine: turn one food name into exactly one group label
def classify(name):     
    words = set(re.findall(r"[a-z]+", name.lower()))    
    for group, keywords in RULES:       
        for kw in keywords:     
            if kw in words:     
                return group        
    return DEFAULT      

## self-test: this block runs ONLY when launching the file directly
if __name__ == "__main__":      
    samples = [     
        "Beef tallow",      
        "Low fat milk 0.5%",        
        "Chocolate milk drink",     
        "Potato boiled",        
        "Soy milk",     
        "Wholegrain bread",     
    ]    

    ## send every sample name through the engine and print group <- name   
    for s in samples:     
        print(f"{classify(s):15s} <- {s}")

    ##  one row per food = its id number + our group
    with open("foods.csv", newline="") as fin, open("food_groups.csv", "w", newline="") as fout:
        reader = csv.DictReader(fin)                              
        writer = csv.writer(fout)                               
        writer.writerow(["nummer", "food_group"])              
        for row in reader:                                     
            writer.writerow([row["nummer"], classify(row["namn"])])

    ## full run: classify every food in foods.csv 
    groups = Counter()                       
    with open("foods.csv", newline="") as f: 
        for row in csv.DictReader(f):        
            groups[classify(row["namn"])] += 1   
    print()                                  
    for group, n in groups.most_common():    
        print(f"{group:15s} {n}")            
    print(f"{'TOTAL':15s} {sum(groups.values())}")  

    ## skip words already jugged
    SKIP = {"raw", "fried", "frozen", "boiled", "canned", "dried", "homemade",  
            "fortified", "white", "salt", "product", "fat", "brine", "rtd", 
            "vol", "based", "plant", "fresh", "whole", "cooked",      
            "sauce", "soup", "protein"}
    ## diagnose        
    other_words = Counter()                  
    with open("foods.csv", newline="") as f: 
        for row in csv.DictReader(f):        
            if classify(row["namn"]) == "Other":          
                for w in re.findall(r"[a-z]+", row["namn"].lower()):  
                    if len(w) > 2 and w not in SKIP: 
                        other_words[w] += 1  
    print()                                  
    print("top UNKNOWN words inside Other:")         
    for w, n in other_words.most_common(25): 
        print(f"{n:5d}  {w}")                
