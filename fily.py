import sys, os, shutil, re
from pathlib import Path

###   Creates an empty folder. If the folder exists, it will be erased
def touchFolder(folderName):                
    try: 
        os.rmdir(folderName)                          
    except FileNotFoundError:
        print("Create temporal folder  " + str(folderName))
    except OSError:
        shutil.rmtree(folderName, ignore_errors=True) 
    os.makedirs(folderName)

###   Creates an empty file. If the file exists, it will be erased
def touchFile(fileName):
    if not os.path.exists(fileName):
        Path(fileName).touch()
    else:
        os.remove(fileName)
        Path(fileName).touch()

###   Starts a new GEO file with initialization of indeces of the GEO 
###     features 
def resetFile(nameFile,extension):
    try: 
        with open(nameFile,"w") as outFile:
            if extension in ["GEO"]:
                outFile.write('P=1;\nL=1;\nLL=1;\nPS=0;\n\n')                
            elif extension in ["T3S"]:
                outFile.write('')
            else:
                print("Error in f.resetFile")
            outFile.close()
    except FileNotFoundError:
        print("File could not be found when reseting")

###   Reads a file without parsing by columns
#def readFile(pathToFile):
    # try: 
    #     X = (open(pathToFile,"r"))
    #     return(X)
    # except FileNotFoundError:
    #     print("in f.readFile\n " + str(pathToFile) + " could not be found\n")
    # try: 
    #     with open(pathToFile,"r") as X:
    #         return(X)
    # except FileNotFoundError:
    #     print("in f.readFile\n " + str(pathToFile) + " could not be found\n")

###   Appends a list to a file
def appendFile(what, whereToFile, isString = False):
    if not isString :
        with open(whereToFile,"a") as outFile:
            for i in range(len(what)):
                outFile.write(str(what[i]) + "\n")
            outFile.close()
    else:
        with open(whereToFile,"a") as outFile:
            outFile.write(str(what))
            outFile.close()

###   Takes a text file and splits it as a list of strings. Each line
###     on the file is an element of the list
def parseFile(pathToFile):
    try: 
        with open(pathToFile,"r") as varFile:
            X = str(varFile.read())
        return(X.split("\n"))
    except FileNotFoundError:
        print("in f.parseFile\n " + str(pathToFile) + " could not be found\n")
