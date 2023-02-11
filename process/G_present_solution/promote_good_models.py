# https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
#os.listdir() returns everything inside a directory -- including both files and directories.

#os.path's isfile() can be used to only list files:
mypath = "model_list/initial_trained_models"
newpath = "model_list/webapp_final_models"

from os import listdir
from os.path import isfile, join
#onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))] #os.path's isfile() can be used to only list files:
onlyfiles = [f for f in listdir(mypath) if ('(v' in f and not isfile(join(mypath, f))) or '.pkl' in f]

#print(onlyfiles)
print("\n\n")
print("PROMOTE THE BEST MODELS INTO THE WEBAPP")
print("---------------------------------------\n")
for i, each in zip(range(len(onlyfiles)), onlyfiles):
    print(f"{i+1}: {each}")

if len(onlyfiles) == 0:
    print("There are no promotable models available, try training some models first!")
    print("Exiting.")
    print("\n")
    quit()
    
output = input("\nWhich model do you want to promote?  ")

try:
    promotable = int(output) - 1
    if promotable < 0 or promotable > len(onlyfiles) - 1:
        raise ValueError()
        
    promote = onlyfiles[promotable]
    print(promote)
    
    import os
    import shutil

    os.rename(f"{mypath}/{promote}", f"{newpath}/{promote}")
    #os.replace("path/to/current/file.foo", "path/to/new/destination/for/file.foo")
    #shutil.move("path/to/current/file.foo", "path/to/new/destination/for/file.foo")

    
except ValueError:
    print(f"\nYou didn't enter a number between 1 and {len(onlyfiles)}. Exiting!\n")