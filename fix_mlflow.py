## this little script makes the model paths relative so docker can find the model later

## i need two helpers from python
import sqlite3                              
import shutil                                

## make a backup of the database before i change anything, in case i mess up
shutil.copy("mlflow.db", "mlflow.db.bak")    
print("backup made: mlflow.db.bak")          

## this is the long part of the path that i want to delete from the database
old_path = "/Users/jyx/dev/nutrition_ops/"    

## open the database so i can edit it
con = sqlite3.connect("mlflow.db")            
cur = con.cursor()                           

## cut the long path out of the three tables where mlflow saved it
cur.execute("UPDATE experiments SET artifact_location = REPLACE(artifact_location, ?, '')", (old_path,))     
cur.execute("UPDATE logged_models SET artifact_location = REPLACE(artifact_location, ?, '')", (old_path,))
cur.execute("UPDATE runs SET artifact_uri = REPLACE(artifact_uri, ?, '')", (old_path,))                      

## save the changes and close the database
con.commit()                                 
con.close()                                  
print("done, the paths are now relative")
